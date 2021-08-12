이글에서는 T3Q MPL 코드에서 사용자가 알아야 할 부분, 혹은 수정할 수 있는 부분에 대해 따로 다루었다. 다른 내용은 몰라도 해당부분만 알고 수정하면 T3Q MPL 코드를 잘 사용할 수 있지 않을까 한다.

다음과 같은 순서로 설명하겠다.

- Input dataset 생성방법
- MyModel: 사용자 정의 Model 생성 및 사용법
- Augmentation: 사용자 정의 data augmentation 적용법

# Input dataset 생성방법

MNIST dataset을 예시로 들어보자.

1. MNIST: labeled_data, unlabeled_data, (있다면 test_data)로 폴더명을 정한다.
이때 dataset의 이름으로 폴더명을 정하도록 하자. Ex) MNIST <br/>
![image](https://user-images.githubusercontent.com/84768279/128147817-d04a6db1-7f82-4f49-9bcf-d0e2bcfadee4.png)

2. MNIST\labeled_data: 각 이미지들의 label을 폴더이름으로 하여 이미지들을 넣어준다. 
(있다면 MNIST\test_data도 같은 형태로 구성한다.) <br/>
![image](https://user-images.githubusercontent.com/84768279/128147903-1c775117-5fe7-44b3-9fd5-ac1ef25fd9b9.png)

3. MNIST\labeled_data\0,1,2,3,4,5,6,7,8,9, MNIST\unlabeled_data 폴더 안에 각 label에 해당하는, 혹은 unlabeled된 image file을 넣어준다. <br/>
![image](https://user-images.githubusercontent.com/84768279/128147965-8d6632ec-8ddb-49b9-b961-3f934dceadb0.png)

4. MNIST.zip으로 압축한다.

# MyModel
T3Q MPL 코드에서 기본적으로 제공하는 model은 **torchvision.models**에서 제공하는 model들 중 **resnet18**, **vgg19**, **wideresnet**이다. 그리고 추가적으로 *model_name* parameter에 MyModel을 입력하면 사용자가 정의한 model을 사용할 수 있다. 사용자는 `MyModel`을 model.py에서 정의할 수 있다. 해당 부분은 다음과 같다.

```python

#############you can make your own model#################
class MyModel(nn.Module):
    def __init__(self):
        super(MyModel, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=20, 
                               kernel_size=5, stride=1)
        self.conv2 = nn.Conv2d(in_channels=20, out_channels=50, 
                               kernel_size=5, stride=1)
        self.fc1 = nn.Linear(in_features=50, out_features=500)
        self.fc2 = nn.Linear(in_features=500, out_features=10)
    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2, 2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2, 2)
        x = F.adaptive_avg_pool2d(x, 1)
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x
#################################################################
```

# Augmentation
augmentation이 이루어지는 곳은 총 2곳이 있다.

1. augmentation.py
2. data.py

### augmentation.py
먼저 augmentation.py에서의 경우 여러가지 augmentation 기법을 추가하거나 삭제하여 사용할 수 있다했었다. 그 중 아래의 코드 부분에서 수정이 이루어질 수 있는데,
```python

###############you can change augs component if you want###############
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
#############################################################################
```
augs의 list를 Random하게 적용하는 것이기 때문에 해당 list의 요소들을 추가하거나 제거해주면 된다.

2. data.py
data.py에서는 data를 받고 원하는 transform을 적용한 dataset을 생성한다. 이때, transform의 형태를 조절함으로써 augmentation을 조절할 수 있다. data.py에서는 총 3개의 transform이 정의되어 있는데, `transform_labeled`, `transform_val`, 그리고 `TransformMPL`이 그것이다. 

##### transform_labeled
```python
    transform_labeled = transforms.Compose([
        transforms.RandomHorizontalFlip(),
        transforms.RandomCrop(size=resize,
                              padding=int(resize*0.125),
                              padding_mode='reflect'),
        transforms.ToTensor(),
        transforms.Normalize(normal_mean, normal_std)])
```
##### transform_val
```python
    transform_val = transforms.Compose([
        transforms.Resize((resize,resize)),
        transforms.ToTensor(),
        transforms.Normalize(normal_mean, normal_std)])
```
##### TransformMPL
```python
class TransformMPL(object):
    def __init__(self, tm, mean, std):
        resize = int(tm.param_info['resize'])
        rand_num = int(tm.param_info['rand_num'])
        rand_val = int(tm.param_info['rand_val'])


        self.ori = transforms.Compose([
            transforms.RandomHorizontalFlip(),
            transforms.RandomCrop(size=resize,
                                  padding=int(resize*0.125),
                                  padding_mode='reflect')])
        self.aug = transforms.Compose([
            transforms.RandomHorizontalFlip(),
            transforms.RandomCrop(size=resize,
                                  padding=int(resize*0.125),
                                  padding_mode='reflect'),
            RandAugment(n=rand_num, m=rand_val)  
            ])
        self.normalize = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std)])

    def __call__(self, x):
        ori = self.ori(x)
        aug = self.aug(x)
        return self.normalize(ori), self.normalize(aug)
```

해당 코드 부분을 적절히 수정하면 dataset에 원하는 tranform을 가할 수 있다.
