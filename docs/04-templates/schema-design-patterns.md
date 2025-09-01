# スキーマ設計パターン - 参考資料

## 概要
このドキュメントは、Pydanticスキーマ設計における様々なパターンと実装例を記録したものです。
Phase 2実装時に検討された教育的な内容を含んでいます。

## 1. DRY原則を守る更新スキーマの実装パターン

### 問題
BaseModelで定義したフィールドを、UpdateModelで全てOptionalとして再定義するのは重複が多い。

### 解決策1: 明示的な定義
```python
class AssistantUpdate(BaseModel):
    """全フィールドを明示的にOptionalとして定義"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    # ... 全フィールドを列挙
```

### 解決策2: 動的なOptional化
```python
class AssistantUpdateSmart(AssistantBase):
    """実行時にフィールドをOptional化"""
    def __init__(self, **data):
        for field_name, field in self.__fields__.items():
            field.required = False
            if field.default is ...:
                field.default = None
        super().__init__(**data)
```

### 解決策3: ファクトリパターン
```python
def create_partial_model(base_model: type[BaseModel]) -> type[BaseModel]:
    """BaseModelから更新用モデルを動的生成"""
    from typing import Optional
    
    fields = {}
    for field_name, field_info in base_model.__fields__.items():
        fields[field_name] = (
            Optional[field_info.type_],
            Field(None, **field_info.field_info.extra)
        )
    
    UpdateModel = type(
        f"{base_model.__name__}Update",
        (BaseModel,),
        {
            '__annotations__': {k: v[0] for k, v in fields.items()},
            **{k: v[1] for k, v in fields.items()}
        }
    )
    
    return UpdateModel

# 使用例
AssistantUpdateAuto = create_partial_model(AssistantBase)
```

## 2. 外部キーのバリデーション

### 問題
存在しないIDが送られてきた場合、DBアクセス時までエラーが発生しない。

### 解決策: カスタムバリデータ
```python
class AssistantWithValidation(AssistantCreate):
    """外部キーの存在チェックを行うスキーマ"""
    
    @validator('personality_template_id')
    def validate_personality_template(cls, v, values):
        if v is not None:
            # DBアクセスして存在確認
            from app.validators import check_personality_template_exists
            if not check_personality_template_exists(v):
                raise ValueError(f"Personality template {v} does not exist")
        return v
    
    @validator('voice_id')
    def validate_voice(cls, v, values):
        # 同様の実装
        pass
```

### 実装上の課題
- バリデータ内でのDB接続が必要
- 非同期処理との組み合わせが複雑
- パフォーマンスへの影響

## 3. 空文字列の処理

### 問題
フロントエンドから空文字列("")が送られてきた場合の処理。

### 解決策: Pre-validator
```python
@validator('*', pre=True)
def empty_str_to_none(cls, v):
    """空文字列をNoneに変換"""
    if v == '':
        return None
    return v
```

## 4. レスポンスの最適化

### Noneフィールドの除外
```python
def dict(self, *args, **kwargs) -> Dict[str, Any]:
    """レスポンスからNoneを除外"""
    kwargs['exclude_none'] = True
    return super().dict(*args, **kwargs)
```

## 5. 実装の選択基準

| パターン | メリット | デメリット | 採用場面 |
|---------|---------|-----------|----------|
| 明示的定義 | 分かりやすい、IDE補完が効く | 重複が多い | 小規模プロジェクト |
| 動的Optional化 | DRY原則を守れる | 実行時の処理、型ヒントが弱い | 中規模プロジェクト |
| ファクトリパターン | 完全に自動化、再利用可能 | 複雑、デバッグが困難 | 大規模プロジェクト |

## 最終的な採用案

Phase 2では、以下の理由から**明示的定義**を採用：
1. コードの可読性が高い
2. IDEの型補完が完全に機能する
3. デバッグが容易
4. チーム開発での理解が容易

## 参考文献
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/body-updates/)

---
*このドキュメントは2025年8月30日のPhase 2実装時に作成された参考資料です。*