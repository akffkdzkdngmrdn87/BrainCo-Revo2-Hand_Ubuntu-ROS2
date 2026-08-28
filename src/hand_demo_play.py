#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BrainCo Revo2 Basic 로봇손 - 전체 동작 데모 플레이
================================================================================

이 파일 하나로 로봇손의 '모든 동작'을 순서대로 자동 시연합니다.
  1) 프리셋 제스처 전체        (보/주먹/브이/OK/엄지척/총/러브/하트/숫자3)
  2) 손가락 웨이브             (엄지→소지 차례로 물결처럼)
  3) 손가락 3단계 순환 데모     (폄→반쯤→쥠)
  4) 손가락 미세조정 데모       (100씩 쥐기 → 펴기)
  5) 손가락으로 숫자 세기       (1→2→3→4→5)
  6) 전체 쥐기 레벨 데모        (0→25%→50%→75%→100%)
  7) 피날레                    (주먹 → 인사)

■ 실행법
      python3 src/hand_demo_play.py           (1회 재생)
      python3 src/hand_demo_play.py --loop    (무한 반복, Ctrl+C 종료)
"""

import asyncio
import os
import sys

# ─────────────────────────────────────────────────────────────────────────────
# import 경로 준비
#   ① 이 파일이 놓인 폴더  → hand_keyboard.py(HandController) 재사용을 위해
#   ② 공식 SDK 예제 폴더    → revo2_utils.py 를 위해 (STARK_SDK_DIR 로 덮어쓰기 가능)
# ─────────────────────────────────────────────────────────────────────────────
_SELF_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_SDK_DIR = "~/1/brainco/src/stark-serialport-example"
_SDK_DIR = os.path.expanduser(os.environ.get("STARK_SDK_DIR", _DEFAULT_SDK_DIR))
_REVO2_DIR = os.path.join(_SDK_DIR, "python", "revo2")

if not os.path.isdir(_REVO2_DIR):
    sys.exit(
        f"[오류] 공식 SDK 예제 폴더를 찾을 수 없습니다: {_REVO2_DIR}\n"
        f"       예) export STARK_SDK_DIR=~/1/brainco/src/stark-serialport-example"
    )

for _p in (_SELF_DIR, _REVO2_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from bc_stark_sdk import main_mod as libstark
from revo2_utils import open_modbus_revo2
from hand_keyboard import HandController, GESTURES


def banner(text):
    """구간 제목을 보기 좋게 출력."""
    print("\n" + "─" * 60)
    print(f"  {text}")
    print("─" * 60)


async def section_gestures(hand):
    """1) 프리셋 제스처 전체 순회."""
    banner("1) 프리셋 제스처")
    order = ['p', 'f', 'v', 'o', 'u', 'g', 'l', 'c', 'n', 'p']
    for k in order:
        name, positions = GESTURES[k]
        await hand.set_all(positions, duration_ms=700, name=name)
        await asyncio.sleep(1.3)


async def section_wave(hand):
    """2) 손가락 웨이브 - 엄지부터 소지까지 차례로 굽혔다 폄."""
    banner("2) 손가락 웨이브 🌊")
    await hand.set_all([0] * 6, name="손 펴기")
    await asyncio.sleep(0.8)
    # 차례로 굽히기
    for i in range(6):
        pos = list(hand.pos)
        pos[i] = 1000
        await hand.set_all(pos, duration_ms=250)
        await asyncio.sleep(0.35)
    # 차례로 펴기
    for i in range(6):
        pos = list(hand.pos)
        pos[i] = 0
        await hand.set_all(pos, duration_ms=250)
        await asyncio.sleep(0.35)


async def section_cycle(hand):
    """3) 손가락 3단계 순환 데모(검지로 시연)."""
    banner("3) 손가락 3단계 순환 (검지: 폄→반쯤→쥠→폄)")
    await hand.set_all([0] * 6, name="손 펴기")
    await asyncio.sleep(0.6)
    for _ in range(3):
        await hand.cycle_finger(2)          # 검지(index 2) 정방향
        await asyncio.sleep(0.9)


async def section_finetune(hand):
    """4) 손가락 미세조정 데모(중지로 시연)."""
    banner("4) 손가락 미세조정 (중지: 100씩 쥐기 → 펴기)")
    await hand.set_all([0] * 6, name="손 펴기")
    await asyncio.sleep(0.6)
    for _ in range(10):                      # 0 → 1000 까지 쥐기
        await hand.nudge_finger(3, +100)     # 중지(index 3)
        await asyncio.sleep(0.25)
    for _ in range(10):                      # 다시 펴기
        await hand.nudge_finger(3, -100)
        await asyncio.sleep(0.25)


async def section_counting(hand):
    """5) 손가락으로 숫자 1~5 세기."""
    banner("5) 손가락으로 숫자 세기 (1→2→3→4→5)")
    # [엄지, 엄지보조, 검지, 중지, 약지, 소지]  (0=폄, 1000=쥠)
    numbers = {
        1: [1000, 1000, 0, 1000, 1000, 1000],   # 검지
        2: [1000, 1000, 0, 0, 1000, 1000],       # 검지+중지
        3: [1000, 1000, 0, 0, 0, 1000],          # 검지+중지+약지
        4: [1000, 1000, 0, 0, 0, 0],             # 네 손가락
        5: [0, 0, 0, 0, 0, 0],                    # 전부 폄
    }
    for n in range(1, 6):
        await hand.set_all(numbers[n], duration_ms=500, name=f"숫자 {n}")
        await asyncio.sleep(1.0)


async def section_grip_levels(hand):
    """6) 전체 쥐기 레벨 0→100%."""
    banner("6) 전체 쥐기 레벨 (0→25→50→75→100%)")
    for lv in (0, 250, 500, 750, 1000, 0):
        await hand.set_all([lv] * 6, duration_ms=500, name=f"쥐기 {lv // 10}%")
        await asyncio.sleep(0.9)


async def section_finale(hand):
    """7) 피날레 - 주먹 쥐었다 활짝 펴며 인사."""
    banner("7) 피날레 👋")
    await hand.set_all([1000] * 6, duration_ms=400, name="주먹 ✊")
    await asyncio.sleep(0.9)
    await hand.set_all([0] * 6, duration_ms=400, name="활짝 펴기(인사) ✋")
    await asyncio.sleep(0.9)


async def play_once(hand):
    """전체 데모 1회 재생."""
    print("\n" + "=" * 60)
    print("  🎭  BrainCo Revo2 로봇손 - 전체 동작 데모 플레이")
    print("=" * 60)
    await hand.set_all([0] * 6, name="시작 준비(펴기)")
    await asyncio.sleep(1.0)

    await section_gestures(hand)
    await section_wave(hand)
    await section_cycle(hand)
    await section_finetune(hand)
    await section_counting(hand)
    await section_grip_levels(hand)
    await section_finale(hand)

    print("\n" + "=" * 60)
    print("  ✅ 데모 완료!")
    print("=" * 60 + "\n")


async def main():
    # 로봇손 연결(자동 감지) + 천분비 모드
    (client, slave_id) = await open_modbus_revo2()
    await client.set_finger_unit_mode(slave_id, libstark.FingerUnitMode.Normalized)
    hand = HandController(client, slave_id)

    try:
        if "--loop" in sys.argv:
            print("\n🔄 무한 반복 모드 (Ctrl+C 로 종료)\n")
            while True:
                await play_once(hand)
                await asyncio.sleep(2.0)
        else:
            await play_once(hand)
    except KeyboardInterrupt:
        print("\n\n👋 데모를 종료합니다...")
    finally:
        # 종료 시 손 펴고 연결 닫기
        await hand.set_all([0] * 6)
        libstark.modbus_close(client)
        print("연결을 종료했습니다.")


if __name__ == "__main__":
    asyncio.run(main())
