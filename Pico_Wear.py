'''
Pico_Wear.py
PicoWear 類別于控制 Pico Wear 硬件，主要函数说明如下：
__init__(): 初始化 PicoWear 对象，设置定时器、LED、显示屏、MPU6050 传感器、Wi-Fi、RTC 和 MQTT 客户端。
detect_button(timer, callback=None): 检测按钮状态，若检测到按钮被按下，调用指定的回调函数。
register_button_callback(callback): 注册按钮Click的回调函数,callback 是一個沒有參數的函數
line_notify_message(token, msg): 使用 LINE Notify API 发送消息。参数 token 为授权令牌，msg 为发送的消息内容。
mqtt_connect(mqtt_broker): 连接到指定的 MQTT 服务器。参数 mqtt_broker 为服务器地址，成功连接后返回 MQTT 客户端对象。
通过使用 PicoWear 类，您可以：
初始化并控制 Pico Wear 的硬件组件。
注册并处理按钮按下事件。
发送消息到 LINE Notify 服务。
连接到 MQTT 服务器进行消息通信。
PicoWear示例：
from Pico_Wear import PicoWear  # 引入 PicoWear 類別
# 创建 PicoWear 对象
pico = ()
# 注册按钮回调函数
def on_button_click():
    print("Button Click")
pico.register_button_callback(on_button_click)#PicoWear只有一個按鈕
Wifi屬性：
    pico_wear.wifi.connect(SSID, PASSWORD)
    pico_wear.wifi.isconnected()
    ip_address = pico_wear.wifi.ifconfig()[0]  # 獲取 IP 地址
    
PicoWear.display使用說明
這是Micropython中一個OLED的驅動
他的大小為128x128的單色螢幕
基本繪圖:
繼承framebuf.FrameBuffer 除了原本framebuf.FrameBuffer的函數還包含如下
畫點: display.pixel(x, y, color)
畫線: display.line(x1, y1, x2, y2, color)
畫矩形: display.draw_rectangle(x, y, width, height, color)
填充矩形: display.fill_rectangle(x, y, width, height, color)
畫圓: display.draw_circle(x, y, radius, color)
填充圓: display.fill_circle(x, y, radius, color)
畫三角形: display.draw_triangle(x0, y0, x1, y1, x2, y2, color)
填充三角形: display.fill_triangle(x0, y0, x1, y1, x2, y2, color)
顯示文字: display.text("Hello", x, y, color)
讀取圖片：Image_fb = display.read_bmp_mono('圖片路徑名稱')
繪製位圖: display.drawBitmap(self,Image_fb, x, y )
更新顯示: display.show()
清除顯示: display.fill(0) 然後 display.show()

注意:
顏色使用1表示點亮，0表示熄滅
座標系統從左上角(0,0)開始
該物件已經使用Double Buffer調用display.show()將緩衝顯示出來
把畫面填充完畢再一次性顯示可以去除閃爍問題

PicoWear.mpu使用說明
Mpu6050_mahony.py
使用 MPU6050 陀螺儀和加速度計感測器設計的。
它可以進行平躺Roll Pitch ，站立時傾斜角度的計算，並透過Mahony濾波算法來實現更準確的姿態估計。
務必每秒100計算才能取得穩定角度,請單獨一個Timer呼叫計算
mpu.update_mahony()  #如果要取得roll pitch
mpu.calculate_tilt_angle() #如果要站立Get_tilt_angle
該類別已使用雙緩衝去除角度計算競爭
注意
Timer中斷頻率高,請在主程式判斷KeyboardInterrupt時使用for timer in timers: timer.deinit(),關閉所有Timer
主要方法
__init__(self, i2c, addr=0x68)
    初始化 MPU6050 類別。
    參數 i2c 是必須的，它是一個已配置的 I2C 對象。
    參數 addr 是設備的 I2C 地址，默認為 0x68。
calibrate(self, samples=100)
    校準 MPU6050 roll pitch，減少讀數誤差。
update_mahony(self)
    計算mpu6050平躺的。更新姿態估計，使用 Mahony 濾波算法。
    這個方法會自動根據加速度計和陀螺儀的讀數更新四元數，從而得到較準確的姿態角。
    每秒需要進行100運算,運算結果使用get_angles() 取得
get_angles(self)
    獲取計算後的歐拉角（Roll, Pitch, Yaw）。角度以度（°）為單位。
read_accel(self)
    讀取加速度數據，從 MPU6050 的加速度計傳感器獲取數據。返回的加速度數據經過轉換為 g 單位（重力加速度的倍數）。
read_gyro(self)
    讀取陀螺儀數據，從 MPU6050 的陀螺儀傳感器獲取數據。返回的陀螺儀數據經過轉換為度每秒（deg/s），描述角速度。
read_accel_raw(self)
    直接讀取原始加速度數據。
calculate_tilt_angle(self)
    計算mpu6050站立之後的傾斜角度，使用互補濾波器來平滑角度變化，以應對快速動態變化。
    務必每秒100計算才能算出穩定角度。
    只有計算要取出角度請使用Get_tilt_angle()
Get_tilt_angle(self)
    取得calculate_tilt_angles計算後的tilt角度
    此方法返回tilt角度以(度)為單位，並會將角度維持在 -180° 到 180° 的範圍內。
calibrate_tilt(self, num_samples=100)
    校準站立時傾斜角度，主要用於設置加速度計的偏移值。
  
'''

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