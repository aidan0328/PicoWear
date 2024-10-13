from Pico_Wear import PicoWear  # 引入 PicoWear 類別
import time

# ========== 全域變數 ==========
pico_wear = None

# =============================

def main():
    global pico_wear
    pico_wear = PicoWear()
    print('完成 Pico Wear 的初始化')
    
    while True:
        time.sleep(0.1)

if __name__ == '__main__':
    main()
