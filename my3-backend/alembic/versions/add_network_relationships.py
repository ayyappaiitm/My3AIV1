"""add network relationships

Revision ID: add_network_relationships
Revises: f3f37db5d6a6
Create Date: 2025-01-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_network_relationships'
down_revision: Union[str, None] = 'f3f37db5d6a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    # Check if columns already exist before adding
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_columns = [col['name'] for col in inspector.get_columns('recipients')]
    
    # Add new columns to recipients table if they don't exist
    if 'is_core_contact' not in existing_columns:
        op.add_column('recipients', sa.Column('is_core_contact', sa.Boolean(), nullable=True, server_default='true'))
        op.execute("UPDATE recipients SET is_core_contact = true WHERE is_core_contact IS NULL")
        op.alter_column('recipients', 'is_core_contact', nullable=False)
    
    if 'network_level' not in existing_columns:
        op.add_column('recipients', sa.Column('network_level', sa.Integer(), nullable=True, server_default='1'))
        op.execute("UPDATE recipients SET network_level = 1 WHERE network_level IS NULL")
        op.alter_column('recipients', 'network_level', nullable=False)
    
    # Check if table already exists
    existing_tables = inspector.get_table_names()
    
    # Create recipient_relationships table if it doesn't exist
    if 'recipient_relationships' not in existing_tables:
        op.create_table(
            'recipient_relationships',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('from_recipient_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('to_recipient_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('relationship_type', sa.String(100), nullable=False),
            sa.Column('is_bidirectional', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['from_recipient_id'], ['recipients.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['to_recipient_id'], ['recipients.id'], ondelete='CASCADE'),
        )
        
        # Create indexes for better query performance
        op.create_index('ix_recipient_relationships_user_id', 'recipient_relationships', ['user_id'])
        op.create_index('ix_recipient_relationships_from_recipient', 'recipient_relationships', ['from_recipient_id'])
        op.create_index('ix_recipient_relationships_to_recipient', 'recipient_relationships', ['to_recipient_id'])
        op.create_index('ix_recipient_relationships_type', 'recipient_relationships', ['relationship_type'])
    else:
        # Table exists, check if indexes exist
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('recipient_relationships')]
        index_names = [
            'ix_recipient_relationships_user_id',
            'ix_recipient_relationships_from_recipient',
            'ix_recipient_relationships_to_recipient',
            'ix_recipient_relationships_type'
        ]
        for idx_name in index_names:
            if idx_name not in existing_indexes:
                if idx_name == 'ix_recipient_relationships_user_id':
                    op.create_index(idx_name, 'recipient_relationships', ['user_id'])
                elif idx_name == 'ix_recipient_relationships_from_recipient':
                    op.create_index(idx_name, 'recipient_relationships', ['from_recipient_id'])
                elif idx_name == 'ix_recipient_relationships_to_recipient':
                    op.create_index(idx_name, 'recipient_relationships', ['to_recipient_id'])
                elif idx_name == 'ix_recipient_relationships_type':
                    op.create_index(idx_name, 'recipient_relationships', ['relationship_type'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_recipient_relationships_type', table_name='recipient_relationships')
    op.drop_index('ix_recipient_relationships_to_recipient', table_name='recipient_relationships')
    op.drop_index('ix_recipient_relationships_from_recipient', table_name='recipient_relationships')
    op.drop_index('ix_recipient_relationships_user_id', table_name='recipient_relationships')
    
    # Drop recipient_relationships table
    op.drop_table('recipient_relationships')
    
    # Remove columns from recipients table
    op.drop_column('recipients', 'network_level')
    op.drop_column('recipients', 'is_core_contact')

