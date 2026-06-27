import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import os
import whisper
from openai import OpenAI
import pyttsx3

# ================= 配置区 =================
DEEPSEEK_API_KEY = "sk-xxx"  # ⚠️ 替换为你自己的 DeepSeek API Key
MODEL_SIZE = "tiny"                # Whisper 模型大小 (tiny, base, small, medium, large)
LANGUAGE = "zh"                    # 识别语言 ('zh' 为中文)
RECORD_DURATION = 6                # 录音时长（秒）
SAMPLE_RATE = 16000                # Whisper 推荐 16kHz 采样率
# ===========================================

def record_audio(filename="temp_record.wav"):
    """第一步：录音并保存"""
    print(f"🎙️ 准备录音... ({RECORD_DURATION}秒)")
    print("🔴 录音开始...")
    audio_data = sd.rec(int(RECORD_DURATION * SAMPLE_RATE), 
                        samplerate=SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait()  
    print("🟢 录音结束！")
    write(filename, SAMPLE_RATE, (audio_data * 32767).astype(np.int16))
    return filename

def transcribe_audio(audio_path):
    """第二步：Whisper 语音转文字"""
    print("🤖 正在加载 Whisper 模型...")
    model = whisper.load_model(MODEL_SIZE)
    print("🎧 正在识别语音...")
    result = model.transcribe(audio_path, language=LANGUAGE)
    user_text = result["text"].strip()
    print(f"👤 你说: {user_text}")
    return user_text

def ask_deepseek(prompt):
    """第三步：发送给 DeepSeek 获取回答"""
    if not prompt:
        return "我没有听清，请再说一遍。"
    
    print("🧠 正在思考中...")
    try:
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        ai_reply = response.choices[0].message.content
        print(f"🤖 DeepSeek: {ai_reply}")
        return ai_reply
    except Exception as e:
        print(f"❌ 调用 DeepSeek 失败: {e}")
        return "抱歉，我在思考时遇到了一些问题。"

def speak_text(text):
    """第四步：TTS 语音播报（已修复 espeak 弱引用报错）"""
    print("🔊 正在合成语音并播报...")
    engine = None  # 显式声明，防止变量作用域问题
    try:
        engine = pyttsx3.init(driverName='espeak')
        
        # 尝试匹配中文语音
        voices = engine.getProperty('voices')
        for voice in voices:
            # 兼容不同系统对中文语音的命名方式
            if 'zh-cn' in [lang.lower() for lang in voice.languages] or 'chinese' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
                
        # 播报文本并等待完成
        engine.say(text)
        engine.runAndWait()
        
    except Exception as e:
        print(f"❌ TTS 播报失败: {e}")
    finally:
        # 关键修复：播报结束后，手动停止并销毁引擎，防止弱引用报错
        if engine is not None:
            try:
                engine.stop()
            except Exception:
                pass

if __name__ == "__main__":
    temp_audio = "temp_record.wav"
    
    # 执行完整的闭环流程
    record_audio(temp_audio)
    user_text = transcribe_audio(temp_audio)
    ai_reply = ask_deepseek(user_text)
    speak_text(ai_reply)
    
    # 清理临时录音文件
    if os.path.exists(temp_audio):
        os.remove(temp_audio)