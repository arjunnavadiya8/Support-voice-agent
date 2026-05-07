import asyncio
import edge_tts
import httpx
import json

async def test_transcribe():
    print("Generating MP3 with edge-tts...")
    communicate = edge_tts.Communicate("Hello, I need help uploading my bank statement today.", "en-US-AriaNeural")
    mp3_data = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            mp3_data.extend(chunk["data"])

    print(f"Generated {len(mp3_data)} bytes. Sending to /transcribe...")
    
    async with httpx.AsyncClient(timeout=30) as client:
        files = {'file': ('test.mp3', bytes(mp3_data), 'audio/mpeg')}
        response = await client.post('http://localhost:8000/transcribe', files=files)
        
        print("Response status:", response.status_code)
        print("Response body:", response.json())

if __name__ == "__main__":
    asyncio.run(test_transcribe())
