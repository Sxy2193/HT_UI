import sys
import UI.untitled
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.QtCore import QTimer

from Software.Camera import Camera  # 导入Camera类
from Software.Serial import SerialPort  # 导入SerialPort类
from Software.IOStream import Stream  # 导入Stream类


class MainWindow(QMainWindow, UI.untitled.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # 初始化UI

        self.weight_file = None  # 权重文件

        # 创建自定义输出流并连接信号
        self.stream_self = Stream()
        self.stream_self.new_text.connect(self.append_text)
        # 重定向标准输出到自定义流
        sys.stdout = self.stream_self

        # 翻页按钮
        self.pushButton_pape1.clicked.connect(self.click_button1)
        self.pushButton_pape2.clicked.connect(self.click_button2)

        # 初始化Camera类
        self.camera = Camera(self.label_camera, self.pushButton_camera)
        self.pushButton_camera.clicked.connect(self.camera.video_button)  # 打开摄像头

        # 初始化SerialPort类
        self.serial = SerialPort(
            self.comboBox,  # 串口号选择框
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
        if data:
            self.serial.send_data(data)  # 发送数据

    def read_data(self):
        """读取串口数据并显示到接收框"""
        if self.serial.is_open:
            data = self.serial.receive_data()
            if data:
                self.textEdit_receive.insertPlainText(data)  # 追加接收的数据

    def clear_send(self):
        """清空发送框"""
        self.textEdit_send.clear()

    def clear_receive(self):
        """清空接收框"""
        self.textEdit_receive.clear()

    def load_weights(self):
        """打开文件对话框选择权重文件"""
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        weight_file, _ = QFileDialog.getOpenFileName(self, "选择权重文件", "", "Weights Files (*.pt);;All Files (*)",
                                                     options=options)
        if weight_file:  # 如果成功选择了权重文件
            self.weight_file = weight_file  # 存储权重文件路径
            print(f"已选择权重文件: {self.weight_file}")
        else:
            print("未选择权重文件！")

    def enable_detection(self):
        """点击识别按钮后启用检测功能"""
        if self.weight_file:
            self.camera.load_model(self.weight_file)  # 加载模型权重
        else:
            print("未选择权重文件！")

    def click_button1(self):
        self.stackedWidget.setCurrentIndex(0)

    def click_button2(self):
        self.stackedWidget.setCurrentIndex(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
