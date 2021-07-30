#! /bin/bash

random_num="$(($RANDOM% 1000))"

python /examples/DistributeTrain_PreTraining.py \
            --num-gpus=$1 \
            --rand-num=$random_num \
            --image=$2 \
            --port=$3 \
            --filename=$4 \
            --host-network=$5

sleep 30

python /examples/DistributeTrain_PostTraining.py \
            --rand-num=$random_num


