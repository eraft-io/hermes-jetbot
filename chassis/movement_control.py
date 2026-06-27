import serial
import struct
import time

class ClbBotController:
    def __init__(self, port='/dev/ttyACM0', baudrate=115200):
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            print(f"[INFO] 成功连接串口: {port} (波特率: {baudrate})")
        except Exception as e:
            print(f"[ERROR] 串口打开失败: {e}")
            exit(1)

    def check_sum(self, data):
        """计算校验和（累加和取低8位）"""
        return sum(data) & 0xFF

    def send_velocity(self, linear_x, angular_z):
        """
        发送速度控制指令
        :param linear_x: 线速度 (m/s)，正数前进，负数后退
        :param angular_z: 角速度 (rad/s)，正数左转，负数右转
        """
        # 将浮点型速度转换为协议要求的整数 (乘以 1000)
        vx_int = int(linear_x * 1000)
        vz_int = int(angular_z * 1000)

        # 组装数据帧 (大端序 '>')
        # 2s: 2字节帧头
        # B: 帧长度 (1字节)
        # B: 指令码 (1字节)
        # h: 线速度 X (2字节)
        # h: 线速度 Y (2字节)
        # h: 角速度 Z (2字节)
        frame = struct.pack('>2sBBhhh', 
                            b'\xAB\xCD',   # 帧头 (2字节)
                            0x0B,          # 帧长度 (11字节)
                            0x11,          # 指令码 (速度控制)
                            vx_int,        # 线速度 X
                            0,             # 线速度 Y (固定为0)
                            vz_int         # 角速度 Z
                            )
        
        # 计算校验和并追加到帧尾
        checksum = self.check_sum(frame)
        frame += struct.pack('B', checksum)

        # 发送数据
        self.ser.write(frame)
        print(f"[TX] 发送指令: Vx={linear_x:.2f} m/s, Vz={angular_z:.2f} rad/s")

    def stop(self):
        """发送停止指令"""
        self.send_velocity(0.0, 0.0)

    def close(self):
        self.stop()
        self.ser.close()
        print("\n[INFO] 串口已关闭")

# --- 键盘控制主程序 ---
if __name__ == "__main__":
    controller = ClbBotController(port='/dev/ttyACM0', baudrate=115200)
    
    print("\n========================================")
    print("   键盘控制底盘 (按 Ctrl+C 退出)")
    print("----------------------------------------")
    print("  W : 前进        S : 后退")
    print("  A : 左转        D : 右转")
    print("  空格 : 停止")
    print("========================================\n")

    try:
        while True:
            key = input("请输入控制指令 (w/a/s/d/空格): ").strip().lower()
            
            if key == 'w':
                controller.send_velocity(linear_x=0.2, angular_z=0.0)
            elif key == 's':
                controller.send_velocity(linear_x=-0.2, angular_z=0.0)
            elif key == 'a':
                controller.send_velocity(linear_x=0.0, angular_z=0.4)
            elif key == 'd':
                controller.send_velocity(linear_x=0.0, angular_z=-0.4)
            elif key == ' ':
                controller.stop()
            else:
                print("[WARN] 无效指令，请重新输入")
                
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n[INFO] 用户手动停止")
    finally:
        controller.close()
