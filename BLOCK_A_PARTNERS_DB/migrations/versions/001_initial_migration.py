"""Создание таблиц партнеров и логов верификации

Revision ID: 001_initial_migration
Revises: 
Create Date: 2024-01-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Таблица партнеров
    op.create_table('partners',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('public_id', sa.String(length=50), nullable=False),
        sa.Column('company_name', sa.String(length=200), nullable=False),
        sa.Column('trading_name', sa.String(length=200), nullable=True),
        sa.Column('legal_form', sa.Enum('OOO', 'IP', 'AO', 'ZAO', 'INVALID', name='legalform'), nullable=False),
        sa.Column('inn', sa.String(length=12), nullable=False),
        sa.Column('ogrn', sa.String(length=15), nullable=True),
        sa.Column('kpp', sa.String(length=9), nullable=True),
        sa.Column('legal_address', sa.Text(), nullable=False),
        sa.Column('actual_address', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=120), nullable=True),
        sa.Column('website', sa.String(length=200), nullable=True),
        sa.Column('contact_person', sa.String(length=100), nullable=True),
        sa.Column('contact_position', sa.String(length=100), nullable=True),
        sa.Column('telegram', sa.String(length=100), nullable=True),
        sa.Column('whatsapp', sa.String(length=20), nullable=True),
        sa.Column('main_category', sa.String(length=100), nullable=True),
        sa.Column('specializations', sa.JSON(), nullable=True),
        sa.Column('services', sa.JSON(), nullable=True),
        sa.Column('portfolio', sa.JSON(), nullable=True),
        sa.Column('regions', sa.JSON(), nullable=True),
        sa.Column('cities', sa.JSON(), nullable=True),
        sa.Column('work_radius_km', sa.Integer(), nullable=True),
        sa.Column('verification_status', sa.Enum('PENDING', 'IN_PROGRESS', 'VERIFIED', 'REJECTED', 'SUSPENDED', name='verificationstatus'), nullable=True),
        sa.Column('verification_score', sa.Float(), nullable=True),
        sa.Column('verification_date', sa.DateTime(), nullable=True),
        sa.Column('verified_by', sa.String(length=50), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('documents', sa.JSON(), nullable=True),
        sa.Column('tier', sa.Enum('BASIC', 'PRO', 'ENTERPRISE', name='partnertier'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_blocked', sa.Boolean(), nullable=True),
        sa.Column('max_active_leads', sa.Integer(), nullable=True),
        sa.Column('subscription_expires', sa.DateTime(), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('reviews_count', sa.Integer(), nullable=True),
        sa.Column('completed_projects', sa.Integer(), nullable=True),
        sa.Column('response_time_avg', sa.Float(), nullable=True),
        sa.Column('created_by', sa.String(length=50), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('inn'),
        sa.UniqueConstraint('public_id')
    )
    
    # Таблица логов верификации
    op.create_table('verification_logs',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('partner_id', postgresql.UUID(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('performed_by', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['partner_id'], ['partners.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создание индексов
    op.create_index('idx_partners_verification_status', 'partners', ['verification_status'], unique=False)
    op.create_index('idx_partners_is_active', 'partners', ['is_active'], unique=False)
    op.create_index('idx_partners_rating', 'partners', ['rating'], unique=False)
    op.create_index('idx_partners_created_at', 'partners', ['created_at'], unique=False)


def downgrade():
    op.drop_table('verification_logs')
    op.drop_table('partners')
    op.execute('DROP TYPE legalform')
    op.execute('DROP TYPE verificationstatus')
    op.execute('DROP TYPE partnertier')
