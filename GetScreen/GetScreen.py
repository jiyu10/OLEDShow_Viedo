import cv2
from PIL import ImageGrab
import numpy as np
import serial
#打开串口
serial_port = serial.Serial('COM7', 921600)
# 将128*64的二值化图像转换为OLED数组格式
def img2array(frame):
    array = np.zeros((8, 128), dtype='uint8')

    for j in range(64):
        for i in range(128):
            if frame[j][i] > 0:
                array[j // 8][i] = (array[j // 8][i]) | (0x01 << (j % 8))

    return array

def capture_screen():
    try:
        # 直接捕获整个屏幕
        screen = ImageGrab.grab()
    except IOError:
        print("无法捕获屏幕。请检查屏幕共享设置或权限。")
        return None
    # 将PIL图像转换为numpy数组
    screen_np = np.array(screen)
    # 由于PIL的图像是RGB，而OpenCV默认使用BGR，所以需要转换颜色空间
    screen_np = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
    return screen_np

def main():
    capture_rate = 25  # 设置捕获屏幕的频率（单位：ms）
    while True:
        # 捕获屏幕图像
        img = capture_screen()
        # 帧图像处理
        img = cv2.resize(img, (128, 64))  # 修改尺寸
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 灰度化
        ret,img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        #img = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)[1]  # 二值化
        if img is None:
            break  # 如果无法捕获屏幕，则退出循环
        # 显示图像
        cv2.imshow('Real-time Desktop', img)
        # 转换为数组并使用串口发送
        img_array = img2array(img)
        serial_port.write(img_array)

        # 按'q'退出
        if cv2.waitKey(capture_rate) & 0xFF == ord('q'):
            break
    # 释放资源并关闭窗口
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()