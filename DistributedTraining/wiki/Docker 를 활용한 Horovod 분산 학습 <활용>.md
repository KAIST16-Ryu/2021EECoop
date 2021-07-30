**이번 포스트에서는 주어진 자원을 활용해서 Docker Container를 사용하여 Horovod 분산 학습을 진행하는 방법에 대한 설명을 작성했다.**


# Docker를 활용한 Horovod 분산 학습의 장, 단점.
-------------------------------------------------------------------------------------------------
<장점>
+ Docker는 Container 의 개념을 사용하여 특정 임무를 수행하기 위한 격리된 환경을 제공한다.　따라서 적절한 Docker 이미지를 가지고 있다면, 컴퓨터별로 별도의 프로그램을 설치하지 않고, 임무를 수행하기 위한 환경을 제공할 수 있다.　특히, 많은 Tools 및 Framework 를 설치해야 하는 AI 개발 환경에서 Docker 를 사용하면 기본 환경 설정을 편리하게 할 수 있다.

<단점>
+ 별도로 Docker 를 설치해야 하고, GPU를 사용하기 위해서는 Nvidia-docker 를 설치해야 한다.
  + Docker Desktop 설치　:　[Docker 설치 사이트](https://www.docker.com/products/docker-desktop)
  + Nvidia-docker 설치　:　[Nvidia-docker 설치 사이트](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker)
  + 위 사이트 Guide 를 참조한다.       
  <br/>
  
+ 분산학습을 진행하기 위한 Node 들이 별도의 password 없이 SSH 통신을 할 수 있도록 기본 환경을 준비해주어야 한다.
  + Node(컴퓨터) 들끼리 서로 SSH 접속이 가능한지 확인해야 한다. (어떻게 확인할 수 있는가?... 작성)
  + Node(컴퓨터) 들끼리 서로 SSH 접속이 가능하다면, 이후에 도커 컨테이너끼리 서로 SSH 접속을 하기 위한 설정을 해야 한다.
  + 분산 학습을 진행하기 위해서 코드를 일부 수정해야 한다.

# Docker를 활용하여 Horovod 분산 학습을 돌려보자.
-------------------------------------------------------------------------------------------------

## 1. Docker 를 설치해야 하고, GPU를 사용하기 위해서는 추가적으로 Nvidia-docker 를 설치해야 한다.

+ Docker Desktop 설치　:　[Docker 설치 사이트](https://www.docker.com/products/docker-desktop)<br/>
+ Nvidia-docker 설치　:　[Nvidia-docker 설치 사이트](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker)<br/>
+ 위 사이트 Guide 를 참조한다.<br/>

<br/>
<br/>

## 2. 분산 학습에 필요한 리소스는 아래 Github 나 Docker Image를 활용하는 것을 추천한다.

+ Git 소스 : [neo21top/doc-hvd-v2 이미지 소스](http://lab.t3q.co.kr:9999/kaist-co-op/data-parallel-training-with-horovod/-/tree/master/horovod-docker-resources/doc-hvd-v2)<br/>
+ neo21top/doc-hvd-v2 :　**$ sudo docker pull neo21top/doc-hvd-v2** 명령어를 사용하면 이미지를 다운 받아 사용할 수 있다.


혹시 보안을 위해서 개별 private, public 키를 생성해서 활용하고자 한다면 위의 Git 소스에서 일부를 수정하는 것을 추천한다.<br/>
　[**보안을 강화하고자 한다면, 직접 public, private 키를 생성해서 image에 추가시켜주자.**](http://lab.t3q.co.kr:9999/kaist-co-op/data-parallel-training-with-horovod/-/wikis/Docker%EB%A5%BC-%ED%99%9C%EC%9A%A9%ED%95%9C-Horovod-%EB%B6%84%EC%82%B0-%ED%95%99%EC%8A%B5--Git-)<br/>

<br/>
<br/>
전체적인 Docker Container 분산 학습 디자인은 다음과 같다.

![image](https://user-images.githubusercontent.com/71695489/127619435-8e95f9f1-90ed-4021-8158-1fcd1b7fdc9c.png)

<br/>
<br/>

## 3. 우리는 노드의 동일한 경로에 총 3개의 파일을 저장할 것이다. 중요한 것은 (**동일한 경로!**)에 (**동일한 이름!**)의 파일을 저장해야 한다.<br/>
　[**보안을 강화하고자 한다면, 직접 public, private 키를 생성해서 image에 추가시켜주자.**](http://lab.t3q.co.kr:9999/kaist-co-op/data-parallel-training-with-horovod/-/wikis/Docker%EB%A5%BC-%ED%99%9C%EC%9A%A9%ED%95%9C-Horovod-%EB%B6%84%EC%82%B0-%ED%95%99%EC%8A%B5--Git-)


/ (Mount 할 디렉토리)<br/>
↳ Train.py (분산 학습 스크립트 코드)<br/>
↳ /Data (데이터가 저장된 디렉토리 또는 파일)<br/>
↳ Config (각 노드의 정보가 담긴 Config 파일) => 아래와 같이 작성한다.<br/>

![image](https://user-images.githubusercontent.com/71695489/127619458-0ffa9292-39f3-4cff-938a-a5b0e5c72fd7.png)

이렇게 완료되면 이후에 마운트 할 Host Worker 의 디렉토리에는 다음과 같이 파일들이 만들어져 있어야 한다.

![image](https://user-images.githubusercontent.com/71695489/127619478-be3c56b1-d86d-48c4-80b5-9a2358c3dd1d.png)

<br/>
<br/>

## 4. sudo docker run 명령어를 통한 분산 컨테이너 생성.<br/>

Horovod 에서 제공하는 Docker 분산 학습 실행 명령어는 공식 홈페이지에 잘 정의되어 있다.

[Horovod Docker 실행에 관하여](https://horovod.readthedocs.io/en/stable/docker_include.html)

요약해서 설명하면 다음과 같다.
+ Horovod 를 사용한 분산학습에서는 1개의 Worker 가 Master worker로서 학습을 진행, Update 된 파라미터의 저장 등 주요 역할을 맡고, 나머지 Worker 는 학습을 진행한다.

+ 1개의 Main Worker의 Docker Container 실행 명령어는 다음과 같다.<br/>
  Ex) $ sudo docker run --rm -it --network host --gpus all -v ~/docker_dir:/train neo21top/doc-hvd-v3 bash -c "cp /train/config /root/.ssh; /bin/bash"<br/>
다음과 같이 Shell 을 실행할 수 있는 상태가 된다.
![image](https://user-images.githubusercontent.com/71695489/127619499-0a20a853-643c-458d-bf7f-a1d74600babf.png)
**cp /train/config /root/.ssh**　　　　=> Mount 해온 config 파일을 .ssh 디렉토리로 복사해야 SSH 통신 가능.<br/>
**/bin/bash**　　　　　　　　　　　　　　　=> 컨테이너에서 Bash Shell 을 사용하기 위한 명령어.

+ 나머지 Worker 의 Docker Container 실행 명령어는 다음과 같다.<br/>
  Ex) $ sudo docker run --rm -it --network host --gpus all -v ~/docker_dir:/train neo21top/doc-hvd-v3 bash -c "/usr/sbin/sshd -p 12345; sleep infinity"<br/>
다음과 같이 특정 포트(Ex 12345)를 열고 대기 중인 상태가 된다.
![image](https://user-images.githubusercontent.com/71695489/127619513-13f1161e-1712-416f-a0d0-f9d9ef6541b2.png)
**/usr/sbin/sshd -p 12345**　　　=> 특정 SSH 포트(Ex 12345) 를 열어 놓는 명령어<br/>
**sleep infinity**　　　　　　　　 => 계속 대기하도록 명령하기 위한 명령어

+ 주요 Docker run 의 옵션에 대한 설명은 다음과 같다
  - \- it => container에서 shell을 사용하기 위한 옵션
  - --rm => container가 실행이 끝난 후 제거하기 위한 옵션
  - --gpus all => gpu를 할당하기 위한 옵션
![image](https://user-images.githubusercontent.com/71695489/127619530-8e3d64a2-78c2-4cda-9b9f-571635f993e4.png)
  - --network=host => Host Network를 사용하기 위한 옵션
  - -v /mnt/share/ssh:/root/.ssh => ssh 디렉토리에 있는 ssh 인증 관련 파일들을 mount 하기 위한 옵션<br/>
( -v (Mount 할 Host의 경로):(Mount 할 Docker Container 경로) )

이후에 다음의 horovodrun 명령어를 Master Worker 에서 사용하여 학습을 진행할 수 있다.<br/>
$ horovodrun -np 2 -H localhost:1,133.186.247.252:1 -p 12345 python /train/hvd_train.py

여기서,<br/>
-np 2　         => 사용하는 총 GPU 갯수<br/>
-H localhost:1,133.186.247.252:1　       => Master worker에서 1개, 133.186.247.252 IP를 가진 Worker에서 GPU 를 1대 사용하겠다는 뜻.<br/>
-p 12345　     => 12345 번 SSH 포트를 사용하겠다는 뜻.<br/>

![image](https://user-images.githubusercontent.com/71695489/127619549-b0e89971-c891-4d7b-8a43-afc893fdb1e7.png)

<br/><br/><br/><br/><br/><br/>

Posted by. 유어진 (플랫폼부분 기술연구소 인턴)
