"""Restore user role field

Revision ID: a9e08e8f4caf
Revises: 4c385095699c
Create Date: 2026-08-20
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a9e08e8f4caf"

down_revision = "4c385095699c"

branch_labels = None

depends_on = None


def upgrade():

    # ------------------------------------------------------
    # ADD ROLE COLUMN
    # ------------------------------------------------------
    #
    # Existing users will temporarily receive "customer".
    #

    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
            server_default="customer"
        )
    )

    # ------------------------------------------------------
    # REMOVE SERVER DEFAULT
    # ------------------------------------------------------
    #
    # The application model already has:
    #
    # default="customer"
    #
    # Therefore we don't need PostgreSQL to keep the
    # server-side default permanently.
    #

    op.alter_column(
        "users",
        "role",
        server_default=None
    )


def downgrade():

    # ------------------------------------------------------
    # REMOVE ROLE COLUMN
    # ------------------------------------------------------

    op.drop_column(
        "users",
        "role"
    )