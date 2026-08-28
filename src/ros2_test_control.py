#!/usr/bin/env python3
"""
ROS2로 STARK 손 제어 테스트
"""
import rclpy
from rclpy.node import Node
from ros2_stark_msgs.msg import SetMotorMulti
import time


def main():
    rclpy.init()
    node = Node('test_controller')
    
    # Publisher 생성 (slave_id 127 = 0x7F)
    publisher = node.create_publisher(SetMotorMulti, '/set_motor_multi_127', 10)
    
    # 잠시 대기 (연결 안정화)
    time.sleep(1)
    
    print("1️⃣  손가락을 모두 펴는 중...")
    msg = SetMotorMulti()
    msg.slave_id = 127
    msg.mode = 5  # 위치 + 시간
    msg.positions = [0, 0, 0, 0, 0, 0]  # 모두 펴기
    msg.speeds = [0, 0, 0, 0, 0, 0]
    msg.currents = [0, 0, 0, 0, 0, 0]
    msg.pwms = [0, 0, 0, 0, 0, 0]
    msg.durations = [1000, 1000, 1000, 1000, 1000, 1000]  # 1초
    publisher.publish(msg)
    time.sleep(2)
    
    print("2️⃣  손가락을 반만 구부리는 중...")
    msg.positions = [500, 500, 500, 500, 500, 500]  # 중간 위치
    msg.durations = [1000, 1000, 1000, 1000, 1000, 1000]
    publisher.publish(msg)
    time.sleep(2)
    
    print("3️⃣  주먹 꽉 쥐는 중...")
    msg.positions = [1000, 1000, 1000, 1000, 1000, 1000]  # 완전히 쥐기
    msg.durations = [1000, 1000, 1000, 1000, 1000, 1000]
    publisher.publish(msg)
    time.sleep(2)
    
    print("4️⃣  다시 펴는 중...")
    msg.positions = [0, 0, 0, 0, 0, 0]  # 다시 펴기
    msg.durations = [1000, 1000, 1000, 1000, 1000, 1000]
    publisher.publish(msg)
    time.sleep(2)
    
    print("✅ 테스트 완료!")
    
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

