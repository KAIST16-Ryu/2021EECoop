git에 올라와있는 MPL코드를 일부 수정하여 플랫폼에서 사용할 수 있는 T3Q MPL 코드를 작성하였다. 실제 플랫폼상에서 실행했을 때 잘 작동했으나, 일부 해결하지 못한 issue들이 존재한다. Issue는 다음과 같다.

1. checkpoint를 저장하는 코드를 제거하지는 않았다. 그리고 기존 MPL 코드에서는 argument 중에 `resume`이라는 값을 받았는데 이는 저장된 checkpoint부터 다시 training하도록 하는 parameter이다. 하지만 checkpoint를 tm.mode_path에 저장하도록 작성은 했지만 플랫폼 상에서 어떻게 다시 이 경로에 접근하여 해당 checkpoint부터 다시 학습을 진행할 수 있는지는 플랫폼 구조에 대한 이해가 부족해 해결하지 못했다.
=> 즉, 현 T3Q MPL 코드는 checkpoint 저장 및 해당 checkpoint에서 학습 재개 기능이 없다.

2. resize의 크기가 너무 크면 memory error가 뜬다. <br/>
![image](https://user-images.githubusercontent.com/84768279/128659896-8ba84f70-1120-4c52-b446-8132cc3bbb39.png)

3. 실제 적용해볼 data가 없어 아직까지는 MNIST와 CIFAR10 dataset으로만 실험해보았다. 

4. 해당 알고리즘을 적용하기 위해 필요한 최소 data의 양을 알아야 할 필요가 있다. 실험할 때에는 46000개의 unlabeled data와 4000개의 labeled data를 사용했다. 

## 희망 시나리오
초기의 목표는 online-training 환경상에서의 auto-labeling model을 만드는 것이다. 만약 지속적으로 input data가 들어오는 환경이라면 아래와 같은 시나리오로 model이 train 될 수 있다면 좋을 것이다. 지금 플랫폼에 올라가 있는 알고리즘은 일반적인 training처럼 특정 정적인 dataset을 등록하고 해당 dataset을 사용하는 것이다. 즉, data가 새로 유입되는 환경이 아니라 희망하는 시나리오처럼 구현하지는 못했다.

![image](https://user-images.githubusercontent.com/84768279/128663881-9e015c64-ef54-410f-a5d2-e4347c78a3a4.png)

위의 그림을 간단하게 설명하자면, 
- Day 1
1. 처음 unlabeled data가 들어왔을 때 사람이 직접 일부분에 대해 labeling을 진행한다.
2. 일부 labeling 된 data와 unlabeled data에 대해 meta pseudo labels을 진행하고 unlabeled data에 학습된 model로 auto-labeling을 진행한다.
3. Auto-labeling 된 data 중 error를 찾고 수정한다.
4. 3까지의 작업이 수행된다면, labeled data와 auto-labeled data 모두 labeled data로 볼 수 있다.
- Day 2
5. 4에서 얻은 labeled data와 새로 들어온 unlabeled data에 대해 MPL을 진행한다.
6. 3번과 4번 과정을 반복한다.

이와 같은 방법으로 계속 새로 들어오는 unlabeled data에 대해 model을 train할 수 있을 것이다.

하지만 여기에 크게 2가지 문제가 존재한다.
1. **Model Accuracy** <br/>
: 어떤 model이 학습되고 있다는 것을 수치로 확인하기 위해서 **accuracy**를 사용하는데, 이때 일반적으로 test data를 사용한다. 하지만 online-training 환경 상에서 test data를 제공하는 방법을 알아내지 못했다. 사용자가 직접 test를 위해 labeling을 진행해야 하지 않을까 한다.

2. **Finding Mislabeled Data** <br/>
: 위의 순서중 3번에서 auto-labeling 된 data 중 error를 찾고 수정한다고 말했다. 하지만 이 error를 찾을 때 사용자가 직접 수동으로 찾거나, error을 찾아주는 model을 또 구현해야하지 않을까 한다. 이 부분을 앞서서 **uncertainty**를 통해 해결해보고자 했으나 결과가 좋지 않았다.
