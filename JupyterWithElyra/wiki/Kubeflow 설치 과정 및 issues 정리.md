- Kubeflow 는 현재도 개발 중인 툴이다. 따라서 설치하는 과정에서, 또는 사용하는 과정에서 다양한 이슈가 발생할 수 있다. 직접 Kubeflow 를 설치했던 과정을 정리하고, 발생한 문제에 대해서 이야기한다.

- 본인은 노트북에 microk8s 를 설치하고, 그 위에 kubeflow 를 설치했다. 설치 과정은 다음과 같다.

1) microk8s 설치

2. kubeflow 설치

- 노트북 환경은 다음과 같다.
1) OS Linux 18.04


## microk8s 및 kubeflow 설치

#### 다음 URL 들을 같이 참고해도 좋다.
(URL - https://sidepun.ch/entry/Kubeflow-%EC%84%A4%EC%B9%98-WSL2-Ubuntu-Docker-Desktop)

#### 다음 URL 의 설치 과정을 따른다.
(**URL- https://gist.github.com/etheleon/80414516c7fbc7147a5718b9897b1518**)


- 여기에도 microk8s 를 설치하는 방법이 설명되어 있다. 이곳의 설치 과정을 따른다. 중간 중간 설명한 부분과 다르게 설치한 부분은 아래에서 설명한다. 기본적으로 설치 환경, 및 시기에 따라서 설치 방법이 변동될 수 있기 때문에 설명을 참고하여 개별적으로 설치하는 것을 권장한다.

# 1.
![image](https://user-images.githubusercontent.com/71695489/127605667-d6a82f96-087f-49ec-a8c5-3d71778b32c6.png)
-------------------------------------------------------------------------------------------------

- microk8s 의 특정 버전을 선택해서 설치할 수 있다. --classic 옵션과 --channel 옵션을 활용한다.

<br/>
<br/>

# 2.
![image](https://user-images.githubusercontent.com/71695489/127605691-06a1733b-d5ae-4727-bcf7-909df7b436d6.png)
-------------------------------------------------------------------------------------------------

- microk8s 는 kubernetes 의 light weight version 이다. 따라서 실제로 필요한 몇몇 추가적인 툴들을 모듈처럼 추가 설치하여 사용할 수 있도록 제공하고 있다. kubeflow 를 사용하기 위해서 필요한 add-on 를 다음 이미지에서 추가하여 설치한다. 별도로 추가하고 싶은 항목은 개별적으로 추가한다. 전체 항목은 아래 그림과 같다. **여기서 add-on으로 kubeflow를 설치하면 제대로 설치되지 않으니 kubeflow 는 add-on을 사용하여 설치하지 않고 아래 방법을 따라서 설치하는 것을 추천한다.**

![image](https://user-images.githubusercontent.com/71695489/127605728-c2bad6c1-8fe9-46bd-9c2a-28a4fe653be8.png)

<br/>
<br/>

# 3.
![image](https://user-images.githubusercontent.com/71695489/127605763-c60a0283-46fb-499c-a0ac-884d1585eca1.png)
-------------------------------------------------------------------------------------------------

git issue URL - https://github.com/kubeflow/manifests/issues/959

- micrioservice 환경에서 개별적인 어플리케이션을 적용하기 위해서 istio 가 트래픽 관리, 보안 등 여러 문제들을 처리해 주는데, 이런 istio 툴을 연동해서 사용하기 위해서는 해당 프로그램이 kubernetes apiserver 에 접근할 수 있도록 기능들을 제공해주어야 한다. 해당 service account key 관련 항목을 추가해 준다.

- ` $ vim /var/snap/microk8s/current/args/kube-apiserver ` 명령어를 입력하면 kube-apiserver 파일을 열어볼 수 있는데, 아래에 2줄을 추가해준다.

--service-account-signing-key-file=${SNAP_DATA}/certs/serviceaccount.key<br/>
--service-account-issuer=kubernetes.default.svc

- 추가했을 때 설정 파일은 다음과 같다.<br/>
![image](https://user-images.githubusercontent.com/71695489/127605812-363bd811-7280-407e-b622-1bacbdba02af.png)

<br/>
<br/>

# 4.
![image](https://user-images.githubusercontent.com/71695489/127605862-c5ca65ef-af75-41d5-b0cb-ed33307963b4.png)
-------------------------------------------------------------------------------------------------

- microk8s 를 재시작한다.

<br/>
<br/>

# 5.
![image](https://user-images.githubusercontent.com/71695489/127605941-4b67381c-1b60-4277-b647-025f77fa6cd9.png)
-------------------------------------------------------------------------------------------------

- microk8s 에서 사용하는 kube config 항목을 추가한다. (이유는 잘 모르겠다...)
- 위의 명령어를 따라서 그대로 진행한다.

<br/>
<br/>

# 6.
![image](https://user-images.githubusercontent.com/71695489/127605986-68563fb0-6054-4010-8b66-7121c3f8b9ef.png)
-------------------------------------------------------------------------------------------------

1) kfctl 을 실행할 수 있는 압축 파일을 원하는 경로에 다운로드 받는다.
` $ wget --directory-prefix=(원하는 경로) (다운받을 URL) `

2) 다운 받은 파일의 압축을 해제한다.
` $ tar -xvf kfctl_v1.2.0-0-gbc038f9_linux.tar.gz `

3) kfctl 을 사용하기 위해서 압축 파일을 해제한 실행 파일이 있는 경로를 PATH 에 추가한다.
  - 영구적으로 추가하기 위해서는 ~/.bashrc 파일을 다음 명령어를 통해서 연다. 
` $ vim ~/.bashrc `

  - 다음 명령어를 추가하여 PATH 환경변수에 추가한다.
` $ export PATH=(추가할 경로)${PATH:+:${PATH}} `<br />
  ![image](https://user-images.githubusercontent.com/71695489/127607302-8b7ae892-edc3-4e76-bcb2-8bdda8be6c4d.png)


<br/>
<br/>

# 7.
![image](https://user-images.githubusercontent.com/71695489/127607393-f95c3d7b-fa10-47be-a31b-c0bd21aa2635.png)
-------------------------------------------------------------------------------------------------

1) Kubeflow 기본 manifests 에서 필요한 버전 및 양식에 대한 yaml 을 찾아서 설치할 수 있다.
  - 환경변수로 URL 등록 ` $ export CONFIG_URI="https://(yaml URL)" `

2) 현재 위의 그림에서 기본적으로 추천하는 v1.2.0 버전에 대한 URL 은 다음과 같다.
  - https://raw.githubusercontent.com/kubeflow/manifests/v1.2-branch/kfdef/kfctl_k8s_istio.v1.2.0.yaml

3) admin access 를 허용하기 위해서는 빨간 박스의 지시를 따른다.

4) 다음 그림의 안내에 따라 kf_installation_temp 디렉토리를 생성하고, 거기에서 kubectl apply 명령어를 실행한다.
  - ` $ mkdir $HOME/kf_installation_temp && cd $HOME/kf_installation_temp `
  - ` $ kfctl apply -V -f $CONFIG_URI `

<br/>
<br/>

# 8.
![image](https://user-images.githubusercontent.com/71695489/127607466-5dec2cf9-5a53-4139-975f-2de419748bfb.png)
-------------------------------------------------------------------------------------------------

1) Argo Workflow 를 통해서 파드가 생성되도록 하려면 몇몇 설정을 추가해야 한다. 위 그림의 안내에 따른다.

  - ` $ vim /var/snap/microk8s/current/args/kubelet ` 명령어를 입력하여 kubelet 파일을 연다.
  
  - 위의 두 줄에는 #을 달아 주석 처리하고, 아랫줄을 추가해서 작성한다.<br />
 ` # --container-runtime=remote `<br />
 ` # --container-runtime-endpoint=${SNAP_COMMON}/run/containered.sock `<br />
 ` --container-runtime=docker `

  - 내용은 다음과 같이 작성되어야 한다.<br />
![image](https://user-images.githubusercontent.com/71695489/127607521-10939b21-fc8f-4dd7-a6d4-1738bc427c61.png)

<br/>

## 이렇게 되면 Kubeflow 기능을 사용할 수 있다.!!

<br/>
<br/>
<br/>

# 9. Kubeflow Dashboard URL 접속

![image](https://user-images.githubusercontent.com/71695489/127607570-28ce2922-9297-42d8-a7d3-95d2d43d998a.png)
---
- 위의 그림에서는 다음 명령어를 통해서 대시보드 URL 에 접속할 수 있다고 설명하지만, 이 방법에 따르지 않고 아래 안내에 따른다.

- 여기서 우리가 확인할 것은 Kubeflow 에서 Microservice 간 통신을 빠르고 안전하게 하기 위해서 istio 를 사용하고, 대시보드를 위한 주소 및 포트를 ` istio-system ` 의 namespace 에, 그리고 ` istio-ingressgateway service ` 를 사용하여 노출한다는 것을 확인할 수 있다.

- 따라서 다음 명령어를 사용하여 리소스를 확인해 보면, ` $ kubectl describe svc/istio-ingressgateway -n istio-system ` 아래 그림처럼 리소스를 확인할 수 있다.

![image](https://user-images.githubusercontent.com/71695489/127607616-a81cdcd8-edeb-498b-9909-53b5609c9680.png)

- 위 그림에서 보면 http2 통신 포트가 31380 이기 때문에, 노드 IP (**현재 작성자 노트북의 경우, 192.168.0.127**) 의 Kubeflow DashBoard 에 접속하기 위해서 다음과 같이 입력해보면, ` http://192.168.0.127:31380 `

![image](https://user-images.githubusercontent.com/71695489/127607664-49e6191e-8620-4b8a-a5d4-4cc2c5f81a49.png)

- 다음과 같은 로그인 화면이 뜨고, 기본으로 설정된 email: admin@kubeflow.org, password: 12341234 를 입력하면,

![image](https://user-images.githubusercontent.com/71695489/127607723-9460881d-d25e-4069-ad7e-37a6c16d1f3b.png)

- 다음과 같이 Kubeflow Dashboard 에 접속한 것을 확인할 수 있다.!

**T3Q 플랫폼부문 기술연구소**
**인턴 유어진**
