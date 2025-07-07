#!/bin/bash

# 1. 종속성 패치 (시스템 업데이트 및 필요한 라이브러리 설치)
echo "1. 시스템 업데이트 및 종속성 설치 중..."
sudo apt update -y
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev \
liblzma-dev git
echo "종속성 설치 완료."

# 2. pyenv 설치
echo "2. pyenv 설치 중..."
curl https://pyenv.run | bash
echo "pyenv 설치 완료."

# 3. ~/.bashrc 에 pyenv 관련 코드 삽입
echo "3. ~/.bashrc 에 pyenv 설정 추가 중..."
# 이미 추가되어 있는지 확인하고, 없으면 추가
if ! grep -q "export PYENV_ROOT=\"\$HOME/.pyenv\"" ~/.bashrc; then
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
fi
if ! grep -q 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' ~/.bashrc; then
    echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
fi
if ! grep -q 'eval "$(pyenv init - bash)"' ~/.bashrc; then
    echo 'eval "$(pyenv init - bash)"' >> ~/.bashrc
fi
echo "~/.bashrc 설정 완료."

# 4. 소스 적용
# 스크립트 내에서 pyenv 명령어를 바로 사용하기 위해 환경 변수를 현재 쉘에 적용
echo "4. 환경 변수 적용 중..."
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"
echo "환경 변수 적용 완료."

# 5. 파이썬 설치
echo "5. Python 3.11.13 설치 중 (시간이 다소 소요될 수 있습니다)..."
pyenv install 3.11.13
echo "Python 3.11.13 설치 완료."

# 6. 프로젝트 폴더 이동
echo "6. 'bo-mqtt-node' 프로젝트 폴더로 이동 중..."
cd bo-mqtt-node || { echo "오류: 'bo-mqtt-node' 폴더를 찾을 수 없습니다. 스크립트를 종료합니다."; exit 1; }
echo "프로젝트 폴더 이동 완료."

# 7. 로컬 파이썬 등록
echo "7. 로컬 파이썬 버전 3.11.13 등록 중..."
pyenv local 3.11.13
echo "로컬 파이썬 버전 등록 완료."

echo "모든 스크립트 실행 완료."