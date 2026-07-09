"""Create Phone number for Users table

Revision ID: b1888c2a8ffc
Revises: 
Create Date: 2026-07-02 06:08:47.692344

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1888c2a8ffc'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users",sa.Column("phone_number",sa.String(),nullable=True)) # op references to alembic


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users","phone_number")
