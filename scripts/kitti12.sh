#!/usr/bin/env bash
set -x
DATAPATH="/dssg/home/scs2010810793/data/benchmark/benchmark/kitti/2012/"
python main_kitti12.py --dataset kitti \
    --datapath $DATAPATH --trainlist ./filenames/kitti12_train.txt --testlist ./filenames/kitti12_val.txt \
    --epochs 300 --lrepochs "200, 600:10" \
    --model gwcnet-gc --logdir ./checkpoints/kitti12/hda_s1/ \
    --loadckpt ./checkpoints/sceneflow/hda/truetrue8/checkpoint_000015.ckpt \
    --test_batch_size 1 \
    --out_add 'true' --key_query_same 'true' --deformable_groups 8

python main_kitti12.py --dataset kitti \
    --datapath $DATAPATH --trainlist ./filenames/kitti12_train.txt --testlist ./filenames/kitti12_val.txt \
    --epochs 300 --lrepochs "200, 600:10" \
    --model gwcnet-gc --logdir ./checkpoints/kitti12/hda_s2/ \
    --loadckpt ./checkpoints/sceneflow/hda/truetrue8/checkpoint_000015.ckpt \
    --test_batch_size 1 \
    --out_add 'true' --key_query_same 'true' --deformable_groups 8

python main_kitti12.py --dataset kitti \
    --datapath $DATAPATH --trainlist ./filenames/kitti12_train.txt --testlist ./filenames/kitti12_val.txt \
    --epochs 300 --lrepochs "200, 600:10" \
    --model gwcnet-gc --logdir ./checkpoints/kitti12/hda_s3/ \
    --loadckpt ./checkpoints/sceneflow/hda/truetrue8/checkpoint_000015.ckpt \
    --test_batch_size 1 \
    --out_add 'true' --key_query_same 'true' --deformable_groups 8

