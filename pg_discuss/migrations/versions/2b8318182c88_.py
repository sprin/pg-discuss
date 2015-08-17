"""empty message

Revision ID: 2b8318182c88
Revises: None
Create Date: 2015-08-17 20:05:36.188551

"""

# revision identifiers, used by Alembic.
revision = '2b8318182c88'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('comment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tid', sa.Integer(), nullable=True),
    sa.Column('parent', sa.Integer(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('modified', sa.DateTime(), nullable=True),
    sa.Column('text', sa.String(), nullable=True),
    sa.Column('custom_json', postgresql.JSONB(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('thread',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('thread')
    op.drop_table('comment')
    ### end Alembic commands ###
