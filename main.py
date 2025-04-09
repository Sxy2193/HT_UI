import sys
import UI.untitled_ui
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.QtCore import QTimer
import datetime

from Software.Camera import Camera  # 导入Camera类
from Software.Serial import SerialPort  # 导入SerialPort类
from Software.IOStream import Stream  # 导入Stream类
from Software.Model import Model  # 导入Model类
import Software.MyUART


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

    def append_text(self, text):
        """重定义print输出"""
        self.textEdit_iostream.append(text)

    def send_data(self):
        """发送数据"""
        data = self.textEdit_send.toPlainText()  # 获取发送框中的数据
        if not data:
            return

        try:
            hex_data = data.replace(' ', '').replace('\n', '').replace('\r', '')
            if self.checkBox_HEXSend.isChecked():
                if len(hex_data) % 2 != 0:
                    raise ValueError("Hex数据长度必须是偶数")
                data_bytes = bytes.fromhex(hex_data)
                if self.comboBox_barity.currentText() == 'CRC':
                    data_final = Software.MyUART.build_packet(data_bytes)
                else:
                    data_final = data_bytes
            else:
                data_final = data.encode('utf-8')

            self.serial.send_data(data_final)
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

                self.textEdit_receive.insertPlainText(data_display)

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
        """切换检测状态"""
        current_obj = self.comboBox_recognizing_Objects.currentText()  # 直接获取当前选择
        if not current_obj:
            print("请先选择识别对象！")
            self.pushButton_detect.setChecked(False)
            return

        if current_obj not in self.model.loaded_models:
            print(f"请先为 [{current_obj}] 加载权重文件！")
            self.pushButton_detect.setChecked(False)
            return
        self.camera.start_detection(current_obj)  # 传递当前对象到摄像头模块

    def click_button1(self):
        self.stackedWidget.setCurrentIndex(0)

    def click_button2(self):
        self.stackedWidget.setCurrentIndex(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
