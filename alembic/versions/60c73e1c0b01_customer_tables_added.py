"""Customer Tables Added

Revision ID: 60c73e1c0b01
Revises: 72a42c578142
Create Date: 2025-05-20 17:57:37.847866

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '60c73e1c0b01'
down_revision: Union[str, None] = '72a42c578142'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('auctionsbigstar',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('auction_name', sa.String(length=55), nullable=True),
    sa.Column('auction_location', sa.String(length=55), nullable=True),
    sa.Column('auction_status', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auctionsbigstar_id'), 'auctionsbigstar', ['id'], unique=False)
    op.create_table('customerauction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('phone_number', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customerauction_id'), 'customerauction', ['id'], unique=False)
    op.create_table('customers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('phone_number', sa.String(length=20), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customers_id'), 'customers', ['id'], unique=False)
    op.create_table('itemss',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('item_type', sa.String(length=55), nullable=False),
    sa.Column('item_name', sa.String(length=255), nullable=False),
    sa.Column('chassis_number', sa.String(length=55), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('notes', sa.String(length=255), nullable=True),
    sa.Column('offer_price', sa.Float(), nullable=True),
    sa.Column('status', sa.String(length=55), nullable=False),
    sa.Column('category', sa.String(length=55), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_itemss_customer_id'), 'itemss', ['customer_id'], unique=False)
    op.create_index(op.f('ix_itemss_id'), 'itemss', ['id'], unique=False)
    op.create_table('transactionss',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
    sa.ForeignKeyConstraint(['item_id'], ['itemss.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transactionss_customer_id'), 'transactionss', ['customer_id'], unique=False)
    op.create_index(op.f('ix_transactionss_id'), 'transactionss', ['id'], unique=False)
    op.create_index(op.f('ix_transactionss_item_id'), 'transactionss', ['item_id'], unique=False)
    op.create_table('customerauctionsbids',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fk_customer_id', sa.Integer(), nullable=True),
    sa.Column('fk_auctionbigstar_id', sa.Integer(), nullable=True),
    sa.Column('fk_vehicle_id', sa.Integer(), nullable=True),
    sa.Column('fk_truck_id', sa.Integer(), nullable=True),
    sa.Column('fk_part_id', sa.Integer(), nullable=True),
    sa.Column('bid_amount', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['fk_auctionbigstar_id'], ['auctionsbigstar.id'], ),
    sa.ForeignKeyConstraint(['fk_customer_id'], ['customerauction.id'], ),
    sa.ForeignKeyConstraint(['fk_part_id'], ['spareparts.id'], ),
    sa.ForeignKeyConstraint(['fk_truck_id'], ['trucks.id'], ),
    sa.ForeignKeyConstraint(['fk_vehicle_id'], ['vehicles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customerauctionsbids_fk_auctionbigstar_id'), 'customerauctionsbids', ['fk_auctionbigstar_id'], unique=False)
    op.create_index(op.f('ix_customerauctionsbids_fk_customer_id'), 'customerauctionsbids', ['fk_customer_id'], unique=False)
    op.create_index(op.f('ix_customerauctionsbids_fk_part_id'), 'customerauctionsbids', ['fk_part_id'], unique=False)
    op.create_index(op.f('ix_customerauctionsbids_fk_truck_id'), 'customerauctionsbids', ['fk_truck_id'], unique=False)
    op.create_index(op.f('ix_customerauctionsbids_fk_vehicle_id'), 'customerauctionsbids', ['fk_vehicle_id'], unique=False)
    op.create_index(op.f('ix_customerauctionsbids_id'), 'customerauctionsbids', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_customerauctionsbids_id'), table_name='customerauctionsbids')
    op.drop_index(op.f('ix_customerauctionsbids_fk_vehicle_id'), table_name='customerauctionsbids')
    op.drop_index(op.f('ix_customerauctionsbids_fk_truck_id'), table_name='customerauctionsbids')
    op.drop_index(op.f('ix_customerauctionsbids_fk_part_id'), table_name='customerauctionsbids')
    op.drop_index(op.f('ix_customerauctionsbids_fk_customer_id'), table_name='customerauctionsbids')
    op.drop_index(op.f('ix_customerauctionsbids_fk_auctionbigstar_id'), table_name='customerauctionsbids')
    op.drop_table('customerauctionsbids')
    op.drop_index(op.f('ix_transactionss_item_id'), table_name='transactionss')
    op.drop_index(op.f('ix_transactionss_id'), table_name='transactionss')
    op.drop_index(op.f('ix_transactionss_customer_id'), table_name='transactionss')
    op.drop_table('transactionss')
    op.drop_index(op.f('ix_itemss_id'), table_name='itemss')
    op.drop_index(op.f('ix_itemss_customer_id'), table_name='itemss')
    op.drop_table('itemss')
    op.drop_index(op.f('ix_customers_id'), table_name='customers')
    op.drop_table('customers')
    op.drop_index(op.f('ix_customerauction_id'), table_name='customerauction')
    op.drop_table('customerauction')
    op.drop_index(op.f('ix_auctionsbigstar_id'), table_name='auctionsbigstar')
    op.drop_table('auctionsbigstar')
    # ### end Alembic commands ###
