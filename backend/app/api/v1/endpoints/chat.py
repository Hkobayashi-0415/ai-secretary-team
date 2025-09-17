from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid
from app.core.database import get_async_db
from app.models.models import Conversation, Message
from app.services.llm.mock_llm import stream_mock_reply

router = APIRouter()

@router.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket, conversation_id: uuid.UUID = Query(...), db: AsyncSession = Depends(get_async_db)):
    await websocket.accept()
    # 会話存在チェック
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conv = result.scalars().first()
    if not conv:
        await websocket.close(code=4404)
        return
    try:
        while True:
            payload = await websocket.receive_json()
            # { "type":"user_message", "text":"..." }
            text = (payload or {}).get("text") or ""
            if not text:
                await websocket.send_json({"type":"error", "message":"empty text"})
                continue

            # DB: user message
            user_msg = Message(conversation_id=conversation_id, role="user", content=text)
            db.add(user_msg)
            await db.commit()

            # streaming assistant reply (mock)
            await websocket.send_json({"type":"assistant_start"})
            collected = ""
            async for token in stream_mock_reply(text):
                collected += token
                await websocket.send_json({"type":"token", "text": token})
            # DB: assistant message
            asst_msg = Message(conversation_id=conversation_id, role="assistant", content=collected)
            db.add(asst_msg)
            await db.commit()

            await websocket.send_json({"type":"assistant_end", "message": collected})
    except WebSocketDisconnect:
        return
