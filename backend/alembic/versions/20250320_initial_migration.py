"""Initial migration

Revision ID: 2025_03_20_initial
Revises: 
Create Date: 2025-03-20 23:47

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2025_03_20_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 创建用户表
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('username', sa.String(32), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_staff', sa.Boolean(), nullable=False, default=False),
        sa.Column('full_name', sa.String(100), nullable=True),
        sa.Column('role', sa.String(20), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email'),
    )
    
    # 创建小说表
    op.create_table(
        'novel',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('genre', sa.String(50), nullable=True),
        sa.Column('target_word_count', sa.Integer(), nullable=False),
        sa.Column('current_word_count', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('PLANNING', 'WRITING', 'REVIEWING', 'COMPLETED', 'PAUSED', 'ABANDONED', name='novelstatus'), nullable=False),
        sa.Column('outline', sa.Text(), nullable=True),
        sa.Column('creator_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['creator_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # 创建章节表
    op.create_table(
        'chapter',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('chapter_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('word_count', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('novel_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['novel_id'], ['novel.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )

    # 创建角色表
    op.create_table(
        'character',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('role_type', sa.String(50), nullable=True),
        sa.Column('personality', sa.Text(), nullable=True),
        sa.Column('background', sa.Text(), nullable=True),
        sa.Column('novel_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['novel_id'], ['novel.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )

    # 创建事件表
    op.create_table(
        'event',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('chapter_number', sa.Integer(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('novel_id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['character_id'], ['character.id'], ),
        sa.ForeignKeyConstraint(['novel_id'], ['novel.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )

    # 创建Agent表
    op.create_table(
        'agent',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('agent_type', sa.Enum('PLOT', 'CHARACTER', 'SCENE', 'WRITING', 'QA', 'COHERENCE', name='agenttype'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('IDLE', 'WORKING', 'PAUSED', 'ERROR', name='agentstatus'), nullable=False),
        sa.Column('parameters', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('stats', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

def downgrade() -> None:
    # 按照依赖关系的反序删除表
    op.drop_table('event')
    op.drop_table('character')
    op.drop_table('chapter')
    op.drop_table('novel')
    op.drop_table('agent')
    op.drop_table('user')
    
    # 删除枚举类型
    op.execute('DROP TYPE IF EXISTS novelstatus')
    op.execute('DROP TYPE IF EXISTS agenttype')
    op.execute('DROP TYPE IF EXISTS agentstatus')