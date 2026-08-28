#!/usr/bin/env python3
import sys
import os
# 공식 SDK 예제 폴더(STARK_SDK_DIR 미설정 시 참조 설치 경로 사용)
_SDK_DIR = os.path.expanduser(
    os.environ.get("STARK_SDK_DIR", "~/1/brainco/src/stark-serialport-example")
)
sys.path.append(os.path.join(_SDK_DIR, "python", "revo2"))

from revo2_utils import libstark

print("손가락 인덱스:")
print(f"  Thumb (엄지):  {int(libstark.FingerId.Thumb)}")
print(f"  Index (검지):  {int(libstark.FingerId.Index)}")
print(f"  Middle (중지): {int(libstark.FingerId.Middle)}")
print(f"  Ring (약지):   {int(libstark.FingerId.Ring)}")
print(f"  Pinky (소지):  {int(libstark.FingerId.Pinky)}")
print(f"  Wrist (손목):  {int(libstark.FingerId.Wrist)}")

print("\n배열 인덱스 매핑:")
print("positions = [Thumb, Index, Middle, Ring, Pinky, Wrist]")
print("positions = [  0  ,   1  ,   2   ,  3  ,   4  ,   5  ]")

