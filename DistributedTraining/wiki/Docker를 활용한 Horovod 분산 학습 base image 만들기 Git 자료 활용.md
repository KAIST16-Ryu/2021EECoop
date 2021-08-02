(작성중...)

아래의 링크를 통해서 Dockerfile 양식을 받아오자.
[도커 base 컨테이너 양식](http://lab.t3q.co.kr:9999/kaist-co-op/data-parallel-training-with-horovod/-/tree/master/horovod-docker-resources/doc-hvd-v2)

다음과 같이 총 3개의 파일이 존재한다.
+ Dockerfile
+ authorized_keys (Public Key)
+ lifelog-lab-t3q.pem (Private Key)

![image](https://user-images.githubusercontent.com/71695489/127619208-11d58b99-9550-4b3a-9e9a-d20d5ba86176.png)

보안을 위해서 위의 인증키를 개인 소유 인증키로 바꾸고 싶다면 다음의 작업을 진행한다.

#### 1. Public, Private 키를 직접 생성한다.

#### 2. 위의 Public Key 및 Private 키를 생성한 키로 변경한다.

#### 3. Dockerfile 을 일부 수정한다.
+ Dockerfile 코드를 들여다보면 마지막 부분의 코드는 다음과 같다.
![image](https://user-images.githubusercontent.com/71695489/127619231-a5564d30-e027-4730-96c0-62f8c8cccbc3.png)

위를 완료하면, 도커 생성을 위해 만든 디렉토리에는 다음과 같이 새로운 파일들이 생성되어 있다.

![image](https://user-images.githubusercontent.com/71695489/127619253-f16bebb4-f563-427e-8452-479a568f013a.png)

마지막으로 다음과 같은 명령어를 사용하여 이미지를 생성한다.

$ sudo docker build -t (**Image_Name**) .
(마지막에 . 있다!)

$ sudo docker tag (**Image_name**) (**DockerAccount_Name/Image_name**)

$ sudo docker push (**DockerAccount_Name/Image_name**)
