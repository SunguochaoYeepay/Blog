"""fix_is_superuser_null_values

Revision ID: 6ae879ae82aa
Revises: 43437a4d0a04
Create Date: 2024-03-21 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ae879ae82aa'
down_revision: Union[str, None] = '43437a4d0a04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. 将现有的 NULL 值更新为 False
    op.execute("""
        UPDATE users 
        SET is_superuser = FALSE 
        WHERE is_superuser IS NULL
    """)
    
    # 2. 修改列定义，设置 NOT NULL 约束和默认值
    op.alter_column('users', 'is_superuser',
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.text('FALSE'),
        existing_server_default=None
    )


def downgrade() -> None:
    # 移除 NOT NULL 约束和默认值
    op.alter_column('users', 'is_superuser',
        existing_type=sa.Boolean(),
        nullable=True,
        server_default=None,
        existing_server_default=sa.text('FALSE')
    )
