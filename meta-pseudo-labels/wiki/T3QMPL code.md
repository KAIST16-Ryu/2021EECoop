앞서서 설명한 [본래 코드](MPL 코드 분석)를 활용하여 실제 T3Q platform에 탑재하여 많은 unlabeled dataset과 적은 labeled dataset이 있을 때 MPL 알고리즘을 통해 training하는 코드를 만들어 보았다.

T3Q Platform에서 알고리즘을 탑재하기 위해 생성해야하는 것은 총 3가지이다.
1. 실행환경
2. 전처리모듈
3. 학습알고리즘

플랫폼 상에서 추가해 준 환경, 모듈, 알고리즘이 무엇인지 알려주고, 각각에 대해 설명하겠다.

# 1. 실행환경

![image](https://user-images.githubusercontent.com/84768279/128146458-8d4d96f4-9f7c-411a-b94b-949ff5b3b1c3.png)

T3Q platform 실행환경 중 mpl_test라는 이름으로 등록했다. mpl_test의 requirements로 추가한 것들은 아래와 같다.

- torch==1.8.1
- torchvision==0.9.1
- tensorflow

이외에 tensorboard와 tqdm도 추가되어있는데 이 모듈들을 사용안하는 코드로 바꾸었기 때문에 필요 없다.

# 2. 전처리모듈

![image](https://user-images.githubusercontent.com/84768279/128147018-d5985c87-0eb7-462c-964a-3a0078317baa.png)

T3Q platform 전처리모듈 중 mpl_test라는 이름으로 등록했다.
- 모듈명: mpl_test
- 파일: run.py
- 역할: dataset 압축 해제 코드

![image](https://user-images.githubusercontent.com/84768279/128147211-c8d8937d-8fca-4782-866c-54f2021624e1.png)

### Input dataset

원본 코드와 달리 우리는 실제 unlabeled data와 labeled data를 input data로 넣어주어야 한다. 그래서 아래와 같은 구조의 dataset 압축파일을 T3Q platform에 등록하고 mpl_test 전처리 코드를 통해 압축을 해제하여 다음 학습알고리즘에서 사용할 수 있도록 한다.

![image](https://user-images.githubusercontent.com/84768279/128147532-1f432c77-9b9b-4ca7-9603-58777e563087.png)

추가적으로 test data가 존재하면 test data 폴더도 생성해야한다. 그 형태는 labeled data 폴더와 유사하다.

input 폴더를 생성하는 법은 [사용자 가이드](사용자 가이드)에 설명해두었다.


# 3. 학습알고리즘

![image](https://user-images.githubusercontent.com/84768279/128817270-e43d0ad4-15fe-41b3-84b3-7bb878397c5e.png)

T3Q platform 학습알고리즘 중 mpl_semifinal이라는 이름으로 등록했다.
- 모듈명: mpl_semifinal
- 파일: augmentation.py, data.py, main.py(실행모듈), models.py, utils.py

## 파일 구성

![image](https://user-images.githubusercontent.com/84768279/128817258-cd17b27a-451d-4277-9dfd-8e5dcfed0076.png)

- augmentation.py : data에 가하는 augmentation 설정
- data.py : augmentation을 가한 dataset 생성
- main.py : MPL 알고리즘을 구현한 main 코드로 train을 진행한다.
- models.py : ModelEMA와 WideResNet 구현
- utils.py : utils 코드

학습알고리즘의 parameter에 대해 궁금하다면 [여기](parameter)

## main.py

본래 코드와 달라진 함수는 크게 4가지가 있다.
1. train_loop
2. evaluate
3. auto-labeling
4. train

일단 우선, 플랫폼 탑재를 위해 수정한 코드이므로 모든 함수에 tm객체를 인자로 받는다. 그리고 원래 코드에서의 main함수는 train함수로 이름을 변경해주었다. 

이제 각 함수들을 살펴보도록 하자.

#### train_loop
main.py에서 가장 중요한 MPL 알고리즘을 구현한 부분이기 때문에 수정할 부분이 크게 없다. 다만, 원래 코드에서와 달리 unlabeled data에 label이 존재하지 않기 때문에 다음과 같이 수정해주었다.
(원래 코드에서는 unlabeled data가 따로 주어진 것이 아닌, label이 되어있는 data에서 label만 제거하여 사용했었다.)

```python
# 본래 코드
        try:
            (images_uw, images_us), _ = unlabeled_iter.next()

        except:
            unlabeled_iter = iter(unlabeled_loader)
            
            (images_uw, images_us), _ = unlabeled_iter.next()

```
에서

```python
# 바꾼 코드
        try:
            (images_uw, images_us) = unlabeled_iter.next()

        except:
            unlabeled_iter = iter(unlabeled_loader)
            
            (images_uw, images_us) = unlabeled_iter.next()

```
로 변경해주었다.

#### evaluate
원래 코드에서는 test data가 존재해 test data를 통해 evaluation을 진행했었다. 하지만 본 코드에서는 test data가 존재하지 않을 수 있다. test data가 있을 때는 해당 data로 evaluation을 진행하지만 없는 경우에는 labeled data로 진행한다. labeled data로 evaluation을 진행할 경우, accuracy가 test data로 진행했을 때 보다 더 높게 나온다.

#### auto-labeling
unlabeled dataset에 training 된 model로 labeling을 진행하여 zip파일로 tm.model_path에 저장한다.  사실 model training을 목표로 바꾸었기때문에 labeling을 따로 진행할 필요는 없지만 나중을 위해 만들어놓았다.

#### train
해당 함수에서는 model이나 dataset, optimizer등을 선언한다. 이때, 본래 코드에서는 model을 WideResnet 하나만 사용했는데, 이때 model을 다양하게 쓸 수 있도록 하기 위해 parameter로 model의 이름을 str로 받아 정의된 model을 쓸 수 있게 만들었다. 또한, 뒤에 model.py에서 언급하겠지만, 사용자가 정의한 model을 쓸수 있도록 했는데, 해당 model은 MyModel이라는 class로 정의했다. 해당 model도 사용할 수 있도록 했다.

```python

###you can add your own argument in model###############
    if model_name == "MyModel":
        teacher_model = MyModel()
        student_model = MyModel()
#########################################################3

    elif model_name == "resnet18":
        teacher_model = models.resnet18(num_classes=my_num_classes)
        student_model = models.resnet18(num_classes=my_num_classes)

    elif model_name == "vgg19":
        teacher_model = models.vgg19(num_classes=my_num_classes)
        student_model = models.vgg19(num_classes=my_num_classes)

    else: ##default is wideresnet
        teacher_model = models.wide_resnet50_2(num_classes=my_num_classes)
        student_model = models.wide_resnet50_2(num_classes=my_num_classes)


    logger.info(f"Model: {model_name}")
```

## augmentation.py
이 부분은 사용자가 원하는대로 augmentation 기법 종류를 추가하거나 삭제할 수 있다. 아래의 부분에 새로운 augmentation 기법을 list에 추가하거나 주석처리를 하면 된다. <br/>

```python
def rand_augment_pool():
    augs = [(AutoContrast, None, None),
            (Brightness, 1.8, 0.1),
            (Color, 1.8, 0.1),
            (Contrast, 1.8, 0.1),
            (CutoutConst, 40, None),
            (Equalize, None, None),
            (Invert, None, None),
            (Posterize, 4, 0),
            (Rotate, 30, None),
            (Sharpness, 1.8, 0.1),
            (ShearX, 0.3, None),
            (ShearY, 0.3, None),
            (Solarize, 256, None),
            (TranslateXConst, 100, None),
            (TranslateYConst, 100, None),
            ]
    return augs
```

> augmentation의 경우 MPL 알고리즘 내에서 data의 augmentation을 진행해주는데, 이때 데이터셋의 종류에 따라 training에 영향을 끼치는 augmentation이 있을 수 있으므로 이떄는 수동으로 주석처리를 해주는게 좋다. 아래와 같은 경우에는 좌우반전 augmentation이 training에 치명적인 영향을 끼칠 수 있다. <br/>
>![image](https://user-images.githubusercontent.com/84768279/128141766-8be4667b-d0ab-44ed-8f19-0868be8929a0.png)

## data.py
우선 살펴봐야 할 것은 크게 2가지 이다.
1. transform
2. unlabeled data

### Transform
우선 본래 코드에서 transform은 크게 3개, `transform_labeled`, `transform_val`, 그리고 `TransformMPL`이 있었다. 여기서 위의 augmentation에서 언급했던 것처럼 단순 flip transform도 모델 training에 치명적인 영향을 끼칠 수 있다. 고로 각 transform들의 component를 상황에 따라 수정할 필요가 있다. 

### Unlabeled data
원본 코드와는 달리 우리는 unlabeled dataset이 실제로 존재하는 경우를 다룬다. 고로, dataset을 download하고 transform하는 방법이 조금 달라질 수 밖에 없다. 

원본 코드에서는 `CIFAR10SSL` class를 통해 transform을 적용한 dataset들을 만들었다. 하지만 이 class를 계속 사용하기에는 여러가지 문제가 있다. 우선 `CIFAR10SSL`은 `torchvision.datasets.CIFAR10` class를 상속받는다. 고로 `datasets.CIFAR10`으로 download 받는 data가 아닌 이상 해당 class는 사용할 수 없다. 고로 새로 `UnlabeledDataset` class를 생성했다. 추가로 main.py함수에서 auto-labeling을 위해 dataset의 경로가 필요한데 이를 위한 `UnlabeledDatasetwithPath` class도 생성해주었다.

이렇게 생성한 두 class를 이용하여 다음과 같이 labeled dataset, unlabeled dataset, test dataset 그리고 unlabeled dataset을 labeling 하기 위해 경로를 포함하고있는 unlabeled dataset을 생성해주었다.

```python
    ####################for real case#####################################
    train_labeled_dataset = torchvision.datasets.ImageFolder(os.path.join(data_path,data_name,'labeled_data'),transform= transform_val)
    train_unlabeled_dataset = UnlabeledDataset(os.path.join(data_path,data_name,'unlabeled_data'),transform=TransformMPL(tm, normal_mean, normal_std))
    ##################################################################
    
    if os.path.exists(os.path.join(data_path,data_name,'test_data')):
        test_set = torchvision.datasets.ImageFolder(os.path.join(data_path,data_name,'test_data'), transform = transform_val)
    else:
        test_set = torchvision.datasets.ImageFolder(os.path.join(data_path,data_name,'labeled_data'), transform = transform_val)

    labeling_set = UnlabeledDatasetwithPath(os.path.join(data_path,data_name, 'unlabeled_data'), transform = transform_val)

    return train_labeled_dataset, train_unlabeled_dataset, test_set, labeling_set
```

## models.py
원본 models.py에서는 크게 2가지 class를 정의했다.

1. ModelEMA
2. WideResNet

여기서 실제 teacher 및 student model로 사용되는 WideResNet의 경우, 학습에 있어서 사용자가 원하면 다른 model로 바꿀 수 있다. 그래서 WideResNet 대신 `MyModel`이라는 class를 정의해주었다. `MyModel` class로 원하는 model을 정의하면, main.py에서 아래와 같이 해당 model을 통해 training 할 수 있도록 되어있다.

```python
if model_name == "MyModel":
    teacher_model = MyModel()
    student_model = MyModel()
```


