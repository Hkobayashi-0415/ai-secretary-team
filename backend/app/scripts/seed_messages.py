"""
Utility: seed many messages into an existing conversation for paging tests.

Usage (inside container):

  python -m app.scripts.seed_messages --conversation-id <UUID> --count 100 \
      [--pair] [--text "seed"]

Notes
- --pair inserts user/assistant pairs. Without it, inserts only user messages.
- This script uses the app's async DB session.
"""
from __future__ import annotations

import argparse
import asyncio
import uuid as _uuid
from datetime import datetime, timedelta

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.phase2_models import Conversation, Message


async def _seed(conversation_id: str, count: int, pair: bool, text: str) -> None:
    cid = _uuid.UUID(conversation_id)
    async with AsyncSessionLocal() as session:
        # validate conversation
        conv = (await session.execute(select(Conversation).where(Conversation.id == cid))).scalars().first()
        if not conv:
            raise SystemExit(f"Conversation not found: {conversation_id}")

        now = datetime.utcnow()
        delta = timedelta(seconds=1)
        to_add: list[Message] = []
        for i in range(count):
            ts = now + i * delta
            to_add.append(
                Message(
                    conversation_id=cid,
                    role="user",
                    content=f"{text} user #{i+1}",
                    content_type="text",
                    created_at=ts,
                )
            )
            if pair:
                to_add.append(
                    Message(
                        conversation_id=cid,
                        role="assistant",
                        content=f"You said: {text} user #{i+1}",
                        content_type="text",
                        created_at=ts + timedelta(milliseconds=1),
                    )
                )

        session.add_all(to_add)
        await session.commit()
        print(f"Inserted {len(to_add)} messages into {conversation_id}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--conversation-id", required=True, help="Target conversation UUID")
    ap.add_argument("--count", type=int, default=50, help="Number of batches (user messages) to insert")
    ap.add_argument("--pair", action="store_true", help="Insert user/assistant pairs")
    ap.add_argument("--text", default="seed", help="Base text")
    args = ap.parse_args()

    asyncio.run(_seed(args.conversation_id, args.count, args.pair, args.text))


if __name__ == "__main__":
    main()

