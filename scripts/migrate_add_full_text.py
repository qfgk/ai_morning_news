"""
数据库迁移脚本：添加 full_text 字段

为 daily_briefings 表添加 full_text 字段
"""
from database.base import get_db_manager


def migrate():
    """执行迁移"""
    print("=" * 60)
    print("数据库迁移：添加 full_text 字段")
    print("=" * 60)

    try:
        db_manager = get_db_manager()

        # 检查字段是否已存在
        from sqlalchemy import text
        with db_manager.get_session() as session:
            result = session.execute(text(
                "SHOW COLUMNS FROM daily_briefings LIKE 'full_text'"
            ))
            exists = result.fetchone()

            if exists:
                print("✓ full_text 字段已存在，无需迁移")
                return

        # 添加字段
        print("正在添加 full_text 字段...")
        with db_manager.get_session() as session:
            session.execute(text(
                "ALTER TABLE daily_briefings "
                "ADD COLUMN full_text TEXT COMMENT '完整的格式化早报文本（可直接发送）' "
                "AFTER ai_summary"
            ))
            session.commit()

        print("✓ 迁移成功！")

    except Exception as e:
        print(f"✗ 迁移失败: {e}")
        raise


if __name__ == '__main__':
    migrate()
