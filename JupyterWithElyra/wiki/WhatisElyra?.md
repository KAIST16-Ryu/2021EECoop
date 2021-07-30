## 목차
#### 1. Elyra 이란 무엇인가?
#### 2. Elyra 를 연동해서 사용하는 Jupyter 의 장점
#### 3. Elyra 의 장점

<br />
<br />
<br />

## 1. Elyra 이란 무엇인가?

- Elyra 이란, Jupyter Lab Extension 기능 중 하나이다. 현재 머신러닝, 딥러닝 개발 환경에서 주피터를 많이 사용하고 있는데, Elyra는 주피터상에서 개발한 각 단계의 작업을 하나의 파이프라인으로 묶어서 다양한 환경에서 실행할 수 있도록 기능을 제공하고 있다. 아래의 그림을 보면 Elyra 가 지원하는 기능에 대해서 몇 가지 서술하고 있다. 기본적인 정보는 공식 홈페이지에서 확인할 수 있다. [여기](https://elyra.readthedocs.io/en/latest/getting_started/overview.html)<br/>

![image](uploads/6a966b352700b50ffb8dff2080e7cb14/image.png)
 
<br/>
<br/>
<br/>

## 2. Elyra 를 연동해서 사용하는 Jupyter 의 장점

- Elyra 는 기존의 Jupyter 개발 환경이 가지는 장점을 활용하여 자신의 기능을 추가한 Jupyter Extension 이다. 따라서 Elyra 를 사용한다면, 주피터의 장점을 같이 활용할 수 있다. Jupyter는 .ipynb 확장자의 노트북 파일을 지원한다. 이 파일은 기존의 파이썬 스크립트와는 다른 구조를 가지고 있어 이에 따른 장점이 있다.

<br/>

1) 노트북 파일은 내부에서 셀(cell) 구조를 사용하고 있는데, 전체 프로그램이 아니고 셀 단위로 프로그램을 실행할 수 있다. 그리고 이전에 실행했던 셀의 실행 정보를 저장하여, 다음 셀에서 활용 가능하다.

( notebook.ipynb )<br/>
![image](uploads/eb5717edcee5637768f1f4ac1f9b0d92/image.png)
---

2) 각 셀의 실행 결과가 문자가 아니어도, 다양하게 출력해서 결과를 받아볼 수 있다. 예를 들어 출력 결과를 그래프로 나타내거나, 표를 사용하거나, 그림을 출력하는 등 원하는 결과를 직접적으로 받아볼 수 있는 장점이 있다. 이는 머신러닝, 딥러닝 데이터 전처리 과정에서 여러 데이터를 분석하거나, 학습 결과를 시각화 하는 과정에서도 정말 효과적이다.

![image](uploads/8a60ea98064113aa7abe0d9e013bc1c9/image.png)<br/>
---

3) 노트북은 Markdown 양식을 함께 사용 가능하다. 이는 작업한 내용 중간 중간에 마크다운 양식으로 상세하게 설명할 수 있다는 뜻이다.

![image](uploads/3d6fdc64be3a4f09ae3fbb98d5944124/image.png)

<br/>
<br/>
<br/>

## 3. Elyra 는 여러 기능을 제공하고 있지만, 우리가 특징적으로 활용할 장점은 다음과 같다.

1) AI pipeline visual Editor - Elyra 는 일련의 작업을 하나의 파이프라인으로 조직할 수 있고, 이를 GUI 로 제공한다. 사용자는 직접 파이프라인 구조를 눈으로 보고 파악할 수 있다. 또한 각 작업이 어떤 순서로 실행되는지 등의 정보를 시각적으로 빠르게 파악할 수 있다.

![image](uploads/000a484f0b03559173490ccd87f29d9d/image.png)

2) Ability to run a notebook, Python or R script as a batch job. - Elyra 는 파이프라인의 각 작업에 소속된 다수의 파이썬, R 및 notebook 파일을 한 번에 실행할 수 있도록 기능을 지원하고 있다. 또한 다양한 환경에서 파이프라인 내부의 개별 노드만 별도로 batch job 으로 실행할 수 있는 기능 또한 지원한다.

  - 다음과 같이 **Run pipeline** 을 통해서 여러 단계의 소스 파일이 포함된 파이프라인을 한번에 실행할 수 있다.<br/>
![image](uploads/04281f19aa473e0c47412db5709efed7/image.png)

  - 다음과 같이 파이프라인의 개별 노드만 별도로 다양한 환경에서도 실행 가능하다.<br/>
![image](uploads/3b696dafee8d6e4533f95f08ca38c40a/image.png)

<br/>
<br/>
<br/>

`T3Q Platform 부문 기술연구소`<br/>
`인턴 유어진`<br/>
`인턴 김시연`