### @ 문서 흐름 및 가이드라인.

이 문서의 내용은 Jupyter Lab, Elyra 및 Kubeflow 가 업데이트되면, 내용이 변경될 수 있다. 이 문서를 읽는 목적에 따라서 정리하자면...

## 1. Jupyter + Elyra

  1) [Elyra 이란 무엇인가?](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/Elyra-%EC%9D%B4%EB%9E%80-%EB%AC%B4%EC%97%87%EC%9D%B8%EA%B0%80%3F)
  2) [Jupyter 및 Elyra 설치 과정 및 issues 정리.](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/Jupyter-%EB%B0%8F-Elyra-%EC%84%A4%EC%B9%98-%EA%B3%BC%EC%A0%95-%EB%B0%8F-issues-%EC%A0%95%EB%A6%AC)
  3) [Elyra 사용 가이드 -> 1. Local 환경에서 Elyra 실행에 관한 예제.](https://github.com/elyra-ai/examples/tree/master/pipelines/introduction-to-generic-pipelines)

(+ kubeflow 환경에서 실행하고 싶을때)<br/>

  4) [Kubeflow 설치 과정 및 issues 정리.](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/Kubeflow-%EC%84%A4%EC%B9%98-%EA%B3%BC%EC%A0%95-%EB%B0%8F-issues-%EC%A0%95%EB%A6%AC.)
  5) [Elyra 사용 가이드 -> 2. Kubeflow Pipelines 를 활용한 Elyra 실행에 관한 예제.](https://github.com/elyra-ai/examples/tree/master/pipelines/run-generic-pipelines-on-apache-airflow)

  순서로 읽어보는 것을 추천한다.

<br/>
<br/>
<br/>

## 2. Kubeflow Dashboard UI 및 다중 사용자

  1) 먼저 Kubeflow의 Pipeline 구성 요소 및 Kubeflow Pipeline Dashboard UI 상에서 각각의 리소스를 다루는 방법에 대해서 설명한다.<br/>
  [ Kubeflow pipeline 리소스 및 Dashboard UI 설명 ](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/Kubeflow-pipeline-%EB%A6%AC%EC%86%8C%EC%8A%A4-%EB%B0%8F-Dashboard-UI-%EC%84%A4%EB%AA%85.)<br/>

  2) 다수의 사용자들이 Kubeflow Cluster 의 리소스들을 나눠 사용하는 방법, 그리고 현재 리소스 격리 수준의 한계에 대해서 설명한다.<br/>
  [ Kubeflow 리소스 격리에 대한 이해 ](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/Kubeflow-%EB%A6%AC%EC%86%8C%EC%8A%A4-%EA%B2%A9%EB%A6%AC%EC%97%90-%EB%8C%80%ED%95%9C-%EC%9D%B4%ED%95%B4)

<br/>
<br/>
<br/>

## 3. T3QDemoElyraProcessor

- Jupyter+Elyra 환경을 사용해 보지 않았다면, [1. Jupyter + Elyra를 사용하고자 할 때. (+ kubeflow 환경에서 실행하고 싶을때)](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/%23-%EB%AC%B8%EC%84%9C-%ED%9D%90%EB%A6%84-%EB%B0%8F-%EA%B0%80%EC%9D%B4%EB%93%9C%EB%9D%BC%EC%9D%B8.#1-jupyter-elyra) 를 먼저 한 번 읽어보고 시작하는 것을 추천한다.<br/>

  1) Elyra가 실제로 pipeline을 어떤 형태로 저장하고, 실행 단계에서 전달 및 처리하는지, 메타데이터는 어떻게 관리하는지, 실제로 파이프라인이 실행되는 과정이 어떻게 구성되어있는지 설명한다.<br/>
  [ Elyra 리소스 자료구조 ](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/Elyra-%EB%A6%AC%EC%86%8C%EC%8A%A4-%EC%9E%90%EB%A3%8C%EA%B5%AC%EC%A1%B0)<br/>
  [ Elyra 동작 과정에서 관여하는 코드 리뷰 ](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/Elyra-%EB%8F%99%EC%9E%91-%EA%B3%BC%EC%A0%95%EC%97%90%EC%84%9C-%EA%B4%80%EC%97%AC%ED%95%98%EB%8A%94-%EC%BD%94%EB%93%9C-%EB%A6%AC%EB%B7%B0)

  2) T3QDemoElyraProcessor도 Custom Processor 이다. **Custom Processor** 를 만들기 위해서 Elyra 파일의 어떤 리소스를 추가하거나, 수정 및 반영해야 하는지에 대해 설명한다.<br/>
  [ ElyraCustomProcessorDemo ](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/ElyraCustomProcessorDemo)

  3) 현재 Kubeflow Runtime의 불편한 점에 대해서 알아보고, 불편했던 점을 어떻게 개선했는지 대해서 파악한다.<br/>
  [ T3QDemoElyraProcessor ](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/T3QDemoElyraProcessor)

  4) 실제로 불편했던 점을 개선하기 위해서 Elyra의 어떤 리소스를 추가, 수정 및 반영했는지에 대해 설명한다.<br/>
  [ T3QDemoElyraProcessor 제작 ](http://lab.t3q.co.kr:9999/kaist-co-op/jupyterwithelyraproject/-/wikis/T3QDemoElyraProcessor%EC%A0%9C%EC%9E%91)

(별도로 custom processor 를 제작하고자 한다면, 같은 방식으로 만들되, processor 등의 내용은 새롭게 구현해주어야 한다.)
