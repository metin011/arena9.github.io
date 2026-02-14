"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}
"""

from alembic import op
import sqlalchemy as sa

${exports if exports}

def upgrade():
    ${upgrade_ops if upgrade_ops else 'pass'}


def downgrade():
    ${downgrade_ops if downgrade_ops else 'pass'}
