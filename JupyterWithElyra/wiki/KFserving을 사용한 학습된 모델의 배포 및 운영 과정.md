## KFserving 을 사용한 학습된 모델의 배포 및 운영 과정

#### Base Tutorial
맨 처음 KFserving 의 동작을 파악하기 위해서 다음 Tutorial 을 진행한다.

kfserving tensorflow 기본 튜토리얼.<br/>
( https://github.com/kubeflow/kfserving/tree/master/docs/samples/v1alpha2/tensorflow )

- 위 튜토리얼을 그대로 진행하면 minio 저장소에 접근하기 위한 관련 인증 문제가 발생한다. session cookie 를 인자 옵션에 추가해야 한다. 다음 URL에서 관련 내용을 참조한다.<br/>
( https://github.com/kubeflow/kfserving/tree/master/docs/samples/istio-dex )

- 관련 내용을 다시 설명하자면 다음과 같다.

![image](https://user-images.githubusercontent.com/71695489/127602098-c72a94e5-e892-4edf-ae60-be7b6991e7a7.png)

1. Minio URL 에 접근해서 위를 보면, not secure 경고와 함께 다음 란이 보이는 것을 확인할 수 있다.

![image](https://user-images.githubusercontent.com/71695489/127602132-97afe83c-ff76-436d-b2aa-3ca3c6d677f9.png)

2. 클릭하면 보이는 여러 cookies 들 중에 authservice_session 을 선택하고, Content 항목에 있는 내용을 복사한다.

![image](https://user-images.githubusercontent.com/71695489/127602176-a8ba597e-2143-4887-b0c0-6bb9e406db15.png)

3. 복사한 내용을 SESSION 쉘 변수로 추가하여 사용한다.
  SESSION = CONTENTS

따라서, 기존 튜토리얼의 다음 방법은 이렇게 변경하여 사용한다.

다음 URL에는 아래와 같은 step 이 있다.
( https://github.com/kubeflow/kfserving/tree/master/docs/samples/v1alpha2/tensorflow )

![image](https://user-images.githubusercontent.com/71695489/127603694-e3c77117-ef7f-4894-b8dc-c32f73ae9081.png)

위의 방법을 아래와 같이 변경해서 진행한다.
여기서 INGRESS_HOST 와 INGRESS_PORT 는 Kubeflow Dashboard 에 접근하기 위한 Endpoint 와 Port 이다.

![image](https://user-images.githubusercontent.com/71695489/127603733-63364d50-8c1f-4c9c-bb1d-cd0e0c88d91b.png)

<br/>
<br/>
<br/>
<br/>
<br/>
<br/>

#### Minio S3 storage 를 사용한 튜토리얼.

- Jupyter Lab + Elyra 를 사용하고 Kubeflow runtime 에서 모델 개발을 완료하면, 학습이 완료된 모델은 Minio S3 Cloud Storage 에 저장된다.
- 따라서 다음 Tutorial을 우선시하여 Minio S3 cloud storage 에 저장되어 있는 모델을 서빙하기 위한 tutorial 을 진행한다.



- 현재 다음과 같은 이슈가 발생해서 storage initializer image 의 버전을 v0.4.1 을 v0.4.0 으로 롤백해주어야 한다.<br/>
( https://github.com/kubeflow/kfserving/issues/1246 )
