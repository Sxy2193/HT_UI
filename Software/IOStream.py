from PyQt5 import QtCore


# 自定义输出流类，用于捕获输出
class Stream(QtCore.QObject):
    new_text = QtCore.pyqtSignal(str)

    def write(self, text):
        # 去除末尾的换行符
        clean_text = text.rstrip('\n')
        #
        self.new_text.emit(clean_text)

    def flush(self):
        pass  # 不需要执行任何操作
