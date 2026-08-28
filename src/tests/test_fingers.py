#!/usr/bin/env python3
import sys
import os
# 공식 SDK 예제 폴더(STARK_SDK_DIR 미설정 시 참조 설치 경로 사용)
_SDK_DIR = os.path.expanduser(
    os.environ.get("STARK_SDK_DIR", "~/1/brainco/src/stark-serialport-example")
)
sys.path.append(os.path.join(_SDK_DIR, "python"))

from bc_stark_sdk import libstark

print("FingerId enum:")
print(f"  Thumb: {libstark.FingerId.Thumb}")
print(f"  Index: {libstark.FingerId.Index}")
print(f"  Middle: {libstark.FingerId.Middle}")
print(f"  Ring: {libstark.FingerId.Ring}")
print(f"  Pinky: {libstark.FingerId.Pinky}")
print(f"  Wrist: {libstark.FingerId.Wrist}")

