import logging
import os
import time
import asyncio
from contextlib import asynccontextmanager

import soundfile as sf
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.core.device_manager import DeviceManager
from src.core.vad_processor import VADProcessor
from src.core.translator_engine import TranslatorEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Global state to hold models
models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load models
    logger.info("Initializing models...")
    device_mgr = DeviceManager()
    models["translator"] = TranslatorEngine(device_mgr)
    # VAD is fast to load, but we keep it here for consistency
    models["vad"] = VADProcessor()
    logger.info("Application startup complete. Models loaded.")
    yield
    # Shutdown: Clean up resources if needed
    models.clear()
    logger.info("Application shutdown complete.")


app = FastAPI(title="Local S2S Translation API", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/status")
async def get_status():
    """Returns the current status of the API."""
    return {"status": "online", "device": DeviceManager().get_device()}


@app.websocket("/ws/translate")
async def websocket_endpoint(websocket: WebSocket, tgt_lang: str = "eng"):
    """
    WebSocket endpoint for real-time speech translation.
    Receives Float32 PCM audio chunks, processes through VAD,
    and returns translated audio blobs.
    """
    await websocket.accept()
    logger.info(f"Client connected to translation WebSocket. Target Language: {tgt_lang}")
    
    vad: VADProcessor = models["vad"]
    translator: TranslatorEngine = models["translator"]
    
    # We should reset VAD state for each new connection
    vad.reset()

    # Create an asyncio queue for communication between input and translation loops
    queue = asyncio.Queue()

    async def input_loop():
        """Producer: Reads from WS, runs VAD, pushes to Queue."""
        try:
            while True:
                # Receive audio chunk as bytes
                data = await websocket.receive_bytes()
                
                # Process chunk through VAD
                sentence_audio = vad.process(data)
                
                if sentence_audio is not None:
                    timestamp = int(time.time())
                    logger.info(f"Sentence detected, pushing to queue... (Timestamp: {timestamp})")
                    
                    # DEBUG: Save Input Audio
                    os.makedirs("static/debug", exist_ok=True)
                    input_filename = f"static/debug/input_{timestamp}.wav"
                    sf.write(input_filename, sentence_audio, 16000)

                    await queue.put(sentence_audio)
        except WebSocketDisconnect:
            logger.info("Client disconnected (input loop).")
            # Signal consumer to stop
            await queue.put(None)
        except Exception as e:
            logger.error(f"Error in input_loop: {e}")
            await queue.put(None)

    async def translation_loop():
        """Consumer: Pulls from Queue, Translates (Thread), Sends to WS."""
        try:
            while True:
                sentence_audio = await queue.get()
                
                if sentence_audio is None:
                    # Sentinel received, stop
                    break

                logger.info(f"Processing sentence from queue. Queue size: {queue.qsize()}")
                
                # Run blocking translation inference in a separate thread
                loop = asyncio.get_running_loop()
                translated_audio_bytes = await loop.run_in_executor(
                    None, translator.translate, sentence_audio, tgt_lang
                )

                # DEBUG: Save Output Audio
                timestamp = int(time.time())
                output_filename = f"static/debug/output_{timestamp}.wav"
                with open(output_filename, "wb") as f:
                    f.write(translated_audio_bytes)

                # Send back the translated audio bytes (WAV)
                await websocket.send_bytes(translated_audio_bytes)
                logger.info(f"Translated audio ({tgt_lang}) sent to client.")
                
                queue.task_done()
        except Exception as e:
            logger.error(f"Error in translation_loop: {e}")

    # Run both loops concurrently
    await asyncio.gather(input_loop(), translation_loop())


# Mount static files to /static instead of root to avoid WebSocket conflict
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_index():
    return FileResponse("static/index.html")
