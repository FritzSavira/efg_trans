import logging
import json
import asyncio
import os
import shutil
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.core.asr.whisper_engine import WhisperASR
from src.core.llm.llama_engine import LlamaTranslator
from src.core.tts.xtts_engine import XTTSEngineWrapper
from src.pipeline.orchestrator import PipelineOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Global models
engines = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load models individually for better error reporting
    logger.info("--- Modular Trinity Engine Initialization ---")

    # 1. ASR
    try:
        engines["asr"] = WhisperASR()
        logger.info("ASR Engine (Whisper) loaded successfully.")
    except Exception as e:
        logger.error(f"ASR Engine failed to load: {e}")
        engines["asr"] = None

    # 2. LLM
    try:
        model_path = "models/Meta-Llama-3-8b-Instruct-Q4_K_M.gguf"
        if os.path.exists(model_path):
            engines["llm"] = LlamaTranslator(model_path=model_path)
            logger.info("LLM Engine (Llama) loaded successfully.")
        else:
            logger.error(f"LLM Model file NOT FOUND at {os.path.abspath(model_path)}. Translation will be unavailable.")
            engines["llm"] = None
    except Exception as e:
        logger.error(f"LLM Engine failed to load: {e}")
        engines["llm"] = None

    # 3. TTS
    try:
        engines["tts"] = XTTSEngineWrapper()
        logger.info("TTS Engine (XTTS) loaded successfully.")
    except Exception as e:
        logger.error(f"TTS Engine failed to load. Reason: {e}", exc_info=True)
        engines["tts"] = None

    logger.info("--- Initialization Phase Complete ---")
    yield
    # Shutdown
    engines.clear()
    logger.info("Application shutdown.")


app = FastAPI(title="Modular Trinity S2S API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/status")
async def get_status():
    return {
        "status": "online",
        "engines": {k: (v is not None) for k, v in engines.items()},
    }


@app.post("/upload_ref")
async def upload_reference(file: UploadFile = File(...)):
    """Uploads a reference WAV file for voice cloning."""
    os.makedirs("uploads", exist_ok=True)
    file_id = str(uuid.uuid4())
    file_path = os.path.join("uploads", f"{file_id}_{file.filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"path": file_path}


@app.websocket("/ws/translate")
async def websocket_endpoint(websocket: WebSocket, src_lang: str = "en", tgt_lang: str = "de"):
    await websocket.accept()
    logger.info(f"Client connected. {src_lang} -> {tgt_lang}")

    orchestrator = PipelineOrchestrator(asr=engines.get("asr"), llm=engines.get("llm"), tts=engines.get("tts"))
    orchestrator.set_languages(src_lang, tgt_lang)
    await orchestrator.start()

    async def input_loop():
        try:
            while True:
                message = await websocket.receive()

                if "bytes" in message:
                    await orchestrator.process_audio_chunk(message["bytes"])

                elif "text" in message:
                    try:
                        payload = json.loads(message["text"])
                        if payload.get("type") == "config":
                            src = payload.get("src_lang")
                            tgt = payload.get("tgt_lang")
                            if src and tgt:
                                orchestrator.set_languages(src, tgt)

                            ref_path = payload.get("speaker_ref_path")
                            if ref_path:
                                orchestrator.set_speaker_reference(ref_path)

                    except Exception as e:
                        logger.warning(f"Invalid config: {e}")

        except WebSocketDisconnect:
            logger.info("Client disconnected.")
        except Exception as e:
            if "receive" not in str(e):
                logger.error(f"Input loop error: {e}")
        finally:
            await orchestrator.stop()

    async def output_loop():
        try:
            while orchestrator.is_running:
                audio_bytes = await orchestrator.get_output()
                if audio_bytes:
                    await websocket.send_bytes(audio_bytes)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Output loop error: {e}")

    # Run loops and ensure cleanup
    try:
        await asyncio.gather(input_loop(), output_loop())
    except Exception:
        pass


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_index():
    return FileResponse("static/index.html")
