Semi-supervised learning(준지도학습)이란, **labeled data와 unlabeled data 모두를 이용**하여 training하는 것을 의미한다. 준지도학습이 등장하게 된 배경에는 어떤 것이 있을까?
 
일반적으로 우리가 알고 있는 머신러닝은 **Supervised learning**(지도학습)을 바탕으로 하고 있다.

# Supervised Learning

![image](https://user-images.githubusercontent.com/84768279/127954010-49b7b6b0-dcfd-45d1-acbe-bdf76c2a71d6.png)

지도학습은 **레이블링**이 되어있는 data들을 가지고 model을 학습시키는 것을 의미한다. 그러나 문제는 **레이블링**이다. 세상에는 수많은 data들이 존재하는데, model의 학습을 위해 이 data들에 사람이 하나하나 labeling하기에는 너무 많은 시간과 비용이 든다. 그렇게해서 등장한 것이 **Semi-supervised learning**이다.

# Semi-supervised Learning

![image](https://user-images.githubusercontent.com/84768279/127953987-c71ddff6-1818-4eeb-93e0-ab8920cca8d7.png)

앞에서 설명했듯이, Semi-supervised learning이란 labeled data와 unlabeled data 모두를 이용하여 training하는 것을 의미한다. 일반적으로, 준지도학습에서는 적은 양의 labeled data와 많은 양의 unlabeled data를 가지고 model을 train한다. 그렇기 때문에 Supervised learning보다 더 적은 labeling 만으로 머신러닝을 진행할 수 있어 **레이블링에 드는 시간과 비용을 절감**할 수 있다. 지금까지도 많은 사람들이 더 성능이 좋은 Semi-supervised learning 기법을 찾기 위해 연구하고 있다. 

SSL method에는 다음과 같은 것들이 있다. 각 method들에 대해 자세하게 알 필요는 없지만 각 method의 논문을 링크로 걸어두었다. 알아두어서 나쁘지 않을 것 같다.

### - Old Method
아래의 method들은 비교적 옛날에 나온 method들이라 old method라 칭하겠다.
  - Self-training
  - [Co-training (1998)](https://www.cs.cmu.edu/~avrim/Papers/cotrain.pdf)
  - [Democratic co-learning (2004)](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.76.3152&rep=rep1&type=pdf)
  - [Tri-training (2005)](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.487.2431&rep=rep1&type=pdf)


### - Current Method
Old Method라 칭한 기법들과는 달리, current method에서는 **[Consistency Regularization](Consistency Regularization)** 기법을 이용하여 만들어진 method들이 많다. 다른 구체적인 method들은 크게 볼 필요는 없지만 최근 Semi-supervised Learning method들에 많이 쓰이는 **Consistency Regularization**이 무엇인지는 알고 넘어가야할 필요가 있다.

  - [π-model (2017)](https://arxiv.org/pdf/1610.02242.pdf)
  - [Mean-teacher (2017)](https://arxiv.org/pdf/1703.01780.pdf)
  - [MixMatch (2019)](https://arxiv.org/pdf/1905.02249.pdf)
  - [Self-Supervised Semi-Supervised Learning (S4L) (2019)](https://openaccess.thecvf.com/content_ICCV_2019/papers/Zhai_S4L_Self-Supervised_Semi-Supervised_Learning_ICCV_2019_paper.pdf)
  - [Cow Mask (2020)](https://arxiv.org/pdf/2003.12022.pdf)
  - [Big Self-Supervised Learning (2020)](https://arxiv.org/pdf/2006.10029.pdf)
  - [Meta Pseudo Labels (2020)](Meta Pseudo Labels 논문 리뷰)

