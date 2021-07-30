###### @ 본문은 kubeflow v1.2.0 버전에 따라서 작성되었습니다. 기본적인 설명은 비슷하지만, 다른 버전은 차이가 있을 수 있습니다. @

-------------------------------------------------------------------------------------------------
# 1. Kubeflow 란 무엇인가?

자세한 설명은 다음 URL을 참조한다. ( https://v1-2-branch.kubeflow.org/docs/started/kubeflow-overview/ )

Kubeflow 는 다음과 같이 설명할 수 있다.

- Kubernetes의 ML toolkit.
- ML system 을 개발(developement) 및 배포(deployment) 하기 위한 플랫폼
  => 운영(management), 및 확장(scaling)이 가능.

![image](uploads/3d5362421245e1fb06861dde1dd7d600/image.png)
- 다음 그림을 보면 다양하게 존재하는 ML tools 및 Workflow tools 등을 kubeflow 리소스를 사용하여 kubernetes 환경 위에서 실행하고, 그 과정에서 쿠버네티스의 장점(스케일링, 실행 관리 등)을 활용 가능하다는 것을 알 수 있다.

- 조금 더 자세하게 설명하면, 머신러닝, 딥러닝을 위한 파이프라인을 구성하기 위해서는 기존의 일련의 작업 흐름 뿐만이 아니라, 각 단계를 수행하고, 그 과정에서 발생한 결괏값 등을 필요한 다음 단계의 입력값으로 구성하는 등의 추가적인 작업이 필요하다. 또한, 파라미터를 변경하면서 파이프라인을 지속적으로 실행하는 과정의 편의성 또한 제공할 필요가 있고, 각각의 결과를 편리하게 비교하고, 모니터링 할 수 있어야 한다. kubeflow 는 이런 과정에서 편의성을 제공한다.

- 또한, Kubeflow 는 주피터와의 연계로 주피터 상에서 자유로운 개발을 지원한다. Pipeline 기능을 통해서 개발한 모델을 파이프라인화 하도록 하며, 자체 대시보드를 통해서 각 파이프라인 실행 결과를 시각화하고 비교할 수 있도록 지원한다. 마지막으로 Katib 를 사용해서 HyperParameter Tuning 기능을 지원한다.

<br/>
<br/>
<br/>

# 2. Kubeflow 항목

![image](uploads/b5de8216465bfec79d01e8e24da8d617/image.png)<br/>

- 실제로 Kubeflow 자체도 여러 기능이 있는 리소스의 집합이라고 생각할 수 있다. 선호에 따라서 일부 모듈만 설치해서 사용하는 것도 가능하다. 우리는 이 중에서 실제로 Elyra 와 함께 사용하는 몇몇 기능에 대해서만 설명하고자 한다.

  [**Central Dashboard**](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/Kubeflow-pipeline-%EB%A6%AC%EC%86%8C%EC%8A%A4-%EB%B0%8F-Dashboard-UI-%EC%84%A4%EB%AA%85.#3-central-dashboard)<br/>

  [**Kubeflow Pipelines**](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/Kubeflow-pipeline-%EB%A6%AC%EC%86%8C%EC%8A%A4-%EB%B0%8F-Dashboard-UI-%EC%84%A4%EB%AA%85.#pipeline)<br/>

  [**Multi-Tenancy**](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/Kubeflow-%EB%A6%AC%EC%86%8C%EC%8A%A4-%EA%B2%A9%EB%A6%AC%EC%97%90-%EB%8C%80%ED%95%9C-%EC%9D%B4%ED%95%B4)<br/>

(이부분 다시 작성해야 한다.)

<br/>
<br/>
<br/>

# Central Dashboard

- 기본적으로 Kubeflow Dashboard 에서 확인할 수 있는 항목은 다음과 같다.

![image](uploads/f8f6af89213fea495a885d43eb6393a7/image.png)

- 여러 항목들이 있는데, 간단하게 설명하면 다음과 같다.<br/>

  1) Home - Dashboard 홈 화면
  2) Pipelines - Kubeflow 의 여러 항목중 Pipeline 기능을 위한 Dashboard
  3) Notebook Servers - Kubeflow Dashboard 상에서 주피터 이미지를 불러와 컨테이너 내부에서 개발할 수 있는 기능 지원.
  4) Katib - 개발된 모델을 다양한 파라미터를 통해서 Hyperparameter Tuning 하기 위한 기능을 위한 Dashboard
  5) Manage Contributors - Kubeflow Dashboard 를 namespace 별로 격리하여 Multi user 환경에서 개별 user의 접근 권한을 제어하기 위한 항목.

<br/>

- 우리는 여기서 **Pipelines 항목**과 **Manage Contributors 항목**을 주로 다룬다. 각각에 대한 설명은 다음 링크에서 확인하 수 있다.<br/>

  [Pipelines](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/Kubeflow-pipeline-%EB%A6%AC%EC%86%8C%EC%8A%A4-%EB%B0%8F-Dashboard-UI-%EC%84%A4%EB%AA%85.#pipeline)<br/>
  
  [Manage Contributors](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/Kubeflow-%EB%A6%AC%EC%86%8C%EC%8A%A4-%EA%B2%A9%EB%A6%AC%EC%97%90-%EB%8C%80%ED%95%9C-%EC%9D%B4%ED%95%B4).

<br/>
<br/>
<br/>

# Pipeline

![image](uploads/304bf943d3902de5b7e8e91fb9e1102a/image.png)

- **Kubeflow Pipeline** Dashboard 항목은 크게 다음과 같다.

  1) Pipelines - 실제로 가지고 있는 파이프라인에 대한 정보를 가지고 있다.
  2) Experiments - Workspace 라고 생각하면 된다. 실제 파이프라인 정보가 아니라, 파이프라인을 실행했을 때 각각의 실행 정보를 저장하는 작업 공강.
  3) Artifacts - 파이프라인의 모든 실행 과정에서 생성되는 파일 데이터를 artifacts 로 정의하고, 이곳에서 확인 가능.
  4) Executions - 실행 과정(run)에 대한 메타 정보를 이곳에서 확인 가능.
  5) Archive - (내용 추가하자)


### 1. pipelines

![image](https://user-images.githubusercontent.com/84768279/127106957-25065838-9c31-4577-809b-2f4f33c25585.png)

- Machine Learning Workflow (Ex) Argo Workflow)에서 사용하는 노드들과, 해당 노드들간의 작업 처리 규칙(Ex) 순서)을 그래프 형태로 정의하고, 개별 inputs 및 outputs에 대한 정의를 포함한 것. (여기서 파이프라인은 실제 입력 데이터에 대한 정보를 직접 보관하고 있지 않다. 해당 데이터의 위치 정보 등을 가졌다가 실제 run 시에 거기로부터 가져온다.)

- 일반적으로 파이프라인을 떠올렸을 때 떠오르는 일련의 작업 흐름을 실행하기 위해서 필요한 모든 데이터, 실행 코드, 중간 산물 및, 작업 흐름에 대한 정의를 포함한다. (실제 산물을 보유한 것이 아닌, 해당 산물의 형식, 경로 등에 대한 정보이다.)

- 다음과 같이 파이프라인 목록에서 현재 보유 중인 파이프라인의 항목을 조회할 수 있고, 새로운 파이프라인은 업로드할 수 있다.
![image](uploads/ee562fb3ce0035044cceba86a76543fb/image.png)

- 또한 파이프라인을 업로드하기 위해서는 파이프라인 정보에 대한 명세를 담은 yaml 파일 (Ex) Argo Workflow) 을 .yaml, .zip. .tar.gz 등의 형식으로 업로드해야 한다.<br />
![image](uploads/f89451870533527fd9fcc802d5626002/image.png)

- 이렇게 개별 파이프라인을 조회하면, 다음과 같이 그래프의 형태로 GUI 로 보여주거나, yaml 파일을 보여준다. 파이프라인의 구조에 대한 정보를 포함하기 때문에 실제 실행 후 이력(각각의 실행 결과, 동적으로 생성되는 정보)에 대한 정보는 없다. (run 에 있다.)<br />
![image](uploads/11e1e75b710e14a23241297f15d9192f/image.png)

![image](uploads/0de7c0640d70ed1e4ef3bba61a53d7f4/image.png)

<br/>
<br/>
<br/>

# Experiment
![image](https://user-images.githubusercontent.com/84768279/127107157-eb3fce07-2668-411d-a4af-e1b982ee80ae.png)

- 다양한 파이프라인을 실행할 수 있는 작업공간.

- 개별적인 파이프라인을 한번 한번 실행한 이력에 대한 메타데이터의 정보를 run 인스턴스로 저장한다고 했을 때, 이러한 run 인스턴스의 그룹이다.

- 아래 그림에서 Experiment 목록에서 하나를 선택해 들어가 보면,

![image](https://user-images.githubusercontent.com/84768279/127107848-7f77e9a5-e802-4929-9baf-9db94d1e683e.png)

- 각종 파이프라인에 대한 개별 실행 이력 (run) 의 목록을 확인할 수 있다.

![image](uploads/2a0afdb4da946a07f9e3b05204123ad7/image.png)

- 그리고 run 항목을 보면,

![image](uploads/e9cc2237b5e96c3f96a2a85fab2347a9/image.png)

- 다음과 같이 각 실행에서 생성된 각 노드의 로그, input, output 데이터들을 조회할 수 있다.

<br/>
<br/>
<br/>

# Artifacts

 - Kubeflow 는 각 노드에 필요한 데이터를 크게 2종류로 분류하고 있다. 1) parameters, 2) arguments.
 - 이 중에서 용량이 크고, 파일 형식으로 된 것을을 artifacts 로 만들어서 저장한다.
 - 모든 run 에서 사용된 artifacts 들을 여기에 항목으로 나열하고 있다.

![image](uploads/383bfa2536d7f480a75a52d2d17e6572/image.png)<br/>

- 해당 URI 에 들어가 보면 개별 run 에서 생성되거나, 활용했던 artifacts 데이터를 다운받아 보거나, 개별 artifacts 를 클릭하여 상세 정보를 확인할 수 있다.

<br/>
<br/>
<br/>

# Executions

 - 모든 run 의 실행 메타데이터 정보 목록을 항목으로 나열하고 있다.
 
 - 별도로 중요한 정보는 없다.

<br/>
<br/>
<br/>

# Archive
 
 - 생성된 run 및 experiments 에 대한 정보를 archive 로 옮겨서 보관할 수 있다.

 - 별도로 중요한 정보는 없다.