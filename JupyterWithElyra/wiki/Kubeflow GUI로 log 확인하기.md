**@ 이 문서는 Kubeflow v1.2.0 버전을 활용하여 작성한 코드에 대한 문서입니다. 다른 버전의 경우 오류가 발생할 수 있습니다.**

# 1. Kubeflow 의 Log 관리 및 활용.

- Kubeflow 는 다음과 같이 개별 파이프라인의 각각의 실행 결과(run) 에 대한 메타데이터 정보의 일부로 Log를 활용하고, 각 단계별로 실행된 컨테이너의 Log를 다음과 같이 출력한다.

![image](https://user-images.githubusercontent.com/71695489/127608056-ccd24c07-2998-48f8-89d1-4f285171b25e.png)

- 위 사진은 **Preprocessing.py** 의 스크립트를 실행하는 컨테이너의 로그에 대한 출력이다. 그러나 이 것은 실제로 preprocessing.py 에 대한 로그가 아니다. 자세한 것은 이후에 설명한다.

- 자세하게 보면, 일반적인 Info 및 Debug 수준의 로그 및 STDOUT에 대한 출력은 평범하게 출력되는 것을 확인할 수 있다.

- Warning 수준의 로그는 **노랑 배경색**으로 칠한 뒤 출력하는 것을 확인할 수 있다.

- 마찬가지로 Error 수준의 로그는 **빨강 배경색**으로 칠한 뒤 출력한다.

- 따라서 우리는 파이프라인의 각 단계별 컨테이너 실행에 대한 로그 정보를 확인 및 추적이 가능하다.

<br/>
<br/>
<br/>
<br/>
<br/>

# 2. Elyra 의 Log 관리 및 활용.

- 앞에서도 설명했지만, Elyra는 자체적으로 컨테이너 내부에서 파이프라인의 각 단계를 직접 실행하는 구조를 채택하지 않고, 조금 다른 방식을 활용하고 있다. 이에 대한 설명으로는 다음과 같다.
<br/>

#### 1) 먼저, Elyra 파이프라인을 Kubeflow runtime 에서 실행했을 때 실행된 파드를 조회(describe)해 보면, 다음과 같다.<br/>
  (실행된 파드의 컨테이너 생성란에 대한 정보...)<br/>
![image](https://user-images.githubusercontent.com/71695489/127608104-94613dd9-e4b7-445f-80bf-cabf875debf1.png)

  명령어를 정리해보면 다음과 같다.

  - `$ mkdir -p ./jupyter-work-dir/`

  - `$ cd ./jupyter-work-dir/`

  - `$ curl -H "Cache-Control: no-cache" -L https://raw.githubusercontent.com/elyra-ai/kfp-notebook/master/etc/docker-scripts/bootstrapper.py --output bootstrapper.py`

  - `$ curl -H "Cache-Control: no-cache" -L https://raw.githubusercontent.com/elyra-ai/kfp-notebook/v0.23.0/etc/requirements-elyra.txt --output requirements-elyra.txt`

  - `$ python3 -m pip install  packaging`

  - `$ python3 -m pip freeze > requirements-current.txt`

  - $ **python3 bootstrapper.py** `--cos-endpoint http://10.152.183.244:9000 --cos-bucket t3qflow-demo-storage --cos-directory "cifar10-0722091616" --cos-dependencies-archive "preprocessing-f7e8deca-c84c-4dd2-92eb-0754475fc70b.tar.gz" --file "t3qmember/JupyterLab/seeyeon_tutor/kubeflow_elyra_project/`**preprocessing.py**" `--outputs "dataset.zip"`

---

<br/>
<br/>

(위의 마지막 명령어를 잘 보면...)
#### 2) Elyra KFP runtime을 실행했을 때, 실제로 컨테이너에서 실행되어야 할 **preprocessing.py**가 실행되지 않고, **bootstrapper.py**를 실행하는 것을 확인할 수 있다.

- 실제로 Elyra 는 각 단계별로 별도의 코드 수정 없이 컨테이너 내부에서 코드를 실행할 수 있도록 기능을 지원하기 위해서 필요한 백엔드 기능들을 bootstrapper.py 스크립트로 작성해 놓고, 파이썬의 subprocess.run 함수를 사용해서 bootstrapper.py 스크립트 내부에서 실제 preprocessing.py 를 실행하도록 구조를 디자인해놓았다. 전체적인 과정은 다음과 같다. [bootstrapper.py 코드 보기](https://raw.githubusercontent.com/elyra-ai/kfp-notebook/master/etc/docker-scripts/bootstrapper.py)

![image](https://user-images.githubusercontent.com/71695489/127608177-31dda8ef-601e-4b36-b80f-61edd719d4f0.png)

  **1.** bootstrapper.py 가 컨테이너 내부에서 먼저 실행됨.

  **2.** bootstrapper.py 는 **package_install** 함수를 통해서 아직 install 하지 못했던 Elyra 필수 모듈들을 설치. (pip install)

  **3.** bootstrapper.py 는 **process_dependencies** 함수를 통해서 각 단계별로 필요한 input artifacts 및 파라미터들을 minio에서 현재 컨테이너로 다운로드 받는다. (이렇게 되면 **별도의 코드 수정 없이 컨테이너에서도 로컬에서와 동일하게 같은 경로에서 파일을 읽어와서 실행 가능**.)

  **4.** bootstrapper.py 는 execute 함수 내부에 있는 **subprocess 묘듈의 subprocess.run** 함수를 사용해서 preprocess.py 스크립트를 실행하고, 이때 발생한 로그에 대한 정보를 .log 파일로 저장한다.

  **5.** 마지막으로 bootstrapper.py 는 preprocess.py 를 실행하고 발생한 결과와 .log 파일을 **process_metrics_and_metadata** 함수를 통해서 다시 minio 로 저장한다.

---

<br/>
<br/>
<br/>
<br/>
<br/>

# 3. T3QDemoElyraProcessor 의 Log 관리 및 활용 방안 정리.

##### 위의 [1. Kubeflow 의 Log 관리](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/8_1.-Kubeflow-GUI와%EB%A1%9C-log-%ED%99%95%EC%9D%B8%ED%95%98%EA%B8%B0#1-kubeflow-%EC%9D%98-log-%EA%B4%80%EB%A6%AC-%EB%B0%8F-%ED%99%9C%EC%9A%A9) 와 [2. Elyra 의 Log 관리 및 활용](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/8_1.-Kubeflow-GUI%EB%A1%9C-log-%ED%99%95%EC%9D%B8%ED%95%98%EA%B8%B0#2-elyra-%EC%9D%98-log-%EA%B4%80%EB%A6%AC-%EB%B0%8F-%ED%99%9C%EC%9A%A9) 을 고려했을때 우리는 다음과 같은 사실을 확인할 수 있다.

- 기존의 Elyra KFP runtime 을 사용하여 실행했을 때, 우리는 실제로 실행하는 스크립트의 Log 가 아니라 bootstrapper.py 의 로그가 출력 되는 이유를 이제 알 수 있다. 실제로 컨테이너 내부에서 메인으로 돌아가는 스크립트는 preprocess.py 가 아닌 bootstrapper.py 인 것이다.

- 따라서 우리는 preprocess.py 의 로그를 출력하기 위해서 bootstrapper.py 의 코드를 일부 수정할 필요가 있다. 기존의 bootstrapper.py 는 subprocess.run 함수를 통해 실행한 결과를 .log 파일로 저장하고, 이를 minio 에 저장한 채로 끝내지만, 우리는 여기에 덧붙여서 **컨테이너의 STDOUT에 preprocess.py 에 대한 로그를 함께 출력하도록 해야 실제 kubeflow pipeline dashboard UI 에 출력된다는 사실을 유추할 수 있다.**

- 실제로 아래에서 수정한 **custom-processor.py** 의 일부 코드를 보면, 출력 결과를 log_file 에 저장하고, logger.info 수준으로 다시 표준 출력하는 것을 확인할 수 있다.<br/>
![image](https://user-images.githubusercontent.com/71695489/127608235-ef60e572-3289-4369-861f-3f6a796a182d.png)

- 이렇게 코드를 수정했을 때, 실제 kubeflow pipeline dashboard UI 에서는 다음과 같이 기존 스크립트의 결과가 추가되어 나타나는 것을 확인할 수 있다.<br/>
![image](https://user-images.githubusercontent.com/71695489/127608293-32728060-f322-4d2b-925f-3643b04d0cb1.png)
