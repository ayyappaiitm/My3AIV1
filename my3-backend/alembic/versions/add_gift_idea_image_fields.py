"""add gift idea image and personalized reason fields

Revision ID: add_gift_idea_image_fields
Revises: add_recipient_address_fields
Create Date: 2025-01-02 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_gift_idea_image_fields'
down_revision: Union[str, None] = 'add_recipient_address_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    # Add new columns to gift_ideas table
    op.add_column('gift_ideas', sa.Column('personalized_reason', sa.Text(), nullable=True))
    op.add_column('gift_ideas', sa.Column('image_url', sa.String(500), nullable=True))


def downgrade() -> None:
    # Remove columns from gift_ideas table
    op.drop_column('gift_ideas', 'image_url')
    op.drop_column('gift_ideas', 'personalized_reason')

