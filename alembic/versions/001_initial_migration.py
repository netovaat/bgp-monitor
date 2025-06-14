"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-12-09 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    
    # Create asn_snapshots table
    op.create_table(
        'asn_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asn', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('announced_prefixes', sa.JSON(), nullable=False),
        sa.Column('prefix_count', sa.Integer(), nullable=False),
        sa.Column('peer_data', sa.JSON(), nullable=True),
        sa.Column('upstream_count', sa.Integer(), nullable=True),
        sa.Column('is_announcing', sa.Boolean(), nullable=False),
        sa.Column('data_source', sa.String(length=50), nullable=False),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_asn_timestamp', 'asn_snapshots', ['asn', 'timestamp'], unique=False)
    op.create_index('idx_timestamp_asn', 'asn_snapshots', ['timestamp', 'asn'], unique=False)
    op.create_index(op.f('ix_asn_snapshots_asn'), 'asn_snapshots', ['asn'], unique=False)
    op.create_index(op.f('ix_asn_snapshots_timestamp'), 'asn_snapshots', ['timestamp'], unique=False)
    
    # Create prefix_history table
    op.create_table(
        'prefix_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prefix', sa.String(length=43), nullable=False),
        sa.Column('asn', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('is_announced', sa.Boolean(), nullable=False),
        sa.Column('origin_asn', sa.Integer(), nullable=True),
        sa.Column('routing_status', sa.JSON(), nullable=True),
        sa.Column('as_path', sa.JSON(), nullable=True),
        sa.Column('data_source', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_asn_prefix_timestamp', 'prefix_history', ['asn', 'prefix', 'timestamp'], unique=False)
    op.create_index('idx_prefix_timestamp', 'prefix_history', ['prefix', 'timestamp'], unique=False)
    op.create_index(op.f('ix_prefix_history_asn'), 'prefix_history', ['asn'], unique=False)
    op.create_index(op.f('ix_prefix_history_prefix'), 'prefix_history', ['prefix'], unique=False)
    op.create_index(op.f('ix_prefix_history_timestamp'), 'prefix_history', ['timestamp'], unique=False)
    
    # Create bgp_alerts table
    op.create_table(
        'bgp_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asn', sa.Integer(), nullable=False),
        sa.Column('alert_type', sa.String(length=50), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('prefix', sa.String(length=43), nullable=True),
        sa.Column('old_value', sa.JSON(), nullable=True),
        sa.Column('new_value', sa.JSON(), nullable=True),
        sa.Column('acknowledged', sa.Boolean(), nullable=False),
        sa.Column('resolved', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_asn_alert_type_timestamp', 'bgp_alerts', ['asn', 'alert_type', 'timestamp'], unique=False)
    op.create_index(op.f('ix_bgp_alerts_alert_type'), 'bgp_alerts', ['alert_type'], unique=False)
    op.create_index(op.f('ix_bgp_alerts_asn'), 'bgp_alerts', ['asn'], unique=False)
    op.create_index(op.f('ix_bgp_alerts_prefix'), 'bgp_alerts', ['prefix'], unique=False)
    op.create_index(op.f('ix_bgp_alerts_timestamp'), 'bgp_alerts', ['timestamp'], unique=False)
    
    # Create system_metrics table
    op.create_table(
        'system_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('api_calls_count', sa.Integer(), nullable=False),
        sa.Column('api_errors_count', sa.Integer(), nullable=False),
        sa.Column('api_response_time_ms', sa.Integer(), nullable=True),
        sa.Column('asns_processed', sa.Integer(), nullable=False),
        sa.Column('prefixes_processed', sa.Integer(), nullable=False),
        sa.Column('alerts_generated', sa.Integer(), nullable=False),
        sa.Column('metrics_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_metrics_timestamp'), 'system_metrics', ['timestamp'], unique=False)
    
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('system_metrics')
    op.drop_table('bgp_alerts')
    op.drop_table('prefix_history')
    op.drop_table('asn_snapshots')
    # ### end Alembic commands ###
