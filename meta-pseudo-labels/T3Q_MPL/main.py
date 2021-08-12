import argparse
import logging
import math
import os
import random
import time
import shutil
import zipfile
import numpy as np
import torch
from torch.cuda import amp
from torch import nn
from torch.nn import functional as F
from torch import optim
from torch.optim.lr_scheduler import LambdaLR
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler
from torch.utils.data.distributed import DistributedSampler
from tqdm import tqdm
import torchvision.models as models
from data import get_data
from models import MyModel, ModelEMA
from utils import (AverageMeter, accuracy, create_loss_fn,
                   save_checkpoint, reduce_tensor, model_load_state_dict)

logger = logging.getLogger(__name__)

best_top1 = 0
best_top2 = 0
def set_seed(tm):
    seed = int(tm.param_info['random_seed'])
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def get_cosine_schedule_with_warmup(optimizer,
                                    num_warmup_steps,
                                    num_training_steps,
                                    num_wait_steps=0,
                                    num_cycles=0.5,
                                    last_epoch=-1):
    def lr_lambda(current_step):
        if current_step < num_wait_steps:
            return 0.0

        if current_step < num_warmup_steps + num_wait_steps:
            return float(current_step) / float(max(1, num_warmup_steps + num_wait_steps))

        progress = float(current_step - num_warmup_steps - num_wait_steps) / \
            float(max(1, num_training_steps - num_warmup_steps - num_wait_steps))
        return max(0.0, 0.5 * (1.0 + math.cos(math.pi * float(num_cycles) * 2.0 * progress)))

    return LambdaLR(optimizer, lr_lambda, last_epoch)


def get_lr(optimizer):
    return optimizer.param_groups[0]['lr']


def train_loop(tm, labeled_loader, unlabeled_loader, test_loader, labeling_loader,
               teacher_model, student_model, avg_student_model, criterion,
               t_optimizer, s_optimizer, t_scheduler, s_scheduler, t_scaler, s_scaler):
    
    global best_top1
    global best_top2
    name = str(tm.param_info['name'])
    model_path=tm.model_path
    save_path=model_path
    dataset = str(tm.param_info['dataset'])
    #num_labeled = int(tm.param_info['num_labeled'])
    total_steps = int(tm.param_info['total_steps'])
    eval_step = int(tm.param_info['eval_step'])
    start_step = int(tm.param_info['start_step'])
    ema = float(tm.param_info['ema'])
    grad_clip = float(tm.param_info['grad_clip'])
    threshold = float(tm.param_info['threshold'])
    temperature = float(tm.param_info['temperature'])
    lambda_u = float(tm.param_info['lambda_u'])
    uda_steps = float(tm.param_info['uda_steps'])
    amp_val = bool(int(tm.param_info['amp']))

    logger.info("***** Running Training *****")
    logger.info(f"   Task = {dataset}")
    logger.info(f"   Total steps = {total_steps}")


    labeled_iter = iter(labeled_loader)
    unlabeled_iter = iter(unlabeled_loader)

    for step in range(start_step, total_steps):
        if step % eval_step == 0:
            batch_time = AverageMeter()
            data_time = AverageMeter()
            s_losses = AverageMeter()
            t_losses = AverageMeter()
            t_losses_l = AverageMeter()
            t_losses_u = AverageMeter()
            t_losses_mpl = AverageMeter()
            mean_mask = AverageMeter()

        teacher_model.train()
        student_model.train()
        end = time.time()

        try:
            images_l, targets = labeled_iter.next()
        except:
            labeled_iter = iter(labeled_loader)
            images_l, targets = labeled_iter.next()
        
        try:
            ##test case#################
            #(images_uw, images_us), _ = unlabeled_iter.next()
            #images_uw: original, images_us: augmented
            
            ##real case#######################
            (images_uw, images_us) = unlabeled_iter.next()
            
            
        except:
            unlabeled_iter = iter(unlabeled_loader)
            
            ###test case##############
            #(images_uw, images_us), _ = unlabeled_iter.next()
            
            ##real case###############
            (images_uw, images_us) = unlabeled_iter.next()

        data_time.update(time.time() - end)

        if torch.cuda.is_available():
            device = torch.device('cuda', 0)
            images_l = images_l.to(device)
            images_uw = images_uw.to(device)
            images_us = images_us.to(device)
            targets = targets.to(device)

        else:
            device = torch.device('cpu')

        with amp.autocast(enabled=amp_val):
            batch_size = images_l.shape[0]
            t_images = torch.cat((images_l, images_uw, images_us))
            t_logits = teacher_model(t_images)
            t_logits_l = t_logits[:batch_size]
            t_logits_uw, t_logits_us = t_logits[batch_size:].chunk(2)
            del t_logits
            logger.info(get_lr(t_optimizer))
            t_loss_l = criterion(t_logits_l, targets)

            soft_pseudo_label = torch.softmax(t_logits_uw.detach()/temperature, dim=-1)
            max_probs, hard_pseudo_label = torch.max(soft_pseudo_label, dim=-1)
            mask = max_probs.ge(threshold).float()
            t_loss_u = torch.mean(
                -(soft_pseudo_label * torch.log_softmax(t_logits_us, dim=-1)).sum(dim=-1) * mask
            )
            weight_u = lambda_u * min(1., (step+1) / uda_steps)
            t_loss_uda = t_loss_l + weight_u * t_loss_u

            s_images = torch.cat((images_l, images_us))
            s_logits = student_model(s_images)
            s_logits_l = s_logits[:batch_size]
            s_logits_us = s_logits[batch_size:]
            del s_logits

            s_loss_l_old = F.cross_entropy(s_logits_l.detach(), targets)
            s_loss = criterion(s_logits_us, hard_pseudo_label)

        s_scaler.scale(s_loss).backward()
        if grad_clip > 0:
            s_scaler.unscale_(s_optimizer)
            nn.utils.clip_grad_norm_(student_model.parameters(), grad_clip)
        s_scaler.step(s_optimizer)
        s_scaler.update()    #student update
        s_scheduler.step()
        if ema > 0:
            avg_student_model.update_parameters(student_model)

        with amp.autocast(enabled=amp_val):
            with torch.no_grad():
                s_logits_l = student_model(images_l)
            s_loss_l_new = F.cross_entropy(s_logits_l.detach(), targets)
            dot_product = s_loss_l_old - s_loss_l_new
            _, hard_pseudo_label = torch.max(t_logits_us.detach(), dim=-1)
            t_loss_mpl = dot_product * F.cross_entropy(t_logits_us, hard_pseudo_label)
            t_loss = t_loss_uda + t_loss_mpl

        t_scaler.scale(t_loss).backward()  
        if grad_clip > 0:
            t_scaler.unscale_(t_optimizer)
            nn.utils.clip_grad_norm_(teacher_model.parameters(), grad_clip)
        t_scaler.step(t_optimizer)
        t_scaler.update()  # teacher update
        t_scheduler.step()

        teacher_model.zero_grad()
        student_model.zero_grad()

        s_losses.update(s_loss.item())
        t_losses.update(t_loss.item())
        t_losses_l.update(t_loss_l.item())
        t_losses_u.update(t_loss_u.item())
        t_losses_mpl.update(t_loss_mpl.item())
        mean_mask.update(mask.mean().item())

        batch_time.update(time.time() - end)

        if (step+1) % 10 == 0:
            logger.info(f"Train Iter: {step+1:3}/{total_steps:3}. S_Loss: {s_losses.avg:.4f}.  T_Loss: {t_losses.avg:.4f}. Mask: {mean_mask.avg:.4f} ")
        
        num_eval = step//eval_step
        if (step+1) % eval_step == 0:
            test_model = avg_student_model if avg_student_model is not None else student_model
            test_loss, top1, top2 = evaluate(tm, test_loader, test_model, criterion)

            is_best = top1 > best_top1
            if is_best:
                best_top1 = top1
                best_top2 = top2

            logger.info(f"top-1 acc: {top1:.2f}")
            logger.info(f"Best top-1 acc: {best_top1:.2f}")

            save_checkpoint(tm, {
                'step': step + 1,
                'teacher_state_dict': teacher_model.state_dict(),
                'student_state_dict': student_model.state_dict(),
                'avg_state_dict': avg_student_model.state_dict() if avg_student_model is not None else None,
                'best_top1': best_top1,
                'best_top2': best_top2,
                'teacher_optimizer': t_optimizer.state_dict(),
                'student_optimizer': s_optimizer.state_dict(),
                'teacher_scheduler': t_scheduler.state_dict(),
                'student_scheduler': s_scheduler.state_dict(),
                'teacher_scaler': t_scaler.state_dict(),
                'student_scaler': s_scaler.state_dict(),
            }, is_best)
    # finetune
    del t_scaler, t_scheduler, t_optimizer, teacher_model, unlabeled_loader
    del s_scaler, s_scheduler, s_optimizer
    ckpt_name = f'{save_path}/{name}_best.pth.tar'
    loc = f'cpu'
    checkpoint = torch.load(ckpt_name, map_location=loc)
    logger.info(f"=> loading checkpoint '{ckpt_name}'")
    if checkpoint['avg_state_dict'] is not None:
        model_load_state_dict(student_model, checkpoint['avg_state_dict'])
    else:
        model_load_state_dict(student_model, checkpoint['student_state_dict'])
    finetune(tm, labeled_loader, test_loader, student_model, criterion)
    auto_labeling(tm, labeling_loader, student_model)
    
    #save model
    model_path=tm.model_path
    save_path=os.path.join(model_path, 'mpl_model.pt')
    torch.save(student_model.state_dict(),save_path)
    
    return


def evaluate(tm, test_loader, model, criterion):
    amp_val = bool(int(tm.param_info['amp']))
    my_num_classes = int(tm.param_info['num_classes'])

    batch_time = AverageMeter()
    data_time = AverageMeter()
    losses = AverageMeter()
    top1 = AverageMeter()
    top2 = AverageMeter()
    model.eval()
    with torch.no_grad():
        end = time.time()
        for step, (images, targets) in enumerate(test_loader):
            data_time.update(time.time() - end)
            batch_size = targets.shape[0]
            if torch.cuda.is_available():
                device = torch.device('cuda', 0)
                images = images.to(device)
                targets = targets.to(device)
            with amp.autocast(enabled=amp_val):
                outputs = model(images)
                loss = criterion(outputs, targets)
            
            acc1, acc2 = accuracy(outputs, targets,(1,2))
            #actually acc1, acc2 is right.....
            
            
            
            losses.update(loss.item(), batch_size)
            top1.update(acc1[0], batch_size)
            top2.update(acc2[0], batch_size)
            batch_time.update(time.time() - end)
            end = time.time()
            if (step+1) % 100 == 0: 
                logger.info(f"Test Iter: {step+1:3}/{len(test_loader):3}. top1: {top1.avg:.2f}. top2: {top2.avg:.2f}.")

        return losses.avg, top1.avg, top2.avg


def finetune(tm, train_loader, test_loader, model, criterion):
    global best_top1
    global best_top2
    workers = int(tm.param_info['workers'])
    finetune_epochs = int(tm.param_info['finetune_epochs'])
    finetune_batch_size = int(tm.param_info['finetune_batch_size'])
    finetune_lr = float(tm.param_info['finetune_lr'])
    finetune_weight_decay = float(tm.param_info['finetune_weight_decay'])
    finetune_momentum = float(tm.param_info['finetune_momentum'])
    amp_val = bool(int(tm.param_info['amp']))

    train_sampler = RandomSampler
    labeled_loader = DataLoader(
        train_loader.dataset,
        sampler=train_sampler(train_loader.dataset),
        batch_size=finetune_batch_size,
        num_workers=workers,
        pin_memory=True)
    optimizer = optim.SGD(model.parameters(),
                          lr=finetune_lr,
                          momentum=finetune_momentum,
                          weight_decay=finetune_weight_decay)
    scaler = amp.GradScaler(enabled=amp_val)

    logger.info("***** Running Finetuning *****")
    logger.info(f"   Finetuning steps = {len(labeled_loader)*finetune_epochs}")

    for epoch in range(finetune_epochs):

        batch_time = AverageMeter()
        data_time = AverageMeter()
        losses = AverageMeter()
        model.train()
        end = time.time()
        for step, (images, targets) in enumerate(labeled_loader):
            data_time.update(time.time() - end)
            batch_size = targets.shape[0]
            if torch.cuda.is_available():
                device = torch.device('cuda', 0)
                images = images.to(device)
                targets = targets.to(device)
            with amp.autocast(enabled=amp_val):
                model.zero_grad()
                outputs = model(images)
                loss = criterion(outputs, targets)

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            losses.update(loss.item(), batch_size)
            batch_time.update(time.time() - end)
            logger.info(f"Finetune Epoch: {epoch+1:2}/{finetune_epochs:2}. Loss: {losses.avg:.4f}. ")
        test_loss, top1, top2 = evaluate(tm, test_loader, model, criterion)
        is_best = top1 > best_top1
        if is_best:
            best_top1 = top1
            best_top2 = top2

        logger.info(f"top-1 acc: {top1:.2f}")
        logger.info(f"Best top-1 acc: {best_top1:.2f}")

        save_checkpoint(tm, {
            'step': step + 1,
            'best_top1': best_top1,
            'best_top2': best_top2,
            'student_state_dict': model.state_dict(),
            'avg_state_dict': None,
            'student_optimizer': optimizer.state_dict(),
        }, is_best, finetune=True)
    return

def auto_labeling(tm, labeling_loader, model):  #labeling part in here
    amp_val = bool(int(tm.param_info['amp']))
    model.eval()
    auto_label=[]
    save_path = os.path.join(tm.model_path, 'auto_labeled')
    if not os.path.isdir(save_path):
        os.makedirs(save_path)

    num_class = int(tm.param_info['num_classes'])
    for i in range(num_class):
        if not os.path.isdir(os.path.join(save_path, str(i))):
            os.makedirs(os.path.join(save_path,str(i)))


    with torch.no_grad():
        end = time.time()
        for step, (images, path) in enumerate(labeling_loader):
            with amp.autocast(enabled=amp_val):
                outputs = model(images)
                outputs=torch.argmax(outputs, dim=1)
                label = str(outputs.item())
                shutil.copy(path[0], os.path.join(save_path, label))


    zip_file = zipfile.ZipFile(os.path.join(save_path,'auto_labeled.zip'), "w")
    
    for root, dirs, files in os.walk(save_path):
        for file in files:
            if not file.endswith('.zip'):
                zip_file.write(os.path.join(root,file),compress_type=zipfile.ZIP_DEFLATED)
                os.remove(os.path.join(root,file))
    
    zip_file.close()
    
    for i in range(num_class):
        if os.path.isdir(os.path.join(save_path,str(i))):
            os.rmdir(os.path.join(save_path,str(i)))

    return 

def train(tm):
    dataset = str(tm.param_info['dataset'])
    total_steps = int(tm.param_info['total_steps'])
    start_step = int(tm.param_info['start_step'])
    workers = int(tm.param_info['workers'])
    my_batch_size = int(tm.param_info['batch_size'])
    teacher_lr = float(tm.param_info['teacher_lr'])
    student_lr = float(tm.param_info['student_lr'])
    momentum = float(tm.param_info['momentum'])
    nesterov = bool(int(tm.param_info['nesterov']))
    weight_decay = float(tm.param_info['weight_decay'])
    ema = float(tm.param_info['ema'])
    warmup_steps = int(tm.param_info['warmup_steps'])
    student_wait_steps = int(tm.param_info['student_wait_steps'])
    #resume = str(tm.param_info['resume'])
    #evaluate_val = bool(int(tm.param_info['evaluate']))
    #finetune_val = bool(int(tm.param_info['finetune']))
    seed = int(tm.param_info['random_seed'])
    mu = int(tm.param_info['mu'])
    amp_val = bool(int(tm.param_info['amp']))
    model_name = str(tm.param_info['model_name'])
    my_num_classes = int(tm.param_info['num_classes'])
    
    global best_top1 
    best_top1 = 0.
    global best_top2
    best_top2 = 0.

    if torch.cuda.is_available():
        device = torch.device('cuda',0)
        device_ver = 'cuda'

    else:
        device = torch.device('cpu')
        device_ver='cpu'

    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.INFO )

    logger.warning(
        f"device: {device_ver}, "
        f"16-bits training: {amp_val}")


    if seed is not None:
        set_seed(tm)

    labeled_dataset, unlabeled_dataset, test_dataset, labeling_dataset = get_data(tm)


    train_sampler = RandomSampler
    labeled_loader = DataLoader(
        labeled_dataset,
        sampler=train_sampler(labeled_dataset),
        batch_size=my_batch_size,
        num_workers=workers,
        drop_last=True)

    unlabeled_loader = DataLoader(
        unlabeled_dataset,
        sampler=train_sampler(unlabeled_dataset),
        batch_size=my_batch_size*mu,
        num_workers=workers,
        drop_last=True)

    test_loader = DataLoader(test_dataset,
                             sampler=SequentialSampler(test_dataset),
                             batch_size=my_batch_size,
                             num_workers=workers)
    
    labeling_loader = DataLoader(labeling_dataset,
                             sampler=SequentialSampler(labeling_dataset),
                             batch_size=1,
                             num_workers=workers)

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
    logger.info(f"Params: {sum(p.numel() for p in teacher_model.parameters())/1e6:.2f}M")

    if torch.cuda.is_available():
        teacher_model.to(device)
        student_model.to(device)

    avg_student_model = None
    if ema > 0:
        avg_student_model = ModelEMA(student_model, ema)

    criterion = create_loss_fn(tm)

    no_decay = ['bn']
    teacher_parameters = [
        {'params': [p for n, p in teacher_model.named_parameters() if not any(
            nd in n for nd in no_decay)], 'weight_decay': weight_decay},
        {'params': [p for n, p in teacher_model.named_parameters() if any(
            nd in n for nd in no_decay)], 'weight_decay': 0.0}
    ]
    student_parameters = [
        {'params': [p for n, p in student_model.named_parameters() if not any(
            nd in n for nd in no_decay)], 'weight_decay': weight_decay},
        {'params': [p for n, p in student_model.named_parameters() if any(
            nd in n for nd in no_decay)], 'weight_decay': 0.0}
    ]

    t_optimizer = optim.SGD(teacher_parameters,
                            lr=teacher_lr,
                            momentum=momentum,
                            nesterov=nesterov)
    s_optimizer = optim.SGD(student_parameters,
                            lr=student_lr,
                            momentum=momentum,
                            nesterov=nesterov)

    t_scheduler = get_cosine_schedule_with_warmup(t_optimizer,
                                                  warmup_steps,
                                                  total_steps)
    s_scheduler = get_cosine_schedule_with_warmup(s_optimizer,
                                                  warmup_steps,
                                                  total_steps,
                                                  student_wait_steps)

    t_scaler = amp.GradScaler(enabled=amp_val)
    s_scaler = amp.GradScaler(enabled=amp_val)

    # optionally resume from a checkpoint
    '''
    if resume:
        if os.path.isfile(resume):
            logger.info(f"=> loading checkpoint '{resume}'")
            loc = f'cpu'
            checkpoint = torch.load(resume, map_location=loc)
            best_top1 = checkpoint['best_top1'].to(torch.device('cpu'))
            best_top2 = checkpoint['best_top2'].to(torch.device('cpu'))
            if not (evaluate_val or finetune_val):
                start_step = checkpoint['step']
                t_optimizer.load_state_dict(checkpoint['teacher_optimizer'])
                s_optimizer.load_state_dict(checkpoint['student_optimizer'])
                t_scheduler.load_state_dict(checkpoint['teacher_scheduler'])
                s_scheduler.load_state_dict(checkpoint['student_scheduler'])
                t_scaler.load_state_dict(checkpoint['teacher_scaler'])
                s_scaler.load_state_dict(checkpoint['student_scaler'])
                model_load_state_dict(teacher_model, checkpoint['teacher_state_dict'])
                if avg_student_model is not None:
                    model_load_state_dict(avg_student_model, checkpoint['avg_state_dict'])

            else:
                if checkpoint['avg_state_dict'] is not None:
                    model_load_state_dict(student_model, checkpoint['avg_state_dict'])
                else:
                    model_load_state_dict(student_model, checkpoint['student_state_dict'])

            logger.info(f"=> loaded checkpoint '{resume}' (step {checkpoint['step']})")
        else:
            logger.info(f"=> no checkpoint found at '{resume}'")
    '''
#아래는 단순히 finetune을 1회 진행, 혹은 evaluate를 1회 진행하고 끝내는 부분이다.
'''  
    if finetune_val:
        del t_scaler, t_scheduler, t_optimizer, teacher_model, unlabeled_loader
        del s_scaler, s_scheduler, s_optimizer
        finetune(tm, labeled_loader, test_loader, student_model, criterion)
        return

    if evaluate_val:
        del t_scaler, t_scheduler, t_optimizer, teacher_model, unlabeled_loader, labeled_loader
        del s_scaler, s_scheduler, s_optimizer
        evaluate(tm, test_loader, student_model, criterion)
        return
'''

    teacher_model.zero_grad()
    student_model.zero_grad()
    train_loop(tm, labeled_loader, unlabeled_loader, test_loader, labeling_loader,
               teacher_model, student_model, avg_student_model, criterion,
               t_optimizer, s_optimizer, t_scheduler, s_scheduler, t_scaler, s_scaler)
    return


def init_svc(im):
    load_data = os.path.join(im.model_path, 'auto_labeled.zip')
    return {"data": load_data}


def inference(df, params, batch_id):
    load_data = params['data']
