import rclpy
import math
import numpy as np
from rclpy.node import Node
import json
import os
import datetime
import time
from std_msgs.msg import String
from sensor_msgs.msg import Image
import cv2

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
        img_d = np.array(image_msg.data, dtype=np.uint8)
        img_d = img_d.reshape((image_msg.height, image_msg.width, 3))
        current_datetime = datetime.datetime.now()
        current_time_milliseconds = int(current_datetime.timestamp() * 1000)
        # file_path = f"/home/serene/images/{current_time_milliseconds}.png"
        # cv2.imwrite(file_path, img_d)
        self.get_logger().info(f"{len(image_msg.data)}")

    

def main(args=None):
    rclpy.init(args=args)
    minimal_subscriber = MinimalSubscriber()
    rclpy.spin(minimal_subscriber)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
