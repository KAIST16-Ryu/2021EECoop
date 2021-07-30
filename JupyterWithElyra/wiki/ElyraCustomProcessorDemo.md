# Demo Runtime Processor
Elyra에서는 기본적으로 Local 환경 만이 아니라 Kubeflow, Airflow 환경에서도 pipeline을 실행할 수 있는 기능을 지원한다. 하지만 그 이외에도 사용자가 별도로 원하는 환경에서 pipeline을 실행할 수 있도록 [pipeline processor customization](https://elyra.readthedocs.io/en/latest/developer_guide/pipelines.html) 이라고 하는 사용자 추가 기능 또한 제공한다. 우리는 직접 Elyra에서 제공하는 pipeline processor cutomization 기능을 참고하면서 실제로 custom processor 를 생성하기 위해서 어떤 리소스를 추가해야 하는지 파악하였고, 기본 동작만을 수행하는 **Demo processor**을 만들어 실행되는 것을 확인했다.

Elyra에서 custom processor를 생성하기 위해 요구하는 작업들은 다음과 같다.
1. Custom Runtime Schema 작성.
2. Custom Runtime Pipeline Processor 구현.
3. Elyra 내부 entry_point에 Processor 등록.

## Demo Runtime Processor 생성하기 
### 1. Custom Runtime Schema

Elyra에서 Kubeflow runtime으로 pipeline을 실행하기 위해서는 먼저 아래 그림의 Kubeflow pipelines runtime configuration을 작성해야 한다.<br/>
configuration 항목에는 Kubeflow 환경에서 pipeline 을 실행하기 위한 환경 Metadata 정보들이 있다(Kubeflow API endpoint, user account, user password 등).<br/>
Elyra는 미리 작성된 kfp json schema 양식을 보고, 거기에 맞추어서 아래 그림처럼 configuration 을 띄우고, json 양식을 저장하는 것이다.<br/>

![image](uploads/61d72675ba4a7b3e3ad2523b8a6c133b/image.png)

마찬가지로 사용자가 custom runtime 환경에 관한 Metadata 정보를 담을 수 있는 json schema 를 작성하면, Elyra 는 위의 **kubeflow pipeline runtime configuration** 과 유사한 **custom runtime configuration**을 생성해주고, 우리는 custom runtime 을 등록할 수 있게 된다.

*elyra/metadata/schemas* 경로에 새로운 runtime을 위한 metadata를 정의하는 json schema 파일을 만든다. **demoruntime.json** json schema를 위해 작성한 코드는 [여기](http://192.168.0.10:9999/kaist-co-op/jupyterwithelyraproject/-/blob/master/elyra_demo_runtime/demoruntime.json)에 있다.<br/>
별도로 json schema를 작성하기 위해서는 기존의 json schema 와 runtime configuration 을 참고하면서 작성하는 것을 추천한다.

### 2. Custom Runtime Pipeline Processor

*elyra/pipeline* 경로에 새로운 runtime을 위한 processor python script 파일을 만든다. Custom Processor를 생성할 때 조건이 두가지가 있다. <br/>
1. 해당 Customized runtime pipeline processor는 **elyra.pipeline.processor.RuntimePipelineProcessor의 하위 클라스**여야 한다.
> ![image](uploads/a4bf616be45e2dfb8cee1b9c97bee79f/image.png) <br/> ![image](https://user-images.githubusercontent.com/84768279/126590679-49a962b9-3be3-45ed-8f37-d6c3d4e1a4b3.png) <br/>
2. 해당 processor의 **type property**가 앞에서 작성한 Schema(= demoruntime.json)의 name이어야 한다. <br/> - 이는 pipeline engine에서 검색되기 위해서이다.
> ![image](https://user-images.githubusercontent.com/84768279/126590567-cd83ec73-d327-435e-b3fa-8f2ecd886268.png) <br/>
![image](https://user-images.githubusercontent.com/84768279/126590621-23c9446d-4a23-49f6-a8f5-a80d971a26b1.png)

해당 파트를 위해 작성한 processor_demo.py의 DemoPipelineProcessor 코드는 [여기](http://192.168.0.10:9999/kaist-co-op/jupyterwithelyraproject/-/blob/master/elyra_demo_runtime/processor_demo.py)에 있다.

### 3. Processor Registration
해당 과정은 앞서 생성한 processor를 등록하는 과정이다. Elyra에서는 

```python
entry_points={
        'elyra.pipeline.processors': [
            'my_runtime = acme.my_runtime:MyRuntimePipelineProcessor'
        ]
},
```

항목을 추가해주어야 한다고 설명하고 있다. 하지만 어디서 어떤 파일에 추가해야 하는지를 설명해주지 않았다. 직접 찾아본 결과, *site-packages/elyra-2.2.4.dist-info/* 경로에서 **entry_point.txt**라는 파일을 찾을 수 있었다.

해당 문서의 내용에서 `[elyra.pipeline.processsors]` 항목에, `demoruntime = elyra.pipeline.processor_demo:DemoPipelineProcessor` 을 추가해주었다.<br/>각각 `processor type = elyra.processor.<custom module name>:<custom class name>` 양식으로 다음과 같이 추가하면 된다.
> ![image](https://user-images.githubusercontent.com/84768279/126592168-fad9f6e3-a659-47ca-ab1e-70671a82eff3.png)

## Demo Runtime Processor 결과

앞서 설명한 단계들을 모두 진행했다. 이때 해당 Demo Runtime Processor는 별도로 pipeline을 실행하지 않고, 우선 runtime과 pipeline에 대한 metadata를 로그로 띄워 해당 metadata 정보를 processor가 잘 읽어오는지 동작 여부만 확인한다. <br/>
> ![image](https://user-images.githubusercontent.com/84768279/126593894-555bf2e6-bd70-4fb1-b4b1-347bca350285.png)

그 결과 아래와 같이 jupyter lab을 킬때 해당 runtime processor가 설치됨을 확인할 수 있었고 <br/>
> ![image](https://user-images.githubusercontent.com/84768279/126593009-dce5d48d-a555-48a2-83c2-8adb3699c85b.png)

실제 elyra의 UI에서도 해당 demo runtime processor를 확인할 수 있었으며 <br/>
> ![image](https://user-images.githubusercontent.com/84768279/126593138-f4954900-9379-49f6-80e9-5e6e1222b334.png) <br/>
![image](https://user-images.githubusercontent.com/84768279/126593234-fa4570be-44f1-4870-b80e-445760af54a8.png)

실제로 Demo runtime processor를 실행해보면 <br/>
> ![image](https://user-images.githubusercontent.com/84768279/126593559-b75e2c94-ba6b-4c5e-8930-1cbb479efa57.png) <br/>
![image](https://user-images.githubusercontent.com/84768279/126593655-bd2f3779-d07f-40d3-8bcc-26d18a139930.png)

다음과 같이 metadata에 대한 정보를 로그로 띄워 해당 processor가 잘 작동함을 확인할 수 있었다. <br/>
> ![image](https://user-images.githubusercontent.com/84768279/127126637-6b128d7f-6276-4acc-8bc4-84b588a8d518.png)