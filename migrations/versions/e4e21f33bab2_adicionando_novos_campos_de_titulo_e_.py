"""Adicionando novos campos de titulo e nome de arquivo

Revision ID: e4e21f33bab2
Revises: 82d1513e711a
Create Date: 2023-04-27 21:55:39.648552

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4e21f33bab2'
down_revision = '82d1513e711a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('wallpaper', schema=None) as batch_op:
        batch_op.add_column(sa.Column('title', sa.String(length=200), nullable=False))
        batch_op.add_column(sa.Column('filename', sa.String(length=500), nullable=False))
        batch_op.drop_column('name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('wallpaper', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.VARCHAR(length=200), autoincrement=False, nullable=False))
        batch_op.drop_column('filename')
        batch_op.drop_column('title')

    # ### end Alembic commands ###
