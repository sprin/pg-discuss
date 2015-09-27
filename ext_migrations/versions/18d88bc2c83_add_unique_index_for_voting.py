"""Add unique index for voting

Revision ID: 18d88bc2c83
Revises: 
Create Date: 2015-09-27 21:17:27.003073

"""

# revision identifiers, used by Alembic.
revision = '18d88bc2c83'
down_revision = None

from alembic import op

def upgrade():
    op.get_bind().execute('''
CREATE UNIQUE INDEX _voting_uc
ON identity_comment (identity_id, comment_id)
WHERE (rel_type = 'upvote' OR rel_type='downvote');
''')


def downgrade():
    op.get_bind().execute('''
DROP INDEX _voting_uc
''')
