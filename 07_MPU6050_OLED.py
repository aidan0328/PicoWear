from Pico_Wear import PicoWear  # 引入 PicoWear 類別
import time

# ========== 全域變數 ==========
pico_wear = None  # 儲存 PicoWear 物件

# =============================

def update_and_display_angles():
    """
    更新 MPU6050 姿態數據並顯示尤拉角。
    """
    pico_wear.mpu.update_mahony()  # 更新姿態數據
    angles = pico_wear.mpu.get_angles()  # 取得尤拉角
    
    # 將尤拉角數據格式化為字串
    roll_str = "Roll: {:.2f}".format(angles[0])
    pitch_str = "Pitch: {:.2f}".format(angles[1])
    yaw_str = "Yaw: {:.2f}".format(angles[2])
    
    # 更新 OLED 顯示器
    pico_wear.display.fill(0)  # 清空顯示器
    
    # 確保每行顯示不超過 16 個字元
    def display_line(text, line_number):
        """
        顯示一行文字到 OLED 顯示器上，最多顯示 16 個字元。
        
        Args:
            text: 要顯示的文字。
            line_number: 顯示的行數（0, 1, 2）。
        """
        max_chars_per_line = 16
        for i in range(0, len(text), max_chars_per_line):
            pico_wear.display.text(text[i:i+max_chars_per_line], 0, line_number * 16)
            line_number += 1
    
    # 顯示尤拉角數據
    display_line(roll_str, 0)  # 顯示 Roll 在第一行
    display_line(pitch_str, 1)  # 顯示 Pitch 在第二行
    display_line(yaw_str, 2)    # 顯示 Yaw 在第三行
    
    pico_wear.display.show()  # 更新顯示器

def main():
    """
    主函式，初始化 PicoWear 物件，並每 100 毫秒更新一次尤拉角顯示。
    """
    global pico_wear
    pico_wear = PicoWear()  # 初始化 PicoWear 物件
    print('完成 Pico Wear 的初始化')
    
    while True:
        update_and_display_angles()  # 更新並顯示尤拉角
        time.sleep(0.1)  # 每 100 毫秒更新一次

if __name__ == '__main__':
    try:
        main()  # 執行主函式
    except KeyboardInterrupt:
        # 捕捉到中斷訊號時，重啟裝置
        print("捕捉到中斷訊號，重啟裝置...")
        machine.reset()  # 重啟裝置
    except Exception as e:
        # 捕捉其他錯誤
        print(f"發生其他錯誤: {e}")
