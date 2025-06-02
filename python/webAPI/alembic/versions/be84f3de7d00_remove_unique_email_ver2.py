"""remove_unique email ver2

Revision ID: be84f3de7d00
Revises: 3072676c13f7
Create Date: 2025-05-20 10:44:37.352929

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'be84f3de7d00'
down_revision = '3072676c13f7'
branch_labels = None
depends_on = None


def upgrade():
   # 1. Создаем новую таблицу без UNIQUE(email)
    op.execute("""
        CREATE TABLE users_tmp (
            id VARCHAR NOT NULL PRIMARY KEY,
            name VARCHAR NOT NULL,
            email VARCHAR
        );
    """)
    # 2. Копируем данные
    op.execute("""
        INSERT INTO users_tmp (id, name, email)
        SELECT id, name, email FROM users;
    """)
    # 3. Удаляем старую таблицу
    op.execute("DROP TABLE users;")
    # 4. Переименовываем временную таблицу
    op.execute("ALTER TABLE users_tmp RENAME TO users;")


def downgrade():
    # (По желанию — возврат ограничения UNIQUE, если потребуется откат)
    op.execute("""
        CREATE TABLE users_tmp (
            id VARCHAR NOT NULL PRIMARY KEY,
            name VARCHAR NOT NULL,
            email VARCHAR UNIQUE
        );
    """)
    op.execute("""
        INSERT INTO users_tmp (id, name, email)
        SELECT id, name, email FROM users;
    """)
    op.execute("DROP TABLE users;")
    op.execute("ALTER TABLE users_tmp RENAME TO users;")
