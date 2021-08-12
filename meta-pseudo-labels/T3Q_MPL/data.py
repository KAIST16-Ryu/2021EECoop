import logging
import math
import os
import numpy as np
from PIL import Image
import torchvision
from torchvision import datasets
from torchvision import transforms
from torch.utils.data import DataLoader
from torch.utils.data import Dataset
from augmentation import RandAugment
import pandas as pd
import torchvision.transforms.functional as F
import torch

logger = logging.getLogger(__name__)
pil_logger = logging.getLogger('PIL')
pil_logger.setLevel(logging.INFO)

normal_mean = (0.5, 0.5, 0.5)
normal_std = (0.5, 0.5, 0.5)

def cal_mean_std(data_path, data_name, tm):
    train_labeled_dataset = torchvision.datasets.ImageFolder(os.path.join(data_path,data_name,'labeled_data'),transform= transforms.Compose([transforms.ToTensor()]))
    meanRGB = [np.mean(x.numpy(),axis=(1,2)) for x,_ in train_labeled_dataset]
    stdRGB = [np.std(x.numpy(),axis=(1,2)) for x,_ in train_labeled_dataset]
    meanR = np.mean([m[0] for m in meanRGB])
    meanG = np.mean([m[1] for m in meanRGB])
    meanB = np.mean([m[2] for m in meanRGB])

    stdR = np.mean([s[0] for s in stdRGB])
    stdG = np.mean([s[1] for s in stdRGB])
    stdB = np.mean([s[2] for s in stdRGB])

    return (meanR, meanG, meanB), (stdR, stdG, stdB)


def get_data(tm):
    resize = int(tm.param_info['resize'])
    data_name = str(tm.param_info['dataset'])
    data_path= tm.train_data_path
    #data_mean,data_std = cal_mean_std(data_path, data_name, tm)
    transform_labeled = transforms.Compose([
        ###################you can delete here#########################
        transforms.RandomHorizontalFlip(),
        ############################################################
        
        transforms.RandomCrop(size=resize,
                              padding=int(resize*0.125),
                              padding_mode='reflect'),
        transforms.ToTensor(),
        transforms.Normalize(normal_mean, normal_std)])

    transform_val = transforms.Compose([
        transforms.Resize((resize,resize)),
        transforms.ToTensor(),
        transforms.Normalize(normal_mean, normal_std)])

    ##################### for test########################################################
    '''
    train_set = torchvision.datasets.ImageFolder(os.path.join(data_path,data_name,'labeled_data'),transform= transform_val)
    sample=[]
    for i in train_set.samples:
        sample.append(i[0])
    

    train_labeled_idxs, train_unlabeled_idxs = x_u_split(tm, train_set.targets)
    
    
    train_labeled_dataset = SSL(
        sample, train_set.targets, indexs=train_labeled_idxs, 
        transform=transform_labeled
    )

    train_unlabeled_dataset = SSL(
        sample, train_set.targets, indexs=train_unlabeled_idxs, 
        transform=TransformMPL(tm, normal_mean, normal_std)
    )
    '''
    #######################################################################################3
    
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

######################for test############################
'''
def x_u_split(tm, labels):
    num_labeled = int(tm.param_info['num_labeled'])
    num_classes = int(tm.param_info['num_classes'])
    expand_labels = bool(tm.param_info['expand_labels'])
    batch_size = int(tm.param_info['batch_size'])
    eval_step = int(tm.param_info['eval_step'])

    label_per_class = num_labeled // num_classes
    labels = np.array(labels)
    labeled_idx = []
    # unlabeled data: all training data
    unlabeled_idx = np.array(range(len(labels)))
    for i in range(num_classes):
        idx = np.where(labels == i)[0]
        idx = np.random.choice(idx, label_per_class, False)
        labeled_idx.extend(idx)
    labeled_idx = np.array(labeled_idx)
    assert len(labeled_idx) == num_labeled

    if expand_labels or num_labeled < batch_size:
        num_expand_x = math.ceil(
            batch_size * eval_step / num_labeled)
        labeled_idx = np.hstack([labeled_idx for _ in range(num_expand_x)])
    np.random.shuffle(labeled_idx)
    return labeled_idx, unlabeled_idx
'''
################################################################################

########you can change transform component if you want################
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
#############################################################################

class UnlabeledDataset(Dataset):
    
    def __init__(self, root_dir, transform):
        self.root_dir = root_dir
        self.all_imgs = os.listdir(root_dir)
        self.transform = transform

    def __len__(self):
        return len(self.all_imgs)

    def __getitem__(self, index):
        img_path = os.path.join(self.root_dir, self.all_imgs[index])
        img = Image.open(img_path).convert("RGB")
        img_transformed = self.transform(img)

        return img_transformed
        
class UnlabeledDatasetwithPath(Dataset):
    
    def __init__(self, root_dir, transform):
        self.root_dir = root_dir
        self.all_imgs = os.listdir(root_dir)
        self.transform = transform

    def __len__(self):
        return len(self.all_imgs)

    def __getitem__(self, index):
        img_path = os.path.join(self.root_dir, self.all_imgs[index])
        img = Image.open(img_path).convert("RGB")
        img_transformed = self.transform(img)
        return img_transformed, img_path

##################for test###################################
'''
class SSL(Dataset):
    def __init__(self, images, labels, indexs, transform=None, target_transform=None):
        self.data = np.array(images)
        self.targets = np.array(labels)
        self.transform = transform
        self.target_transform =target_transform
        if indexs is not None:
            self.data = self.data[indexs]
            self.targets = np.array(self.targets[indexs])
         
    def __len__(self):
        return (len(self.data))
    
    def __getitem__(self, i):
        img = self.data[i]
        target = self.targets[i]
        #logger.warning(type(img))
        #img = np.asarray(img).astype(np.uint8).reshape(28, 28, 1)
        #img = img.reshape(28,28)
        img = Image.open(img)
        img = img.convert('RGB')
        img = np.asarray(img)
        #img = img.reshape(224,224)
        img = Image.fromarray(img)
        
        if self.transform is not None:
            img = self.transform(img)

        if self.target_transform is not None:
            target = self.target_transform(self.target)
            
        if self.targets is not None:
            return (img, target)
        else:
            return img
'''
#################################################################

