from Pico_Wear import PicoWear  # 引入 PicoWear 類別
import time
import ntptime
from machine import Timer  # 引入 Timer
# import struct
# import socket

# ========== 全域變數 ==========
rp2.country('TW') # change to <your> country code

# SSID = 'Hi-NET'
# PASSWORD = '0976023369'

SSID = "TP-Link_5E4C_2.4G"
PASSWORD = "0976023369"

pico_wear = None
mqtt_broker = 'broker.mqttgo.io'
mqtt_topic = None  # 將會在連上 WiFi 後設置

# 設置 NTP 伺服器
ntptime.host = 'time.google.com'  # 或 'time.nist.gov'

NTP_DELTA = 2208988800
host = "time.google.com"

# =============================
def set_time():
    retry = 0
    while retry < 3:
        try:
            ntptime.settime()
            break
        except:
            retry += 1
            time.sleep(1)
    
    # 调整时区 (+8 小时)    
    current_time = list(time.localtime())
    current_time[3] = (current_time[3] + 8) % 24  # 调整小时
    pico_wear.rtc.datetime((current_time[0], current_time[1], current_time[2], current_time[6] + 1,
                  current_time[3], current_time[4], current_time[5], 0))

def button_clicked():
    """
    按鈕回呼函式，當按鈕被按下時，LED 轉態並推送訊息到 MQTT。
    """
    # LED 轉態
    pico_wear.led.value(not pico_wear.led.value())

    # 取得 MAC 地址
    mac_addr = pico_wear.mac_addr

    # 取得 RTC 時間並手動格式化為 HH:MM:SS
    rtc_time = pico_wear.rtc.datetime()  # 回傳格式: (年, 月, 日, 星期, 時, 分, 秒, 毫秒)
    time_str = "{:02d}:{:02d}:{:02d}".format(rtc_time[4], rtc_time[5], rtc_time[6])

    # 取得尤拉角
    pico_wear.mpu.update_mahony()
    angles = pico_wear.mpu.get_angles()
    roll_str = "Roll: {:.2f}".format(angles[0])
    pitch_str = "Pitch: {:.2f}".format(angles[1])
    yaw_str = "Yaw: {:.2f}".format(angles[2])

    # 格式化訊息 [mac_addr] hh:mm:ss : 尤拉角
    msg = f"[{mac_addr}] {time_str} : Roll:{roll_str}, Pitch:{pitch_str}, Yaw:{yaw_str}"
    
    # 發送 MQTT 訊息
    if pico_wear.mqtt_client:
        pico_wear.mqtt_client.publish(mqtt_topic, msg)
        print(f"已推送 MQTT 訊息: {mqtt_topic} : {msg}")

def display_info_on_oled():
    """
    顯示 Wi-Fi IP、MAC 地址、RTC 時間和尤拉角在 OLED 上，每行最多 16 個字元。
    """
    # 取得 IP 地址
    ip = pico_wear.wifi.ifconfig()[0]
    
    # 取得 MAC 地址
    mac_addr = pico_wear.mac_addr
    
    # 取得目前 RTC 的時間
    rtc_time = pico_wear.rtc.datetime()
    time_str = "{:02d}:{:02d}:{:02d}".format(rtc_time[4], rtc_time[5], rtc_time[6])

    # 取得尤拉角
    pico_wear.mpu.update_mahony()
    angles = pico_wear.mpu.get_angles()
    roll_str = "Roll: {:.2f}".format(angles[0])
    pitch_str = "Pitch: {:.2f}".format(angles[1])
    yaw_str = "Yaw: {:.2f}".format(angles[2])

    # 清空 OLED 顯示器
    pico_wear.display.fill(0)

    # 顯示 IP 在第 1 行
    pico_wear.display.text(f"IP: {ip}", 0, 0)

    # 顯示 MAC 地址在第 2~3 行（最多顯示 16 個字元，因此分兩行顯示）
    pico_wear.display.text(f"MAC: {mac_addr[:8]}", 0, 16)  # 顯示前 8 個字元
    pico_wear.display.text(f"     {mac_addr[9:]}", 0, 32)  # 顯示後面的字元

    # 顯示時間在第 4 行
    pico_wear.display.text(f"Time: {time_str}", 0, 48)

    # 顯示尤拉角在第 5~7 行
    pico_wear.display.text(roll_str, 0, 80)
    pico_wear.display.text(pitch_str, 0, 96)
    pico_wear.display.text(yaw_str, 0, 112)

    # 更新顯示器
    pico_wear.display.show()

def connect_wifi():
    """
    連接到指定的 Wi-Fi 網路，並控制 LED 的閃爍狀態。
    """
    pico_wear.wifi.connect(SSID, PASSWORD)
    print('正在連接 Wi-Fi...')
    
    # 持續檢查 Wi-Fi 連線狀態
    while not pico_wear.wifi.isconnected():
        pico_wear.led.value(not pico_wear.led.value())  # LED 閃爍
        time.sleep(0.5)
    
    pico_wear.led.value(1)  # LED 恆亮
    print('Wi-Fi 連接成功')

    # 設置 MQTT 主題為 pico_w/[MAC_addr]/status
    global mqtt_topic
    mac_addr = pico_wear.mac_addr.replace(":", "_")  # 將 MAC 地址中的 ":" 替換為 "_"
    mqtt_topic = f"pico_w/{mac_addr}/status"

def main():
    global pico_wear
    pico_wear = PicoWear()

    # 設定按鈕回呼函式
    pico_wear.register_button_callback(button_clicked)

    # 清空 OLED 顯示器
    pico_wear.display.fill(0)
    # 第 1 行
    pico_wear.display.text(f"SANITYCORE ", 0, 0)
    # 第 2 行
    pico_wear.display.text(f"Ready", 0, 16)  # 顯示前 8 個字元
    # 第 3 行
    pico_wear.display.text(f"Connect to WiFi:", 0, 32)  # 顯示後面的字元
    # # 第 4 行
    pico_wear.display.text(f"{SSID}", 0, 48)
    # 更新顯示器
    pico_wear.display.show()

    print('完成 Pico Wear 的初始化')
    
    connect_wifi()

    # 透過 NTP 設定 RTC
    set_time()

    # 連接到 MQTT 服務器
    mqtt_client = pico_wear.mqtt_connect(mqtt_broker)
    if mqtt_client:
        print('已連接到 MQTT 服務器')
    
    # 持續更新 OLED 顯示內容，每 50 毫秒更新一次尤拉角
    while True:
        display_info_on_oled()
        time.sleep(0.05)  # 每 50 毫秒更新一次

if __name__ == '__main__':
    main()
