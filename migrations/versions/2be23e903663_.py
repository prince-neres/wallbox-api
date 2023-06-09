"""empty message

Revision ID: 2be23e903663
Revises: 8106675005a1
Create Date: 2023-05-01 23:46:00.395131

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2be23e903663'
down_revision = '8106675005a1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('wallpaper', schema=None) as batch_op:
        batch_op.alter_column('image',
               existing_type=postgresql.BYTEA(),
               type_=sa.String(length=500),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('wallpaper', schema=None) as batch_op:
        batch_op.alter_column('image',
               existing_type=sa.String(length=500),
               type_=postgresql.BYTEA(),
               existing_nullable=False)

    # ### end Alembic commands ###
