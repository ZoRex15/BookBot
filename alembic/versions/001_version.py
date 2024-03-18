import sqlalchemy as sa
from alembic import op


revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'Users',
        sa.Column('id', sa.Integer ,primary_key=True),
        sa.Column('page', sa.Integer, default=1, nullable=False)
    )

    op.create_table(
        'Bookmarks',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('Users.id')),
        sa.Column('page', sa.Integer, nullable=False)
    )

def downgrade():
    op.drop_table('Users')
    op.drop_table('Bookmarks')
    