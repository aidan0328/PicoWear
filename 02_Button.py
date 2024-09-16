from Pico_Wear import PicoWear  # 引入 PicoWear 類別
import machine  # 引入 machine 模組
import time

# ========== 全域變數 ==========
pico_wear = None  # 儲存 PicoWear 物件
led_on = False    # 記錄 LED 的狀態

# =============================

def button_clicked():
    """
    按鈕的回呼函式。當按鈕被按下時，切換 LED 的狀態（開/關）。
    """
    global led_on
    led_on = not led_on  # 切換 LED 狀態
    pico_wear.led.value(1 if led_on else 0)  # 設定 LED 狀態

def main():
    """
    主函式，初始化 PicoWear 物件，註冊按鈕回呼函式，並保持主循環運行。
    """
    global pico_wear
    pico_wear = PicoWear()  # 初始化 PicoWear 物件
    print('完成 Pico Wear 的初始化')

    # 註冊按鈕回呼函式
    pico_wear.register_button_callback(button_clicked)
    
    # 主循環，保持程式持續運行
    while True:
        time.sleep(0.1)  # 暫停 0.1 秒，以減少 CPU 使用率

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
