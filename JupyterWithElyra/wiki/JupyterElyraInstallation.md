# 1. Install Jupyter Lab

- 공식 홈페이지의 설치 가이드를 참고한다.
( URL - https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html )

![image](https://user-images.githubusercontent.com/71695489/127601597-65818686-fcbb-4f36-baab-7c589023dcc9.png)<br/>
- 콘다 환경에서는 다음 명령어를 통해 설치한다. ` $ conda install -c conda-forge jupyterlab `

![image](https://user-images.githubusercontent.com/71695489/127601630-c7b5d0e0-138b-4ff5-810d-74f0733f3e89.png)<br/>
- pip 를 사용하는 경우에도 간단하게 다음 명령어를 통해서 설치한다. pip 또는 pip3 를 사용한다.` $ pip install jupyterlab `

<br/>
<br/>
<br/>

# 2. Install Elyra

- 공식 홈페이지의 설치 가이드를 참고한다.
( URL - https://elyra.readthedocs.io/en/latest/getting_started/installation.html )

### 1. 다음 툴들이 설치 되어있는지 확인한다.
- [Node.js 12+](https://nodejs.org/en/)
  다음처럼 ` $node -v ` 명령어를 통해 설치 여부 및 버전 확인 가능<br/>
![image](https://user-images.githubusercontent.com/71695489/127601673-1d7d91c9-63ee-46da-a253-b2e49af53921.png)

- [Python 3.x](https://www.python.org/downloads/)
  ` $ python --version ` 또는 ` $ python3 --version ` 명령어를 통해서 설치 여부 및 버전 확인 가능<br/>
![image](https://user-images.githubusercontent.com/71695489/127601727-4a1a8282-003c-42d6-972e-4fc8550e70b6.png)

### 2. 설치 자체는 간단하다.

![image](https://user-images.githubusercontent.com/71695489/127601763-095dbaec-e3ad-48d7-b9ef-bc7647847e38.png)<br/>
- 콘다 환경에서는 다음 명령어를 통해 설치한다. ` $ conda install -c conda-forge elyra `

![image](https://user-images.githubusercontent.com/71695489/127601851-1c610586-7bed-46b7-961f-0af9e32fa3eb.png)
- pip를 사용하는 경우에도 간단하게 다음 명령어를 통해서 설치한다. pip 또는 pip3 를 사용한다. ` $ pip3 install --upgrade elyra `

### 3. 설치 이슈 문제 해결

- 설치 자체는 명령어만 따라서 입력하면 잘 설치되지만, 그대로 설치해도 잘 동작하지 않는 경우가 많다. 다음 2가지를 먼저 확인해야 한다.

  [1. 주피터 serverextension 설치 여부 확인](https://elyra.readthedocs.io/en/latest/getting_started/installation.html#verify-the-server-extensions)

  [2. 주피터 labextension 설치 여부 확인](https://elyra.readthedocs.io/en/latest/getting_started/installation.html#verify-the-lab-extensions)

- 위의 2가지 extension들을 아래의 3가지 명령어를 통해 잘 설치되었는지 확인할 수 있다. 
- 각 명령어를 실행한 뒤, 아래의 리스트와 비교하여 각각의 목록들이 잘 enabled 되어 있는지 확인하고, 되어있지 않다면 다음 명령어를 통해서 enable 시켜 준다.<br/>
` $ jupyter server extension enable <extension_name> `

  1. ` $ jupyter server extension list `<br/>
아래의 목록들이 enabled 되어있는지 확인한다.<br/>
![image](https://user-images.githubusercontent.com/71695489/127601894-d7609fe2-120e-478d-bd38-b746d1da7a23.png)

  2. ` $ jupyter serverextension list `<br/>
아래의 목록들이 enabled 되어있는지 확인한다.<br/>
![image](https://user-images.githubusercontent.com/71695489/127601924-3671ed60-d220-49c6-ab06-c99ff97e863b.png)

  3. ` $ jupyter labextension list `<br/>
아래의 목록들이 enabled 되어있는지 확인한다.<br/>
![image](https://user-images.githubusercontent.com/71695489/127601964-99553963-aca3-43ca-8417-6beab7135133.png)

<br/>
<br/>
<br/>

# (+3. Install kubeflow)

- Kubeflow 설치하는 과정은 다음 자료를 참고한다. [6. Kubeflow 설치 과정 및 issues 정리.](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/Kubeflow-%EC%84%A4%EC%B9%98-%EA%B3%BC%EC%A0%95-%EB%B0%8F-issues-%EC%A0%95%EB%A6%AC.)
