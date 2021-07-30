![image](https://user-images.githubusercontent.com/84768279/127245192-bdea5168-5879-4095-80f4-ebce7034087a.png)

Juypter Lab에서 개발을 마치고 Elyra를 통해 pipeline을 구성한다. 그리고 구성된 pipeline은 kubeflow와 같은 운영 플랫폼에 올라가게 된다. 이때, Elyra에서 kubeflow로 넘어가기까지 어떤 data가 쓰이고 저장되고 변환되는지 그 구조를 파해쳐보자. 

우선 Elyra를 사용할 때 사용자가 생성하야하는 2가지가 존재한다. 
1. **Pipeline**
2. **Runtime Configuration** (runtime data + storage data)

**어떤 pipeline**을 **어떤 runtime configuration**으로 돌릴 것인가? 에 대한 정보를 주어야한다. 
<br/>
우선, pipeline에 대한 data가 어떻게 저장되고 변환되는지 그 구조를 파해쳐보았다.

# Pipeline
## Pipeline Json 
![image](https://user-images.githubusercontent.com/84768279/127248252-b02a32a4-ec1c-4b74-8fb6-9cd661544dd5.png) <br/>
Pipeline에 대한 정보는 UI 상에서 .pipeline이라는 확장자를 가진 elyra 정의 리소스에 저장되어 있다. 그리고 **pipeline editor**라는 GUI를 통해 설정할 수 있다. GUI를 통해 정의된 pipeline은 아래의 사진처럼 내부에서 **JSON** 데이터로 저장된다. 붉은색 화살표로 표시된 부분은 [pipeline editor의 JSON](https://github.com/elyra-ai/pipeline-schemas/blob/master/common-pipeline/pipeline-flow/pipeline-flow-v3-schema.json) 양식이 어떤 JSON schema 규칙을 따르는지 나타내고 있다. <br/><br/>
![image](https://user-images.githubusercontent.com/84768279/127248226-b42cc251-9ad4-45b6-97d7-f8cc8abebfc9.png) <br/>

간단히 정리하면 다음과 같다. GUI pipeline은 내부에서 json 데이터로 저장된다. 이 Json 데이터를 편의상 **pipeline flow json** 이라 하겠다. 하나의 pipeline flow는 고유한 id를 가진다. 그리고 이 'pipeline flow'는 여러개의 pipeline들을 가질 수 있지만 일반적으로는 한 개의 pipeline을 가지며, 각 pipeline들도 고유 id를 가지고 있다. 그리고 하나의 pipeline에는 각 노드들에 대한 정보를 담고 있다. pipeline flow json의 구조를 도식화 하면 다음과 같다. <br/>
<br/>
![image](https://user-images.githubusercontent.com/84768279/127253943-4832c272-0e08-4f2f-969e-c111a6d05480.png)

**pipeline flow** json은 다음과 같은 형태를 가지고 있다. <br/>

```text
{
    “doc_type”: “pipeline”,
    “version”: “3.0”,
    “json_schema”: (JSON Schema URL, http://url.com),
    “id”: “2a7430ac-61fa-4a07-b56e-293e24a75786”,
    “primary_pipeline”: “1b9971a5-cea7-49d3-9317-eaf8183b8c0b",
    “pipelines”: [{pipeline}, {...}], (일반적으로 1개만 존재)
    “schemas”: [{...}],
}
```

내부의 pipelines 항목에는 여러 개의 pipeline을 배열 형태로 지니고 있다. 일반적으로 대부분의 경우에는 한 개의 pipeline만 가지고 있고, 하나의 **pipeline**은 다음과 같은 형태를 가진다.( 위의 **pipeline flow** json에서 "pipelines" 항목의 pipeline 원소 하나의 json 형태를 말한다.) <br/>

```text
{
   "id": "1b9971a5-cea7-49d3-9317-eaf8183b8c0b",
   "nodes": [{node},{node},...],
   "app_data": {"ui_data":{"comments":[{comment},{comment}...]}, "version":3},
   "runtime_ref":""
}
```
<br/>

그리고 **pipeline** 의 nodes 항목에는 여러 개의 node를 배열 형태로 가지고 있다. 하나의 **node**는 아래와 같은 형태를 가진다. Elyra pipeline UI에서 각 노드에 입력한 property들에 대한 정보들이 node의 "app_data" 항목에 정의되어있음을 확인할 수 있다. 또한, "inputs" 항목에서는 직전 노드의 id에 대한 정보를 가지고 있는데, 각 노드들이 직전 노드들을 가리킴으로써 node들의 실행 순서를 알 수 있다. <br/>

```text
{
   "id": "f7e8deca-c84c-4dd2-92eb-0754475fc70b",
   "type": "execution_node",
   "op": "execute-python-node",
   "app_data": {
        "filename": "preprocessing.py",
        "runtime_image": "neo21top/seeyeon-tutor",
        "include_subdirectories": false,
        "outputs": ["dataset.zip"],
        "env_vars": [],
        "dependencies": ["0.zip","1.zip",...],
        "invalidNodeError": null,
        "cpu": 1,
        "memory": 1,
        "gpu": 1,
        "ui_data": {something about UI}
        },
  "inputs":[],
  "outputs":[]
}
```

이렇게 GUI를 통해 입력된 pipeline에 대한 정보들이 elyra가 어떤 형태로 정의하는지 알아보았다. 그럼 elyra에서 이 정의된 pipeline을 어떻게 가공하여 가지고 있다가 kubeflow로 전달하는 것일까? Elyra는 이 data를 `Pipeline`이라는 객체에 전달하여 저장한다.

## [Pipeline Object](https://github.com/elyra-ai/elyra/blob/3ac7544c95eaf172a8c86f87e3234acf8253070b/elyra/pipeline/pipeline.py)
Elyra는 **pipeline flow json** 파일로부터 정보들을 읽어와 `Pipeline` 객체를 생성한다. `Pipeline` 객체는 크게 다음과 같은 속성들을 가진다. (이외에도 다른 속성들이 존재한다.) <br/>

![image](https://user-images.githubusercontent.com/84768279/127265431-b876a5bd-efb8-454b-860d-d3e032916ad8.png)

`Pipeline` 객체는 `Operation`이라는 객체들의 Dictionary를 `_operations` 라는 속성으로 가지고 있다. 그럼 `Operation` 객체는 무엇일까? 이 `Operation` 객체는 앞서 설명한 **node** 하나를 의미한다. 즉, **node** 에 대한 정보들을 속성으로 가지는 객체가 `Operation`이다. `Operation` 객체는 크게 아래와 같은 속성들을 가진다. (이외에도 다른 속성들이 존재한다.)<br/>
`component_params` 속성을 보면 앞에서 **pipeline flow json**의 node 항목의 "app_data" 항목들의 정보들이 들어가 있음을 확인할 수 있다.<br/>
`parent_operation_id` 속성은 node의 "inputs" 항목처럼 직전(parent) operation들의 id를 가리킴으로써 `operation` 객체간의 순서 혹은 관계를 알 수 있다. <br/>

![image](https://user-images.githubusercontent.com/84768279/127268304-65714eb2-f0d9-455a-85d5-085ac9f8a4fe.png)

즉, `Pipeline` 객체는 **pipeline flow json**의 **pipeline** 항목과, `Operation` 객체는 **node** 항목과 대응되는 관계임을 알 수 있다. 해당 json 파일로부터 `Pipeline` 객체를 생성하여 elyra 내에서 동작하고 data들을 kubeflow에 올릴 수 있다.
<br/><br/>
# Runtime Configuration
지금까지 Pipeline data에 대해 살펴보았다. 그렇다면 Runtime Configuration data는 어떻게 생성하고 보관되어질까? 

앞에서 언급했듯이 여기서의 **Runtime Configuration**은 kubeflow와 같은 workflow에 대한 data 뿐만 아니라 minio와 같은 storage에 대한 data도 포함한다.

Runtime Configuration은 elyra의 **Runtimes**라는 UI를 통해 생성할 수 있다. 뿐만 아니라, `elyra-metadata` CLI를 통해서도 생성할 수 있다. 

#### [JupyterLab UI](https://elyra.readthedocs.io/en/latest/user_guide/runtime-conf.html?#managing-runtime-configurations-using-the-jupyterlab-ui)
JupyterLab UI를 통한 Runtime Configuration 생성 창은 다음과 같다. <br/>
![image](https://user-images.githubusercontent.com/84768279/127275748-e89775ba-39b8-4c9b-a4ca-e15cd8f33c95.png)<br/>
> 왼편에서 생성되어있는 Runtime Configuration에 대한 list를 확인할 수 있으며, list 위의 `+` 를 클릭하면, 원하는 runtime (kubeflow, airflow)를 선택 후 각 runtime의 양식에 맞는 runtime configuration 설정화면이 나타난다. (오른쪽 붉은색 박스) 

#### [Elyra CLI](https://elyra.readthedocs.io/en/latest/user_guide/runtime-conf.html?#managing-runtime-configurations-using-the-elyra-cli) <br/>
Elyra의 `elyra-metadata` CLI를 이용하여 runtime configuration을 생성할 수 있는데, 그 양식은 아래와 같다. 

```text
elyra-metadata install runtimes \
       --display_name="My Kubeflow Pipelines Runtime" \
       --api_endpoint=https://kubernetes-service.ibm.com/pipeline \
       --api_username=username@email.com \
       --api_password=mypassword \
       --engine=Argo \
       --cos_endpoint=http://minio-service.kubeflow:9000 \
       --cos_username=minio \
       --cos_password=minio123 \
       --cos_bucket=test-bucket \
       --tags="['kfp', 'v1.0']" \
       --schema_name=kfp
```
<br/>
조금 더 수월한 이해를 위해 JupyterLab UI를 바탕으로 이어서 설명하도록 하겠다. <br/>
![image](https://user-images.githubusercontent.com/84768279/127279570-5c4538c2-d861-47b6-a694-d2b85854154c.png)

Runtime Configuration Setting에서 입력해주어야 하는 부분은 크게 2가지이다.
1. **Runtime**에 대한 data
> ex) kubeflow, airflow
2. **Storage**에 대한 data
> ex) minio

생성된 runtime configuration은 pipeline editor 창에서 `run`을 눌렀을때 선택하여 원하는 runtime으로 실행시킬 수 있다. <br/>
![image](https://user-images.githubusercontent.com/84768279/127281565-06b41a8e-684c-45ab-b271-7faef5f41ea1.png)


