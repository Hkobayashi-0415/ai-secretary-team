from typing import AsyncIterator

async def stream_mock_reply(user_text: str) -> AsyncIterator[str]:
    # すぐ使えるモック: "You said: {text}" をトークン分割で返す
    reply = f"You said: {user_text}"
    for chunk in reply.split(" "):
        yield chunk + " "
