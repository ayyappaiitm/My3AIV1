"""add recipient address fields

Revision ID: add_recipient_address_fields
Revises: add_network_relationships
Create Date: 2025-01-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_recipient_address_fields'
down_revision: Union[str, None] = 'add_network_relationships'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    # Add address columns to recipients table
    op.add_column('recipients', sa.Column('street_address', sa.String(255), nullable=True))
    op.add_column('recipients', sa.Column('city', sa.String(100), nullable=True))
    op.add_column('recipients', sa.Column('state_province', sa.String(100), nullable=True))
    op.add_column('recipients', sa.Column('postal_code', sa.String(20), nullable=True))
    op.add_column('recipients', sa.Column('country', sa.String(100), nullable=True))
    op.add_column('recipients', sa.Column('address_validation_status', sa.String(20), nullable=True))
    op.add_column('recipients', sa.Column('validated_address_json', sa.Text(), nullable=True))
    
    # Set default validation status for existing records
    op.execute("UPDATE recipients SET address_validation_status = 'unvalidated' WHERE address_validation_status IS NULL")


def downgrade() -> None:
    # Remove address columns from recipients table
    op.drop_column('recipients', 'validated_address_json')
    op.drop_column('recipients', 'address_validation_status')
    op.drop_column('recipients', 'country')
    op.drop_column('recipients', 'postal_code')
    op.drop_column('recipients', 'state_province')
    op.drop_column('recipients', 'city')
    op.drop_column('recipients', 'street_address')

