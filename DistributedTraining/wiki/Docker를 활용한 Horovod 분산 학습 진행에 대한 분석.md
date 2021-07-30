<1.  Dockerfile 작성 요령>

공식 홈페이지에 Docker Container를 생성할 수 있는 base Dockerfile을 제공하고 있다.

- https://github.com/horovod/horovod/blob/master/Dockerfile.gpu

그러나 공식 홈페이지의 Dockerfile을 단순히 가져와서는 분산 학습 프로그램이 실행되지 않고 다양한 Issues 들이 발생한다. 이에 대한 내용을 정리하고 실제로 잘 돌아갈 수 있도록 필요한 부분을 추가하고, 겪은 Issues 들을 정리한다.

-------------------------------------------------------------------------------------------------

전체적으로 추가한 부분은 다음과 같다.

![image](https://user-images.githubusercontent.com/71695489/127618860-4082b56e-48e3-44f0-8a52-bb43f6c75b68.png)

먼저, Docker 단계에서 분산 학습을 진행하기 위해서 필요한 선행 요구사항들이 있다.

1. Master worker는 나머지 Worker에 대해서 별도의 password가 필요 없이 SSH 접근이 가능해야 한다.

  - 이를 위해서는 Dockerfile을 작성할때 필요한 공인 인증서의 public keys와 private keys를 추가해야 하며, 이 정보를 포함한 Config 파일 또한 보유하고 있어야 한다.

  - 또한 이러한 인증을 이용해서 비밀번호 없이 SSH 접근하기 위한 기본 Ubuntu docker image 설정을 변경해 주어야 한다.

-------------------------------------------------------------------------------------------------

필요한 Config, authorized_keys, pem 파일은 다음과 같은 방법으로 추가하였다.

![image](https://user-images.githubusercontent.com/71695489/127618895-a7442318-22b8-4120-861e-21b39d5bb54a.png)

- config 파일에는 서버 Node에 대한 정보와, 필요한 public_key 파일의 정보를 담고 있다. 내용은 다음과 같다.

![image](https://user-images.githubusercontent.com/71695489/127618905-e3179d34-0a28-48ba-b249-ad25c3ec77bb.png)

-------------------------------------------------------------------------------------------------

두번째로, Base Ubuntu Image에서 SSH 접속을 위한 기본 설정을 변경해야 한다. 관련한 Dockerfile 코드는 다음과 같다.

![image](https://user-images.githubusercontent.com/71695489/127618923-329dd280-fb77-47cf-abe5-9ee5990146e6.png)

위 그림에서 보면 알 수 있듯이, 직접 수정한 파일은 **/etc/ssh/sshd_config** 파일이다. sshd 파일이란 OpenSSH를 사용하기 위한 데몬(=서비스와 유사한 개념) 파일이며, 이에 관한 config 설정이 담겨 있는 파일이다. 실제로 보면 SSH 통신에 필요한 여러 조건들을 담고 있다. 이에 대한 내용은 대략 다음과 같다.

![image](https://user-images.githubusercontent.com/71695489/127618937-09e87b11-1626-472b-a10a-bddc35c448d3.png)

여기서 우리가 변경해야 할 옵션은 크게 2가지 이다.

첫 번째로, **PermitRootLogin without-password** 명령어-옵션 이고, RootLogin을 비밀번호 없이 가능하도록 설정한다.

두 번째로, **StrictModes no** 명령어-옵션 이고, 이에 대한 설명으로는 **로그인을 허용하기 전에 사용자 홈 디렉터리에 대한 소유권 및 접근 권한을 sshd가 확인할지 결정한다. 혹시 모를 악의적인 사용자가 숨겨 놓은 악성 코드를 찾아내기 위한 옵션이다.** 라고 한다. 정확한 의미는 잘 모르겠다.

-------------------------------------------------------------------------------------------------

< 2. Docker 실행 관련 내용 >

Docker 에서는 학습을 주도학 Master와 나머지 Worker 들의 명령을 다르게 하여 실행해야 한다. 공식 홈페이지에 기본적으로 나와 있는 내용은 다음과 같다.

- https://horovod.readthedocs.io/en/stable/docker_include.html

그러나 현재 내가 작성한 Dockerfile은 공식 홈페이지와는 조금 다르기 때문에 조금 다른 명령어로 학습을 진행한다. 먼저 Horovod Docs에서 제시한 명령어는 다음과 같다.

<Master>
$ sudo docker run -it --rm --gpus all --network=host -v /mnt/share/ssh:/root/.ssh horovod:latest

  root@<container_id>:/examples# horovodrun -np 16 -H host1:4,host2:4,host3:4,host4:4 -p 12345 python keras_mnist_advanced.py


<Worker>
$ sudo docker run -it --rm --gpus all --network=host -v /mnt/share/ssh:/root/.ssh horovod:latest bash -c "/usr/sbin/sshd -p 12345; sleep infinity"


(설명)
- -it => container에서 shell을 사용하기 위한 옵션
- --rm => container가 실행이 끝난 후 제거하기 위한 옵션
- --gpus all => gpu를 할당하기 위한 옵션
- --network=host => Host Network를 사용하기 위한 옵션
- -v /mnt/share/ssh:/root/.ssh => ssh 디렉토리에 있는 ssh 인증 관련 파일들을 mount 하기 위한 옵션
- /usr/sbin/sshd -p 12345 => OpenSSH 12345 Port를 열기 위한 명령어.

차이점은 다음과 같다.

- DockerFile에서는 Host Node의 SSH 관련 파일들을 Mount 해서 사용한다. 그러나 나는 관련 파일들을 그냥 복사하여 Container에 저장하는 방식을 사용했다.

따라서 내가 사용한 명령어는 다음과 같다.

<Master>
$ sudo docker run -it --rm --gpus all --network=host neo21top/doc-hvd-v1

root@<container_id>:/examples# horovodrun -np 2 -H localhost:1,133.186.247.252 -p 12345 python /examples/tensorflow2_keras_mnist.py


<Worker>
$ sudo docker run -it --rm --gpus all --network=host neo21top/doc-hvd-v1 bash -c "/usr/sbin/sshd -p 12345; sleep infinity"


-------------------------------------------------------------------------------------------------

학습이 잘 진행되는 것을 확인할 수 있다.

![image](https://user-images.githubusercontent.com/71695489/127618960-6424810d-6ca3-4e71-8e73-3c59bd528746.png)

-------------------------------------------------------------------------------------------------

** 다음 : Kubernetes를 활용한 Horovod 분산 학습 진행에 대한 분석 **

[Kubernetes를 활용한 Horovod 분산 학습 진행에 대한 분석](Kubernetes를 활용한 Horovod 분산 학습 진행에 대한 분석)
