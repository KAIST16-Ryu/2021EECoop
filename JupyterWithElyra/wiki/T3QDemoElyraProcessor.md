우리가 원하는 Elyra를 통한 개발-운영의 흐름은 다음과 같다. <br/>
![image](https://user-images.githubusercontent.com/84768279/126740256-71d13a2a-da2d-4b2e-8f62-f1ad399c47e4.png)

하지만 기존의 elyra의 kubeflow processor는 kubeflow pipeline의 UI들을 잘 활용하지 못했다는 단점이 있다. 활용한다면 굉장히 유용할 kubelfow pipeline UI에는 크게 3가지가 있었다. 

1. 각 container의 log를 확인할 수 있다.
2. Run Parameter 기능
3. Input/Output Artifact

우리는 이 기능들을 다 활용할 수 있는 elyra의 custom processor를 제작하고자 했다. 제작방법을 알려주기에 앞서 kubeflow pipeline에서 제공하는 위의 기능들에 대해 좀 더 알아보고, elyra에서 왜 이 기능들을 사용할 수 없는지, 그리고 이를 사용하기 위해서는 어떻게 해야할지에 대해 알려주고자 한다. 

# 유용한 Kubeflow pipeline UI

## 1. 각 container의 log를 확인할 수 있다.

Kubeflow run UI에서 각 container에 대한 logs를 확인할 수 있다.

#### With Elyra
Elyra를 통해서 pipeline을 업로드 할때에도 이 기능을 사용하지만, 이때 뜨는 로그는 우리가 확인하고자 하는 model에 대한 로그가 아닌, bootstrapper.py 이라는 코드의 로그이다. [자세한 설명은 여기](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/Kubeflow-GUI%EB%A1%9C-log-%ED%99%95%EC%9D%B8%ED%95%98%EA%B8%B0#2-elyra-%EC%9D%98-log-%EA%B4%80%EB%A6%AC-%EB%B0%8F-%ED%99%9C%EC%9A%A9)

> bootstrapper.py : 이 코드는 elyra에서 제작한 코드로, kubeflow에서 container을 실행하면 실제 각 단계별 코드가 아닌 bootstrapper.py 코드를 실행한다. bootstrapper.py 에서 1) requirements.txt의 필요한 모듈들을 추가 설치하고, 2) minio storage에서 필요한 input data를 다운로드 받는 등의 역할을 담당한다. 3) 그리고 나서 subprocess.run 함수로 우리가 실제로 돌리고자 하는 파일을 실행시킨다.

![image](https://user-images.githubusercontent.com/84768279/126741498-6b8afc00-ba3e-4a7c-aed3-5157fcf60c5e.png)

위 kubeflow dashboard 에서 볼 수 있는 로그는 실제로 실행 파일에 대한 log가 아니고, **bootstrapper 의 실행 로그**이다. 정작 우리가 보고자 하는 로그는 해당 로그창에서는 확인할 수 없다. bootstrapper가 코드 내부에서 실제 실행 파일에 대한 로그를 minio에 저장한다(python script의 경우). 우리는 해당 minio에 따로 접속을 해야만 .log 파일을 확인할 수 있다. 

#### Solve
Elyra는 실제 model의 실행 로그를 container의 로그창이 아닌 (python script의 경우) .log 파일을 작성하여 minio에 저장하도록 구현했다. minio에서 로그 파일을 열어 보는 번거로운 과정을 거쳐야 하므로, 우리는 bootstrapper의 코드를 일부 수정하여 해당 log파일을 실제 container의 로그창에 띄울 수 있도록 변경 했다.

<br/>
<br/>
<br/>

## 2. Run Parameter

Kubeflow에서는 pipeline dashboard 상에 업로드 한 pipeline을 parameter를 바꿔가며 run 할 수 있는 기능을 제공한다.<br/>
![image](https://user-images.githubusercontent.com/84768279/126745731-e4e50e78-78c0-4c00-9ec8-48e61f977da4.png)

#### With Elyra
하지만 이 기능이 elyra의 kubeflow runtime을 통해 pipeline을 생성해 주었을 때는 작동하지 않는다. Elyra에서는 batch size, epoch와 같은 input 값으로 받을 parameter 들을 environment variables로 kubeflow pipeline에 넘겨주기 때문에 다른 값으로 run 해보고 싶다면 다시 elyra를 통해 pipeline을 재업로드해야 한다. 
> ![image](https://user-images.githubusercontent.com/84768279/126743387-20ff9412-2353-42ef-b82b-ddd065f0cc2c.png)

Elyra를 통해 매번 parameter를 바꾸기에는 다소 번거로울 수 있으며, run 뿐만 아니라 pipeline의 version이 새로 생성되는 것이기 때문에 관리가 조금 귀찮을 수 있다. 

#### Solve
kubeflow pipeline dashboard UI 상에서 parameter 변경 기능을 사용하기 위해서는 pipeline yaml 양식을 맞추어서 작성해야 한다. 기존의 Elyra kubeflow processor 는 parameter 변경 기능을 반영할 수 있는 yaml을 생성하지 못한다. 따라서 Kubeflow pipeline dashboard 상의 **run parameters** 기능을 활용할 수 있도록 관련한 yaml 양식을 수정해주는 코드를 추가했다.

<br/>
<br/>
<br/>

## 3. Input/Output Artifact

Kubeflow 내에 각 container간에 output artifact와 input artifact를 주고받을 수 있는 별도의 방법이 있다. Kubeflow에서 제공하는 방법을 사용하면 다음과 같이 pipeline dashboard의 각 container UI에서도 해당 artifact에 대한 정보를 확인할 수 있다.

> ![image](https://user-images.githubusercontent.com/84768279/126751783-e813a28c-6812-4235-aa57-e2832687c9e6.png)

또한, Kubeflow Pipeline에서 **Artifact** UI에서도 확인이 가능하다. (하지만 이 UI는 여러모로 조금 개선이 필요할 듯 하다.)

> ![image](https://user-images.githubusercontent.com/84768279/126751968-9d9ec6d5-670f-4cf0-be48-59924a27abf0.png)

#### Elyra
Kubeflow에서 제공하는 artifact 관련 기능을 사용하면, kubeflow가 직접 minio storage에서 file을 업로드하고 다운로드한다. 하지만 Elyra의 경우, kubeflow를 통해서가 아닌, 직접 minio storage에 업로드하고 다운로드한다. 해당 작업도 앞서 언급했던 bootstrapper.py의 역할이다. 그렇기 때문에 Elyra를 통해 pipeline을 생성하면 Kubeflow Pipeline의 UI로 확인할 수 없다. 다만 Eylra에서 Kubeflow metadata UI를 위해 *mlpipeline-metrics.json* 파일과 *mlpipeline-ui-metadata.json* 파일만은 자동으로 생성하여 kubeflow의 output artifact로 저장하기 때문에 해당 두 artifact들은 UI 상에서 확인할 수 있다. (아래 사진 참고)
> ![image](https://user-images.githubusercontent.com/84768279/126754539-5f17b484-cce9-4762-8fa5-11f21bf5a98f.png)

#### Solve
조금 더 구체적으로 설명하자면, Elyra에서는 input/output artifact 요소들을 bootstrapper.py가 관리하기 때문에 관련된 정보들을 yaml 파일에서 `spec.container.args` 란으로 전달한다.
> ![image](https://user-images.githubusercontent.com/84768279/126754965-211b61be-c9ce-4695-8bd8-448aba299e5d.png)

하지만 kubeflow가 관리하기 위해서는 yaml 파일에서 각 container의 `inputs.artifacts` 와 `outputs.artifacts` 란으로 정보를 전달해야한다.
> ![image](https://user-images.githubusercontent.com/84768279/126755722-d7ec694f-2f29-4ff7-9156-728e262344f3.png)

# Therefore...

우리는 지금까지 설명한 세가지 Kubeflow UI를 사용할 수 있도록 하는 elyra processor를 만들고자 한다. 이로써 우리는 Jupyter Lab 환경에서 개발을 완료하고, Elyra를 통해 pipeline을 kubeflow에 **한번만** 등록하고, kubeflow pipeline의 UI로 재실험 및 artifacts들을 확인할 수 있는 등 kubeflow pipeline 내의 기능들을 더 잘 활용할 수 있을 것이다.
> ![image](https://user-images.githubusercontent.com/84768279/126757018-89be73db-43e4-4ebc-b7e5-efb6e39238bf.png)

[여기](8. T3QDemoElyraProcessor제작)
