#!/usr/bin/env bash
set -x
DATAPATH="/dssg/home/scs2010810793/data/benchmark/benchmark/kitti/2012/"
python main_kitti12_DispNO.py --dataset kittiDispNO \
    --datapath $DATAPATH --trainlist ./filenames/kitti12_train.txt --testlist ./filenames/kitti12_val.txt \
    --epochs 300 --lrepochs "200, 600:10" \
    --model gwcnet-gc-dispno --logdir ./checkpoints/kitti12/DispNO_s1/ \
    --loadckpt ./checkpoints/sceneflow/DispNO/truetrue8/checkpoint_000049.ckpt \
    --test_batch_size 1 \
    --out_add 'true' --key_query_same 'true' --deformable_groups 8 \
    --output_representation 'bimodal' --sampling 'dda' \
    --train_scale_min 4 --train_scale_max 7 --test_scale_min 4 --test_scale_max 4 \

python main_kitti12_DispNO.py --dataset kittiDispNO \
    --datapath $DATAPATH --trainlist ./filenames/kitti12_train.txt --testlist ./filenames/kitti12_val.txt \
    --epochs 300 --lrepochs "200, 600:10" \
    --model gwcnet-gc-dispno --logdir ./checkpoints/kitti12/DispNO_s2/ \
    --loadckpt ./checkpoints/sceneflow/DispNO/truetrue8/checkpoint_000049.ckpt \
    --test_batch_size 1 \
    --out_add 'true' --key_query_same 'true' --deformable_groups 8 \
    --output_representation 'bimodal' --sampling 'dda' \
    --train_scale_min 4 --train_scale_max 7 --test_scale_min 4 --test_scale_max 4 \

python main_kitti12_DispNO.py --dataset kittiDispNO \
    --datapath $DATAPATH --trainlist ./filenames/kitti12_train.txt --testlist ./filenames/kitti12_val.txt \
    --epochs 300 --lrepochs "200, 600:10" \
    --model gwcnet-gc-dispno --logdir ./checkpoints/kitti12/DispNO_s3/ \
    --loadckpt ./checkpoints/sceneflow/DispNO/truetrue8/checkpoint_000049.ckpt \
    --test_batch_size 1 \
    --out_add 'true' --key_query_same 'true' --deformable_groups 8 \
    --output_representation 'bimodal' --sampling 'dda' \
    --train_scale_min 4 --train_scale_max 7 --test_scale_min 4 --test_scale_max 4 \