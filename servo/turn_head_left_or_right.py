'''
Fashion Star 总线舵机交互式控制脚本
功能：通过命令行输入角度，实时控制舵机并监控其状态
'''

# 1. 导入必要的库
import sys
import time
import serial
# 确保 uservo.py 文件与当前脚本在同一目录
from uservo import UartServoManager

# 2. 参数配置
# --- 请根据你的实际情况修改以下参数 ---
SERVO_PORT_NAME = '/dev/ttyACM2'  # 舵机连接的串口端口
SERVO_BAUDRATE = 115200           # 舵机通讯波特率
SERVO_ID = 0                      # 你想控制的舵机ID号
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
            timeout=1
        )
        print(f"✅ 成功打开串口: {SERVO_PORT_NAME}")
    except serial.SerialException as e:
        print(f"❌ 无法打开串口 {SERVO_PORT_NAME}: {e}")
        return

    # 4. 创建舵机管理器
    uservo = UartServoManager(uart)

    print(f"🎮 舵机 (ID: {SERVO_ID}) 控制脚本已启动。")
    print("💡 使用说明：")
    print("   - 输入目标角度 (例如 0.0) 并回车，舵机将移动到指定位置。")
    print("   - 输入 'q' 并回车，退出程序。")
    print("-" * 40)

    try:
        while True:
            # 5. 获取用户输入
            user_input = input("请输入目标角度: ")
            
            if user_input.lower() == 'q':
                print("👋 正在退出...")
                break

            try:
                target_angle = float(user_input)
            except ValueError:
                print("⚠️ 输入无效，请输入一个数字或 'q' 退出。")
                continue

            if target_angle < -50.0 or target_angle > 50.0:
                print("⚠️ 输入无效，请输入一个 -50.0 到 50.0 之间的数字。")
                continue

            # 6. 发送角度指令
            print(f"📡 正在设置舵机角度为 {target_angle}° ...")
            # 使用默认速度移动，您也可以添加 velocity, interval 等参数
            uservo.set_servo_angle(SERVO_ID, target_angle)
            

    except KeyboardInterrupt:
        print("\n\n👋 用户通过 Ctrl+C 中断程序。")
    except Exception as e:
        print(f"\n\n❌ 运行过程中发生错误: {e}")
    finally:
        # 8. 关闭串口
        uart.close()
        print("串口已关闭。")

if __name__ == '__main__':
    main()
