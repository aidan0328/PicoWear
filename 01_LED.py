from Pico_Wear import PicoWear  # 引入 PicoWear 類別
import time

# ========== 全域變數 ========== 
pico_wear = None

# ============================= 

def main():
    global pico_wear
    pico_wear = PicoWear()
    print('完成 Pico Wear 的初始化')
    
    # LED 閃爍控制
    led_on = False
    while True:
        if led_on:
            pico_wear.led.value(1)  # 點亮 LED
        else:
            pico_wear.led.value(0)  # 熄滅 LED
        
        led_on = not led_on  # 切換 LED 狀態
        time.sleep(0.1)  # 等待 0.1 秒

if __name__ == '__main__':
    main()
