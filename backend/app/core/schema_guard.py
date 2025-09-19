# backend/app/core/schema_guard.py
from typing import Iterable, Tuple, Set
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import text

async def _existing_columns(conn: AsyncConnection, table: str) -> Set[str]:
    q = text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = current_schema()
          AND table_name   = :t
    """)
    res = await conn.execute(q, {"t": table})
    return {row[0] for row in res}

async def _ensure_columns(conn: AsyncConnection, table: str, cols: Iterable[Tuple[str, str]]) -> None:
    existing = await _existing_columns(conn, table)
    for name, ddl in cols:
        if name not in existing:
            # 例: ('started_at', 'TIMESTAMPTZ NULL')
            await conn.execute(text(f'ALTER TABLE "{table}" ADD COLUMN {name} {ddl}'))
    # NOTE: ここにインデックス/制約の self-heal も足せる

async def ensure_runtime_schema(conn: AsyncConnection) -> None:
    """
    起動時に既存テーブルへ不足カラムを追加してスキーマ差異を自己修復する。
    追加は“前方互換な NULL カラム”のみに限定（安全）。
    """
    # conversations: initdb 側に無い可能性がある列を補完
    await _ensure_columns(conn, "conversations", [
        ("started_at", "TIMESTAMPTZ NULL"),
        ("ended_at",   "TIMESTAMPTZ NULL"),
    ])
    # 必要に応じて他テーブルもここで補修できる
