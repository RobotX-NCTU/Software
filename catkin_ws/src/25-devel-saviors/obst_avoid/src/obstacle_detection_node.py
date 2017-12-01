#!/usr/bin/env python
import rospy
from sensor_msgs.msg import CompressedImage
from geometry_msgs.msg import PoseArray
from visualization_msgs.msg import MarkerArray

### note you need to change the name of the robot to yours here
from obst_avoid.detector import Detector
from obst_avoid.visualizer import Visualizer
from duckietown_utils import get_base_name, rgb_from_ros, rectify, load_camera_intrinsics

class ObstDetectNode(object):
    """
    Obstacle Detection Node
    """
    def __init__(self):
        self.node_name = "Obstacle Detecion Node"
        robot_name = rospy.get_param("~robot_name", "")
        self.show_marker = (rospy.get_param("~show_marker", ""))
        self.show_image = (rospy.get_param("~show_image", ""))
        self.count = 1
        self.crop = 150


        self.detector = Detector(robot_name=robot_name,crop_rate=self.crop)
        self.visualizer = Visualizer(robot_name=robot_name,crop_rate=self.crop)

        # Load camera calibration parameters
	self.intrinsics = load_camera_intrinsics(robot_name)

        # Create a Publisher
        self.pub_topic_arr = '/{}/obst_detect/posearray'.format(robot_name)
        self.publisher_arr = rospy.Publisher(self.pub_topic_arr, PoseArray, queue_size=1)

        if (self.show_marker):
                self.pub_topic_marker = '/{}/obst_detect/visualize_obstacles'.format(robot_name)
                self.publisher_marker = rospy.Publisher(self.pub_topic_marker, MarkerArray, queue_size=1)
                print "YEAH I GIVE YOU THE MARKER"

        if (self.show_image):
                self.pub_topic_img = '/{}/obst_detect/image/compressed'.format(robot_name)
                self.publisher_img = rospy.Publisher(self.pub_topic_img, CompressedImage, queue_size=1)
                print "YEAH I GIVE YOU THE IMAGE"

        # Create a Subscriber
        self.sub_topic = '/{}/camera_node/image/compressed'.format(robot_name)
        self.subscriber = rospy.Subscriber(self.sub_topic, CompressedImage, self.callback)

    def callback(self, image):
        if (self.count==10): #only run with 30/self.count Hz WOULD BE POSSIBLE AS INPUT PARAM!!!!

            obst_list = PoseArray()
            marker_list = MarkerArray()
        
            # pass RECTIFIED IMAGE TO DETECTOR MODULE
            #1. EXTRACT OBSTACLES and return the pose array
            obst_list = self.detector.process_image(rectify(rgb_from_ros(image),self.intrinsics))
            self.publisher_arr.publish(obst_list)
            #EXPLANATION: (x,y) is world coordinates of obstacle, z is radius of obstacle
            #QUATERNION HAS NO MEANING!!!!    

            #3. VISUALIZE POSE ARRAY IN TF
            if (self.show_marker):
                    marker_list = self.visualizer.visualize_marker(obst_list)
                    self.publisher_marker.publish(marker_list)


            #4. EVENTUALLY DISPLAY IMAGE
            if (self.show_image):
                    obst_image = CompressedImage()
                    obst_image.header.stamp = image.header.stamp
                    obst_image.format = "jpeg"
                    obst_image.data = self.visualizer.visualize_image(rectify(rgb_from_ros(image),self.intrinsics),obst_list)
                    self.publisher_img.publish(obst_image.data)

            self.count=1
        else:
            self.count+=1
  

    def onShutdown(self):
        rospy.loginfo('Shutting down Obstacle Detection, back to unsafe mode')

# MEINER MEINUNG NACH HIER DANN WARSCH 2.NODE AUCH NOCH REIN WO DANN DIE OBST AVOIDANCE GEMACHT WIRD ODER SO

if __name__ == '__main__':
    rospy.init_node('obst_detection_node', anonymous=False)
    obst_detection_node = ObstDetectNode()
    rospy.on_shutdown(obst_detection_node.onShutdown)
    rospy.spin()