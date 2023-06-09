"""Alterar tipo de coluna da imagem de string para binário

Revision ID: 82d1513e711a
Revises: 
Create Date: 2023-04-27 21:20:06.706021

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '82d1513e711a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('wallpaper', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('image', sa.LargeBinary(), nullable=False, default=b''))
        batch_op.drop_column('image_url')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('wallpaper', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_url', sa.VARCHAR(
            length=256), autoincrement=False, nullable=False))
        batch_op.drop_column('image')

    # ### end Alembic commands ###
