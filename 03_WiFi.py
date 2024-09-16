from Pico_Wear import PicoWear  # 引入 PicoWear 類別
import time

# ========== 全域變數 ==========
pico_wear = None  # 儲存 PicoWear 物件
led_on = False    # 記錄 LED 當前狀態

# Wi-Fi 設定
SSID = "TP-Link_5E4C_2.4G"
PASSWORD = "0976023369"

def update_oled(ip_address):
    """
    更新 OLED 顯示 IP 地址。如果 IP 地址超過 16 個字元，就換行顯示。
    
    Args:
        ip_address: 要顯示的 IP 地址字串。
    """
    # 清空顯示器
    pico_wear.display.fill(0)
    
    # 顯示 IP 地址，最多顯示兩行，每行 16 個字元
    line1 = ip_address[:16]  # 取得前 16 個字元
    line2 = ip_address[16:]  # 取得從第 17 個字元起的剩餘字串
    
    pico_wear.display.text(line1, 0, 0)  # 顯示第一行
    if line2:
        pico_wear.display.text(line2, 0, 16)  # 顯示第二行
    
    # 更新顯示器
    pico_wear.display.show()

def connect_wifi():
    """
    連接到指定的 Wi-Fi 網路。
    """
    pico_wear.wifi.connect(SSID, PASSWORD)
    print('正在連接 Wi-Fi...')
    
    # 確保 Wi-Fi 連線成功
    while not pico_wear.wifi.isconnected():
        # 每隔 0.5 秒閃爍 LED
        global led_on
        led_on = not led_on
        pico_wear.led.value(1 if led_on else 0)
        time.sleep(0.5)
    
    # Wi-Fi 連線成功，讓 LED 恆亮
    pico_wear.led.value(1)
    print('Wi-Fi 連線成功')
    
    # 獲取並顯示 IP 地址
    ip_address = pico_wear.wifi.ifconfig()[0]  # 獲取 IP 地址
    update_oled(ip_address)

def main():
    """
    主函式，初始化 PicoWear 物件，連接 Wi-Fi，並顯示 IP 地址。
    """
    global pico_wear
    pico_wear = PicoWear()  # 初始化 PicoWear 物件
    print('完成 Pico Wear 的初始化')
    
    # 連接 Wi-Fi
    connect_wifi()
    
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
