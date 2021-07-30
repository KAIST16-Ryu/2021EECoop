분산 학습 소스코드는 크게 4 부분으로 나누어져 있다.

![image](https://user-images.githubusercontent.com/71695489/127614788-5f50b08b-eeb9-4f09-9c04-1714b8321d6c.png)

### 1. DistributeTrain_BaseImage
= Manager Image  (Docker Image )를 생성하기 위한 리소스를 가지고 있는 디렉토리.

### 2. DistributeTrain_ManagerImage
= Base Image ( Docker Image ) 를 생성하기 위한 리소스를 가지고 있는 디렉토리.

### 3. 클러스터롤, 클러스터롤바인딩, 서비스 어카운트
= 기존의 컨테이너 외부에서 명령을 수행하는 Job resource와는 다르게 Manager Pod 는 컨테이너 내부에서 Kubernetes Cluster 리소스에 접근하고, 리소스를 수정할 수 있는 권한(Worker Pod를 컨테이너 내부에서 생성하기 위한 권한)이 필요하다. 따라서 서비스 계정을 생성하고, 권한을 인가하는 과정이 아래의 3가지 리소스 ( 1. DistributeTrain_ClusterRole.yaml, 2. DistributeTrain_ServiceAccount.yaml, 3. DistributeTrain_ClusterRoleBinding.yaml ) 에 해당한다.

### 4. DistributeTrain_Manager.yaml
= 마지막으로 DistributeTrain_Manager.yaml 은 매니저 파드를 생성하기 위한 YAML 양식이다.

<hr />
<br/>
<br/>
<br/>


# 1. DistributeTrain_BaseImage

![image](https://user-images.githubusercontent.com/71695489/127614816-0e640411-27b7-446a-bd48-0db81c1d43cc.png)

#### 1) Dockerfile

= DistributeTrain_BaseImage 디렉토리 내의 파일들을 가지고 도커 Base Image 를 생성하기 위한 Dockerfile 이다.

= 자세한 설명은 git repository 에서 확인할 수 있다.
  - http://lab.t3q.co.kr:9999/kaist-co-op/data-parallel-training-with-horovod/-/blob/master/horovod-kubernetes-resources/DistributeTrain_v1/DistributeTrain_BaseImage/Dockerfile

= 위 Dockerfile 은 크게 2가지 파트로 나뉜다.

  1. 학습을 진행하기 위한 Framework를 설치하기 위한 코드
    - 기존의 학습 DockerFile과 동일한 구성
    - 필요에 맞게 이부분을 수정해야 한다.

  2. 각 컨테이너 간의 SSH 통신 설정을 위한 코드
    - OpenSSH 관련 툴을 설치하고, 필요한 SSH 설정을 변경하기 위한 부분이 있다.
    - 고정된 코드이므로 변경하지 않아야 한다
<br/>

#### 2) Train.py

= 학습을 진행하기 위한 Python Script 이다. Horovod 를 사용한 분산학습을 진행하기 위해서는 Horovod 분산 학습 코드로 작성해야 한다. 기존의 코드에서 일부만 수정하면 분산 학습을 진행 가능하다

= 현재는 BaseImage 에 포함되어 있지만, 별로의 공유 Volume Storage 에 저장하고, 작업하는 부분으로 코드를 수정해야 한다.
<br/>
<br/>

#### 3) authorized_keys (= public key) & lifelog-lab-t3q.pem (= private key)

= Horovod 분산학습에서는 각 Node들이 서로 별도의 비밀번호 없이 SSH 통신을 통해서 학습 Parameters 를 공유한다. 따라서 비밀번호 없이 SSH 통신을 하기 위해서 공개키, 비밀키를 가지고 있어야 한다. Dockerfile 을 생성하는 과정에서 각 컨테이너에 전달된다.

= 이 부분은 사전에 제공하는 Public Key, Private 키를 사용해도 되고, 별도의 생성된 키를 추가해주어도 된다.

<hr />
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>


# 2. DistributeTrain_ManagerImage

= 분산 학습 리소스에서 가장 Main이 되는 부분이다. 분산 학습을 관련해서 준비하면서 느낀 것은 분산학습에서 추가적으로 조치하는 부분이 크게 다음과 같다는 것이다.

  1) 기존의 코드를 분산학습이 가능하도록 수정하는 것. ( Multi Process Program으로 바꿔줘야 하나 대부분의 Framework 에서 간단하게 수정할 수 있도록 지원하고 있다. )

  2) 분산 학습이 가능하도록 관련 환경을 설정하는 것. (SSH 통신이 가능하도록 만들고, 관련 리소스(Pod)를 조건에 맞게 생성하는 것 )

= 첫 번째 내용은 사용자가 직접 수정해주어야 하고, 두 번째 부분은 ManagerImage 파트가 담당하는 부분이다.

![image](https://user-images.githubusercontent.com/71695489/127614833-f5c0459d-06d3-4e18-99ed-eb21c448a07c.png)

#### 1) Dockerfile

= 위의 DistributeTrain_BaseImage 디렉토리 내의 파일들을 가지고 DistributeTrain_Base Docker Image를 만들기 위한 Dockerfile 이다. 설명은 다음 git repository 에서 확인할 수 있다.
  - http://lab.t3q.co.kr:9999/kaist-co-op/data-parallel-training-with-horovod/-/blob/master/horovod-kubernetes-resources/DistributeTrain_v1/DistributeTrain_ManagerImage/Dockerfile

= ManagerImage의 DockerFile 은 학습 자체와는 관련이 없다. Manager Pod 가 하는 일을 예시를 들어 설명하면 다음과 같다.

  1. 사용자에게 요청을 받는다. => "GPU 6대로 학습을 진행해 주세요."

  2. 현재 Cluster 에서 사용 가능한 자원 목록을 확인한다.
    ->  "현재 Node 1에 GPU 5대, Node 2에 GPU 3대, Node 3에 GPU 2대 있음."

  3. 현재 목록 중에서 할당할 수 있는 좋은 조건을 찾아서 Worker Pod 리소스를 생성한다.
    ->  "Node 1에 GPU 5대를 가진 Pod, Node 2에 GPU 1대를 가진 Pod를 생성."

  4. 학습을 진행한다.

  5. 학습이 끝난 후에 리소스를 반환한다.

<br/>
<br/>


#### 2) Manager.sh

= "distributetrain-manager" Pod 가 생성되었을 때 해야 할 일들을 하나의 파일에 담은 것이다.

= distributetrain-manager Pod 는 크게 다음 3가지의 일을 한다.

  1. 명시된 조건에 맞는 Worker Pod 들을 생성한다.

  2. 생성된 Worker Pod 들에게 분산 학습 명령을 지시하고, 학습을 진행한다.

  3. 학습이 끝나면, Worker Pod 들을 종료시켜 사용한 자원들을 반환한다.

= 아래 그림처럼, 1번 과 2번 과정은 DistributeTrain_PreTraining.py 파일에서 담당하고, 3번은 DistributeTrain_PostTraining.py 파일에서 담당하여 진행한다.

![image](https://user-images.githubusercontent.com/71695489/127614849-1e467900-9e48-443d-9880-0445cfd46e84.png)

<br/>
<br/>


#### 3) DistributeTrain_PreTraining.py

= DistributeTrain_PreTraining.py 프로그램은 크게 다음과 같은 방식으로 동작한다. 코드에 대한 자세한 설명은 주석을 참고 하는 것이 좋다.
  - http://lab.t3q.co.kr:9999/kaist-co-op/data-parallel-training-with-horovod/-/blob/master/horovod-kubernetes-resources/DistributeTrain_v1/DistributeTrain_ManagerImage/DistributeTrain_PreTraining.py

= 또한 여기서 쿠버네티스 리소스에 접근하고, 사용할 수 있는 Python Kubernetes 모듈을 사용하였다. 이에 대한 정보는 다음 URL 에서 찾아서 활용할 수 있다.
  - 공식 Github : https://github.com/kubernetes-client/python
    ( 여기서 Kubernetes -> Docs 항목에 필요한 필드 및 함수에 대한 설명이 들어있다. )

= 큰 틀의 main 함수는 다음과 같다.

![image](https://user-images.githubusercontent.com/71695489/127614864-ce37e42a-fbf2-4e9b-8cd2-b0e231494461.png)

1. Kubernetes Cluster 내부에서 현재 사용 가능한 모든 GPU 탐색. ( 쿠버네티스는 임의의 노드에 파드를 할당하기 때문에 각 노드의 개수만 내림차순으로 리스트로 저장한다. )

![image](https://user-images.githubusercontent.com/71695489/127614895-273e0e02-906b-4916-9c26-7b3a4b2a3956.png)

<br/>
<br/>


2. 사용 가능한 GPU list 목록 중에 적당한 Scheduling 방식을 사용하여 필요한 방식으로 분할하여 Worker Pod 를 생성한다.

= 아직 모든 부분이 구현되어 있지 않다. 요청 받은 GPU의 개수와, 현재 Kubernetes Cluster 에서 사용 가능한 GPU list ( Ex) [5, 3, 2] ) 를 고려했을 때, 실제로 적용 가능한 조합을 찾아서 available_cluster_gpus 에게 반환하는 임무를 수행한다.

= Ex ) 총 6개의 GPU 사용 요청을 받았을 때, 위에서 제공받은 GPU list 가 [5, 3, 2] 라면, table_allocate_gpus 에게 [5, 1] 을 반환한다.

= 중요한 것은! 최적화 Scheduling Algorithm 이 아직 구현되지 않았다. 실제로 수백 개의 GPU 를 사용하지 않을 것으로 예상되고, 스케줄링이 성능 차이에 크게 기여하지 않을 것이라고 생각하지만, 적어도 더 보완적인 Scheduling Algorithm 을 생각해 볼 필요가 있다고 본다!.

<br/>
<br/>


3. 앞에서 전달받은 List 정보를 토대로 Worker Pod 를 먼저 생성한다. Chief Worker Pod, 또는 Master Pod를 가장 마지막에 생성하는 이유는, 임의로 생성된 리소스의 정보를 조회한 후에, 관련 Config, myhostfile을 cheif worker pod에게 전달해야 하기 때문이다.

= 예를 들어, table_allocate_gpus = [5, 1] 을 전달받았다고 가정하면, 1개 노드에 5개, 남은 1개 노드에 1개의 GPU 를 할당해야 한다

= chief_worker_pod 는 마지막 가장 작은 요소 1을 가져가고( 다음 4번 과정 ),

= 나머지 모든 요소들을 가지고 Worker Pod를 생성한다. 즉, [5,1] 의 예시에서는 1개 노드에 5개 GPU를 사용하는 1개의 Worker Pod를 생성한다.

<br/>
<br/>


4. 마지막으로 남은 요소를 가지고, chief worker pod 를 생성한다.


#### 4) DistributeTrain_PostTraining.py

= Pseudo Code 는 다음과 같다.

![image](https://user-images.githubusercontent.com/71695489/127614924-6c82f3c9-0131-4f1c-8b9e-b6b348bc6b28.png)

1. 학습이 끝나면 Chief worker Pod는 Complete 상태로 대기한다. 따라서 Chief worker pod 가 "Complete” 상태가 되기까지 대기한다.

2. 위 조건을 충족하면 모든 Worker Pod Resource 를 반환한다.

<hr />
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>



# 3. 클러스터롤, 클러스터롤바인딩, 서비스 어카운트

= 기존의 컨테이너 외부에서 명령을 수행하는 Job resource와는 다르게 Manager Pod 는 컨테이너 내부에서 Kubernetes Cluster 리소스에 접근하고, 리소스를 수정할 수 있는 권한(Worker Pod를 컨테이너 내부에서 생성하기 위한 권한)이 필요하다.

#### 1) DistributeTrain_ClusterRole.yaml

![image](https://user-images.githubusercontent.com/71695489/127614941-8776d410-f5de-41dc-a856-086b3e327914.png)

  - 1번 항목을 보면, Pods 리소스에 대한 “create”, “list”, “delete”, “get” 명령에 대한 권한을 제공하고 있다. 실제로 Manager Pod 는 Worker Pod 들을 생성해야 하기 때문에 관련 권한을 제공해야 한다.

  - 또한 2번 항목을 보면, Node 리소스에 대한 “list”, “get” 명령을 허용하고 있다. Manager Pod 는 Kubernetes Cluster 의 각 Node GPU 현황에 대한 정보를 조회해야 하기 때문에 관련 권한을 제공해야 한다.
<br/>

#### 2) DistributeTrain_ServiceAccount.yaml

![image](https://user-images.githubusercontent.com/71695489/127614952-20879881-2a14-46d4-a330-1b5880873838.png)

  - 일반적으로 각 파드는 default ServiceAccount 를 기본 값으로 가진다. 기본적인 default 서비스 계정으로는 다른 파드를 생성하거나, 노드를 조회하는 권한을 획득할 수 없기 때문에 분산학습을 위한 새로운 Service Account (SA) 을 생성하고, 분산학습 Manager Pod 에 해당 계정을 추가한다.

  - DistributeTrain_Manager.yaml 파일에서 Manager Pod 에 대한 정보를 보면, 위의 distributetrain-serviceaccount 계정으로 Pod 를 생성하는 것을 확인할 수 있다.
<br/>

#### 3) DistributeTrain_ClusterRoleBinding.yaml

![image](https://user-images.githubusercontent.com/71695489/127614973-0c08ad8f-7188-4f4c-ace3-d8a339f85e2a.png)

- ClusterRoleBinding 리소스는 특정 ServiceAccount 에게 ClusterRole의 권한을 이어주는 역할을 한다. 위 사진의 distributetrain-clusterrolebinding 리소소는 다음의 역할을 한다.

1. distributetrain-serviceaccount 이름을 가진 ServiceAccount 에게,

2. distributetrain-clusterrole 의 권한을 binding 해준다는 것을 확인할 수 있다.


= 전체적으로 정리하자면, 위의 3가지 리소스를 생성하고, Manager Pod 에게 distributetrain-serviceaccount 계정을 제공하면, Manager Pod는  Pod 를 생성하고, Node 를 조회할 수 있는 권한을 가질 수 있다. 그리고 이 권한을 통해서 다른 Worker Pod를 생성하고, 관리한다. 아래 DistributeTrain_ManagerImage.yaml 양식에서 코드를 확인할 수 있다.

<br/><br/><br/>

# 4. DistributeTrain_Manager.yaml

![image](https://user-images.githubusercontent.com/71695489/127615073-8f3a8995-0060-4db9-98b8-d3f095ada7d5.png)

= 위에서 정의한 "distributetrain-manager" 파드를 생성하기 위한 파드 양식이다.

= 3번에서 생성한 서비스 어카운트를 할당받는다.

= 2번에서 생성한 이미지를 가지고, 필요한 인자들을 전달한다.
