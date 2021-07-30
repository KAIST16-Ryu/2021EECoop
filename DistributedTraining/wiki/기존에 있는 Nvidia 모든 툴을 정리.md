1. **새롭게 다른 버전의 Nvidia-driver를 설치할 경우**
2. **기존의 GPU를 사용하는 프로그램을 돌리는 도중에 비정상적으로 프로그램이 종료되거나 하여 그래픽 드라이버가 손상되었을 경우**

- 기존의 드라이버를 제거하고 새롭게 설치해주어야 한다.

다음과 같은 방법으로 현재 컴퓨터에 남아있는 Nvidia 관련 툴들을 싹 정리한다.

Linux 기준

1. Terminal에, **$ dpkg -l | grep -i nvidia**  입력하면, 현재 설치되어 있는 Nvidia 관련 툴들을 확인할 수 있다.

![image](https://user-images.githubusercontent.com/71695489/127612481-43585c27-49a4-4f5a-962c-1bd0f7cf5938.png)

2. Nvidia 툴들을 지우는 방법은 여러 가지가 있다.
- ** $ sudo apt-get remove --purge nvidia-* ** Nvidia와 관련된 모든 패키지 제거.
- ** $ sudo apt-get autoremove ** 남아있는 패키지들 중 일부 자동적으로 제거.

3. 다시 한번 **$ dpkg -l | grep -i nvidia** 를 입력했을 때 아직도 남아 있는 패키지들은 다음과 같은 명령어로 하나 하나 제거한다.
- ** $ sudo apt purge "name to remove" **
- Ex) $ sudo apt purge libnvidia-compute-450


모든 파일이 제거되었을 경우, 새롭게 필요한 툴들을 설치할 준비를 완료했다.

(+ 추가 : tar이나, zip파일로 CUDA 및 nvidia를 설치했을 경우, dpkg 명령어로 인식이 안될 수 있다.)

- 이때에는 CUDA는 /usr/local/ 디렉토리에 CUDA 디렉토리나, CUDA-(version) 등으로 존재하는데,
![image](https://user-images.githubusercontent.com/71695489/127612594-dedbd63b-903b-40ef-af0d-80b753c2b8a2.png)

$ sudo rm -rf CUDA 등의 명령어로 삭제 가능하다.

- nvidia-driver가 검색이 되지 않는 경우는 다음 경로에서 다음과 같은 방법으로 삭제 가능하다.
![image](https://user-images.githubusercontent.com/71695489/127612664-e001ba7f-3baf-4191-92f3-f2a9c8dcc766.png)
