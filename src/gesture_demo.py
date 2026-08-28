#!/usr/bin/env python3
"""
미리 정의된 제스처 데모 - 자동으로 여러 제스처 실행

각 제스처를 순서대로 보여줍니다.
"""

import rclpy
from rclpy.node import Node
from ros2_stark_msgs.msg import SetMotorMulti
import time


class GestureDemo(Node):
    def __init__(self):
        super().__init__('gesture_demo')
        self.publisher = self.create_publisher(SetMotorMulti, '/set_motor_multi_127', 10)
        time.sleep(0.5)
        
    def send_positions(self, positions, duration=1000, name=""):
        """로봇에 위치 명령 전송"""
        if name:
            print(f"\n{name}")
        
        msg = SetMotorMulti()
        msg.slave_id = 127
        msg.mode = 5
        msg.positions = positions
        msg.speeds = [0] * 6
        msg.currents = [0] * 6
        msg.pwms = [0] * 6
        msg.durations = [duration] * 6
        
        self.publisher.publish(msg)
        time.sleep(duration / 1000.0 + 0.5)
    
    def run_demo(self):
        """제스처 데모 실행"""
        print("\n" + "="*60)
        print("🎭 STARK 로봇 손 제스처 데모")
        print("="*60)
        
        gestures = [
            ([0, 0, 0, 0, 0, 0], "✋ 1. 손 펴기 (인사)"),
            ([1000, 1000, 1000, 1000, 1000, 0], "✊ 2. 주먹 쥐기"),
            ([0, 0, 0, 0, 0, 0], "✋ 3. 다시 펴기"),
            ([1000, 0, 0, 1000, 1000, 0], "✌️  4. 가위"),
            ([1000, 1000, 1000, 1000, 1000, 0], "✊ 5. 바위"),
            ([0, 0, 0, 0, 0, 0], "✋ 6. 보"),
            ([1000, 1000, 0, 0, 0, 0], "👌 7. OK 사인"),
            ([0, 1000, 1000, 1000, 1000, 0], "👍 8. 엄지 척 (Good!)"),
            ([0, 0, 1000, 1000, 0, 0], "🤟 9. Love (사랑해요)"),
            ([500, 500, 1000, 1000, 1000, 0], "💗 10. 하트"),
            ([0, 0, 1000, 1000, 1000, 0], "🔫 11. 총 모양"),
            ([1000, 0, 0, 1000, 1000, 0], "✌️  12. Victory!"),
            ([0, 0, 0, 0, 0, 0], "✋ 13. 마무리 (손 펴기)"),
        ]
        
        for positions, name in gestures:
            self.send_positions(positions, 1500, name)
        
        print("\n" + "="*60)
        print("✅ 데모 완료!")
        print("="*60 + "\n")


def main():
    rclpy.init()
    demo = GestureDemo()
    
    try:
        print("\n🔄 무한 반복 모드 - Ctrl+C로 종료\n")
        while True:
            demo.run_demo()
            time.sleep(2)  # 각 사이클 사이 2초 대기
    except KeyboardInterrupt:
        print("\n\n👋 데모를 종료합니다...")
    finally:
        demo.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

