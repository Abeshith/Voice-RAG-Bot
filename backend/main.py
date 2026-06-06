"""
FastAPI Backend for Voice RAG Bot
Handles audio input, STT conversion, workflow orchestration, and response generation
"""

import logging
import asyncio
import sys
from pathlib import Path
from typing import Optional
from io import BytesIO

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import configuration
from backend.config import settings

# Import workflow
from orchestration.langgraph_workflow import run_workflow
from orchestration.latency_tracker import get_tracker, reset_tracker

# Import STT (Faster Whisper)
from faster_whisper import WhisperModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# MODELS
# ============================================================================

class ProcessAudioResponse(BaseModel):
    response_text: str
    audio_path: Optional[str]
    intent: str
    sentiment: str
    entities: Optional[dict]
    kb_context: str
    history_context: str
    session_count: Optional[int] = None
    active_sessions: Optional[list] = None
    session_tracking_status: Optional[str] = None
    session_memory_status: Optional[str] = None
    memory_routed_by_session: Optional[bool] = None
    session_isolation_verified: Optional[bool] = None
    user_escalation_state: Optional[str] = None
    escalation_state_updated: Optional[bool] = None
    escalation_history_count: Optional[int] = None
    escalation_state_management_status: Optional[str] = None
    escalation_influenced_response: Optional[bool] = None
    sentiment_trend: Optional[str] = None
    consecutive_negative_count: Optional[int] = None
    trend_escalation_recommended: Optional[bool] = None
    trend_escalation_reason: Optional[str] = None
    sentiment_trend_score: Optional[float] = None
    trend_analysis_status: Optional[str] = None
    escalation_confidence: Optional[int] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    llm_model: str
    qdrant_url: str
    whisper_model: str


# ============================================================================
# FASTAPI APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Voice RAG Bot Backend",
    description="AI-powered customer service bot with RAG and voice interface",
    version="1.0.0"
)

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# GLOBAL STATE
# ============================================================================

whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

def extract_audio_content(audio_bytes: bytes) -> str:
    try:
        audio_file = BytesIO(audio_bytes)
        segments, _ = whisper_model.transcribe(audio_file, language="en")
        transcribed_text = " ".join([segment.text for segment in segments])
        
        if not transcribed_text.strip():
            return "No speech detected"
        
        tracker = get_tracker()
        tracker.start("whisper_stt")
        tracker.end("whisper_stt")
        return transcribed_text
        
    except Exception as e:
        logger.error(f"STT Error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"STT failed: {str(e)}")


async def run_workflow_async(user_input: str, customer_id: str, user_id: str = None, session_id: str = None) -> dict:
    try:
        return await run_workflow(user_input, customer_id, user_id, session_id)
    except Exception as e:
        logger.error(f"Workflow Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow failed: {str(e)}")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {
        "status": "healthy",
        "llm_model": settings.groq_model,
        "qdrant_url": settings.qdrant_url,
        "whisper_model": "base"
    }


@app.post("/process-audio", response_model=ProcessAudioResponse)
async def process_audio(
    file: UploadFile = File(...),
    customer_id: str = "DEFAULT_CUSTOMER",
    user_id: str = None,
    session_id: str = None
):
    try:
        reset_tracker()
        tracker = get_tracker()
        tracker.start_total()
        
        audio_bytes = await file.read()
        user_input = extract_audio_content(audio_bytes)
        final_state = await run_workflow_async(user_input, customer_id, user_id, session_id)
        
        response = ProcessAudioResponse(
            response_text=final_state.get("response", ""),
            audio_path=final_state.get("final_audio_path"),
            intent=final_state.get("intent", ""),
            sentiment=final_state.get("sentiment", ""),
            entities=final_state.get("entities"),
            kb_context=final_state.get("kb_context", ""),
            history_context=final_state.get("history_context", ""),
            session_count=final_state.get("session_count"),
            active_sessions=final_state.get("active_sessions"),
            session_tracking_status=final_state.get("session_tracking_status"),
            session_memory_status=final_state.get("session_memory_status"),
            memory_routed_by_session=final_state.get("memory_routed_by_session"),
            session_isolation_verified=final_state.get("session_isolation_verified"),
            user_escalation_state=final_state.get("user_escalation_state"),
            escalation_state_updated=final_state.get("escalation_state_updated"),
            escalation_history_count=final_state.get("escalation_history_count"),
            escalation_state_management_status=final_state.get("escalation_state_management_status"),
            escalation_influenced_response=final_state.get("escalation_influenced_response"),
            sentiment_trend=final_state.get("sentiment_trend"),
            consecutive_negative_count=final_state.get("consecutive_negative_count"),
            trend_escalation_recommended=final_state.get("trend_escalation_recommended"),
            trend_escalation_reason=final_state.get("trend_escalation_reason"),
            sentiment_trend_score=final_state.get("sentiment_trend_score"),
            trend_analysis_status=final_state.get("trend_analysis_status"),
            escalation_confidence=final_state.get("escalation_confidence")
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.post("/process-text")
async def process_text(
    user_input: str,
    customer_id: str = "DEFAULT_CUSTOMER",
    user_id: str = None,
    session_id: str = None
):
    try:
        final_state = await run_workflow_async(user_input, customer_id, user_id, session_id)
        
        return ProcessAudioResponse(
            response_text=final_state.get("response", ""),
            audio_path=final_state.get("final_audio_path"),
            intent=final_state.get("intent", ""),
            sentiment=final_state.get("sentiment", ""),
            entities=final_state.get("entities"),
            kb_context=final_state.get("kb_context", ""),
            history_context=final_state.get("history_context", ""),
            session_count=final_state.get("session_count"),
            active_sessions=final_state.get("active_sessions"),
            session_tracking_status=final_state.get("session_tracking_status"),
            session_memory_status=final_state.get("session_memory_status"),
            memory_routed_by_session=final_state.get("memory_routed_by_session"),
            session_isolation_verified=final_state.get("session_isolation_verified"),
            user_escalation_state=final_state.get("user_escalation_state"),
            escalation_state_updated=final_state.get("escalation_state_updated"),
            escalation_history_count=final_state.get("escalation_history_count"),
            escalation_state_management_status=final_state.get("escalation_state_management_status"),
            escalation_influenced_response=final_state.get("escalation_influenced_response"),
            sentiment_trend=final_state.get("sentiment_trend"),
            consecutive_negative_count=final_state.get("consecutive_negative_count"),
            trend_escalation_recommended=final_state.get("trend_escalation_recommended"),
            trend_escalation_reason=final_state.get("trend_escalation_reason"),
            sentiment_trend_score=final_state.get("sentiment_trend_score"),
            trend_analysis_status=final_state.get("trend_analysis_status"),
            escalation_confidence=final_state.get("escalation_confidence")
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.get("/")
async def root():
    return {
        "name": "Voice RAG Bot Backend",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "process_audio": "POST /process-audio (requires audio file)",
            "process_text": "POST /process-text (requires text input)",
            "voice_bot_start": "POST /voice-bot/start",
            "voice_bot_message": "POST /voice-bot/message",
            "voice_bot_end": "POST /voice-bot/end",
            "docs": "GET /docs (Swagger UI)"
        }
    }


from backend.voice_bot_controller import get_voice_bot_controller

@app.post("/voice-bot/start")
async def voice_bot_start(customer_id: str = "CUST_DEFAULT"):
    try:
        controller = get_voice_bot_controller()
        return await controller.start_session(customer_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice-bot/message")
async def voice_bot_message(user_message: str):
    try:
        controller = get_voice_bot_controller()
        return await controller.process_user_message(user_message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice-bot/end")
async def voice_bot_end():
    try:
        controller = get_voice_bot_controller()
        return await controller.end_session()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/voice-bot/history")
async def voice_bot_history():
    try:
        controller = get_voice_bot_controller()
        return {"history": controller.get_session_history()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    logger.info(f"Backend started - Config: {settings.groq_model}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Backend shutdown")

if __name__ == "__main__":
    logger.info("Starting FastAPI server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
