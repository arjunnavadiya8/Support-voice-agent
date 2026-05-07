import os
import asyncio
from deepgram import DeepgramClient

os.environ['DEEPGRAM_API_KEY'] = 'd40318efc1962577e65fcc926385f1a86ba9695d'

async def test():
    dg = DeepgramClient(api_key=os.environ.get("DEEPGRAM_API_KEY", ""))
    payload = b"RIFF$" + b"\x00"*44
    try:
        res = await asyncio.to_thread(
            dg.listen.v1.media.transcribe_file,
            request=payload,
            model="nova-3",
            extra=["detect_language=en", "detect_language=hi", "detect_language=gu"],
            punctuate=True,
        )
        print("Success!", res.results.channels[0].detected_language)
    except Exception as e:
        print("Failed:", e)

asyncio.run(test())
