from Pico_Wear import PicoWear  # 引入 PicoWear 類別
import time
import network
import machine

# ========== 全域變數 ==========
pico_wear = None
mqtt_client = None

# =============================

def connect_wifi():
    """
    連接到 Wi-Fi 網絡，並根據連線狀態控制 LED。
    """
    ssid = "TP-Link_5E4C_2.4G"
    password = "0976023369"

    pico_wear.wifi.connect(ssid, password)

    # 等待連線完成
    while not pico_wear.wifi.isconnected():
        pico_wear.led.value(1)  # LED 開
        time.sleep(0.5)
        pico_wear.led.value(0)  # LED 關
        time.sleep(0.5)
    
    # 連線完成，LED 恆亮
    pico_wear.led.value(1)
    print('Wi-Fi 連線成功:', pico_wear.wifi.ifconfig())

def display_mac_address():
    """
    在 OLED 顯示器上顯示 MAC 地址，超出 16 個字的部分換行顯示。
    """
    mac_addr = pico_wear.mac_addr
    pico_wear.display.fill(0)  # 清空顯示器
    
    # OLED 顯示字串，每行最多 16 個字元
    max_chars_per_line = 16
    for i in range(0, len(mac_addr), max_chars_per_line):
        pico_wear.display.text(mac_addr[i:i+max_chars_per_line], 0, (i // max_chars_per_line) * 16)
    
    pico_wear.display.show()  # 更新顯示器

def button_clicked():
    """
    按鈕回呼函式，切換 LED 狀態並發送訊息到 MQTT 服務器。
    """
    # 切換 LED 狀態
    pico_wear.led.value(not pico_wear.led.value())
    
    # 發送訊息到 MQTT 服務器
    mac_addr = pico_wear.mac_addr    
    led_state = "ON" if pico_wear.led.value() else "OFF"

    # 取得 RTC 時間和日期
    rtc_time = pico_wear.rtc.datetime()
    
    # 格式化時間與日期
    date_str = "{:04d}-{:02d}-{:02d}".format(rtc_time[0], rtc_time[1], rtc_time[2])  # 年-月-日
    time_str = "{:02d}:{:02d}:{:02d}".format(rtc_time[4], rtc_time[5], rtc_time[6])  # 時:分:秒
    
    # 將日期與時間結合成一個字串
    current_time = "Date: {}\t Time: {}".format(date_str, time_str)
    
    # 構造訊息
    message = f"MAC: {mac_addr}, Time: {current_time}, LED: {led_state}"
    topic = "pico_w/led"
    
    if pico_wear.mqtt_client:
        pico_wear.mqtt_client.publish(topic, message)
    else:
        print("MQTT 客戶端未連接，無法發送訊息。")

def main():
    """
    主函式，初始化 PicoWear 物件，連接 Wi-Fi，顯示 MAC 地址，並設置按鈕回呼函式。
    """
    global pico_wear
    pico_wear = PicoWear()  # 初始化 PicoWear 物件
    print('完成 Pico Wear 的初始化')

    connect_wifi()  # 連接到 Wi-Fi
    display_mac_address()  # 顯示 MAC 地址
    pico_wear.mqtt_connect('broker.mqttgo.io')
    
    # 設置按鈕回呼函式
    pico_wear.register_button_callback(button_clicked)
    
    while True:
        time.sleep(0.1)  # 繼續運行主循環

if __name__ == '__main__':
    try:
        main()  # 執行主函式
    except KeyboardInterrupt:
        print("捕捉到中斷訊號，重啟裝置...")
        machine.reset()  # 重啟裝置
    except Exception as e:
        print(f"發生其他錯誤: {e}")
