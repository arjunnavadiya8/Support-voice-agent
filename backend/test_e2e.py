import asyncio
import json
import websockets
import edge_tts
import io
import wave
import numpy as np

async def test_ws():
    uri = "ws://localhost:8000/ws/call"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as ws:
            # Send call start
            print("Sending call_start...")
            await ws.send(json.dumps({"type": "call_start", "language": "en"}))
            
            # Wait for call_accepted
            msg = await ws.recv()
            print("Received:", msg)
            
            # Wait for greeting TTS
            print("Waiting for greeting...")
            while True:
                msg = await ws.recv()
                if isinstance(msg, bytes):
                    print(f"Received greeting audio chunk: {len(msg)} bytes")
                    continue
                else:
                    print("Received:", msg)
                    try:
                        data = json.loads(msg)
                        if data.get("type") == "tts_end":
                            break
                        if data.get("type") == "status" and data.get("message") == "Listening…":
                            pass
                    except:
                        pass
            
            # Now just wait without sending audio to test if the connection drops or stays stable.
            # We skip sending PCM since we don't have it, and just simulate a silent turn.
            while True:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=20.0)
                    if isinstance(msg, bytes):
                        print(f"Received answer audio chunk: {len(msg)} bytes")
                    else:
                        print("Received:", msg)
                        data = json.loads(msg)
                        if data.get("type") == "tts_end":
                            print("Turn completed!")
                            break
                        if data.get("type") == "error":
                            print("Error occurred!")
                            break
                except asyncio.TimeoutError:
                    print("Timeout waiting for response!")
                    break
            
            print("Sending call_end...")
            await ws.send(json.dumps({"type": "call_end"}))
            
            msg = await ws.recv()
            print("Received:", msg)

    except Exception as e:
        print("WebSocket test failed:", e)

if __name__ == "__main__":
    asyncio.run(test_ws())
