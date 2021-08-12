## UDA(Unsupervised Data Augmentation)

![image](https://user-images.githubusercontent.com/84768279/127807887-0a3ff472-3b13-45fc-8248-c5401ea80f8c.png)

UDA는 semi-supervised learning 기법 중 하나로, **augmentation**을 이용하여 training 한다. 이 또한 **[consistency regularization](Consistency Regularization)** 을 이용하는 방법 중 하나이다. 

> consistency regularization: 모델의 input 에 augmentation을 가해서 새로운 input을 만들었을 때, output(prediction)이 유사해야 한다는 가정을 바탕으로 모델을 regularize 하는 방법

그림을 보면 알 수 있듯이, UDA는 labeled data의 cross-entropy loss와 unlabeled data에 data augmentation을 적용하여 얻은 consistency loss의 합을 최종 loss로 계산하여 이 값을 줄여나가는 방식으로 model을 train한다. 
