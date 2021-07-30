# Demo Runtime

Elyra에서 제공하는 인터페이스 중 [pipeline processor customization](https://elyra.readthedocs.io/en/latest/developer_guide/pipelines.html)을 확인해보기 위함이다. 더미 runtime을 작성하여 runtime customizing이 가능한지만 일단 확인하는 demo를 진행해보고자 한다.

elyra에서 요구하는 작업들은 다음과 같다.

1. Custom Runtime Schema
2. Custom Runtime Pipeline Processor Implementation
3. Processor Registration

#### Custom Runtime Schema

elyra/metadata/schemas 디렉토리에 새로운 runtime을 위한 metadata를 describe하는 JSON schema 파일을 만들어야한다. (공식 홈페이지에서는 이 디렉토리가 바뀔 수 있다고 한다.)

해당 customizing을 위해 작성한 코드는 [여기](http://192.168.0.10:9999/kaist-co-op/jupyterwithelyraproject/-/blob/master/elyra_demo_runtime/demoruntime.json)있다.

#### Custom Runtime Pipeline Processor Implementation

Customize하고자 하는 runtime은 elyra.pipeline.processor.RuntimePipelineProcessor의 하위 클라스여야 한다. 또한 pipeline engine에서 검색되기 위해서는 schema name과 동일한 type property를 가져야 한다.

해당 customizing을 위해 작성한 코드는 [여기](http://192.168.0.10:9999/kaist-co-op/jupyterwithelyraproject/-/blob/master/elyra_demo_runtime/processor_demo.py)있다.

#### Processor Registration

Pipeline processor은 "entry_points"를  통해 registered 되어야 한다. 이때 new runtime의 schema name과 pipeline processor의 type property value와 같은 이름의 name으로 register되어야 한다.

`    entry_points={
        'elyra.pipeline.processors': [
            'my_runtime = acme.my_runtime:MyRuntimePipelineProcessor'
        ]
    },
`

site-packages/elyra-2.2.4.dist-info/entry_points.txt 문서의 내용에서 `[elyra.pipeline.processors]`항목에 `demoruntime = elyra.pipeline.processor_demo:DemoPipelineProcessor` 항목을 추가했다.


## Issue

1. elyra 폴더 경로
> 로컬에 elyra 폴더가 2개가 존재한다.
<br/> **anaconda3/pkgs/elyra-2.2.4-pthd8edlab_0/site-packages/elyra** 와 **anaconda3/Lib/site-packages/elyra** 이다.
<br/> 둘 중 후자의 폴더에 해당 customizing한 요소들을 집어 넣어주어야 한다.

2. 추가적인 코드 
![image](https://user-images.githubusercontent.com/71695489/127621457-7b18554f-75f5-410b-a37a-5444b32051b9.png)
<br/> 우선 위와 같이 demo runtime을 등록은 할 수 있었다. 또한 runtime이나 pipeline에 대한 metadata를 읽어 로그로도 잘 찍어냈다. 하지만 그 외에도 살펴보아야 할 코드들이 있을 듯 하다.
- elyra/elyra/pipeline/parser.py
