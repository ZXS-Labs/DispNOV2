#!/usr/bin/env bash
set -x
DATAPATH="/dssg/home/scs2010810793/data/benchmark/benchmark/kitti/2015/"
python main_kitti_DispNO_test_hasDisp.py --dataset kittiDispNO --datapath $DATAPATH \
    --testlist ./filenames/kitti15_train_all.txt --model gwcnet-gc-dispno \
    --loadckpt ./checkpoints/kitti15/DispNO_s3/truetrue8/checkpoint_000294_best.ckpt \
    --out_add 'true' --key_query_same 'true' --deformable_groups 8 \
    --output_representation 'bimodal' --sampling 'dda' \
    --scale_min 5 --scale_max 5 \

