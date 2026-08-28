#!/usr/bin/env python3
"""
키보드로 STARK 로봇 손 제어하기

키 설명:
- 숫자 0-9: 손가락 펴기/쥐기 (0=완전히 펴기, 9=완전히 쥐기)
- r: 가위바위보 - 바위 (주먹)
- s: 가위바위보 - 가위
- p: 가위바위보 - 보 (손 펴기)
- o: OK 사인
- t: 엄지 척
- v: Victory (브이)
- h: 하트
- Space: 모든 손가락 펴기
- q: 종료
"""

import rclpy
from rclpy.node import Node
from ros2_stark_msgs.msg import SetMotorMulti
import sys
import termios
import tty
import time


class KeyboardController(Node):
    def __init__(self):
        super().__init__('keyboard_controller')
        self.publisher = self.create_publisher(SetMotorMulti, '/set_motor_multi_127', 10)
        time.sleep(0.5)
        
        self.get_logger().info("🎮 키보드 제어 모드 시작!")
        self.print_help()
        
    def print_help(self):
        """도움말 출력"""
        print("\n" + "="*60)
        print("🤖 STARK 로봇 손 키보드 제어")
        print("="*60)
        print("\n📋 제어 방법:")
        print("  숫자 0-9  : 손가락 펴기/쥐기 (0=완전히 펴기, 9=완전히 쥐기)")
        print("\n👆 개별 손가락 테스트:")
        print("  1-5 + Shift : 개별 손가락만 구부리기")
        print("    ! : 엄지 (각도1) - 인덱스 0")
        print("    @ : 엄지 (각도2) - 인덱스 1")
        print("    # : 검지 - 인덱스 2")
        print("    $ : 중지 - 인덱스 3")
        print("    % : 약지 - 인덱스 4")
        print("    ^ : 소지 - 인덱스 5")
        print("\n✋ 제스처:")
        print("  r : 바위 (주먹)")
        print("  s : 가위")
        print("  p : 보 (손 펴기)")
        print("  o : OK 사인 👌")
        print("  t : 엄지 척 👍")
        print("  v : Victory 브이 ✌️")
        print("  h : 하트 💗")
        print("  l : Love 손가락 하트 🤟")
        print("  g : 총 모양 🔫")
        print("\n⚙️  기타:")
        print("  Space : 모든 손가락 펴기")
        print("  ?     : 도움말")
        print("  q     : 종료")
        print("="*60 + "\n")
    
    def send_positions(self, positions, duration=500):
        """로봇에 위치 명령 전송"""
        msg = SetMotorMulti()
        msg.slave_id = 127
        msg.mode = 5  # 위치 + 시간
        msg.positions = positions
        msg.speeds = [0] * 6
        msg.currents = [0] * 6
        msg.pwms = [0] * 6
        msg.durations = [duration] * 6
        
        self.publisher.publish(msg)
        self.get_logger().info(f"위치 전송: {positions}")
    
    def gesture_rock(self):
        """바위 (주먹)"""
        print("✊ 바위!")
        # [엄지1, 엄지2, 검지, 중지, 약지, 소지] - 모두 구부리기
        self.send_positions([1000, 1000, 1000, 1000, 1000, 1000])
    
    def gesture_scissors(self):
        """가위"""
        print("✌️  가위!")
        # 엄지1, 엄지2 구부리고, 검지와 중지만 펴고, 약지와 소지 구부리기
        self.send_positions([1000, 1000, 0, 0, 1000, 1000])
    
    def gesture_paper(self):
        """보 (손 펴기)"""
        print("✋ 보!")
        # 모든 손가락 펴기
        self.send_positions([0, 0, 0, 0, 0, 0])
    
    def gesture_ok(self):
        """OK 사인"""
        print("👌 OK!")
        # 엄지1, 엄지2, 검지만 구부려서 원 만들기
        self.send_positions([1000, 1000, 1000, 0, 0, 0])
    
    def gesture_thumbs_up(self):
        """엄지 척"""
        print("👍 Good!")
        # 엄지1, 엄지2만 펴고 나머지 구부리기
        self.send_positions([0, 0, 1000, 1000, 1000, 1000])
    
    def gesture_victory(self):
        """Victory 브이"""
        print("✌️  Victory!")
        # 엄지1, 엄지2 구부리고, 검지와 중지만 펴고, 약지와 소지 구부리기
        self.send_positions([1000, 1000, 0, 0, 1000, 1000])
    
    def gesture_heart(self):
        """하트"""
        print("💗 Heart!")
        # 엄지1, 엄지2만 반쯤 구부려서 하트 모양
        self.send_positions([500, 500, 1000, 1000, 1000, 1000])
    
    def gesture_love(self):
        """Love (엄지+검지+소지)"""
        print("🤟 Love!")
        # 엄지1, 엄지2, 검지, 소지만 펴기
        self.send_positions([0, 0, 0, 1000, 1000, 0])
    
    def gesture_gun(self):
        """총 모양"""
        print("🔫 Bang!")
        # 검지만 펴고 나머지 구부리기
        self.send_positions([1000, 1000, 0, 1000, 1000, 1000])
    
    def open_hand(self):
        """손 펴기"""
        print("✋ 손 펴기")
        self.send_positions([0, 0, 0, 0, 0, 0])
    
    def set_grip_level(self, level):
        """손가락 쥐는 정도 설정 (0-9)"""
        position = int(level * 111)  # 0-999
        print(f"🤜 쥐기 레벨: {level}/9 (위치: {position})")
        self.send_positions([position, position, position, position, position, position])
    
    def test_single_finger(self, finger_index, position_value=1000):
        """개별 손가락 테스트
        인덱스 매핑: 0=엄지1, 1=엄지2, 2=검지, 3=중지, 4=약지, 5=소지
        """
        finger_names = ["엄지(각도1)", "엄지(각도2)", "검지", "중지", "약지", "소지"]
        if 0 <= finger_index < 6:
            print(f"👉 {finger_names[finger_index]}만 구부리기 (위치: {position_value})")
            positions = [0] * 6
            positions[finger_index] = position_value
            self.send_positions(positions, 1000)
    
    def get_key(self):
        """키 입력 받기"""
        try:
            # TTY 체크
            if not sys.stdin.isatty():
                return None
            
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch
        except (termios.error, OSError, AttributeError) as e:
            # TTY 오류 시 None 반환
            self.get_logger().warn(f"키 입력 오류: {e}")
            return None
    
    def run(self):
        """메인 루프"""
        print("\n⌨️  키를 눌러 로봇 손을 제어하세요...\n")
        
        try:
            while True:
                key = self.get_key()
                
                if key is None:
                    time.sleep(0.05)
                    continue
                
                if key == 'q' or key == '\x03':  # 'q' 또는 Ctrl+C
                    print("\n👋 종료합니다...")
                    break
                elif key == ' ':
                    self.open_hand()
                elif key.isdigit():
                    self.set_grip_level(int(key))
                elif key == 'r':
                    self.gesture_rock()
                elif key == 's':
                    self.gesture_scissors()
                elif key == 'p':
                    self.gesture_paper()
                elif key == 'o':
                    self.gesture_ok()
                elif key == 't':
                    self.gesture_thumbs_up()
                elif key == 'v':
                    self.gesture_victory()
                elif key == 'h':
                    self.gesture_heart()
                elif key == 'l':
                    self.gesture_love()
                elif key == 'g':
                    self.gesture_gun()
                elif key == '!':  # Shift+1 : 엄지 (각도1)
                    self.test_single_finger(0, 1000)  # 인덱스 0: 엄지 각도1
                elif key == '@':  # Shift+2 : 엄지 (각도2)
                    self.test_single_finger(1, 1000)  # 인덱스 1: 엄지 각도2
                elif key == '#':  # Shift+3 : 검지
                    self.test_single_finger(2, 1000)  # 인덱스 2: 검지
                elif key == '$':  # Shift+4 : 중지
                    self.test_single_finger(3, 1000)  # 인덱스 3: 중지
                elif key == '%':  # Shift+5 : 약지
                    self.test_single_finger(4, 1000)  # 인덱스 4: 약지
                elif key == '^':  # Shift+6 : 소지
                    self.test_single_finger(5, 1000)  # 인덱스 5: 소지
                elif key == '?':
                    self.print_help()
                
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\n\n키보드 인터럽트")


def main():
    rclpy.init()
    controller = KeyboardController()
    
    try:
        controller.run()
    finally:
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

