"""add country_codes table

Revision ID: 0fc36eff189a
Revises: a1ca152082e9
Create Date: 2018-08-09 23:13:47.509786

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0fc36eff189a'
down_revision = 'a1ca152082e9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('country_codes',
    sa.Column('country_id', sa.Integer(), nullable=False),
    sa.Column('country_code', sa.String(length=2), nullable=True),
    sa.ForeignKeyConstraint(['country_id'], ['countries.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('country_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('country_codes')
    # ### end Alembic commands ###