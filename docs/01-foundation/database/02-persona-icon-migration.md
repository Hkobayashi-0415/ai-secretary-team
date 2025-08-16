# ペルソナアイコン・画像機能追加マイグレーション

## 1. 概要

AI秘書管理画面のアイコン・画像設定機能を実現するため、既存の`personas`テーブルにアイコン・画像関連フィールドを追加するマイグレーションファイル。

## 2. マイグレーション内容

### 2.1 追加フィールド
- `icon_url`: アイコン画像のURL（VARCHAR(500)）
- `image_url`: プロフィール画像のURL（VARCHAR(500)）
- `icon_type`: アイコンの種類（VARCHAR(50)）
- `icon_metadata`: アイコンの詳細設定（JSONB）

### 2.2 インデックス追加
- `idx_personas_icon_type`: アイコン種類での検索最適化

## 3. マイグレーションファイル

### 3.1 アップグレード（Upgrade）
```python
# alembic/versions/025_add_persona_icon_fields.py
"""Add icon and image fields to personas table

Revision ID: 025
Revises: 024
Create Date: 2025-08-13 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '025'
down_revision = '024'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # ペルソナテーブルにアイコン・画像フィールドを追加
    op.add_column('personas', sa.Column('icon_url', sa.String(500), nullable=True))
    op.add_column('personas', sa.Column('image_url', sa.String(500), nullable=True))
    op.add_column('personas', sa.Column('icon_type', sa.String(50), nullable=False, server_default='preset'))
    op.add_column('personas', sa.Column('icon_metadata', postgresql.JSONB, nullable=True, server_default='{}'))
    
    # アイコン種類でのインデックスを作成
    op.create_index('idx_personas_icon_type', 'personas', ['icon_type'])
    
    # 既存のペルソナにデフォルトアイコン設定を追加
    op.execute("""
        UPDATE personas 
        SET icon_metadata = '{"icon_name": "default", "color": "#6B7280", "style": "professional"}'
        WHERE icon_metadata IS NULL OR icon_metadata = '{}'
    """)

def downgrade() -> None:
    # インデックスを削除
    op.drop_index('idx_personas_icon_type', 'personas')
    
    # 追加したカラムを削除
    op.drop_column('personas', 'icon_metadata')
    op.drop_column('personas', 'icon_type')
    op.drop_column('personas', 'image_url')
    op.drop_column('personas', 'icon_url')
```

## 4. データ移行スクリプト

### 4.1 既存ペルソナのアイコン設定
```python
# scripts/migrate_persona_icons.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.persona import Persona
from app.core.config import settings

async def migrate_persona_icons():
    """既存のペルソナにデフォルトアイコン設定を適用"""
    
    # データベース接続
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 既存のペルソナを取得
        personas = await session.execute(
            sa.select(Persona).where(Persona.icon_metadata == {})
        )
        personas = personas.scalars().all()
        
        # デフォルトアイコン設定を適用
        default_icons = {
            'プロジェクトマネージャー': {
                'icon_name': 'project_manager',
                'color': '#3B82F6',
                'style': 'professional'
            },
            '技術アーキテクト': {
                'icon_name': 'tech_architect',
                'color': '#10B981',
                'style': 'technical'
            },
            'クリエイティブディレクター': {
                'icon_name': 'creative_director',
                'color': '#8B5CF6',
                'style': 'creative'
            },
            'データアナリスト': {
                'icon_name': 'data_analyst',
                'color': '#F59E0B',
                'style': 'analytical'
            },
            '司書AI': {
                'icon_name': 'librarian',
                'color': '#EF4444',
                'style': 'organized'
            }
        }
        
        for persona in personas:
            if persona.name in default_icons:
                persona.icon_metadata = default_icons[persona.name]
                persona.icon_type = 'preset'
        
        await session.commit()
        print(f"Updated {len(personas)} personas with default icons")

if __name__ == "__main__":
    asyncio.run(migrate_persona_icons())
```

## 5. テストデータ更新

### 5.1 テストデータのアイコン設定
```python
# tests/fixtures/persona_icons.py
import pytest
from app.models.persona import Persona

@pytest.fixture
def persona_with_icon():
    """アイコン設定済みのペルソナテストデータ"""
    return Persona(
        name="テストペルソナ",
        description="テスト用のペルソナ",
        personality="テスト的な性格",
        icon_type="preset",
        icon_metadata={
            "icon_name": "test_icon",
            "color": "#FF0000",
            "style": "test"
        }
    )

@pytest.fixture
def persona_with_uploaded_image():
    """アップロード画像設定済みのペルソナテストデータ"""
    return Persona(
        name="画像付きペルソナ",
        description="画像設定済みのペルソナ",
        personality="画像的な性格",
        icon_type="upload",
        image_url="/uploads/personas/test_image.jpg",
        icon_metadata={
            "original_filename": "test_image.jpg",
            "file_size": 1024000,
            "uploaded_at": "2025-08-13T15:00:00Z"
        }
    )
```

## 6. ロールバック手順

### 6.1 緊急時ロールバック
```bash
# マイグレーションをロールバック
alembic downgrade 024

# データベース接続確認
psql -h localhost -U username -d database_name -c "SELECT * FROM personas LIMIT 5;"
```

### 6.2 段階的ロールバック
```python
# アイコンフィールドのみを無効化
op.execute("""
    UPDATE personas 
    SET icon_type = 'disabled', 
        icon_metadata = '{"status": "disabled", "disabled_at": "2025-08-13T15:00:00Z"}'
    WHERE icon_type != 'disabled'
""")
```

## 7. パフォーマンス影響

### 7.1 インデックス効果
- **検索性能**: アイコン種類での検索が高速化
- **ストレージ**: 約50MBの追加容量（1000ペルソナ想定）
- **クエリ性能**: アイコン関連クエリの応答時間改善

### 7.2 監視項目
- テーブルサイズの増加
- アイコン関連クエリの実行時間
- ストレージ使用量の変化

## 8. セキュリティ考慮事項

### 8.1 ファイルアップロード
- ファイル形式の制限（JPG, PNG, GIF, SVG）
- ファイルサイズ制限（5MB以下）
- マルウェアスキャンの実装
- アクセス権限の適切な設定

### 8.2 データ保護
- アイコンメタデータの暗号化
- アクセスログの記録
- 定期的なセキュリティ監査

## 9. 運用・保守

### 9.1 定期メンテナンス
- 未使用アイコンファイルの削除
- ストレージ使用量の監視
- アイコン生成AIの利用状況確認

### 9.2 バックアップ
- アイコンファイルの定期バックアップ
- メタデータの整合性チェック
- 復旧手順の文書化

---

**作成日**: 2025-08-13  
**作成者**: AI Assistant  
**バージョン**: 1.0  
**次回更新予定**: 2025-09-13
