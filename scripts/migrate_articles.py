"""
数据迁移脚本
将 articles_data.json 迁移到数据库
"""

import sys
import os
import json
import asyncio

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from database import get_db_manager, session_scope
from database.models import ArticleDB, DailyBriefingDB
from datetime import datetime


def migrate_articles_from_json(json_file: str = "articles_data.json"):
    """从JSON文件迁移文章数据"""

    print("=" * 60)
    print("📦 数据迁移: JSON -> 数据库")
    print("=" * 60)

    # 检查文件是否存在
    if not os.path.exists(json_file):
        print(f"❌ 错误: 文件不存在 - {json_file}")
        return

    # 读取JSON数据
    print(f"\n📂 读取文件: {json_file}")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not data:
        print("⚠️  文件中没有数据")
        return

    print(f"   找到 {len(data)} 篇文章")

    # 迁移数据
    print(f"\n🔄 开始迁移...")
    success_count = 0
    error_count = 0

    with session_scope() as session:
        for item in data:
            try:
                # 检查是否已存在（根据source_url）
                existing = session.query(ArticleDB).filter_by(
                    source_url=item.get('source_url', '')
                ).first()

                if existing:
                    print(f"   ⏭️  跳过: {item.get('title', '')[:30]}...")
                    continue

                # 创建新记录
                article = ArticleDB(
                    title=item.get('title', ''),
                    content=item.get('content', ''),
                    author=item.get('author'),
                    publication_date=item.get('publication_date'),
                    source_url=item.get('source_url', ''),
                    source_type='aibase',  # 默认为aibase
                    summary=item.get('summary'),
                    status='completed'
                )
                session.add(article)
                success_count += 1
                print(f"   ✅ {item.get('title', '')[:30]}...")

            except Exception as e:
                error_count += 1
                print(f"   ❌ 迁移失败: {e}")

    print(f"\n" + "=" * 60)
    print(f"✅ 迁移完成！")
    print(f"   成功: {success_count} 篇")
    print(f"   失败: {error_count} 篇")
    print("=" * 60)


def main():
    """主函数"""
    migrate_articles_from_json()


if __name__ == "__main__":
    main()
