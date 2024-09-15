import network
import rp2
import machine
from machine import Pin, I2C, RTC, Timer, mem32
import time
import OLED_SH1107
from Mpu6050_mahony import MPU6050
import urequests as requests  # 修改為 urequests，這是 MicroPython 使用的模組
import ubinascii
from umqtt.simple import MQTTClient

class PicoWear:
    def __init__(self):
        """
        初始化 PicoWear 物件。此函數會初始化定時器、LED、顯示器、MPU6050 傾斜感應器、Wi-Fi、RTC 與 MQTT 客戶端。
        """
        # 儲存定時器變數，使其在其他函數中可以使用
        self.tim = Timer()
        self.led = None
        self.display = None
        self.mpu = None
        self.wifi = None
        self.rtc = None
        self.mac_addr = None
        self.mqtt_client = None

        # 初始化Pico Wear硬體
        self.init_hardware()

    def init_hardware(self, button_callback=None):
        """
        初始化 PicoWear 所有硬體，包含 OLED 顯示器、MPU6050 傾斜感應器、Wi-Fi、RTC 與 LED。
        並且設定定時器檢測按鈕的狀態。
        
        Args:
            button_callback: 若按鈕被按下，呼叫的回呼函數。
        """
        #====================PICO WEAR Init====================================
        # OLED 的電源
        PAD_CONTROL_REGISTER = 0x4001c024
        mem32[PAD_CONTROL_REGISTER] = mem32[PAD_CONTROL_REGISTER] | 0b0110000

        # 設定 GP9 為輸出，並設置輸出(GND), GP8 為輸出，並設置輸出 1
        pin9 = Pin(9, Pin.OUT, value=0)
        pin8 = Pin(8, Pin.OUT, value=0)
        time.sleep(1)
        pin8 = Pin(8, Pin.OUT, value=1)

        # MPU6050 的電源
        PAD_CONTROL_REGISTER = 0x4001c05c
        mem32[PAD_CONTROL_REGISTER] = mem32[PAD_CONTROL_REGISTER] | 0b0110000

        # GP22 為輸出，並設置輸出 1
        pin22 = Pin(22, Pin.OUT, value=0)
        time.sleep(1)
        pin22 = Pin(22, Pin.OUT, value=1)
        time.sleep(1)

        # 初始化 I2C
        i2c0 = I2C(0, scl=Pin(21), sda=Pin(20), freq=400000)
        i2c1 = I2C(1, scl=Pin(7), sda=Pin(6), freq=400000)
        self.display = OLED_SH1107.SH1107_I2C(128, 128, i2c1, None, 0x3c)

        # 清空顯示屏
        self.display.fill(0)
        self.display.show()

        # 初始化 MPU6050 傾斜感應器
        self.mpu = MPU6050(i2c0)

        # 初始化定時器，每 40 毫秒檢測按鈕狀態
        self.tim.init(period=40, mode=Timer.PERIODIC, callback=lambda t: self.detect_button(t, button_callback))

        #===============開啟內建硬件======================
        # 內建的 LED 初始化
        self.led = Pin('LED', machine.Pin.OUT)

        # 啟用 RTC
        self.rtc = RTC()

        # 啟動 Wi-Fi 並獲取 MAC 地址
        self.wifi = network.WLAN(network.STA_IF)
        self.wifi.active(True)
        self.mac_addr = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()

        # 超頻至 250MHz
        machine.freq(250000000)

    def detect_button(self, timer, callback=None):
        """
        檢測按鈕狀態，並在按鈕按下時呼叫回呼函數。
        
        Args:
            timer: 定時器，用來週期性檢測按鈕狀態。
            callback: 按鈕被按下時呼叫的回呼函數。
        """
        button = rp2.bootsel_button()
        if button == 1:
            # 確保按鈕釋放後再執行回調
            while button == 1:
                button = rp2.bootsel_button()
            if callback:
                callback()  # 呼叫回呼函數

    def register_button_callback(self, callback):
        """
        註冊一個按鈕的回呼函數，當按鈕被按下時，定時器將呼叫該回呼函數。
        
        Args:
            callback: 按鈕按下時需要呼叫的回呼函數。
        """
        # 重新設置定時器的回呼函數
        self.tim.init(period=40, mode=Timer.PERIODIC, callback=lambda t: self.detect_button(t, callback))

    def line_notify_message(self, token, msg):
        """
        向 LINE Notify API 發送訊息。
        
        Args:
            token: LINE Notify 的授權 Token。
            msg: 要發送的訊息內容。
        """
        headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = 'message=' + msg
        try:
            # 使用 POST 方法發送訊息到 LINE Notify API
            r = requests.post("https://notify-api.line.me/api/notify", headers=headers, data=payload)
            r.close()
        except Exception as e:
            print("LINE Notify 無法連接，錯誤: " + str(e))

    def mqtt_connect(self, mqtt_broker):
        """
        連接到指定的 MQTT 伺服器。
        
        Args:
            mqtt_broker: MQTT 伺服器的地址。
        
        Returns:
            返回已連接的 MQTT 客戶端物件，如果無法連接則返回 None。
        """
        try:
            # 使用 MAC 地址生成唯一的 Client ID
            client_id = 'pico_w_' + self.mac_addr
            self.mqtt_client = MQTTClient(client_id, mqtt_broker)
            self.mqtt_client.connect()
        except Exception as e:
            self.mqtt_client = None
            print("MQTT 無法連接，錯誤: " + str(e))
        return self.mqtt_client