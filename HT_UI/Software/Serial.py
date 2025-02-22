import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import QMessageBox


class SerialPort:
    def __init__(self, combo_box_port, combo_box_baud, combo_box_data_bits, combo_box_stop_bits, pushButton_open_close):
        self.combo_box_port = combo_box_port  # 串口号选择框
        self.combo_box_baud = combo_box_baud  # 波特率选择框
        self.combo_box_data_bits = combo_box_data_bits  # 数据位选择框
        self.combo_box_stop_bits = combo_box_stop_bits  # 停止位选择框
        self.pushButton_open_close = pushButton_open_close
        self.serial_port = None  # 串口对象
        self.is_open = False  # 串口是否打开

    def find_ports(self):
        """查找可用串口并更新到combo_box_port"""
        ports = serial.tools.list_ports.comports()
        self.combo_box_port.clear()  # 清空当前选项
        if not ports:
            print("未找到任何串口设备!")
        else:
            for port in ports:
                self.combo_box_port.addItem(port.device)  # 添加可用串口到下拉框
            print("发现串口设备: ", [port.device for port in ports])

    def toggle_serial(self):
        """切换串口状态（打开/关闭）"""
        if self.is_open:
            self.close_serial()
        else:
            self.open_serial()

    def open_serial(self):
        """打开串口"""
        port = self.combo_box_port.currentText()  # 获取选择的串口号
        baud_rate = int(self.combo_box_baud.currentText())  # 获取选择的波特率
        data_bits = int(self.combo_box_data_bits.currentText())  # 获取选择的数据位
        stop_bits = int(self.combo_box_stop_bits.currentText())  # 获取选择的停止位

        if not port:
            QMessageBox.warning(None, "警告", "请选择串口号！")
            return

        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baud_rate,
                bytesize=data_bits,
                stopbits=stop_bits,
                timeout=1  # 设置超时时间
            )
            self.is_open = True
            self.pushButton_open_close.setText('关闭串口')  # 更新按钮文本
            print(f"串口 {port} 已打开")
        except Exception as e:
            QMessageBox.critical(None, "错误", f"打开串口失败：{e}")

    def close_serial(self):
        """关闭串口"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.is_open = False
            self.pushButton_open_close.setText('打开串口')  # 更新按钮文本
            print("串口已关闭!")
        else:
            print("串口未打开!")

    def send_data(self, data):
        """发送数据"""
        if not self.is_open:
            QMessageBox.warning(None, "警告", "串口未打开！")
            return

        try:
            self.serial_port.write(data.encode('utf-8'))  # 发送数据
        except Exception as e:
            QMessageBox.critical(None, "错误", f"发送数据失败：{e}")

    def receive_data(self):
        """接收数据"""
        if not self.is_open:
            QMessageBox.warning(None, "警告", "串口未打开！")
            return None

        try:
            data = self.serial_port.read_all()  # 读取所有数据
            return data.decode('utf-8')  # 返回解码后的数据
        except Exception as e:
            QMessageBox.critical(None, "错误", f"接收数据失败：{e}")
            return None
