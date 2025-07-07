import cv2 as cv
from PyQt5 import QtGui, QtCore
# from Software.Model import Model  # 导入Model类
import datetime
import time

# 宏Camera_Selection，用于选择摄像头
Camera_Selection = 4  # 4


class Camera:
    def __init__(self, label_camera, pushButton_camera, model, pushButton_photo, label_detect, label_decide):
        self.image = None
        self.label_camera = label_camera  # 用于显示视频的QLabel
        self.pushButton_camera = pushButton_camera  # 控制摄像头的按钮
        self.pushButton_photo = pushButton_photo  # 保存图片的按钮
        self.timer = QtCore.QTimer()  # 定时器，用于刷新视频帧
        self.timer.timeout.connect(self.show_video)  # 连接定时器超时信号到显示视频函数
        self.cap_video = None  # 摄像头对象
        self.flag = 0  # 标记摄像头状态：0表示关闭，1表示打开
        self.camera_in_use = False  # 标记摄像头是否正在使用
        self.model = model  # 使用外部传入的Model实例
        self.detecting_object = None  # 当前检测目标

        self.frame_count = 0  # 帧计数器
        self.start_time = time.time()  # 记录开始时间
        self.fps = 0  # 帧率

        self.label_capture = label_detect  # 新增：用于显示捕捉区域的label
        self.current_boxes = []  # 新增：存储当前检测框坐标
        self.capture_timer = QtCore.QTimer()  # 新增：捕捉定时器
        # self.capture_timer.timeout.connect(self.display_box)  # 连接定时器超时信号到显示检测框函数
        self.capture_timer.start(1000)  # 每秒触发一次
        self.label_decide = label_decide  # 用于显示检测结果的label

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
            self.cap_video = cv.VideoCapture(int(Camera_Selection))  # 打开摄像头
            if not self.cap_video.isOpened():  # 检查摄像头是否成功打开
                print("无法打开摄像头")
                return
            self.timer.start(25)  # 启动定时器，每25毫秒刷新一次
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
            self.image = None  # 清空图像
            self.camera_in_use = False  # 标记摄像头未使用

    def show_video(self):
        """定时器超时事件：从摄像头读取一帧并显示"""
        ret, img = self.cap_video.read()  # 读取一帧

        if ret:
            # 显示帧数
            self.frame_count += 1
            elapsed_time = time.time() - self.start_time
            if elapsed_time > 1:  # 每秒钟更新一次帧率
                self.fps = self.frame_count / elapsed_time
                self.frame_count = 0  # 重置帧计数器
                self.start_time = time.time()  # 重置开始时间
            cv.putText(img, f"FPS:{self.fps:.1f}", (10, 30), cv.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 0), 1)

            # 如果检测目标存在，调用模型检测
            if self.detecting_object:
                try:
                    img, boxes = self.model.detect(img, self.detecting_object)
                    self.current_boxes = boxes  # 保存检测框坐标
                except Exception as e:
                    print(f"检测失败: {e}")
                    img = cv.putText(img, "Detection Error", (50, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            # 显示图像
            self.show_cv_img(img)
            self.image = img
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

    def save_photo(self):
        """保存图片"""
        if self.image is None:
            print("没有可保存的图片")
            return
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%Hh%Mm%Ss")  # 时间戳
        cv.imwrite(timestamp + ".jpg", self.image)
        print("保存成功,文件名: ", timestamp + ".jpg")
        print(self.label_decide.text())

    def start_detection(self, object_name):
        """启动检测"""
        self.detecting_object = object_name
        print(f"开始检测: {object_name}")

    def stop_detection(self):
        """停止检测"""
        self.detecting_object = None
        self.current_boxes = []  # 清空检测框
        print("停止检测")

    def display_box(self):
        """显示检测框"""
        # if not self.current_boxes or self.image is None:
        #     self.label_capture.clear()
        #     return
        try:
            # ###### 获取检测框 #######
            # 处理第一个检测框
            box = self.current_boxes[0]
            # x1, y1, x2, y2 = map(int, box)
            x1, y1, x2, y2, label = box
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            expand = 20  # 外扩像素数

            # 获取图像尺寸
            h, w = self.image.shape[:2]

            # 计算外扩坐标（确保不越界）
            new_x1 = max(0, x1 - expand)
            new_y1 = max(0, y1 - expand)
            new_x2 = min(w, x2 + expand)
            new_y2 = min(h, y2 + expand)

            # 截取目标区域
            cropped = self.image[new_y1:new_y2, new_x1:new_x2]

            if cropped.size == 0:
                return

            # 转换并显示到label_capture
            frame = cv.cvtColor(self.image, cv.COLOR_BGR2RGB)
            qimage = QtGui.QImage(frame.tobytes(), frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)

            # 缩放适应label尺寸（保持比例）
            scaled_image = qimage.scaled(
                self.label_capture.width(),
                self.label_capture.height(),
                QtCore.Qt.KeepAspectRatio)
            self.label_capture.setPixmap(QtGui.QPixmap.fromImage(scaled_image))

            # 在label_decide上显示检测结果
            self.label_decide.setText(f"{label}")

        except Exception as e:
            if self.label_capture is None and self.image is not None:
                # 在label_decide上显示错误信息
                self.label_decide.setText(f"None")
                print(f"显示检测框失败: {e}")

    def return_label(self):
        """返回当前标签"""
        if self.label_decide is not None:
            label = self.label_decide.text()
            return label
        else:
            return None


if "__main__" == __name__:
    pass
