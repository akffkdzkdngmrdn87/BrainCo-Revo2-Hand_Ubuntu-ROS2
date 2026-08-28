#!/usr/bin/env python3
"""
카메라로 손 동작을 인식하고 STARK 로봇 손이 따라하는 프로그램
MediaPipe Hands + ROS2 통합

필요한 설치:
pip install opencv-python mediapipe
"""

import cv2
import mediapipe as mp
import numpy as np
import rclpy
from rclpy.node import Node
from ros2_stark_msgs.msg import SetMotorMulti
import time


class HandTrackingController(Node):
    def __init__(self):
        super().__init__('hand_tracking_controller')
        
        # ROS2 Publisher 생성
        self.publisher = self.create_publisher(SetMotorMulti, '/set_motor_multi_127', 10)
        
        # MediaPipe Hands 초기화
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        # 카메라 초기화
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.get_logger().info("손 추적 시작! 'q'를 눌러 종료하세요.")
        
    def calculate_finger_angles(self, landmarks):
        """
        손가락 landmark로부터 각도 계산 (0-1000 범위)
        손가락이 펴져있으면 0, 완전히 구부러지면 1000
        """
        angles = [0] * 6  # [엄지, 검지, 중지, 약지, 소지, 손목]
        
        # 손목 기준점
        wrist = np.array([landmarks[0].x, landmarks[0].y, landmarks[0].z])
        
        # 각 손가락별 landmark 인덱스
        finger_tips = [4, 8, 12, 16, 20]  # 엄지, 검지, 중지, 약지, 소지 끝
        finger_bases = [2, 5, 9, 13, 17]  # 각 손가락 시작점
        
        for i, (tip_idx, base_idx) in enumerate(zip(finger_tips, finger_bases)):
            tip = np.array([landmarks[tip_idx].x, landmarks[tip_idx].y, landmarks[tip_idx].z])
            base = np.array([landmarks[base_idx].x, landmarks[base_idx].y, landmarks[base_idx].z])
            
            # 손가락이 구부러진 정도 계산
            # 손가락 끝과 손목 사이 거리
            dist_tip_wrist = np.linalg.norm(tip - wrist)
            dist_base_wrist = np.linalg.norm(base - wrist)
            
            # 비율로 각도 추정 (0 = 펴짐, 1000 = 구부림)
            if dist_base_wrist > 0:
                ratio = dist_tip_wrist / dist_base_wrist
                # 엄지는 반대 방향
                if i == 0:  # 엄지
                    angle = max(0, min(1000, int((1.5 - ratio) * 1000)))
                else:
                    angle = max(0, min(1000, int((2.0 - ratio) * 500)))
            else:
                angle = 0
                
            angles[i] = angle
        
        # 손목은 0으로 고정
        angles[5] = 0
        
        return angles
    
    def smooth_angles(self, new_angles, prev_angles, alpha=0.3):
        """
        각도 스무딩 (급격한 변화 방지)
        """
        if prev_angles is None:
            return new_angles
        return [int(alpha * new + (1 - alpha) * prev) 
                for new, prev in zip(new_angles, prev_angles)]
    
    def send_robot_command(self, angles):
        """
        로봇 손에 명령 전송
        """
        msg = SetMotorMulti()
        msg.slave_id = 127  # 0x7F
        msg.mode = 5  # 위치 + 시간
        msg.positions = angles
        msg.speeds = [0] * 6
        msg.currents = [0] * 6
        msg.pwms = [0] * 6
        msg.durations = [100] * 6  # 빠른 반응을 위해 100ms
        
        self.publisher.publish(msg)
    
    def run(self):
        """
        메인 루프
        """
        prev_angles = None
        last_send_time = 0
        send_interval = 0.05  # 50ms마다 전송
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                self.get_logger().error("카메라 읽기 실패")
                break
            
            # 좌우 반전 (거울 모드)
            frame = cv2.flip(frame, 1)
            
            # BGR을 RGB로 변환
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 손 검출
            results = self.hands.process(rgb_frame)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # 손 그리기
                    self.mp_drawing.draw_landmarks(
                        frame, 
                        hand_landmarks, 
                        self.mp_hands.HAND_CONNECTIONS
                    )
                    
                    # 각도 계산
                    angles = self.calculate_finger_angles(hand_landmarks.landmark)
                    
                    # 스무딩
                    angles = self.smooth_angles(angles, prev_angles)
                    prev_angles = angles
                    
                    # 주기적으로 로봇에 전송
                    current_time = time.time()
                    if current_time - last_send_time > send_interval:
                        self.send_robot_command(angles)
                        last_send_time = current_time
                    
                    # 화면에 각도 표시
                    finger_names = ["엄지", "검지", "중지", "약지", "소지", "손목"]
                    for i, (name, angle) in enumerate(zip(finger_names, angles)):
                        cv2.putText(frame, f"{name}: {angle}", 
                                  (10, 30 + i * 30), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 
                                  0.6, (0, 255, 0), 2)
            
            else:
                cv2.putText(frame, "손을 카메라에 보여주세요", 
                          (10, 30), 
                          cv2.FONT_HERSHEY_SIMPLEX, 
                          0.7, (0, 0, 255), 2)
            
            # 화면에 표시
            cv2.imshow('Hand Tracking - STARK Control', frame)
            
            # 'q' 키로 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # 정리
        self.cap.release()
        cv2.destroyAllWindows()
        self.hands.close()


def main():
    rclpy.init()
    controller = HandTrackingController()
    
    try:
        controller.run()
    except KeyboardInterrupt:
        pass
    finally:
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

