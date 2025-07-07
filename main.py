import sys
import time

import UI.untitled_ui
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.QtCore import QTimer
import datetime

from Software.Camera import Camera  # 导入Camera类
from Software.Serial import SerialPort  # 导入SerialPort类
from Software.IOStream import Stream  # 导入Stream类
from Software.Model import Model  # 导入Model类
import Software.MyUART
from Hardware.LabelSending import LabelSender  # 导入LabelSender类


class MainWindow(QMainWindow, UI.untitled_ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # 初始化UI

        # 对象-权重映射字典
        # self.weight_file = None  # 权重文件
        self.object_weights = {}  # 存储对象和权重的映射关系
        self.current_object = None  # 当前选中的识别对象

        # 创建自定义输出流并连接信号
        self.stream_self = Stream()
        self.stream_self.new_text.connect(self.append_text)
        # 重定向标准输出到自定义流
        sys.stdout = self.stream_self

        # 翻页按钮
        self.pushButton_pape1.clicked.connect(self.click_button1)
        self.pushButton_pape2.clicked.connect(self.click_button2)

        # 初始化Model类
        self.model = Model()
        # 初始化Camera类
        self.camera = Camera(self.label_camera,
                             self.pushButton_camera,
                             self.model,
                             self.pushButton_photo,
                             self.label_detect,
                             self.label_decide)
        self.pushButton_camera.clicked.connect(self.camera.video_button)  # 打开摄像头
        self.pushButton_stop_detect.clicked.connect(self.camera.stop_detection)  # 停止识别
        self.pushButton_photo.clicked.connect(self.camera.save_photo)  # 保存图片

        # 初始化SerialPort类
        self.serial = SerialPort(self.comboBox,  # 串口号选择框
                                 self.comboBox_baudrate,  # 波特率选择框
                                 self.comboBox_data,  # 数据位选择框
                                 self.comboBox_stop,  # 停止位选择框
                                 self.pushButton_open_close)
        self.pushButton_find_ports.clicked.connect(self.serial.find_ports)  # 查找串口
        self.pushButton_open_close.clicked.connect(self.serial.toggle_serial)  # 打开/关闭串口
        self.pushButton_send.clicked.connect(self.send_data)  # 发送数据
        self.pushButton_clear_send.clicked.connect(self.clear_send)  # 清空发送
        self.pushButton_clear_receive.clicked.connect(self.clear_receive)  # 清空接收
        self.toolButton_weight.clicked.connect(self.load_weights)  # 加载权重文件
        self.pushButton_detect.clicked.connect(self.enable_detection)  # 识别按钮

        # 初始化定时器用于接收数据
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_data)
        self.timer.start(100)  # 每100毫秒读取一次

        self.label_sender = LabelSender(self.camera,
                                        self.serial,
                                        self.model,
                                        self)
        self.label_sender.detect_trigger.connect(self.enable_detection)  # 识别按钮

    def append_text(self, text):
        """重定义print输出"""
        self.textEdit_iostream.append(text)

    def send_data(self):
        """发送数据"""
        try:
            data = self.textEdit_send.toPlainText()
            # print(f"从输入框获取数据{data}")
            if not data:
                print("发送内容为空")
                return

            hex_data = data.replace(' ', '').replace('\n', '').replace('\r', '')  # 去除空格和换行符
            if self.checkBox_HEXSend.isChecked():
                if len(hex_data) % 2 != 0:
                    raise ValueError("Hex数据长度必须是偶数")
                data_bytes = bytes.fromhex(hex_data)  # 转换为字节

                # 逐个发送字节
                for byte in data_bytes:
                    if self.comboBox_barity.currentText() == 'CRC':
                        # 假设 CRC 处理需要单个字节的封装（根据实际协议调整）
                        data_final = Software.MyUART.build_packet(bytes([byte]))
                    else:
                        data_final = bytes([byte])  # 单个字节
                    self.serial.send_data(data_final)  # 串口发送
                    time.sleep(0.01)
                    
                else:
                    data_final = data_bytes
            else:
                data_final = data.encode('utf-8')
                self.serial.send_data(data_final)  # 串口发送

        except ValueError as e:
            print(f"发送失败：{e}")
        except Exception as e:
            print(f"发送失败：{e}")

    def read_data(self):
        """读取数据（支持Hex接收和时间戳）"""
        if self.serial.is_open:
            data_bytes = self.serial.receive_data()

            if data_bytes:
                # Hex显示处理
                if self.checkBox_HEXReceive.isChecked():
                    data_display = ' '.join(f"{b:02X}" for b in data_bytes) + ' '
                else:
                    try:
                        data_display = data_bytes.decode('gbk')
                    except UnicodeDecodeError:
                        data_display = str(data_bytes)  # 备选显示方案

                # 时间戳处理
                if self.checkBox_time.isChecked():
                    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
                    data_display = timestamp + data_display

                # 换行处理
                if self.checkBox_rn.isChecked():
                    data_display += '\r\n'

                # 输出到textEdit_receive
                self.textEdit_receive.insertPlainText(data_display)
                # print(f"接收数据{data_display}")
                # 进入下位机连接函数
                self.label_sender.handle_received_data(data_bytes)

    def clear_send(self):
        """清空发送框"""
        self.textEdit_send.clear()

    def clear_receive(self):
        """清空接收框"""
        self.textEdit_receive.clear()

    def load_weights(self):
        """为当前选择的对象加载权重"""
        current_obj = self.comboBox_recognizing_Objects.currentText()  # 获取当前选择
        if not current_obj:
            print("请先选择识别对象！")
            return

        # 打开文件对话框
        weight_file, _ = QFileDialog.getOpenFileName(self,
                                                     f"选择{current_obj}权重文件",
                                                     "",
                                                     "Weights Files (*.pt);;All Files (*)"
                                                     )

        if weight_file:
            # 通过模型管理器加载权重
            if self.model.load_weights(current_obj, weight_file):
                print(f"已为 {current_obj} 绑定权重: {weight_file}")

    def enable_detection(self):
        """原检测逻辑增强（支持动态权重）"""
        current_obj = self.comboBox_recognizing_Objects.currentText()

        # 检查是否已加载权重
        if current_obj not in self.model.loaded_models:
            # 弹窗提示用户选择权重文件
            weight_file, _ = QFileDialog.getOpenFileName(
                self,
                f"请选择{current_obj}的权重文件",
                "Weight/",  # 默认打开权重目录
                "Weight Files (*.pt)"
            )
            if not weight_file:
                print("未选择权重文件，检测已取消")
                return

            if self.model.load_weights(current_obj, weight_file):
                print(f"动态加载权重: {weight_file}")
            else:
                return

        # 启动检测
        self.camera.start_detection(current_obj)
        print(f"开始检测: {current_obj}")

    def click_button1(self):
        self.stackedWidget.setCurrentIndex(0)

    def click_button2(self):
        self.stackedWidget.setCurrentIndex(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
