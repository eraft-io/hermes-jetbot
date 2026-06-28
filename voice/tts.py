#
# pip install edge-tts pydub simpleaudio
# 
import edge_tts
import asyncio
from pydub import AudioSegment
from pydub.playback import play
import io

async def tts_and_play(text: str, voice: str = "zh-CN-YunxiaNeural"):  # 改成云夏童声
    # 将音频写入内存缓冲区
    mp3_data = io.BytesIO()
    communicate = edge_tts.Communicate(text, voice=voice)
    
    # 边生成边写入缓冲区
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            mp3_data.write(chunk["data"])
    
    # 回到缓冲区开头，用pydub加载并播放
    mp3_data.seek(0)
    audio = AudioSegment.from_mp3(mp3_data)
    play(audio)

# 运行
asyncio.run(tts_and_play("你好，我是云夏，很高兴认识你！"))
