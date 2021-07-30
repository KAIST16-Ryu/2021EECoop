1. Horovod란? : Tensorflow, Pytorch 등 다양한 딥러닝 플랫폼에서 빠르고 간편한 분산학습을 진행하기 위해서 제공되는 플랫폼이다.

- https://horovod.ai/




----------------------------------------------------------------------------------------------




2. Horovod Installation

- https://horovod.readthedocs.io/en/stable/install_include.html

- 호로보드를 설치하기 위해서는 사전에 설치해 놓아야 할 것들이 정말 많다. 이 많은 프로그램들이 서로 지원하도록 버전을 맞추는 작업은 신경써야 할 것들이 매우 많고 복잡하다.
- 리눅스 18.04를 기준으로 다양한 플랫폼에서 Horovod를 동작하기 위한 Base Image가 공식 Gitub에 존재한다. 또한 nvidia 공식 홈페이지에는 딥러닝 관련 Container를 생성하기 위해서 필요한 툴들의 버전을 안내하고 있다. 아래의 사이트들을 참고하면서 여러 툴들의 버전을 고려하는 것을 추천한다.

- https://github.com/horovod/horovod/blob/master/Dockerfile.gpu
- https://github.com/horovod/horovod/blob/master/Dockerfile.test.gpu
- https://docs.nvidia.com/deeplearning/frameworks/tensorflow-release-notes/rel_20-11.html#rel_20-11
- https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel_20-11.html#rel_20-11

**위 사이트들에는 서로 충동하지 않는 버전들의 reference 및 설치 명령어에 대한 정보도 포함하고 있다.**

**처음 설치하는 분들이라면 꼭! 천천히 읽어보고 참고하여 설치를 진행하는 것을 추천한다.**

**설치 시간과, 도중에 발생하는 문제들을 최소화 시켜줄 것이다!**



----------------------------------------------------------------------------------------------
위의 github 를 참고하여 설치한다.

1. 혹시 설치되지 않았다면, 다음 명령어를 통해 이것들을 설치하는 것을 추천한다.

$ sudo apt update

$ sudo apt-get install -y build-essential

$ sudo apt-get install -y cmake

$ sudo apt-get install -y g++-7

(필요한 버전을 위에서 확인한다!)

$ sudo apt-get install -y git

$ sudo apt-get install -y curl

$ sudo apt-get install -y vim

$ sudo apt-get install -y wget

$ sudo apt-get install -y ca-certificates

----------------------------------------------------------------------------------------------

2.NCCL
- 자신의 CUDA version에 맞추어 다음 사이트에서 설치 파일을 다운로드한다. 어떤 버전을 설치할 것인지는 지금까지 설치한 CUDA, tenworflow 등의 버전과 위 사이트 추천을 고려하여 정한다.

https://developer.nvidia.com/nccl/nccl-legacy-downloads

![image](uploads/73ad4a706cda5267af90c5a65c515072/image.png)

다운 받았으면 다음 명령어를 통해서 압축을 해제하고, 필요한 툴을 설치한다.

$ dpkg -i (download deb파일)

$ sudo apt-get update

$ sudo apt install libnccl2=2.7.8-1+cuda10.1 libnccl-dev=2.7.8-1+cuda10.1

(여기서 2.7.8-1+cuda10.1 등의 버전은 본인의 설치파일에 따라 알맞게 설정.)

----------------------------------------------------------------------------------------------

3. openMPI

- 다음 명령어를 따라 설치한다. 위의 사이트에서 버전을 확인하고 알맞게 바꾸어 설치한다.

$ sudo mkdir /tmp/openmpi

$ sudo cd /tmp/openmpi

$ sudo wget https://www.open-mpi.org/software/ompi/v4.0/downloads/openmpi-4.0.0.tar.gz

$ sudo tar zxf openmpi-4.0.0.tar.gz

$ sudo cd openmpi-4.0.0

$ sudo ./configure --enable-orterun-prefix-by-default

$ sudo make -j $(nproc) all

$ sudo make install

$ sudo ldconfig

$ sudo rm -rf /tmp/openmpi

----------------------------------------------------------------------------------------------

4. 워커 노드들간의 ssh 연결 설정

- Horovod를 통해서 분산 학습을 수행하기 위해서는 실제로 프로그램이 돌아가는 Master Worker 에서 다른 Worker Node 들에게 자유럽게 접근할 수 있어야 한다. SSH 접속을 사용하기 때문에, 이것을 가능하도록 설정한다.

- 여거 가지 방법이 존재한다. **중요한 것은 마스터 워커에서 별다른 비밀번호 없이 ssh HostName@IP 를 통해서 접근할 수 있도록 환경을 세팅해 놓아야 한다. 비밀번호 등이 있다면 실제로 Horovod를 통한 분산 학습이 실행되지 않는다.

- 한 가지 방법이 공식 홈페이지에 나와 있다. 워커 노드에 자유롭게 접근할 수 있는 비밀번호 없는 인증서를 생성하는 것이다.
http://www.linuxproblem.org/art_9.html

----------------------------------------------------------------------------------------------

Horovod 실행 명령어

**공식 Docs 명령어로 실행하면 실행되지 않는다.**
다음의 명령어를 사용한다.

(호로보드 명령어)
1. 멀티노드
horovodrun -np 2 -H localhost:1,133.186.247.252:1 python Keras_TF_MultiNode_GPU.py

2. 싱글노드
horovodrun -np 1 -H localhost:1 python Keras_TF_MultiNode_GPU.py

완료.
