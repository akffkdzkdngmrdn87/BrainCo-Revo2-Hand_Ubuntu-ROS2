# WSL2에서 STARK2.0 USB 장치 연결 가이드

> **경로 표기 안내** — 아래 `$STARK_SDK_DIR` 는 제조사 예제(`stark-serialport-example`)를 내려받은 폴더입니다.
> 터미널에서 먼저 지정하십시오. 예)
> `export STARK_SDK_DIR=~/1/brainco/src/stark-serialport-example`


## 현재 상황

WSL2 환경에서 USB 장치가 아직 인식되지 않았습니다. WSL2에서 USB 장치를 사용하려면 Windows에서 USBIPD를 통해 장치를 WSL2로 전달해야 합니다.

## 해결 방법

### 1단계: Windows에서 USBIPD 설치

Windows PowerShell(관리자 권한)에서 실행:

```powershell
# USBIPD 설치 (Windows 11 또는 Windows 10 1803 이상)
winget install --interactive --exact dorssel.usbipd-win

# 또는 Chocolatey 사용
choco install usbipd
```

### 2단계: 연결된 USB 장치 확인

Windows PowerShell(관리자 권한)에서:

```powershell
usbipd list
```

STARK2.0 장치를 찾으세요 (예: USB Serial Device, FTDI, CH340 등)

### 3단계: USB 장치를 WSL2로 연결

Windows PowerShell(관리자 권한)에서:

```powershell
# WSL2 배포판 이름 확인 (일반적으로 Ubuntu)
wsl --list --verbose

# USB 장치를 WSL2로 연결 (BUSID는 usbipd list에서 확인)
usbipd bind --busid <BUSID>

# 예: usbipd bind --busid 1-2

# WSL2로 연결
usbipd attach --wsl --busid <BUSID>
```

### 4단계: WSL2에서 장치 확인

WSL2 터미널에서:

```bash
# USB 장치 확인
ls -la /dev/ttyUSB* /dev/ttyACM*

# 또는 lsusb로 확인
lsusb

# dmesg로 최근 연결 확인
dmesg | tail -30 | grep -i usb
```

### 5단계: STARK2.0 장치 테스트

```bash
cd $STARK_SDK_DIR/python/revo2

# 의존성 설치 (필요한 경우)
pip3 install -r ../requirements.txt

# 오른손 장치 테스트 (slave_id: 0x7f)
python3 revo2_ctrl.py
```

## 빠른 명령어 참조

### Windows에서:
```powershell
# USB 장치 목록
usbipd list

# WSL2로 연결
usbipd attach --wsl --busid <BUSID>

# 연결 해제
usbipd detach --busid <BUSID>
```

### WSL2에서:
```bash
# USB 장치 확인
ls -la /dev/ttyUSB* /dev/ttyACM*

# 권한 설정 (필요한 경우)
sudo chmod 666 /dev/ttyUSB0

# 사용자를 dialout 그룹에 추가 (필요한 경우)
sudo usermod -a -G dialout $USER
```

## 대안: Windows에서 직접 실행

WSL2에서 USB 연결이 복잡하다면, Windows에서 직접 실행할 수도 있습니다:

1. Windows에서 Python 설치
2. `stark-serialport-example/windows` 디렉토리의 예제 사용
3. 또는 Windows용 SDK 사용

## 문제 해결

### USB 장치가 여전히 보이지 않는 경우:
1. Windows에서 장치가 제대로 인식되는지 확인
2. 드라이버가 설치되어 있는지 확인
3. `usbipd list`에서 장치가 보이는지 확인

### 권한 문제:
```bash
sudo chmod 666 /dev/ttyUSB0
sudo usermod -a -G dialout $USER
# 로그아웃 후 다시 로그인
```

