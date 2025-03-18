from ultralytics import YOLO


class Model:
    def __init__(self):
        self.model = None  # 模型对象
        self.weight_file = None  # 权重文件路径
        self.models = {}  # 存储{对象名称: 模型实例}
        self.loaded_models = {}  # 存储{对象名称: 权重路径}

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
            return img

        try:
            # print(f"正在检测: {object_name}")  # 调试信息
            results = self.models[object_name](img)
            return results[0].plot()  # 返回绘制检测结果的图像
        except Exception as e:
            print(f"[{object_name}] 检测失败: {e}")
            return img

    def release_model(self, object_name):
        """释放指定模型"""
        if object_name in self.models:
            del self.models[object_name]
            del self.loaded_models[object_name]
            print(f"[{object_name}] 模型已释放")
