import rclpy
import math
from rclpy.node import Node
import numpy as np
from std_msgs.msg import String
from sensor_msgs.msg import Imu, NavSatFix, CameraInfo, PointCloud2, Image
import datetime
import os
import cv2 as cv
import numpy as np
import math
import os
import time

Conf_threshold = 0.4
NMS_threshold = 0.4
COLORS = [(0, 255, 0), (0, 0, 255), (255, 0, 0),
        (255, 255, 0), (255, 0, 255), (0, 255, 255)]


def _dir(name):
    return os.path.join(os.path.join('ai', 'resource'), name)


net = cv.dnn.readNet(_dir('road_damage_last.weights'), _dir('road_damage.cfg'))
model = cv.dnn_DetectionModel(net)
model.setInputParams(size=(416, 416), scale=1/255, swapRB=True)

net.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA_FP16)

def use_model(frame):

    class_name = []
    with open(_dir('road_damage.names'), 'r') as f:
        class_name = [cname.strip() for cname in f.readlines()]
    

    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]   

    output_layers = net.getUnconnectedOutLayersNames()
    Conf_threshold = 0.5
    NMS_threshold = 0.4

    class_name = []
    with open(_dir("road_damage.names"), "r") as f:
        class_name = [cname.strip() for cname in f.readlines()]


    classes, scores, boxes = model.detect(frame, Conf_threshold, NMS_threshold)
    for (classid, score, box) in zip(classes, scores, boxes):
        color = COLORS[int(classid) % len(COLORS)]
        label = "%s : %f" % (class_name[classid], score)
    
        cv.rectangle(frame, box, color, 1)
        cv.putText(frame, label, (box[0], box[1]-10),
                cv.FONT_HERSHEY_COMPLEX, 0.5, color, 1)

    current_datetime = datetime.datetime.now()
    current_time_milliseconds = int(current_datetime.timestamp() * 1000)
    file_path = f"/home/serene/{'ai_dev_img'}/{current_time_milliseconds}.png"
    cv.imwrite(file_path, frame)



class MinimalSubscriber(Node):


    def __init__(self):
        super().__init__('minimal_subscriber')

        self.subscription = self.create_subscription(
            Image,
            '/OAK_D_back/color/image',
            self.listener_callback,
            1)
        
        self.subscription  # prevent unused variable warning

      

    def listener_callback(self, image_msg):



        try:
            img_d = np.array(image_msg.data, dtype=np.uint8)
            img_d = img_d.reshape((image_msg.height, image_msg.width, 3))
            img_cv = cv.cvtColor(img_d, cv.COLOR_RGB2BGR)
            use_model(img_cv)
        except:
            self.get_logger().info(f"ошибка обработки")




def main(args=None):
    rclpy.init(args=args)
    minimal_subscriber = MinimalSubscriber()
    rclpy.spin(minimal_subscriber)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
