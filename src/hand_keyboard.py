#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BrainCo Revo2 Basic 로봇손 - 통합 키보드 제어 (직접 SDK 방식, 터미널 1개)
================================================================================

■ 특징
  - ROS2 불필요. 이 파일 하나만 실행하면 됩니다(컨트롤러 노드 별도 실행 X).
  - 프리셋 제스처 + 손가락별 단계 순환 + 손가락별 미세조정으로 자유 조합.

■ 손가락 배열(공식 SDK FingerId 순서로 확정된 매핑)
      인덱스: [ 0     1        2     3     4     5   ]
      손가락: [ 엄지  엄지보조  검지  중지  약지  소지 ]
      값    :   0 = 완전히 폄  ~  1000 = 완전히 쥠

■ 키 배치 요약
      1~6       : 손가락 3단계 순환   (폄 → 반쯤 → 쥠)
      !@#$%^    : 손가락 역순환       (쥠 → 반쯤 → 폄)   ※ Shift+숫자
      q w e r t y : 손가락 미세조정 - 쥐는 방향(+)
      Q W E R T Y : 손가락 미세조정 - 펴는 방향(−)      ※ Shift
        (q=엄지, w=엄지보조, e=검지, r=중지, t=약지, y=소지)

■ 실행법
      python3 src/hand_keyboard.py
      python3 src/hand_keyboard.py --demo   (자동 시연)

■ 공식 SDK 예제 폴더 지정(설치 위치가 다를 때만)
      export STARK_SDK_DIR=~/1/brainco/src/stark-serialport-example
"""

import asyncio
import os
import sys
import termios
import tty

# ─────────────────────────────────────────────────────────────────────────────
# 공식 SDK 예제(stark-serialport-example) 위치 결정
#   - revo2_utils.py 가 그 안에 있으므로 import 경로에 추가해야 한다.
#   - 환경변수 STARK_SDK_DIR 로 설치 위치를 덮어쓸 수 있다.
#   - 미설정이면 아래 기본 경로를 사용한다(참조 설치 위치).
#   → 이 스크립트를 어느 위치에서 실행해도 동작한다.
# ─────────────────────────────────────────────────────────────────────────────
_DEFAULT_SDK_DIR = "~/1/brainco/src/stark-serialport-example"
_SDK_DIR = os.path.expanduser(os.environ.get("STARK_SDK_DIR", _DEFAULT_SDK_DIR))
_REVO2_DIR = os.path.join(_SDK_DIR, "python", "revo2")

if not os.path.isdir(_REVO2_DIR):
    # 경로가 틀렸을 때 ImportError 대신 사람이 읽을 수 있는 안내로 중단한다.
    sys.exit(
        f"[오류] 공식 SDK 예제 폴더를 찾을 수 없습니다: {_REVO2_DIR}\n"
        f"       BrainCoTech/stark-serialport-example 를 내려받은 뒤,\n"
        f"       그 폴더 경로를 환경변수로 지정하십시오.\n"
        f"       예) export STARK_SDK_DIR=~/1/brainco/src/stark-serialport-example"
    )

if _REVO2_DIR not in sys.path:
    sys.path.insert(0, _REVO2_DIR)

from bc_stark_sdk import main_mod as libstark
from revo2_utils import open_modbus_revo2

# ─────────────────────────────────────────────────────────────────────────────
# 손가락 이름(배열 인덱스 순서와 일치)
# ─────────────────────────────────────────────────────────────────────────────
FINGER_NAMES = ["엄지", "엄지보조", "검지", "중지", "약지", "소지"]

# ─────────────────────────────────────────────────────────────────────────────
# 프리셋 제스처 정의  {키: (이름, [엄지, 엄지보조, 검지, 중지, 약지, 소지])}
#   0 = 완전히 폄, 1000 = 완전히 쥠
#   ※ 미세조정 키(q~y)와 겹치지 않도록 엄지척=u, 러브=l 로 배치
# ─────────────────────────────────────────────────────────────────────────────
GESTURES = {
    'p': ("보 (손 펴기) ✋",   [0,    0,    0,    0,    0,    0]),
    'f': ("주먹 ✊",          [1000, 1000, 1000, 1000, 1000, 1000]),
    'v': ("브이/가위 ✌️",      [1000, 1000, 0,    0,    1000, 1000]),
    'o': ("OK 👌",           [600,  750,  550,  0,    0,    0]),
    'u': ("엄지 척 👍",       [0,    0,    1000, 1000, 1000, 1000]),
    'g': ("총 🔫",           [0,    0,    0,    1000, 1000, 1000]),
    'l': ("러브(ILY) 🤟",     [0,    0,    0,    1000, 1000, 0]),
    'c': ("하트 💗",          [500,  600,  500,  1000, 1000, 1000]),
    'n': ("숫자 3 (검지·중지·약지)", [1000, 1000, 0, 0, 0, 1000]),
}

# 개별 손가락을 누를 때마다 순환할 3단계 (폄 → 반쯤 → 쥠)
CYCLE = [0, 500, 1000]

# Shift+숫자 → 역순환 대상 손가락 인덱스
SHIFT_NUM = {'!': 0, '@': 1, '#': 2, '$': 3, '%': 4, '^': 5}

# 미세조정 키 → 손가락 인덱스 (q w e r t y : 쥐는 방향 +)
FINE_KEYS = {'q': 0, 'w': 1, 'e': 2, 'r': 3, 't': 4, 'y': 5}
# Shift 미세조정 키 → 손가락 인덱스 (Q W E R T Y : 펴는 방향 −)
FINE_KEYS_REV = {'Q': 0, 'W': 1, 'E': 2, 'R': 3, 'T': 4, 'Y': 5}

# 미세조정 1회당 변화량
FINE_DELTA = 100


class HandController:
    """로봇손 상태를 배열로 관리하며 SDK로 위치 명령을 보내는 컨트롤러."""

    def __init__(self, client, slave_id):
        self.client = client
        self.sid = slave_id
        # 현재 6개 손가락의 목표 위치(펴진 상태로 시작)
        self.pos = [0, 0, 0, 0, 0, 0]

    async def _apply(self, duration_ms=500):
        """현재 self.pos 배열을 실제 로봇손에 전송."""
        # 0~1000 범위로 안전하게 클램프 후 정수화
        p = [int(max(0, min(1000, v))) for v in self.pos]
        # 위치 + 도달시간(ms) 방식으로 6개 손가락 동시 제어
        await self.client.set_finger_positions_and_durations(
            self.sid, p, [duration_ms] * 6
        )

    async def set_all(self, positions, duration_ms=600, name=""):
        """프리셋 제스처처럼 6개 위치를 한 번에 설정."""
        self.pos = list(positions)
        if name:
            print(f"  ▶ {name}   ->  {self.pos}")
        await self._apply(duration_ms)

    async def cycle_finger(self, idx, reverse=False):
        """개별 손가락을 3단계로 한 단계 순환.
        reverse=False: 폄→반쯤→쥠 순,  reverse=True: 쥠→반쯤→폄 순.
        """
        cur = self.pos[idx]
        if cur in CYCLE:
            i = CYCLE.index(cur)
            nxt = CYCLE[(i - 1) % len(CYCLE)] if reverse else CYCLE[(i + 1) % len(CYCLE)]
        else:
            # 중간값(미세조정으로 만들어진 값)이면, 방향에 맞는 끝값으로
            nxt = 0 if reverse else 1000
        self.pos[idx] = nxt
        state = {0: "폄", 500: "반쯤", 1000: "쥠"}[nxt]
        mark = "◀" if reverse else "▷"
        print(f"  {mark} {FINGER_NAMES[idx]} -> {state}({nxt})   현재: {self.pos}")
        await self._apply(400)

    async def nudge_finger(self, idx, delta):
        """개별 손가락을 delta만큼 미세조정(+: 쥐기, −: 펴기)."""
        self.pos[idx] = int(max(0, min(1000, self.pos[idx] + delta)))
        arrow = f"쥐기+{delta}" if delta > 0 else f"펴기{delta}"
        print(f"  ✎ {FINGER_NAMES[idx]} 미세 {arrow} -> {self.pos[idx]}   현재: {self.pos}")
        await self._apply(200)

    async def nudge_all(self, delta):
        """모든 손가락을 delta만큼 미세 조정(전체 쥐기/펴기 정도)."""
        self.pos = [int(max(0, min(1000, v + delta))) for v in self.pos]
        print(f"  ± 전체 {'+' if delta > 0 else ''}{delta}   현재: {self.pos}")
        await self._apply(300)

    async def read_status(self):
        """실제 로봇손의 현재 물리 위치를 읽어서 출력."""
        st = await self.client.get_motor_status(self.sid)
        print(f"  📟 실제 위치: {list(st.positions)}")


def print_help():
    """도움말 출력."""
    print("\n" + "=" * 66)
    print(" 🤖 BrainCo Revo2 로봇손 키보드 제어")
    print("=" * 66)
    print(" [프리셋 제스처]")
    print("   p 보(펴기)   f 주먹     v 브이/가위   o OK")
    print("   u 엄지척     g 총       l 러브(ILY)   c 하트    n 숫자3")
    print("\n [손가락 단계 순환]   (누를 때마다 한 단계)")
    print("   1~6        폄 → 반쯤 → 쥠      (1엄지 2엄지보조 3검지 4중지 5약지 6소지)")
    print("   ! @ # $ % ^   쥠 → 반쯤 → 폄   (Shift+숫자, 반대 방향)")
    print("\n [손가락 미세조정]   (숫자 아랫줄 q~y)")
    print("   q w e r t y   쥐는 방향(+)     (q엄지 w엄지보조 e검지 r중지 t약지 y소지)")
    print("   Q W E R T Y   펴는 방향(−)     (Shift, 반대 방향)")
    print("\n [전체 조절]")
    print("   Space 전체 펴기   0 전체 주먹   +(=) 전체 조금 쥐기   -(_) 전체 조금 펴기")
    print("\n [기타]   i 실제위치 읽기    ? 도움말    Esc 또는 Ctrl+C 종료")
    print("=" * 66 + "\n")


async def read_key():
    """비차단 방식으로 키 하나를 raw 모드로 읽어온다(엔터 불필요)."""
    loop = asyncio.get_event_loop()
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = await loop.run_in_executor(None, sys.stdin.read, 1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch


async def run_demo(hand):
    """모든 제스처를 순서대로 자동 시연(눈으로 손 모양 확인용)."""
    print("\n🎭 제스처 자동 시연을 시작합니다...\n")
    order = ['p', 'f', 'p', 'v', 'o', 'u', 'g', 'l', 'c', 'n', 'p']
    for k in order:
        name, positions = GESTURES[k]
        await hand.set_all(positions, duration_ms=800, name=name)
        await asyncio.sleep(1.5)  # 손이 모양을 잡을 시간
    print("\n✅ 시연 완료. 손을 폅니다.")
    await hand.set_all(GESTURES['p'][1], name=GESTURES['p'][0])


async def run_interactive(hand):
    """키보드 대화형 제어 루프."""
    print_help()
    print("⌨️  키를 누르면 손이 즉시 움직입니다 (종료: Esc 또는 Ctrl+C)\n")
    while True:
        key = await read_key()

        if key in ('\x1b', '\x03'):       # Esc 또는 Ctrl+C
            print("\n👋 종료합니다. 손을 폅니다.")
            await hand.set_all(GESTURES['p'][1])
            break
        elif key in GESTURES:             # 프리셋 제스처
            name, positions = GESTURES[key]
            await hand.set_all(positions, name=name)
        elif key in ('1', '2', '3', '4', '5', '6'):   # 손가락 3단계 순환(정방향)
            await hand.cycle_finger(int(key) - 1)
        elif key in SHIFT_NUM:            # Shift+숫자 : 손가락 역순환
            await hand.cycle_finger(SHIFT_NUM[key], reverse=True)
        elif key in FINE_KEYS:            # q~y : 손가락 미세조정(쥐기 +)
            await hand.nudge_finger(FINE_KEYS[key], +FINE_DELTA)
        elif key in FINE_KEYS_REV:        # Q~Y : 손가락 미세조정(펴기 −)
            await hand.nudge_finger(FINE_KEYS_REV[key], -FINE_DELTA)
        elif key == ' ':                  # 전체 펴기
            await hand.set_all([0] * 6, name="전체 펴기 ✋")
        elif key == '0':                  # 전체 주먹
            await hand.set_all([1000] * 6, name="전체 주먹 ✊")
        elif key in ('+', '='):           # 전체 조금 쥐기
            await hand.nudge_all(+200)
        elif key in ('-', '_'):           # 전체 조금 펴기
            await hand.nudge_all(-200)
        elif key == 'i':                  # 실제 위치 읽기
            await hand.read_status()
        elif key == '?':                  # 도움말
            print_help()
        # 그 외 키는 무시


async def main():
    # 로봇손 연결(자동 감지: 포트/보드레이트/slave_id)
    (client, slave_id) = await open_modbus_revo2()

    # 위치 값을 0~1000 천분비(Normalized)로 다루도록 설정
    await client.set_finger_unit_mode(slave_id, libstark.FingerUnitMode.Normalized)

    hand = HandController(client, slave_id)

    # 안전을 위해 시작 시 손을 편 상태로 초기화
    await hand.set_all([0] * 6, name="초기화(펴기) ✋")
    await asyncio.sleep(1.0)

    try:
        if "--demo" in sys.argv:
            await run_demo(hand)
        else:
            await run_interactive(hand)
    finally:
        libstark.modbus_close(client)
        print("연결을 종료했습니다.")


if __name__ == "__main__":
    asyncio.run(main())
