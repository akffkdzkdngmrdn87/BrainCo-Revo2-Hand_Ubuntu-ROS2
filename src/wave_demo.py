#!/usr/bin/env python3
"""
손 흔들기 애니메이션 데모
"""

import rclpy
from rclpy.node import Node
from ros2_stark_msgs.msg import SetMotorMulti
import time


class WaveDemo(Node):
    def __init__(self):
        super().__init__('wave_demo')
        self.publisher = self.create_publisher(SetMotorMulti, '/set_motor_multi_127', 10)
        time.sleep(0.5)
        
    def send_positions(self, positions, duration=300):
        """로봇에 위치 명령 전송"""
        msg = SetMotorMulti()
        msg.slave_id = 127
        msg.mode = 5
        msg.positions = positions
        msg.speeds = [0] * 6
        msg.currents = [0] * 6
        msg.pwms = [0] * 6
        msg.durations = [duration] * 6
        
        self.publisher.publish(msg)
        time.sleep(duration / 1000.0)
    
    def wave(self):
        """손 흔들기"""
        print("\n👋 손 흔들기 시작!")
        
        # 손 펴기
        self.send_positions([0, 0, 0, 0, 0, 0], 500)
        time.sleep(0.5)
        
        # 손가락을 순서대로 구부렸다 펴기 (웨이브)
        for _ in range(3):
            for i in range(5):
                positions = [0] * 6
                positions[i] = 800
                self.send_positions(positions, 200)
            
            # 다시 펴기
            self.send_positions([0, 0, 0, 0, 0, 0], 300)
        
        print("✅ 완료!\n")


def main():
    rclpy.init()
    demo = WaveDemo()
    
    try:
        demo.wave()
    finally:
        demo.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

