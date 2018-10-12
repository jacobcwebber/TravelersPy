"""empty message

Revision ID: 6a2169d168f4
Revises: e8fb8a8385b5
Create Date: 2018-08-11 00:37:54.056603

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a2169d168f4'
down_revision = 'e8fb8a8385b5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('countries', sa.Column('country_code', sa.String(length=2), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('dest_images', 'img_url',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    # ### end Alembic commands ###