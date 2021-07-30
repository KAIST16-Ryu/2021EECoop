# T3Q Elyra Processor의 목표

[앞서 설명했듯이](6. T3QDemoElyraProcessor) 우리는 세가지 Kubeflow UI를 사용할 수 있도록 하는 elyra processor를 만들었다. 이로써 우리는 Jupyter Lab 환경에서 개발을 완료하고, Elyra를 통해 pipeline을 kubeflow에 **한번만** 등록하고, kubeflow pipeline의 UI로 재실험 및 artifacts들을 확인할 수 있는 등 kubeflow pipeline 내의 기능들을 더 잘 활용할 수 있을 것이다.
> ![image](https://user-images.githubusercontent.com/84768279/126757018-89be73db-43e4-4ebc-b7e5-efb6e39238bf.png)

# T3Q Elyra Processor 추가 방법

Elyra에서 제공하는 **pipeline processor customization** 인터페이스를 활용하여 T3Q Demo Elyra Processor를 생성했다. 해당과정의 구체적인 내용은 [여기](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/ElyraCustomProcessorDemo)를 참고하면 된다. 

1. Custom Runtime Schema 
> [t3qkfp.json](http://192.168.0.10:9999/kaist-co-op/jupyterwithelyraproject/-/blob/master/t3qkfpprocessor/t3qkfp.json) 생성
2. Custom Runtime Pipeline Processor
> [processor_t3qkfp.py](http://192.168.0.10:9999/kaist-co-op/jupyterwithelyraproject/-/blob/master/t3qkfpprocessor/processor_kfp.py) 생성
3. Procesor Registration
> entry_points.txt에서 `[elyra.pipeline.processors]` 항목에 `t3qkfp = elyra.pipeline.processor_t3qkfp:T3QKfpPipelineProcessor` 추가 <br/>
![image](https://user-images.githubusercontent.com/84768279/127459339-b5c61ce8-c830-4377-b46e-162b2c1bfd5d.png)

# T3Q Elyra Processor 생성과정

우리가 추가하고자 하는 기능은 크게 3가지 이다.

1. Kubeflow GUI로 log 확인하기
2. Kubeflow의 'run parameter' 기능 사용할 수 있는 pipeline
3. Kubeflow의 input/output artifact 관리

각 기능을 어떤 방법을 통해 추가했는지 하나씩 설명하고자 한다. 우선 설명하기에 앞서 우리가 만든 **processor_t3qkfp.py**는 기존 **processor_kfp.py**의 코드를 일부 수정하거나 추가하는 방식으로 만들어졌음을 알린다.

## 1. Kubeflow GUI로 log 확인하기

- 다음 URL 에서 내용을 확인할 수 있다.<br/>

  [Kubeflow GUI로 log 확인하기](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/Kubeflow-GUI%EB%A1%9C-log-%ED%99%95%EC%9D%B8%ED%95%98%EA%B8%B0)<br/>

## 2. Kubeflow의 'run parameter' 기능 사용할 수 있는 pipeline

- 다음 URL 에서 내용을 확인할 수 있다.<br/>

  [Kubeflow의 'run parameter' 기능 사용할 수 있는 pipeline](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/Kubeflow-%EC%9D%98-run-parameter-%EA%B8%B0%EB%8A%A5%EC%9D%84-%EC%82%AC%EC%9A%A9%ED%95%A0-%EC%88%98-%EC%9E%88%EB%8A%94-Pipeline)

## 3. Kubeflow의 input/output artifact 관리

- 다음 URL 에서 내용을 확인할 수 있다.<br/>

  [Kubeflow의 input/output artifact 관리](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/Kubeflow%EC%9D%98-input&output-artifact-%EA%B4%80%EB%A6%AC)