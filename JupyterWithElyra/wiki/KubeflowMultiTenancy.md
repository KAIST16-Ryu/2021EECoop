**@ 이 문서는 Kubeflow v1.2.0 버전을 기준으로 작성되었습니다. 다른 버전의 경우 차이가 있을 수 있습니다.**

#### Kuberflow 의 Multi User 환경 지원 기능. (Kubeflow 기존 v1.2.0 이상에서 multi-user isolation 기능 지원.)

Kubeflow 에서는 **Multi-Tenancy** 라고 불리는 다중 사용자를 위한 일부 리소스(Experiments)의 격리 기능을 제공한다. 실제로 대부분의 상황에서 머신러닝, 딥러닝의 개발을 혼자 하지 않기 때문에 이런 기능은 꼭 필요하다. 그러나 현재 Kubeflow의 개발 의도가 다르거나, 아직 개발이 완료된 플랫폼이 아닌 등의 문제점이 있어서 **현재 일부 불편함 및 문제점**이 있는 상황이다.<br/>
![image](uploads/f602ca68aa8c0f07fec4ab973277eef9/image.png)

## 1. Kubeflow의 리소스 격리에 대한 이해<br/>

<Kubeflow 공식 문서><br/>
[Introduction to Multi-user Isolation.](https://v1-2-branch.kubeflow.org/docs/components/multi-tenancy/overview/)<br/>

[Design for Multi-user Isolation.](https://v1-2-branch.kubeflow.org/docs/components/multi-tenancy/design/)<br/>

[Getting Started with Multi-user Isolation.](https://v1-2-branch.kubeflow.org/docs/components/multi-tenancy/getting-started/)<br/>
**@ 이 문서는 Kubeflow v1.2.0 버전을 기준으로 작성되었습니다. 다른 버전의 경우 차이가 있을 수 있습니다.**

#### Kuberflow 의 Multi User 환경 지원 기능. (Kubeflow 기존 v1.2.0 이상에서 multi-user isolation 기능 지원.)

Kubeflow 에서는 **Multi-Tenancy** 라고 불리는 다중 사용자를 위한 일부 리소스(Experiments)의 격리 기능을 제공한다. 실제로 대부분의 상황에서 머신러닝, 딥러닝의 개발을 혼자 하지 않기 때문에 이런 기능은 꼭 필요하다. 그러나 현재 Kubeflow의 개발 의도가 다르거나, 아직 개발이 완료된 플랫폼이 아닌 등의 문제점이 있어서 **현재 일부 불편함 및 문제점**이 있는 상황이다.<br/>
![image](https://user-images.githubusercontent.com/71695489/127605339-91052b49-6120-44d8-9c8d-920a3577ceeb.png)

## 1. Kubeflow의 리소스 격리에 대한 이해<br/>

<Kubeflow 공식 문서><br/>
[Introduction to Multi-user Isolation.](https://v1-2-branch.kubeflow.org/docs/components/multi-tenancy/overview/)<br/>

[Design for Multi-user Isolation.](https://v1-2-branch.kubeflow.org/docs/components/multi-tenancy/design/)<br/>

[Getting Started with Multi-user Isolation.](https://v1-2-branch.kubeflow.org/docs/components/multi-tenancy/getting-started/)<br/>

- Kubeflow Dashboard 및 Kubeflow Pipeline Dashboard 는 다수의 사용자가 **일부 리소스**(Experiments)를 서로로부터 격리할 수 기능을 지원하고 있다. 그러나 현재 리소스 격리 관련한 기능이 Stable 하게 개발되어 있는 상황은 아니기 때문에 아직 부족한 부분이 존재한다. Ex) 아직 사용자 별로 격리 되지 않는 리소스(Pipelines 는 클러스터 단위로 공유됨.)가 존재하는 문제, 일부 리소스는 대시보드 UI 상에서 수정이 불가 능한 문제(Experiments, Artifacts) 등.

- On-premises ( = 클라우드 상에서 Kubernetes Cluster 를 구축하는 것이 아닌, 서버실 등에 서버를 두고 Cluster 를 구축하여 직접 관리하는 방식) 의 경우, Kubeflow 는 다수의 사용자를 위한 리소스 격리를 위해서 **Dex 등의 통합 OpenID 연결 서비스**등을 함께 사용한다. (현재 문서의 Kubeflow 설치 방식에 따르면, Dex를 함께 설치한다.). 그러나 이러한 경우 Dex 와의 연동에 대한 다양한 인터페이스를 제공하고 있지 않아 각각의 계정에 각기 다른 RBAC 권한을 인가하거나, 특정 리소스를 보고, 수정하는 등의 세밀한 관리가 어렵다.

- 리소스 격리와 관련된 주요 개념으로는 **Administrator, User, Profile** 등이 있다.
  1) Administrator - 쿠버네티스 클러스터에 대한 대표 권한을 보유한 등록자. 리소스에 대한 권한을 다른 User에게 인가 가능.
  2) User - 클러스터의 일부 리소스 그룹에 접근하는 사용자. Administrator로부터 권한을 인가 받아야 한다.
  3) Profile - User 가 소유한 리소스 그룹 Kubernetes의 하나의 namespace와 대응되며, 하나의 계정 별로 하나의 Profile을 소유한다.<br/><br/>

- 구글 클라우드 환경에서 계정을 추가, 삭제 및 변경하거나, 리소스 격리 관련 내용을 추가하고자 한다면 다음 문서를 참고하면 된다.<br/>

  [Getting Started with Multi-user Isolation.](https://v1-2-branch.kubeflow.org/docs/components/multi-tenancy/getting-started/)<br/>


<br/>

## 2. Design for Multi-user Isolation for On-premise & Dex environment.

- Dex와 연동해서 사용하는 On-premise 환경의 경우에는 다음의 방법에 따라서 다수의 사용자들을 격리하는 환경을 제공한다.<br/>

다음의 사이트를 참고한다.<br/>
1. [ Dex를 사용한 격리 방안 공식 문서 ](https://v0-7.kubeflow.org/docs/started/k8s/kfctl-existing-arrikto/#add-static-users-for-basic-auth)<br/>
2. [ Dex를 사용한 격리 방안 블로그 글 ](https://wjddyd66.github.io/kubeflow/Kubeflow(4-2)/)<br/>

다음의 영상을 따라서 진행해도 좋다.<br/>
- [ Dex를 사용한 계정 생성 튜토리얼 Youtube ](https://www.youtube.com/watch?v=AjNbcMGl8Y4)<br/>

전체적으로 글 및 영상이 잘 정리되어 있어 이를 활용하여 생성하면 다음과 같이 Profile 및 계정이 만들어지는 것을 확인할 수 있다.<br/>
![image](https://user-images.githubusercontent.com/71695489/127605362-b5496187-c64e-48d1-bc9c-aea57d15db53.png)<br/>

![image](https://user-images.githubusercontent.com/71695489/127605444-d7b80de8-0373-4f28-8794-ac38015884d2.png)

<br/>
<br/>
<br/>
<br/>
<br/>
<br/>

## 3. 현재 Kubeflow 의 리소스 격리의 한계 및 문제점

- 위에서 언급했듯이, Kubeflow 에서 다수의 사용자에게 모든 리소스를 격리할 수 있는 방법을 제공하고 있지 않다. 예를 들어, Kubeflow 의 Experiments 리소스는 사용자 별로 별로의 격리 방법을 제공하고 있지만, Pipeline은 격리 방법을 제공하고 있지 않기 때문에, 같은 클러스터를 사용하는 사용자라면 다른 사용자가 작성한 Pipeline을 보거나, 수정 및 삭제가 가능하다. 이는 불편한 점이 많다.<br/>
![image](https://user-images.githubusercontent.com/71695489/127605482-bbb7ad28-5623-47bf-832b-018cf56bebe6.png)

- UI 상으로도 격리가 안되는 상황이기 때문에, 실제로 악의적인 접근의 사용자를 방어하기 위한 보안 관리도 아직 잘 되어있지 않은 상황이다.

- 물론 프로젝트 별로 클러스터를 할당 받아 사용하거나, 하나의 프로젝트로 하나의 클러스터만을 사용하는 환경에서는 크게 문제 될 것이 없다.

<br/>
<br/>
<br/>

이를 해결하기 위한 해결 방안으로는 다음과 같다.

1. 프로젝트 별로 사용자에게 별도의 클러스터 환경을 제공할 수 있는 방안 마련. (클러스터 수준의 격리)

2. 컨트롤 플레인 수준의 격리 수단 제공 (가상 클러스터 개념의 격리)

3. Pipeline을 격리할 수 있는 보안 체계를 마련하여, Kubeflow 리소스를 수정.

<br/>
<br/>
<br/>

관련하여 현재 작업을 진행하고 있는 사이트들이 있어서 링크를 추가한다.

https://github.com/argoflow<br/>
![image](https://user-images.githubusercontent.com/71695489/127605513-b2f87251-f765-49b4-a19d-93b172d2cd75.png)<br/>

- Kubeflow Dashboard 및 Kubeflow Pipeline Dashboard 는 다수의 사용자가 **일부 리소스**(Experiments)를 서로로부터 격리할 수 기능을 지원하고 있다. 그러나 현재 리소스 격리 관련한 기능이 Stable 하게 개발되어 있는 상황은 아니기 때문에 아직 부족한 부분이 존재한다. Ex) 아직 사용자 별로 격리 되지 않는 리소스(Pipelines 는 클러스터 단위로 공유됨.)가 존재하는 문제, 일부 리소스는 대시보드 UI 상에서 수정이 불가 능한 문제(Experiments, Artifacts) 등.

- On-premises ( = 클라우드 상에서 Kubernetes Cluster 를 구축하는 것이 아닌, 서버실 등에 서버를 두고 Cluster 를 구축하여 직접 관리하는 방식) 의 경우, Kubeflow 는 다수의 사용자를 위한 리소스 격리를 위해서 **Dex 등의 통합 OpenID 연결 서비스**등을 함께 사용한다. (현재 문서의 Kubeflow 설치 방식에 따르면, Dex를 함께 설치한다.). 그러나 이러한 경우 Dex 와의 연동에 대한 다양한 인터페이스를 제공하고 있지 않아 각각의 계정에 각기 다른 RBAC 권한을 인가하거나, 특정 리소스를 보고, 수정하는 등의 세밀한 관리가 어렵다.

- 리소스 격리와 관련된 주요 개념으로는 **Administrator, User, Profile** 등이 있다.
  1) Administrator - 쿠버네티스 클러스터에 대한 대표 권한을 보유한 등록자. 리소스에 대한 권한을 다른 User에게 인가 가능.
  2) User - 클러스터의 일부 리소스 그룹에 접근하는 사용자. Administrator로부터 권한을 인가 받아야 한다.
  3) Profile - User 가 소유한 리소스 그룹 Kubernetes의 하나의 namespace와 대응되며, 하나의 계정 별로 하나의 Profile을 소유한다.<br/><br/>

- 구글 클라우드 환경에서 계정을 추가, 삭제 및 변경하거나, 리소스 격리 관련 내용을 추가하고자 한다면 다음 문서를 참고하면 된다.<br/>

  [Getting Started with Multi-user Isolation.](https://v1-2-branch.kubeflow.org/docs/components/multi-tenancy/getting-started/)<br/>


<br/>

## 2. Design for Multi-user Isolation for On-premise & Dex environment.

- Dex와 연동해서 사용하는 On-premise 환경의 경우에는 다음의 방법에 따라서 다수의 사용자들을 격리하는 환경을 제공한다.<br/>

다음의 사이트를 참고한다.<br/>
1. [ Dex를 사용한 격리 방안 공식 문서 ](https://v0-7.kubeflow.org/docs/started/k8s/kfctl-existing-arrikto/#add-static-users-for-basic-auth)<br/>
2. [ Dex를 사용한 격리 방안 블로그 글 ](https://wjddyd66.github.io/kubeflow/Kubeflow(4-2)/)<br/>

다음의 영상을 따라서 진행해도 좋다.<br/>
- [ Dex를 사용한 계정 생성 튜토리얼 Youtube ](https://www.youtube.com/watch?v=AjNbcMGl8Y4)<br/>

전체적으로 글 및 영상이 잘 정리되어 있어 이를 활용하여 생성하면 다음과 같이 Profile 및 계정이 만들어지는 것을 확인할 수 있다.<br/>
![image](uploads/e9429ae76004c92a4bc714b2e4c5a929/image.png)<br/>

![image](uploads/912c58f4c8dc65f338171308c782d679/image.png)

<br/>
<br/>
<br/>
<br/>
<br/>
<br/>

## 3. 현재 Kubeflow 의 리소스 격리의 한계 및 문제점

- 위에서 언급했듯이, Kubeflow 에서 다수의 사용자에게 모든 리소스를 격리할 수 있는 방법을 제공하고 있지 않다. 예를 들어, Kubeflow 의 Experiments 리소스는 사용자 별로 별로의 격리 방법을 제공하고 있지만, Pipeline은 격리 방법을 제공하고 있지 않기 때문에, 같은 클러스터를 사용하는 사용자라면 다른 사용자가 작성한 Pipeline을 보거나, 수정 및 삭제가 가능하다. 이는 불편한 점이 많다.<br/>
![image](uploads/e55925afcd8e2fe15897fce25a2518ad/image.png)

- UI 상으로도 격리가 안되는 상황이기 때문에, 실제로 악의적인 접근의 사용자를 방어하기 위한 보안 관리도 아직 잘 되어있지 않은 상황이다.

- 물론 프로젝트 별로 클러스터를 할당 받아 사용하거나, 하나의 프로젝트로 하나의 클러스터만을 사용하는 환경에서는 크게 문제 될 것이 없다.

<br/>
<br/>
<br/>

이를 해결하기 위한 해결 방안으로는 다음과 같다.

1. 프로젝트 별로 사용자에게 별도의 클러스터 환경을 제공할 수 있는 방안 마련. (클러스터 수준의 격리)

2. 컨트롤 플레인 수준의 격리 수단 제공 (가상 클러스터 개념의 격리)

3. Pipeline을 격리할 수 있는 보안 체계를 마련하여, Kubeflow 리소스를 수정.

<br/>
<br/>
<br/>

관련하여 현재 작업을 진행하고 있는 사이트들이 있어서 링크를 추가한다.

https://github.com/argoflow<br/>
![image](uploads/d3cb152bad1a899f5cc5688d4a5af9ea/image.png)<br/>
