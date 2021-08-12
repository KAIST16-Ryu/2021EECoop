

| About        | parameter                              | 설명                                                                                 |
|--------------|----------------------------------------|------------------------------------------------------------------------------------|
| DataLoader   | dataset                                | dataset의 이름 (뒤에서 더 자세히 다룰예정)                                                       |
|              | batch_size                             |                                                                                    |
|              | workers                                |                                                                                    |
| Optimizer    | teacher_lr, student_lr                 |                                                                                    |
|              | momemtum                               | Determining how much to reflect the previous gradient                              |
|              | nesterov                               |                                                                                    |
|              | weight_decay                           | large-> underfitting, small-> overfitting                                          |
| Scheduler    | warmup_steps                           |                                                                                    |
|              | total_steps                            |                                                                                    |
|              | student_wait_steps (student Scheduler) |                                                                                    |
| GPU          | amp_val                                | amp.autocase, amp.GradScaler: related to 16-bits training                          |
| Augmentation | rand_num                               | transformation 종류 수                                                                |
|              | rand_val                               | transformation 정도 value                                                            |
| 그밖에          | seed                                   | random seed                                                                        |
|              | mu                                     | coefficient of unlabeled loss (this is involved in unlabeled dataloader batchsize) |
|              | ema                                    | EMA decay rate                                                                     |
|              | lambda_u                               | coefficient of unlabeled loss                                                      |
|              | grad_clip                              | gradient norm clipping                                                             |
|              | threshold                              | pseudo label threshold                                                             |
|              | temperature                            | pseudo label temperature : as this goes small, become similar to one hot encoding  |
|              | * resume                               | If your training stopped, start from checkpoint                                    |


- batch_size가 labeled data의 수보다 작아야 하며, batch_size*mu가 unlabeled data의 수보다 작아야 한다 <br/>
=> data의 갯수를 고려하지 않고 batch_size를 data의 수보다 크게 하면 error가 생긴다.
