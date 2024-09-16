from Pico_Wear import PicoWear  # 引入 PicoWear 類別
import time

# ========== 全域變數 ========== 
pico_wear = None

# 顯示內容時每行最多顯示 16 個字元
MAX_CHARS_PER_LINE = 16


def button_clicked():
    """
    按鈕回呼函式，當按鈕被按下時，發送 LINE Notify 訊息。
    """
    # 取得 RTC 時間和日期
    rtc_time = pico_wear.rtc.datetime()
    
    # 格式化時間與日期
    date_str = "{:04d}-{:02d}-{:02d}".format(rtc_time[0], rtc_time[1], rtc_time[2])  # 年-月-日
    time_str = "{:02d}:{:02d}:{:02d}".format(rtc_time[4], rtc_time[5], rtc_time[6])  # 時:分:秒
    
    # 將日期與時間結合成一個字串
    message = "Date: {}\nTime: {}".format(date_str, time_str)
    
    # 發送到 LINE Notify
    pico_wear.line_notify_message("VSCM3DTZX4goUUHagdL4HshVYBaoTjvADsEINQVEXbg", message)

def connect_wifi():
    """
    連接到指定的 Wi-Fi 網路。
    """
    SSID = "TP-Link_5E4C_2.4G"
    PASSWORD = "0976023369"
    
    pico_wear.wifi.active(True)  # 啟用 Wi-Fi
    pico_wear.wifi.connect(SSID, PASSWORD)  # 連接到指定的 Wi-Fi
    
    print('正在連接 Wi-Fi...')
    
    # 等待連接成功
    while not pico_wear.wifi.isconnected():
        pico_wear.led.value(not pico_wear.led.value())  # LED 閃爍
        time.sleep(0.5)  # 每 0.5 秒閃爍一次
        
    # 連接成功，LED 恆亮
    pico_wear.led.value(1)
    print('Wi-Fi 連接成功')

def format_text_for_oled(text):
    """
    將超過 16 個字元的文字進行換行處理，適應 OLED 顯示器的限制。
    
    Args:
        text: 要顯示的字串
    
    Returns:
        list: 一個包含每行字串的列表，每行最多 16 個字元
    """
    lines = []
    # 將文字按照 16 字元切割成多行
    for i in range(0, len(text), MAX_CHARS_PER_LINE):
        lines.append(text[i:i + MAX_CHARS_PER_LINE])
    return lines

def display_time_on_oled():
    """
    取得並顯示目前時間與日期在 OLED 上，超過 16 字元自動換行顯示。
    """
    # 取得目前 RTC 的時間
    rtc_time = pico_wear.rtc.datetime()  # 回傳格式: (年, 月, 日, 星期, 時, 分, 秒, 毫秒)
    
    # 格式化時間與日期
    date_str = "{:04d}-{:02d}-{:02d}".format(rtc_time[0], rtc_time[1], rtc_time[2])  # 年-月-日
    time_str = "{:02d}:{:02d}:{:02d}".format(rtc_time[4], rtc_time[5], rtc_time[6])  # 時:分:秒
    
    # 將日期與時間結合成一個字串
    full_text = "Date: {}\nTime: {}".format(date_str, time_str)
    
    # 清空 OLED 顯示器
    pico_wear.display.fill(0)
    
    # 將文字格式化為每行最多 16 字元並顯示在 OLED 上
    formatted_lines = format_text_for_oled(full_text)
    
    # 逐行顯示在 OLED 上，每行高度相差 16 像素
    for i, line in enumerate(formatted_lines):
        pico_wear.display.text(line, 0, i * 16)
    
    # 更新顯示器內容
    pico_wear.display.show()

def main():
    global pico_wear
    pico_wear = PicoWear()

    # 設定按鈕回呼函式
    pico_wear.register_button_callback(button_clicked)

    print('完成 Pico Wear 的初始化')
    
    connect_wifi()
    # 持續更新顯示時間與日期
    while True:
        display_time_on_oled()
        time.sleep(1)  # 每秒更新一次顯示內容

if __name__ == '__main__':
    main()