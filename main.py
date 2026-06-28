import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from funasr import AutoModel
from openai import OpenAI
import edge_tts
from pydub import AudioSegment
from pydub.playback import play
import io
import webrtcvad
import time
import os

# ================= 配置区 =================
DEEPSEEK_API_KEY = "sk-xx"
SAMPLE_RATE = 16000
FRAME_DURATION_MS = 30
VAD_MODE = 3
SILENCE_TIMEOUT = 1.0
# ===========================================

print("=" * 50)
print("🤖 语音对话机器人已启动（Paraformer 中文识别）")
print("直接说话即可，说完停顿自动识别")
print("按 Ctrl+C 退出")
print("=" * 50)

# 1. 加载模型时：禁用更新检查
print("🤖 正在加载 Paraformer 中文语音识别模型...")
asr_model = AutoModel(
    model="paraformer-zh",
    disable_update=True,  # 这里已经设置，很好
    disable_pbar=True,
    disable_log=True
)
print("✅ 模型加载完成！\n")

# 初始化 VAD
vad = webrtcvad.Vad()
vad.set_mode(VAD_MODE)

def is_speech(frame_bytes):
    return vad.is_speech(frame_bytes, SAMPLE_RATE)

def record_until_silence():
    print("🎙️ 请说话...")
    audio_frames = []
    silence_frames = 0
    max_silence_frames = int((SILENCE_TIMEOUT * 1000) / FRAME_DURATION_MS)
    frame_size = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000 * 2)

    def audio_callback(indata, frames, time_info, status):
        nonlocal silence_frames
        frame_bytes = (indata * 32767).astype(np.int16).tobytes()
        if is_speech(frame_bytes):
            audio_frames.append(indata.copy())
            silence_frames = 0
        else:
            silence_frames += 1
            if audio_frames:
                audio_frames.append(indata.copy())

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32',
                        blocksize=frame_size // 2, callback=audio_callback):
        while silence_frames < max_silence_frames:
            time.sleep(FRAME_DURATION_MS / 1000)

    print("✅ 语音输入结束！")
    return np.concatenate(audio_frames, axis=0) if audio_frames else None

def transcribe_audio(audio_data):
    print("🎧 正在识别语音...")
    temp_file = "temp_vad.wav"
    write(temp_file, SAMPLE_RATE, (audio_data * 32767).astype(np.int16))
    
    # 2. 生成结果时：必须加上 disable_update=True
    # 这是解决卡顿的关键！否则每次识别都会尝试联网检查模型更新
    result = asr_model.generate(
        input=temp_file,
        disable_update=True  # ⚠️ 核心修复：禁止在推理时检查更新
    )
    
    text = result[0]["text"].strip() if result else ""
    if text:
        print(f"👤 你说: {text}")
    else:
        print("⚠️ 未识别到有效语音")
    return text

def ask_deepseek(prompt):
    """调用 DeepSeek 获取回复"""
    if not prompt:
        return "我没有听清，请再说一遍。"

    print("🧠 思考中...")
    try:
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个语音对话助手，请用纯文本回复，不要使用任何 Markdown 格式（不要加粗、不要标题、不要代码块、不要用特殊符号装饰），直接返回自然的文字即可。"},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        reply = response.choices[0].message.content
        print(f"🤖 回复: {reply}\n")
        return reply
    except Exception as e:
        print(f"❌ 调用 DeepSeek 失败: {e}")
        return "抱歉，我在思考时遇到了一些问题。"


def speak_text(text):
    if not text:
        return
    print("🔊 正在播报...")
    try:
        communicate = edge_tts.Communicate(text, voice="zh-CN-YunxiaNeural")
        mp3_data = io.BytesIO()
        for chunk in communicate.stream_sync():
            if chunk["type"] == "audio":
                mp3_data.write(chunk["data"])
        mp3_data.seek(0)
        audio = AudioSegment.from_mp3(mp3_data)
        play(audio)
    except Exception as e:
        print(f"❌ TTS 播报失败: {e}")

def main_loop():
    try:
        while True:
            audio_data = record_until_silence()
            if audio_data is None:
                continue
            user_text = transcribe_audio(audio_data)
            if not user_text:
                continue
            ai_reply = ask_deepseek(user_text)
            speak_text(ai_reply)
            print("-" * 30)
            print("🎙️ 请继续说话...")
    except KeyboardInterrupt:
        print("\n\n👋 再见！")

if __name__ == "__main__":
    main_loop()
