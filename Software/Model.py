from ultralytics import YOLO
import cv2


class Model:
    def __init__(self):
        self.model = None                   # 模型对象
        self.weight_file = None             # 权重文件路径
        self.models = {}                    # 存储{对象名称: 模型实例}
        self.loaded_models = {}             # 存储{对象名称: 权重路径}
        self.labeled_boxes = []             # 存储检测框坐标和标签

    def load_weights(self, object_name, weight_file):
        """加载/更新指定对象的权重"""
        try:
            # 释放已有模型
            if object_name in self.models:
                del self.models[object_name]

            # 加载新模型
            self.models[object_name] = YOLO(weight_file)
            self.loaded_models[object_name] = weight_file
            print(f"[{object_name}] 权重加载成功")
            return True
        except Exception as e:
            print(f"[{object_name}] 加载失败: {e}")
            return False

    def detect(self, img, object_name):
        """执行目标检测"""
        if object_name not in self.models:
            print(f"[{object_name}] 模型未加载")
            return img, []

        try:
            # print(f"正在检测: {object_name}")
            results = self.models[object_name](img)                 # 执行检测
            plotted_img = results[0].plot()
            boxes = results[0].boxes.xyxy.cpu().numpy().tolist()    # 获取检测框坐标
            class_ids = results[0].boxes.cls.cpu().numpy().tolist()  # 类别ID列表 [int, ...]
            class_names = results[0].names  # 获取类别名称映射字典

            # 构建带标签的检测框
            labeled_boxes = []
            for box, cls_id in zip(boxes, class_ids):
                # 确保类别ID是整数，并获取名称
                label = class_names[int(cls_id)]  # 例如 'bus'
                # 合并坐标和标签
                labeled_box = [float(coord) for coord in box] + [label]
                labeled_boxes.append(labeled_box)
            self.labeled_boxes = labeled_boxes
            return plotted_img, labeled_boxes                       # 返回绘制后的图像和检测框

        except Exception as e:
            print(f"[{object_name}] 检测失败: {e}")
            return img, []

    def release_model(self, object_name):
        """释放指定模型"""
        if object_name in self.models:
            del self.models[object_name]
            del self.loaded_models[object_name]
            print(f"[{object_name}] 模型已释放")


if "__main__" == __name__:
    model = Model()
    model.load_weights("person", "yolov8n.pt")
    result, box = model.detect("111.jpg", "person")
    model.release_model("person")
    print(f"{box}")
