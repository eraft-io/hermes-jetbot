'''
Fashion Star 总线舵机通讯检测脚本
功能：检测指定ID的舵机是否在线
'''

# 1. 导入必要的库
import sys
import time
import serial
# 确保 uservo.py 文件与当前脚本在同一目录，或者已添加到系统路径
from uservo import UartServoManager

# 2. 参数配置
# --- 请根据你的实际情况修改以下参数 ---
SERVO_PORT_NAME = '/dev/ttyACM2'  # 舵机连接的串口端口 (Windows下如 'COM3', Linux下如 '/dev/ttyUSB0')
SERVO_BAUDRATE = 115200           # 舵机通讯波特率，官方默认为 115200
SERVO_ID = 1                      # 你想检测的舵机ID号，新舵机默认为 0
# ------------------------------------

def main():
    # 3. 初始化串口
    try:
        uart = serial.Serial(
            port=SERVO_PORT_NAME,
            baudrate=SERVO_BAUDRATE,
            parity=serial.PARITY_NONE,
            stopbits=1,
            bytesize=8,
            timeout=1  # 设置1秒超时，避免程序卡死
        )
        print(f"✅ 成功打开串口: {SERVO_PORT_NAME}")
    except serial.SerialException as e:
        print(f"❌ 无法打开串口 {SERVO_PORT_NAME}: {e}")
        print("请检查：1. 串口名称是否正确 2. 串口是否被其他程序占用 3. 权限是否足够")
        return

    # 4. 创建舵机管理器
    uservo = UartServoManager(uart)

    # 5. 执行舵机通讯检测 (Ping)
    print(f"📡 正在检测舵机 (ID: {SERVO_ID})...")
    is_online = uservo.ping(SERVO_ID)

    if is_online:
        print(f"🎉 成功！舵机 ID={SERVO_ID} 在线且通讯正常。")
    else:
        print(f"⚠️ 失败！舵机 ID={SERVO_ID} 未响应。")
        print("请检查：1. 舵机供电是否正常 2. 接线(Tx/Rx)是否正确 3. 舵机ID是否匹配")

    # 6. 关闭串口
    uart.close()
    print("串口已关闭。")

if __name__ == '__main__':
    main()
