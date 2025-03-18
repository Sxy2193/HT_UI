import cv2 as cv
from PyQt5 import QtGui, QtCore
from Software.Model import Model  # 导入Model类


class Camera:
    def __init__(self, label_camera, pushButton_camera, model):
        self.image = None
        self.label_camera = label_camera  # 用于显示视频的QLabel
        self.pushButton_camera = pushButton_camera  # 控制摄像头的按钮
        self.timer = QtCore.QTimer()  # 定时器，用于刷新视频帧
        self.timer.timeout.connect(self.show_video)  # 连接定时器超时信号到显示视频函数
        self.cap_video = None  # 摄像头对象
        self.flag = 0  # 标记摄像头状态：0表示关闭，1表示打开
        self.camera_in_use = False  # 标记摄像头是否正在使用
        self.model = model  # 使用外部传入的Model实例
        self.detecting_object = None  # 当前检测目标

    def __del__(self):
        """析构函数：释放摄像头资源"""
        if self.cap_video is not None and self.cap_video.isOpened():
            self.cap_video.release()

    def video_button(self):
        """按钮点击事件：打开或关闭摄像头"""
        if self.flag == 0:  # 如果是关闭状态
            if self.camera_in_use:
                print("另一个摄像头正在使用，无法打开本地摄像头。")
                return
            self.cap_video = cv.VideoCapture(1)  # 打开摄像头
            if not self.cap_video.isOpened():  # 检查摄像头是否成功打开
                print("无法打开摄像头")
                return
            self.timer.start(50)  # 启动定时器，每50毫秒刷新一次
            self.flag = 1  # 标记摄像头为打开状态
            self.pushButton_camera.setText('关闭本地摄像头')  # 更新按钮文本
            self.camera_in_use = True  # 标记摄像头正在使用
        else:  # 如果是打开状态
            self.timer.stop()  # 停止定时器
            if self.cap_video is not None:
                self.cap_video.release()  # 释放摄像头资源
            self.label_camera.clear()  # 清空QLabel中的内容
            self.pushButton_camera.setText('打开本地摄像头')  # 更新按钮文本
            self.flag = 0  # 标记摄像头为关闭状态
            self.camera_in_use = False  # 标记摄像头未使用

    def show_video(self):
        """定时器超时事件：从摄像头读取一帧并显示"""
        ret, img = self.cap_video.read()  # 读取一帧
        if ret:
            # 如果检测目标存在，调用模型检测
            if self.detecting_object:
                try:
                    img = self.model.detect(img, self.detecting_object)  # 确保返回处理后的图像
                except Exception as e:
                    print(f"检测失败: {e}")
                    img = cv.putText(img, "Detection Error", (50, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # 显示图像
            self.show_cv_img(img)
        else:
            print("无法读取摄像头图像!")

    def show_cv_img(self, img):
        """label上显示图像函数"""
        frame = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        self.image = QtGui.QImage(frame.tobytes(), frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
        # 调整图像大小以适应标签
        image = self.image.scaled(self.label_camera.width(), self.label_camera.height())
        # 在标签上显示图像
        self.label_camera.setPixmap(QtGui.QPixmap.fromImage(image))

    def start_detection(self, object_name):
        """启动检测"""
        self.detecting_object = object_name
        print(f"开始检测: {object_name}")

    def stop_detection(self):
        """停止检测"""
        self.detecting_object = None
        print("停止检测")
