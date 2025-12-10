import base64
from fastapi import APIRouter, HTTPException

from app.schemas.llm import (
    ImageGenerationRequest,
    ImageGenerationResponse,
    TextGenerationRequest,
    TextGenerationResponse,
)
from app.services.llm import generate_image, generate_text

router = APIRouter()


@router.post("/text", response_model=TextGenerationResponse)
async def generate_text_api(payload: TextGenerationRequest):
    if payload.stream:
        raise HTTPException(status_code=400, detail="stream=true is not supported on REST. Use WS.")
    try:
        res = await generate_text(
            payload.prompt,
            model=payload.model,
            thinking_level=payload.thinking_level,
            thinking_budget=payload.thinking_budget,
            include_thoughts=payload.include_thoughts,
            provider_override=payload.provider,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return TextGenerationResponse(
        text=res["text"],
        thoughts=res.get("thoughts"),
        provider=res.get("provider", "mock"),
        model=res.get("model"),
    )


@router.post("/image", response_model=ImageGenerationResponse)
async def generate_image_api(payload: ImageGenerationRequest):
    try:
        res = await generate_image(
            payload.prompt,
            model=payload.model,
            provider_override=payload.provider,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    data_b64 = base64.b64encode(res["data"]).decode("utf-8")
    return ImageGenerationResponse(
        mime_type=res["mime_type"],
        data_base64=data_b64,
        provider=res.get("provider", "mock"),
        model=res.get("model"),
    )
