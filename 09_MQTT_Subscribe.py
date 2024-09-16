from Pico_Wear import PicoWear
import time

# ========== 全域變數 ========== 
pico_wear = None
mqtt_topic = 'pico_w'
mqtt_broker = 'broker.mqttgo.io'

# ============================= 

def on_message(topic, msg):
    """
    處理接收到的 MQTT 訊息，顯示在 OLED 上並轉態 LED。
    
    Args:
        topic: 訊息的主題。
        msg: 訊息內容。
    """
    pico_wear.led.value(not pico_wear.led.value())  # 轉態 LED
    display_message = msg.decode()  # 解碼訊息
    # 清空顯示器
    pico_wear.display.fill(0)
    # 分行顯示訊息，每行最多 16 個字
    for i in range(0, len(display_message), 16):
        pico_wear.display.text(display_message[i:i+16], 0, i//16 * 10)
    pico_wear.display.show()

def connect_wifi():
    """
    連接到指定的 Wi-Fi 網路，並控制 LED 的閃爍狀態。
    """
    ssid = "TP-Link_5E4C_2.4G"
    password = "0976023369"
    pico_wear.wifi.connect(ssid, password)
    print('正在連接 Wi-Fi...')
    
    # 持續檢查 Wi-Fi 連線狀態
    while not pico_wear.wifi.isconnected():
        pico_wear.led.value(not pico_wear.led.value())  # LED 閃爍
        time.sleep(0.5)
    
    pico_wear.led.value(1)  # LED 恆亮
    print('已連接到 Wi-Fi')

def main():
    global pico_wear
    pico_wear = PicoWear()
    print('完成 Pico Wear 的初始化')
    
    connect_wifi()
    
    # 連接到 MQTT 服務器
    mqtt_client = pico_wear.mqtt_connect(mqtt_broker)
    if mqtt_client:
        print('已連接到 MQTT 服務器')
        mqtt_client.set_callback(on_message)  # 先設置回調函數
        mqtt_client.subscribe(mqtt_topic)  # 然後訂閱主題
    
        # 不斷輪詢 MQTT 訊息
        while True:
            try:
                mqtt_client.check_msg()  # 檢查是否有新的 MQTT 訊息
                time.sleep(1)
            except Exception as e:
                print(f"MQTT 發生錯誤: {e}")
                time.sleep(1)

if __name__ == '__main__':
    main()
