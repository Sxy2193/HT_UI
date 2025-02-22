from ultralytics import YOLO


class Model:
    def __init__(self):
        self.model = None  # 模型对象
        self.weight_file = None  # 权重文件路径

    def load_weights(self, weight_file):
        """加载权重文件"""
        try:
            self.model = YOLO(weight_file)  # 加载 YOLOv8 模型
            self.weight_file = weight_file
            print(f"权重文件加载成功: {self.weight_file}")
            return True
        except Exception as e:
            print(f"加载权重文件失败: {e}")
            return False

    def detect(self, img):
        """对图像进行目标检测"""
        if self.model is None:
            print("未加载权重文件，无法进行检测！")
            return img  # 返回原始图像

        try:
            results = self.model(img)  # 进行目标检测
            annotated_frame = results[0].plot()  # 获取带有检测框的帧
            return annotated_frame
        except Exception as e:
            print(f"目标检测失败: {e}")
            return img  # 返回原始图像
