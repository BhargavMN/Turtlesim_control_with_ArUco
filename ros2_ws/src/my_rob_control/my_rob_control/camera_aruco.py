#!/usr/bin/env python3 

import rclpy
from rclpy.node import Node
import numpy as np
import cv2
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist

from std_msgs.msg import String

class ArucoGenerator:
	def __init__(self, type):
		self.type = type
		id = 1
		arucoDict = cv2.aruco.Dictionary_get(ARUCO_DICT[self.type])
		# print("ArUCo type '{}' with ID '{}'".format(type, id))
		tag_size = 250
		self.marker = np.zeros((tag_size, tag_size, 1), dtype="uint8")
		cv2.aruco.drawMarker(arucoDict, id, tag_size, self.marker, 1)
		marker_name = "Marker_" + self.type + "_" + str(id) + ".png"
		cv2.imwrite(marker_name, self.marker)
  
	def showImage(self):
		cv2.imshow("Marker_", self.marker)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
	
	def getImage(self):
		return self.marker

def aruco_display(corners, ids, rejected, image):
	if len(corners) > 0:
		
		ids = ids.flatten()
		
		for (markerCorner, markerID) in zip(corners, ids):
			
			corners = markerCorner.reshape((4, 2))
			(topLeft, topRight, bottomRight, bottomLeft) = corners
			
			topRight = (int(topRight[0]), int(topRight[1]))
			bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
			bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
			topLeft = (int(topLeft[0]), int(topLeft[1]))

			cv2.line(image, topLeft, topRight, (0, 255, 0), 2)
			cv2.line(image, topRight, bottomRight, (0, 255, 0), 2)
			cv2.line(image, bottomRight, bottomLeft, (0, 255, 0), 2)
			cv2.line(image, bottomLeft, topLeft, (0, 255, 0), 2)
			
			cX = int((topLeft[0] + bottomRight[0]) / 2.0)
			cY = int((topLeft[1] + bottomRight[1]) / 2.0)
			cv2.circle(image, (cX, cY), 4, (0, 0, 255), -1)
			
			cv2.putText(image, str(markerID),(topLeft[0], topLeft[1] - 10), cv2.FONT_HERSHEY_SIMPLEX,
				0.5, (0, 255, 0), 2)
			# print("[Inference] ArUco marker ID: {}".format(markerID))
			return image, cX, cY		
	return image, -1, -1	

ARUCO_DICT = {
	"DICT_4X4_50": cv2.aruco.DICT_4X4_50,
	"DICT_4X4_100": cv2.aruco.DICT_4X4_100,
	"DICT_4X4_250": cv2.aruco.DICT_4X4_250,
	"DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
	"DICT_5X5_50": cv2.aruco.DICT_5X5_50,
	"DICT_5X5_100": cv2.aruco.DICT_5X5_100,
	"DICT_5X5_250": cv2.aruco.DICT_5X5_250,
	"DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
	"DICT_6X6_50": cv2.aruco.DICT_6X6_50,
	"DICT_6X6_100": cv2.aruco.DICT_6X6_100,
	"DICT_6X6_250": cv2.aruco.DICT_6X6_250,
	"DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
	"DICT_7X7_50": cv2.aruco.DICT_7X7_50,
	"DICT_7X7_100": cv2.aruco.DICT_7X7_100,
	"DICT_7X7_250": cv2.aruco.DICT_7X7_250,
	"DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
	"DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
	"DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
	"DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
	"DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
	"DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11
}

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('camera_aruco')
        self.cmd_vel_pub_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_sub=self.create_subscription(
            Pose,"/turtle1/pose",self.pose_cb,10) 
    
    
    def pose_cb(self,pose:Pose):
         cmd=Twist()
         ret, frame = vid.read()
         resized = cv2.resize(frame, (CAM_W, CAM_H)) 

         corners, ids, rejected = cv2.aruco.detectMarkers(resized, arucoDict, parameters=arucoParams)
         detected_markers, posX, posY = aruco_display(corners, ids, rejected, resized)

         cv2.imshow("Marker position", detected_markers)

         if posY != -1:
          diff = posY - CENTER
          print(diff)
          if diff >= 0:
            cmd.linear.x=-5.0
            print("DOWN")
          else:
            print("UP")
            cmd.linear.x=5.0

         if cv2.waitKey(1) & 0xFF == ord('q'):
            return None
         self.cmd_vel_pub_.publish(cmd)

        
    
GENERATE_MARKER = False
type = "DICT_5X5_100"
posX = 0
posY = 0
CAM_W = 800
CAM_H = 600
CENTER = CAM_H/2

if GENERATE_MARKER:
     aruco_generator = ArucoGenerator(type)
     aruco_generator.showImage()
     aruco_marker = aruco_generator.getImage()


arucoDict = cv2.aruco.Dictionary_get(ARUCO_DICT[type])
arucoParams = cv2.aruco.DetectorParameters_create()
vid = cv2.VideoCapture(0)	

def main(args=None):
    rclpy.init(args=args)
    minimal_publisher = MinimalPublisher()
    rclpy.spin(minimal_publisher)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
