import time

import Software.MyUART as MyUART
from PyQt5.QtCore import QObject, pyqtSignal


class LabelSender(QObject):
    # send_trigger = pyqtSignal(bytes)  # 串口发送信号
    camera_trigger = pyqtSignal()  # 摄像头触发信号
    detect_trigger = pyqtSignal()  # 触发检测信号

    def __init__(self, camera, serial, model, main_ui):
        super().__init__()
        self.camera = camera  # Camera实例
        self.serial = serial  # SerialPort实例
        self.model = model  # Model实例
        self.main_ui = main_ui
        # self.label_decide = label_decide  # 标签选择框
        self.last_label = None  # 上一次发送的标签
        self.last_07_time = 0
        self.label_map = \
            {  # 标签到指令的映射
                "c1": 0x01,
                "c2": 0x02,
                "c3": 0x03,
                # 添加更多标签映射...
            }

        # 设置定时检测（100ms间隔）
        self.timer = self.startTimer(100)

    # def timerEvent(self, event):
    #     """定时检测当前标签"""
    #     if not self.serial.is_open:
    #         return
    #
    #     current_label = self.get_current_label()
    #     if current_label and current_label != self.last_label:
    #         self.send_label(current_label)
    #         self.last_label = current_label

    def handle_received_data(self, data_bytes):
        """整合指令处理"""
        if data_bytes == b'\x04':
            print("收到04指令：打开/关闭摄像头")
            self.camera.video_button()
        elif data_bytes == b'\x05':
            print("收到05指令：启动识别")
            self.main_ui.enable_detection()
        elif data_bytes == b'\x07':
            # 添加时间阈值检测
            current_time = time.time()
            if current_time - self.last_07_time < 0.6:
                print("0.6秒内重复07指令，已忽略")
                return

            self.last_07_time = current_time  # 更新最后处理时间
            try:
                # if not hasattr(self.camera, 'label_decide') or self.camera.label_decide is None:
                if self.camera.label_decide is None:
                    print("错误：label_decide 未正确初始化！")
                    return
                print("收到07指令：发送当前标签")
                self.camera.display_box()  # 显示检测框和标签

                # print({self.camera.label_decide.text()})
                current_label = self.main_ui.label_decide.text()
                print(f"当前标签: {current_label}")
                if current_label:
                    self.send_label(current_label)

            except AttributeError as e:
                print(f"访问label_decide失败:{e}")

    # def get_current_label(self):
    #     """从Camera获取当前检测标签"""
    #     try:
    #         print(f"当前标签: {self.camera.label_decide.text()}")
    #         return self.camera.label_decide.text()
    #
    #     except AttributeError:
    #         return None

    def send_label(self, label):
        """构造并发送标签数据包"""
        if label not in self.label_map:
            print(f"未知标签: {label}")
            return
        # 构造数据帧
        cmd_byte = bytes([self.label_map[label]])
        # packet = MyUART.build_packet(cmd_byte)
        # packet = b'\xFF' + cmd_byte + b'\xDD'  # 示例数据包格式
        packet = MyUART.build_command(cmd_byte)
        # 触发串口发送
        if self.serial.is_open:

            for byte in packet:
                data_final = bytes([byte])  # 单个字节
                self.serial.send_data(data_final)  # 串口发送
                time.sleep(0.03)

            print(f"已发送标签: {label} -> {packet.hex(' ', 1)}")
