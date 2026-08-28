#!/usr/bin/env python3
"""
손가락 배열 인덱스 테스트 - 실제 어느 손가락이 움직이는지 확인
"""
import asyncio
import sys
import os
# 공식 SDK 예제 폴더(STARK_SDK_DIR 미설정 시 참조 설치 경로 사용)
_SDK_DIR = os.path.expanduser(
    os.environ.get("STARK_SDK_DIR", "~/1/brainco/src/stark-serialport-example")
)
sys.path.append(os.path.join(_SDK_DIR, "python", "revo2"))

from revo2_utils import *

async def test_individual_fingers():
    """각 손가락을 하나씩 움직여서 인덱스 확인"""
    (client, slave_id) = await open_modbus_revo2(port_name=None)
    
    print("\n각 손가락을 순서대로 테스트합니다...")
    print("(3초마다 다음 손가락으로 이동)\n")
    
    # 먼저 모두 펴기
    await client.set_finger_positions_and_speeds(slave_id, [0]*6, [500]*6)
    await asyncio.sleep(2)
    
    finger_names = ["0번 (Base)", "1번 (Thumb 엄지?)", "2번", "3번", "4번", "5번"]
    
    for i in range(6):
        print(f">>> {finger_names[i]} 손가락 구부리는 중...")
        positions = [0] * 6
        positions[i] = 1000  # i번 손가락만 구부림
        await client.set_finger_positions_and_speeds(slave_id, positions, [500]*6)
        await asyncio.sleep(3)
        
        # 다시 펴기
        await client.set_finger_positions_and_speeds(slave_id, [0]*6, [500]*6)
        await asyncio.sleep(1)
    
    print("\n테스트 완료!")
    libstark.modbus_close(client)

if __name__ == "__main__":
    asyncio.run(test_individual_fingers())

