#!/usr/bin/env python
import rospy
import geometry_msgs.msg
import std_msgs.msg
import math

MAX_PWM = 1900				#of each thruster
ZERO_PWM = 1500
MIN_PWM = 1100
MAX_LINEAR_ACCEL = 4				#linear accel of the boat
NO_THRUSTER = 2				#no of thrusters in the boat
MAX_TIME = 2				#in s
MAX_ACCEL = MAX_LINEAR_ACCEL/NO_THRUSTER	#linear accel per thruster
THRUSTER_COB = 0.3			#cob to each thruster
MAX_ANG_ACCEL = MAX_ACCEL/THRUSTER_COB
RATE_CHANGE_ACCEL_PWM = MAX_ANG_ACCEL/(MAX_PWM-ZERO_PWM)
RATE_CHANGE_ACCEL = RATE_CHANGE_ACCEL_PWM/MAX_TIME
RATE_PUB = 100				#100hz
rpm_l = 1500
rpm_r = 1500
cmd_vel = geometry_msgs.msg.Twist()
cur_vel = geometry_msgs.msg.Twist()
accel = [0,0]

def listener():
	global cmd_vel, rpm_l, rpm_r
	rospy.init_node("thruster_controller")
	rospy.Subscriber("/cmd_vel", geometry_msgs.msg.Twist, feedback, callback_args=True)
	rospy.Subscriber("/asv/velocity", geometry_msgs.msg.Twist, feedback, callback_args=False)
	pub_l = rospy.Publisher("/asv/left_thruster/command", std_msgs.msg.Float64, queue_size=10)
	pub_r = rospy.Publisher("/asv/right_thruster/command", std_msgs.msg.Float64, queue_size=10)
	rate = rospy.Rate(RATE_PUB)
	while not rospy.is_shutdown():
		accel[0] = cmd_vel.linear.x-cur_vel.linear.x
		accel[1] = cmd_vel.angular.z-cur_vel.angular.z
		ang_accels = ang_accel(accel_goal()[0], accel_goal[1])
		rospy.loginfo(ang_accels)
		rpm_l = predict_pwm(ang_accels, rpm_l, accels)
		pub_l.publish(rpm_l)
		pub_r.publish(rpm_r)
		rate.sleep()

def feedback(data, args):
	global cmd_vel, cur_vel
	cmd = args
	if(cmd):
		cmd_vel = data
	else:
		cur_vel = data

def accel_goal():
	global cur_vel, cmd_vel
	linear = cmd_vel.linear.x-cur_vel.linear.x
	angular = cmd_vel.angular.z-cur_vel.angular.z
	return(linear,angular)

def predict_pwm(given_accel, cur_pwm, cur_accel):
	max_change = 2
	predict = (given_accel-cur_accel)/0.0167+cur_pwm
	if(predict-cur_pwm>max_change):
		return cur_pwm+max_change
	return predict

def ang_accel(linear_accel, angular_accel):
	global THRUSTER_COB
	return (0.5*(float(linear_accel)/THRUSTER_COB+angular_accel),0.5*(angular_accel-float(linear_accel)/THRUSTER_COB))

listener()