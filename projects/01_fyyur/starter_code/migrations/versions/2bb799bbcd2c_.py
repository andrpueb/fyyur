"""empty message

Revision ID: 2bb799bbcd2c
Revises: caf24d16e2ed
Create Date: 2020-11-29 16:11:28.399660

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2bb799bbcd2c'
down_revision = 'caf24d16e2ed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('shows',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('show_date', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ),
    sa.PrimaryKeyConstraint('id', 'venue_id', 'artist_id')
    )
    op.drop_table('Shows')
    op.drop_constraint('Artist_show_id_fkey', 'Artist', type_='foreignkey')
    op.drop_column('Artist', 'show_id')
    op.drop_constraint('Venue_show_id_fkey', 'Venue', type_='foreignkey')
    op.drop_column('Venue', 'show_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('show_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('Venue_show_id_fkey', 'Venue', 'Shows', ['show_id'], ['id'])
    op.add_column('Artist', sa.Column('show_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('Artist_show_id_fkey', 'Artist', 'Shows', ['show_id'], ['id'])
    op.create_table('Shows',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"Shows_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('date', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='Shows_pkey')
    )
    op.drop_table('shows')
    # ### end Alembic commands ###
