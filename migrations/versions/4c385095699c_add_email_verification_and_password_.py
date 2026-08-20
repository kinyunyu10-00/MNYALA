"""
Add email verification and password reset fields

Revision ID: 4c385095699c
Revises: be8a265f0303
Create Date: 2026-08-20 10:32:47.541379

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '4c385095699c'
down_revision = 'be8a265f0303'
branch_labels = None
depends_on = None


def upgrade():
    # ---------------------------------------------------------
    # 1. Drop old password reset tokens table
    # ---------------------------------------------------------
    op.drop_table('password_reset_tokens')

    # ---------------------------------------------------------
    # 2. Update messages table
    # ---------------------------------------------------------
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.alter_column(
            'subject',
            existing_type=sa.VARCHAR(length=200),
            type_=sa.String(length=100),
            existing_nullable=True
        )

    # ---------------------------------------------------------
    # 3. Add new columns to users table
    # ---------------------------------------------------------
    #
    # IMPORTANT:
    # username and email_verified are initially nullable
    # because existing users already exist in the database.
    #
    with op.batch_alter_table('users', schema=None) as batch_op:

        batch_op.add_column(
            sa.Column(
                'username',
                sa.String(length=100),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                'email_verified',
                sa.Boolean(),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                'verification_token',
                sa.String(length=255),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                'verification_token_expires',
                sa.DateTime(),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                'reset_token',
                sa.String(length=255),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                'reset_token_expires',
                sa.DateTime(),
                nullable=True
            )
        )

    # ---------------------------------------------------------
    # 4. Give existing users a username
    # ---------------------------------------------------------
    #
    # Example:
    # user ID 1 -> user_1
    # user ID 2 -> user_2
    #
    op.execute("""
        UPDATE users
        SET username = 'user_' || id
        WHERE username IS NULL
    """)

    # ---------------------------------------------------------
    # 5. Mark existing users as email verified
    # ---------------------------------------------------------
    #
    # Existing users are considered verified so they can
    # continue using their existing accounts.
    #
    op.execute("""
        UPDATE users
        SET email_verified = TRUE
        WHERE email_verified IS NULL
    """)

    # ---------------------------------------------------------
    # 6. Change username and email_verified to NOT NULL
    # ---------------------------------------------------------
    with op.batch_alter_table('users', schema=None) as batch_op:

        batch_op.alter_column(
            'username',
            existing_type=sa.String(length=100),
            nullable=False
        )

        batch_op.alter_column(
            'email_verified',
            existing_type=sa.Boolean(),
            nullable=False
        )

    # ---------------------------------------------------------
    # 7. Remove old columns
    # ---------------------------------------------------------
    with op.batch_alter_table('users', schema=None) as batch_op:

        batch_op.drop_column('fullname')
        batch_op.drop_column('created_at')
        batch_op.drop_column('role')


def downgrade():

    # ---------------------------------------------------------
    # 1. Restore old users columns
    # ---------------------------------------------------------
    with op.batch_alter_table('users', schema=None) as batch_op:

        batch_op.add_column(
            sa.Column(
                'role',
                sa.VARCHAR(length=20),
                autoincrement=False,
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                'created_at',
                postgresql.TIMESTAMP(),
                server_default=sa.text('now()'),
                autoincrement=False,
                nullable=True
            )
        )

        # IMPORTANT:
        # fullname is restored as nullable=True first so that
        # existing users do not cause a NOT NULL error.
        batch_op.add_column(
            sa.Column(
                'fullname',
                sa.VARCHAR(length=100),
                autoincrement=False,
                nullable=True
            )
        )

        # Remove new password/email fields
        batch_op.drop_column('reset_token_expires')
        batch_op.drop_column('reset_token')
        batch_op.drop_column('verification_token_expires')
        batch_op.drop_column('verification_token')
        batch_op.drop_column('email_verified')
        batch_op.drop_column('username')

    # ---------------------------------------------------------
    # 2. Restore messages.subject length
    # ---------------------------------------------------------
    with op.batch_alter_table('messages', schema=None) as batch_op:

        batch_op.alter_column(
            'subject',
            existing_type=sa.String(length=100),
            type_=sa.VARCHAR(length=200),
            existing_nullable=True
        )

    # ---------------------------------------------------------
    # 3. Recreate password_reset_tokens table
    # ---------------------------------------------------------
    op.create_table(
        'password_reset_tokens',

        sa.Column(
            'id',
            sa.INTEGER(),
            autoincrement=True,
            nullable=False
        ),

        sa.Column(
            'user_id',
            sa.INTEGER(),
            autoincrement=False,
            nullable=False
        ),

        sa.Column(
            'token',
            sa.VARCHAR(length=255),
            autoincrement=False,
            nullable=False
        ),

        sa.Column(
            'expires_at',
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=False
        ),

        sa.Column(
            'created_at',
            postgresql.TIMESTAMP(),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            autoincrement=False,
            nullable=True
        ),

        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
            name=op.f('fk_password_reset_user'),
            ondelete='CASCADE'
        ),

        sa.PrimaryKeyConstraint(
            'id',
            name=op.f('password_reset_tokens_pkey')
        ),

        sa.UniqueConstraint(
            'token',
            name=op.f('password_reset_tokens_token_key'),
            postgresql_include=[],
            postgresql_nulls_not_distinct=False
        )
    )