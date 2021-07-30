- Jupyter 및 Elyra 를 사용하여 동적으로 Pipeline을 구성하고 학습을 진행할 수 있다.
- Elyra 는 다양한 런타임 (kubeflow, Airflow, custom runtimes)에 대해서 파이프라인을 별도의 runtime 위에서 실행할 수 있도록 지원하고 있다.
- 그러나 학습한 모델을 활용하기 위해서는 운영 환경에 올려서 추론 단계를 실시해야 한다.

- Jupyter 및 Elyra 를 활용하여 모델을 개발하고, Kubeflow 의 runtime 에서 pipeline 을 실행할 수 있도록 자동화 한 다음, KFserving 을 사용하여 추론을 돌리는 것을 목표로 하였으나,

- KFserving 을 활용하기 위해서 추론 단계를 custom 하거나, TF serving 또는 다른 Serving 리소스를 활용하고 있다. 따라서 운영 환경을 파악하기 위해서 TFserving 을 활용하여 기존의 Tensorflow 로 학습했던 MNIST 데이터를 운영 환경에 올려보았다.

## TF serving 실행 순서.

#### 필요한 항목
1. 도커 이미지를 통해 서버를 실행하기 위해서 도커 이미지를 다운 받는다.
  $ sudo docker pull tensorflow/serving      또는
  $ sudo docker pull tensorflow/serving:latest-gpu

2. 다양한 딥러닝 Framwork 에서 개발한 학습된 모델 (.h5 또는 .pb 파일)



#### 순서
##### 1. 모델을 추론 서버에 올리기 위한 목적으로 저장해야 한다.

- Tensorflow 에서는 추론을 위한 모델 저장에 대한 메서드를 정의하고 있다.  : tf.keras.models.save_model()

![image](uploads/f12444366d7471ad2436175cd09d8256/image.png)

- 위와 같이 모델을 저장하고, 이후에 여기서 저장한 export_path 경로를 통해서 모델을 불러온다.

##### 2. tensorflow/serving docker image 를 사용하여 학습한 모델에 대한 추론 서비스를 생성한다.

$ sudo docker run \
-t \<br/>
--rm \                    -> 도커 명령어 옵션, 컨테이너를 종료시 삭제한다.<br/>
-p 8501:8501 \            -> 도커 명령어 옵션, 로컬의 8501번 포트를 컨테이너의 8501번 포트로 포워딩.<br/>
-v "/tmp/1:/models/saved_model/1" \        -> "모델이 있는 위치 경로:REST API 경로"<br/>
-e MODEL_NAME=saved_model \                -> 모델의 이름<br/>
tensorflow/serving &



##### 3. 모델을 포함한 추론 서버를 열었기 때문에, 서버에 입력 데이터를 주고 결괏값을 받아와야 한다. TF serving 에서는 별도로 추론에 대한 전처리 과정을 포함하고 있지 않기 때문에, 필요하다면 추론 입력 데이터에 대해서 전처리를 한 후 추론 서버에 Request 를 보내야 한다.

- 코드는 다음과 같다.
![image](uploads/01fb0a5b065096a4a36cd1bbfb003ce7/image.png)

- 코드를 실행하면, 다음과 같은 결과를 확인할 수 있다.
![Screenshot_from_2021-07-01_14-07-32](uploads/ae8ec5ed571a014ce96b1f3fe20cf93c/Screenshot_from_2021-07-01_14-07-32.png)

