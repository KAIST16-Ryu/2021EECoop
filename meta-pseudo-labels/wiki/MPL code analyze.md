[Meta Pseudo Labels 논문](https://arxiv.org/pdf/2003.10580.pdf)에서 공식적으로 작성한 [코드](https://github.com/google-research/google-research/tree/master/meta_pseudo_labels)는 TPU 환경을 기반으로 하고있기 때문에 우리가 활용하기에 적합하지 않다고 판단했다. 

다행이도 github에 Meta Pseudo Labels를 구현한 다른 코드가 몇가지 존재했다. 그 중 MPL을 pytorch로 구현한 [이 코드](https://github.com/kekmodel/MPL-pytorch)를 사용하고자 한다. 본 MPL 코드를 활용하기에 앞서 간단하게 분석해보고자 한다.

# Requirements
- python 3.6+
- torch 1.7+
- torchvision 0.8+
- tensorboard
- wandb
- numpy
- tqdm

# 파일 구성
- augmentation.py : data에 가하는 augmentation 설정
- data.py : augmentation을 가한 dataset 생성
- main.py : MPL 알고리즘을 구현한 main 코드로 train을 진행한다.
- models.py : ModelEMA와 WideResNet 구현
- utils.py : utils 코드

Meta Pseudo Labels은 위와 같이 총 5개의 python script로 구현되었다. 이제 각 script가 어떤 역할, 기능을 하는지 알아보자.

## [main.py](https://github.com/kekmodel/MPL-pytorch/blob/main/main.py)

main.py에는 크게 주요한 함수 2가지가 존재한다.
- main 함수
- train_loop 함수

#### main
우선 main함수에서는 다음과 같은 작업들이 이루어진다.
1. GPU와 분산학습에 대한 설정
2. data.py에서 생성된 dataset으로부터 dataloader 생성
3. teacher & student model 및 optimizer, scheduler 등 선언
4. train하던 모델의 checkpoint가 있다면 불러온다.
5. train_loop 함수 실행

즉, train 할 환경과 data, model 등을 생성하는 과정이다.

#### train_loop
train_loop 함수에서 MPL의 핵심 알고리즘을 찾아볼 수 있다. train_loop에서 구현된 MPL의 전체 과정을 살펴보면 다음과 같다. (앞선 [Meta Pseudo Labels 논문 리뷰](Meta Pseudo Labels 논문 리뷰) 글에서 설명했지만 MPL에서 가장 중요한 내용이므로 한번 더 집고 간다.)

![image](https://user-images.githubusercontent.com/84768279/127806713-43acad48-16cf-4ff1-8218-7043525c2f79.png)

1. 먼저 teacher의 unlabeled data에 대한 pseudo label을 target으로 하여 student가 augmented unlabeled data의 predicted 결과와의 loss를 계산한다.
2. student가 계산한 loss로 student model이 updated된다.
3. updated되기 전 student model과 updated 된 student model 각각의 labeled data에 대한 predict 결과의 loss를 계산하고 그 차를 teacher의 loss 계산에 넘겨준다.
4. teacher의 loss는 크게 2가지 loss가 더해진다. `t_loss = t_loss_uda + t_loss_mpl` 여기서 `t_loss_mpl`를 계산하는 과정에서 3번에서 계산된 student model의 labeled data에 대한 loss의 차가 사용된다. 그리고 `t_loss_uda`를 계산하는 과정에서 UDA 알고리즘이 사용된다. 그리고 `t_loss`로 teacher model을 update한다.

## [augmentation.py](https://github.com/kekmodel/MPL-pytorch/blob/main/augmentation.py)
Augmentation은 다른 의도도 있을 수 있겠지만 가장 큰 목적은 **UDA** 알고리즘이다. Teacher loss를 구하기 위해서는 uda loss를 구해야하는데 uda 알고리즘에 data augmentation이 사용된다. 

코드를 보면 다음과 같이 여러가지 augmentation 기법이 사용되었음을 알 수 있다. <br/>
![image](https://user-images.githubusercontent.com/84768279/127984376-01778ca2-6eac-4cd2-922d-43a76e5b5a5a.png)
> 추가로 논문에서는 다음과 같이 상황에 따라 augmentation 기법의 종류를 수정해도 된다고 한다. <br/>
![image](https://user-images.githubusercontent.com/84768279/127984605-e4fad7e1-22ca-4c3d-8f9b-d3498b47d09c.png)

그리고 여러 augmentation 기법들을 random하게 적용하기 위해 **`RandAugment`** class를 생성했다.


## [data.py](https://github.com/kekmodel/MPL-pytorch/blob/main/data.py)
data.py에서 이루어지는 작업은 크게 3가지 이다.
1. dataset download
2. split train dataset for unlabeled data
3. dataset에 transform 적용

#### 1. dataset download
본 코드에서는 Cifar 10과 Cifar 100 dataset을 활용한다. 편의를 위해 Cifar10 dataset을 사용하는 case로 설명하도록 하겠다. data.py에서 cifar 10 dataset을 torchvision.datasets 함수를 통해 download한다. <br/>
`base_dataset = datasets.CIFAR10(args.data_path, train=True, download=True)`

#### 2. split train dataset for unlabeled data
하지만 다운받은 dataset은 전부 labeling이 되어있다. 하지만 실험을 위해서는 많은 양의 unlabeled data와 적은 양의 labeled data가 필요하다. 그래서 `x_u_split()`함수를 통해 앞에서 받은 `base_dataset`을 labeled data와 unlabeled data로 나누어준다. 이때, 두 그룹 모두 class가 편향되지 않도록 나누어주는 것 또한 `x_u_split()`함수의 역할이다. 하지만 이 함수는 새로 2개의 dataset을 생성하는 것이 아닌, index값을 리턴한다. (ex) labeled_data=[1,5] unlabeled_data=[0,2,3,4,6,7,8])

#### 3. dataset에 transform 적용
`CIFAR10SSL` class는 앞에서 `x_u_split()` 함수가 리턴한 index 값들과, transform 형태를 인자로 받아 Cifar10 dataset에 이를 적용한다. 
```python
    train_labeled_dataset = CIFAR10SSL(
        args.data_path, train_labeled_idxs, train=True,
        transform=transform_labeled
    )

    train_unlabeled_dataset = CIFAR10SSL(
        args.data_path, train_unlabeled_idxs, train=True,
        transform=TransformMPL(args, mean=cifar10_mean, std=cifar10_std)
    )
```
`train_labeled_dataset`은 cifar10 train dataset에서 labeled_data_index 의 data들만 뽑아 transform_labeled라는 normalize하는 transform을 적용한다.

`train_unlabeled_dataset`은 cifar10 train dataset에서 unlabeled_data_index의 data들만 뽑아 TransformMPL이라는 transform을 적용한다. 

[Meta Pseudo Labels 논문 리뷰](Meta Pseudo Labels 논문 리뷰)에서 언급했듯이 unlabeled data에 대해 augmentation을 적용하여 UDA loss를 계산한다고 했다. 그리고 그 random augmentation을 위해 작성한 코드가 **augmentation.py**의 `RandAugment` class이고, 이를 적용해주는 부분이 `TransformMPL` 이다. 

```python
class TransformMPL(object):

...

     return self.normalize(ori), self.normalize(aug)
```

TransformMPL의 return 값을 보면 2가지임을 알 수 있다. self.normalize(ori)가 labeled data 처럼 original한 data에 normalize만 해준것이며, self.normalize(aug)가 `RandAugment` class가 사용된 augmented data이다. 그래서 기존에 (img, target)의 형태였던 dataset이 TransformMPL을 거치면 ((original img, augmented img),target)의 형태를 가지게 된다. 

#### 정리
![image](https://user-images.githubusercontent.com/84768279/128127410-83ecca90-afff-4a81-9c43-c9dea05ae9d9.png)


## [models.py](https://github.com/kekmodel/MPL-pytorch/blob/main/models.py)
models.py에서는 크게 2가지 class를 정의했다.

1. ModelEMA
2. WideResNet

#### 1. ModelEMA
Meta Pseudo Labels 논문에 다음과 같은 글이 있다. <br/>
![image](https://user-images.githubusercontent.com/84768279/128129636-ed4562e6-1dff-4e23-ba73-4c019562702d.png)

ModelEMA는 밑줄 친 부분을 위해 생성된 class라 예상된다. RMSprop는 optimization 방법중 하나로, 해당 계산법에서 **exponentially weighted averages**, 줄여서 **EMA**가 사용된다. RMSprop optimization을 사용하고 싶을 때 이용되는 class이다. 

#### 2. WideResNet
WideResNet이라는 model을 구현한 부분으로, 본 코드에서 teacher model과 student model로 wideresnet을 사용했다.

## [utils.py](https://github.com/kekmodel/MPL-pytorch/blob/main/utils.py)
