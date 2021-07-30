# 1. Install Jupyter Lab

- 공식 홈페이지의 설치 가이드를 참고한다.
( URL - https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html )

![image](uploads/356e490db927f7aa7de684143fdc16fa/image.png)<br/>
- 콘다 환경에서는 다음 명령어를 통해 설치한다. ` $ conda install -c conda-forge jupyterlab `

![image](uploads/753e25420b17221af5da4bb5c5a9e627/image.png)<br/>
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
![image](uploads/065e5616bd118a0b75129ad4f6c62f62/image.png)

- [Python 3.x](https://www.python.org/downloads/)
  ` $ python --version ` 또는 ` $ python3 --version ` 명령어를 통해서 설치 여부 및 버전 확인 가능<br/>
![image](uploads/d637460c736dc4c580195ef6c0a780c0/image.png)

### 2. 설치 자체는 간단하다.

![image](uploads/e312c8a4996524d7b1b17e8cdba30f78/image.png)<br/>
- 콘다 환경에서는 다음 명령어를 통해 설치한다. ` $ conda install -c conda-forge elyra `

![image](uploads/2b6a16831c2c3333ed1f0de37cc07479/image.png)
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
![image](uploads/2526719788c7fd3e35995da5d54b069d/image.png)

  2. ` $ jupyter serverextension list `<br/>
아래의 목록들이 enabled 되어있는지 확인한다.<br/>
![image](uploads/905fcc09953fd65d2e99637ee87c1732/image.png)

  3. ` $ jupyter labextension list `<br/>
아래의 목록들이 enabled 되어있는지 확인한다.<br/>
![image](uploads/3abf7a67bb7eec6027038be4ae854b11/image.png)

<br/>
<br/>
<br/>

# (+3. Install kubeflow)

- Kubeflow 설치하는 과정은 다음 자료를 참고한다. [6. Kubeflow 설치 과정 및 issues 정리.](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/Kubeflow-%EC%84%A4%EC%B9%98-%EA%B3%BC%EC%A0%95-%EB%B0%8F-issues-%EC%A0%95%EB%A6%AC.)