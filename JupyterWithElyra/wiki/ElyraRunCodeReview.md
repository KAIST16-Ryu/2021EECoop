**@ Elyra는 현재도 계속 업데이트 중인 프로그램이기 때문에 버전에 업데이트 되면서 내용이 변경될 수 있습니다.**

- Elyra Custom Processor 를 실행하기 위해서 Elyra 자체적으로 내부 리소스를 파악한 내용에 대해서 정리했다.

- 전체적인 소스 코드에 대한 리소스는 다음 GitHub 에서 찾을 수 있다.

  [ Elyra Github ](https://github.com/elyra-ai)<br/>
  [ Elyra / Elyra Github ](https://github.com/elyra-ai/elyra)<br/>
  [ Elyra / kfp-notebook ](https://github.com/elyra-ai/kfp-notebook)<br/>

<br/>
<br/>
<br/>

실행 흐름을 파악하기 위해서 Elyra 의 몇몇 데이터 저장 구조에 대해서 파악하고 이 글을 읽는 것을 추천한다. [여기]()

# Elyra의 내부 실행 흐름 파악.

- Jupyter + Elyra 에서 작업한 내용을 우리가 원하는 환경에서 실행할 수 있는 Custom Processor 제작하려면, Elyra의 내부 실행 흐름을 어느 정도 파악하고 있어야 한다. 다음과 같이 UI 상에서 파이프라인을 실행했을 때, 가장 처음으로 내부에서 진행되는 코드의 흐름은 다음과 같다.<br/>
![image](uploads/d00c7453f2e3858ddac4c420e2b2df48/image.png)<br/>

<br/>

- 처음에 호출되는 부분은 [ elyra-ai/elyra/cli/pipeline_app.py ](https://github.com/elyra-ai/elyra/blob/3ac7544c95eaf172a8c86f87e3234acf8253070b/elyra/cli/pipeline_app.py#L240) 의 run 함수이다. Local 환경이 아니라, 다른 runtime 에서 실행되는 경우에는 [ submit 함수 ](https://github.com/elyra-ai/elyra/blob/3ac7544c95eaf172a8c86f87e3234acf8253070b/elyra/cli/pipeline_app.py#L206) 를 호출해 시작한다. 내부 코드는 거의 유사하다.<br/>
![image](uploads/2604eedb769479ee02862a365c1fe90d/image.png)

<br/>
<br/>
<br/>

- 위의 그림에서 [ _execute_pipeline(pipeline_definition) ](https://github.com/elyra-ai/elyra/blob/3ac7544c95eaf172a8c86f87e3234acf8253070b/elyra/cli/pipeline_app.py#L152) 함수는 runtime 항목이 추가된 json 데이터를 전달 받아 [Elyra 리소스 데이터 구조]()에서 설명했던 Pipeline 객체와 Operator 객체로 보관한다. 그리고 그 정보를 토대로 각각의 runtime processor의 process 함수를 호출하여 거기서부터 pipeline을 실행한다.<br/>
![image](uploads/850384424d4a8f5330cfa69b6f109572/image.png)<br/>

<br/>
<br/>
<br/>

- 위에서 호출된 [ process 함수 ](https://github.com/elyra-ai/elyra/blob/3ac7544c95eaf172a8c86f87e3234acf8253070b/elyra/pipeline/processor.py#L116)는 실제로 선택한 runtime에 맞는 함수를 다음과 같은 방법으로 호출한다.
![image](uploads/c2e92a1890195efe479eb0675a868e49/image.png)

<br/>
<br/>
<br/>

- 최종적으로 각각의 runtime 에 맞는 processor 함수는 각각 pipeline 객체를 전달받아서 각각의 runtime 에 맞는 실행 명령어를 통해서 pipeline을 실행한다.

  [ Local processor 함수 ](https://github.com/elyra-ai/elyra/blob/3ac7544c95eaf172a8c86f87e3234acf8253070b/elyra/pipeline/processor_local.py#L71)<br/>
  [ Kubeflow processor 함수 ](https://github.com/elyra-ai/elyra/blob/3ac7544c95eaf172a8c86f87e3234acf8253070b/elyra/pipeline/processor_kfp.py#L71)

#### Local을 제외한 processor 함수의 역할은 크게 다음과 같다.
- Pipeline을 실행하고자 하는 서버 권한 획득 및 접속
- Elyra의 pipeline 객체를 전달받아 해당 runtime에 upload 할 수 있는 형태로 변환
- 해당 서버에서 pipeline 실행

<br/>
<br/>
<br/>

  Kubeflow processor 의 process 함수를 설명하기에 앞서 Kubeflow pipeline 리소스에 대해 알 필요가 있다. [이글](Kubeflow pipeline 리소스 및 Dashboard UI 설명.)을 읽지 않았다면 먼저 읽고오는 것을 추천한다.

Kubeflow processor 의 [process 함수](https://github.com/elyra-ai/elyra/blob/3ac7544c95eaf172a8c86f87e3234acf8253070b/elyra/pipeline/processor_kfp.py#L71)를 Pseudo Code로 설명하면 ...<br/>

```python
import kfp
class kfpPipelineprocessor (RuntimePipelineProcessor):
  def process (self, pipeline):
      // get kubeflow account & auth info
      // create KFP client (Argo or Tekton)
      // change pipeline object into kubeflow data object
      // make workflow yaml
      // create experiment & pipeline 
      // run pipeline

```

##### 1. get kubelfow account & auth info
: 주어진 runtime metadata를 이용하여 kubelfow 서버에 접속하고 cookie를 획득한다.

##### 2. create KFP client (Argo or Tekton)
: 앞에서 획득한 권한으로 KFP client 객체를 생성한다. KFP client의 method를 이용해서 코드를 통해 kubeflow 서버에 experiment와 pipeline을 생성하고 run 할 수 있다.

##### 3. change pipeline object into kubeflow data object
: Elyra는 pipeline에 대한 정보를 `pipeline` 객체로 가지고 있다. 이 객체로부터 정보들을 받아 kubeflow를 위한 data 객체로 변환한다.

##### 4. make workflow yaml
: Pipeline을 업로드 하기 위해서는 pipeline 정보에 대한 명세를 담은 yaml 파일을 필요로 한다. 앞에서 변환된 data 객체를 kubeflow pipeline SDK 함수를 이용해 workflow yaml 파일을 생성한다.

##### 5. create experiment & pipeline
: 앞에서 생성한 KFP client 객체의 method를 이용하여 pipeline yaml 파일을 서버에 업로드하고 experiment를 생성한다.

##### 6. run pipeline
: 생성된 experiment에서 업로드한 pipeline을 run한다.