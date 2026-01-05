import asyncio
import websockets
import numpy as np


async def test_websocket():
    uri = "ws://localhost:8000/ws/translate"
    print(f"Connecting to {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")

            # Generate dummy audio: 3 seconds of silence (should be ignored or buffered)
            # followed by simulated speech (random noise for VAD triggering test,
            # though VAD expects real speech patterns, noise might fail or trigger.
            # Ideally we send a real wav file, but let's try noise with high amplitude).

            # Actually, VAD is sensitive. Silence is 0.
            sample_rate = 16000

            # 1. Send 1 second of silence
            silence = np.zeros(sample_rate * 1, dtype=np.float32)
            await websocket.send(silence.tobytes())
            print("Sent 1s silence.")

            # 2. Send 2 seconds of "speech" (Sine wave might trigger VAD better than noise)
            t = np.linspace(0, 2.0, int(sample_rate * 2.0), endpoint=False)
            speech = 0.5 * np.sin(2 * np.pi * 440 * t).astype(np.float32)
            await websocket.send(speech.tobytes())
            print("Sent 2s speech (sine wave).")

            # 3. Send 1 second of silence to trigger "end of sentence"
            await websocket.send(silence.tobytes())
            print("Sent 1s silence (end trigger).")

            print("Waiting for response...")
            # Wait for response with timeout
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=60.0)  # Long timeout for CPU translation
                print(f"Received response of length: {len(response)} bytes")
            except asyncio.TimeoutError:
                print("Timeout waiting for translation response.")

    except Exception as e:
        print(f"Connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_websocket())
