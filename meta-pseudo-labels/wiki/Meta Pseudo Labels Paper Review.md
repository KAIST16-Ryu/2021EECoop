전체 논문을 보고 싶다면 [여기](https://arxiv.org/pdf/2003.10580v4.pdf). 이 논문을 바탕으로 작성된 글이다.

이 글을 읽기전 [이글](UDA)을 읽고 오는 것을 추천한다.

---

Meta Pseudo Labels란 semi-supervised Learning method 중 하나로, 이를 아주 간단하게 도식화하면 다음과 같다.

![image](https://user-images.githubusercontent.com/84768279/127601205-e3fca04e-bb1e-47bb-89e5-701a47b3c985.png)

위의 그림에서 볼 수 있듯이 Meta Pseudo Labels 알고리즘은 **teacher model**과 **student model**, 총 2개의 학습 모델을 사용한다. Teacher model은 student model에게 **pseudo label**을 제공하고, student model은 그로부터 loss를 구해 학습한다. 그리고 teacher model 또한 student model의 **향상정도**를 바탕으로 학습한다. (여기서 향상정도라는 단어표현이 조금 모호하지만 뒤에서 구체적으로 설명하겠다.)

조금 더 구체적으로 살펴보기 위해 두 model이 loss를 각각 어떻게 계산하는지 알 필요가 있다. <br/>

![image](https://user-images.githubusercontent.com/84768279/127601214-5d1a36ed-291c-4d61-8152-6f6fff1646fc.png)

#### Student model loss
: Student loss를 계산할 때는 labeled data가 사용되지 않고 오직 **unlabeled data**로만 구해진다. Unlabeled data를 사용하므로 따로 정답 label이 없다. 대신 teacher model의 pseudo label을 target으로 하여 loss를 계산한다. 정답 label 대신 pseudo label을 사용한다라는 사실 말고는 일반적인 model loss 계산하는 것과 크게 다를바가 없다.

#### Teacher model loss
: Teacher loss는 student가 update된 이후에 계산되는데, 이때 labeled data가 사용된다. 먼저 student model이 update하기 전에 labeled data에 대한 prediction을 구하고, update 된 이후에 같은 data에 대한 prediction을 구해 그 둘의 loss를 이용하여 teacher loss를 계산한다. 앞에서 **향상정도**라 표현한 것이 student model의 update 전후의 차이를 계산하는 것이기 때문에 이렇게 표현했다.

MPL을 구체적으로 도식화하면 다음과 같다.

![image](https://user-images.githubusercontent.com/84768279/127972564-a40f442b-4db2-4ee1-a220-c4fb09b2e5b1.png)

그런데 그림을 보면 의문이 하나 생긴다. Teacher model에 **labeled data**가 쓰이는 것을 확인할 수 있다. 앞에서 알려준 student model과 teacher model의 loss 계산법을 보면 teacher이 labeled data에 대해 prediction을 구하고 target과의 loss를 구하는 부분이 없다. 어찌된 일일까?

앞에서 설명한 loss 계산법은 **순수한 MPL loss** 계산법이다. 하지만 본 논문에서는 MPL 뿐만 아니라 model의 성능향상을 위해 [**UDA method**](UDA)도 사용한다.

![image](https://user-images.githubusercontent.com/84768279/127981771-ae5ac3f4-6862-4ba8-9f3e-321b414bf766.png)

UDA method는 teacher model을 train할 때 사용된다. 조금 어려울 수 있는데, 수식으로 나타내면 다음과 같다.

`teacher loss = teacher mpl loss + teacher uda loss`

teacher mpl loss는 앞에서 말했듯이 student model의 향상정도를 이용하여 계산된다. (다른 계산들도 필요하지만 여기서는 넘어가도록 하자)
**teacher uda loss**는 student model와는 독립적으로 teacher model에 대해 uda loss를 계산한 것이다. uda loss를 계산하기 위해 labeled data와 unlabeled data 둘 다 사용된다. <br/>
`teacher uda loss = supervised cross entropy loss + weight * unsupervised consistency loss`
> UDA method <br/>
![image](https://user-images.githubusercontent.com/84768279/127980505-b5375416-f512-4ccd-9975-0ccf2338c9c7.png) <br/>
그림 상에서는 **M** model이 teacher model이 될 것이며, **Final loss**가 teacher model의 uda loss가 될 것이다.

즉, teacher model은 student model의 향상정도와 teacher model의 UDA final loss를 바탕으로 최종 loss를 계산하고 update된다.

### 정리

정리하면 다음과 같다.

![image](https://user-images.githubusercontent.com/84768279/127806713-43acad48-16cf-4ff1-8218-7043525c2f79.png)

1. 먼저 teacher의 unlabeled data에 대한 pseudo label을 target으로 하여 student가 augmented unlabeled data의 predicted 결과와의 loss를 계산한다.
2. student가 계산한 loss로 student model이 updated된다.
3. updated되기 전 student model과 updated 된 student model 각각의 labeled data에 대한 predict 결과의 loss를 계산하고 그 차를 teacher의 loss 계산에 넘겨준다.
4. teacher의 loss는 크게 2가지 loss가 더해진다. `t_loss = t_loss_uda+t_loss_mpl`. 여기서 `t_loss_mpl`를 계산하는 과정에서 3번에서 계산된 student model의 labeled data에 대한 loss의 차가 사용된다. 그리고 `t_loss_uda`를 계산하는 과정에서 UDA 알고리즘이 사용된다. 그리고 `t_loss`로 teacher model을 update한다.

