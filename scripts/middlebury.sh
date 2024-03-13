#!/usr/bin/env bash
set -x
DATAPATH="/dssg/home/scs2010810793/data/benchmark/benchmark/middlebury-offi/trainingH/"
python main_middlebury.py --dataset middlebury \
    --datapath $DATAPATH --trainlist ./filenames/middlebury_train.txt --testlist ./filenames/middlebury_val.txt \
    --epochs 600 --lrepochs "200, 600:10" \
    --model gwcnet-gc --logdir ./checkpoints/middlebury/hda_s1/ \
    --loadckpt ./checkpoints/sceneflow/hda/truetrue8/checkpoint_000015.ckpt \
    --test_batch_size 1 \
    --out_add 'true' --key_query_same 'true' --deformable_groups 8

python main_middlebury.py --dataset middlebury \
    --datapath $DATAPATH --trainlist ./filenames/middlebury_train.txt --testlist ./filenames/middlebury_val.txt \
    --epochs 600 --lrepochs "200, 600:10" \
    --model gwcnet-gc --logdir ./checkpoints/middlebury/hda_s2/ \
    --loadckpt ./checkpoints/sceneflow/hda/truetrue8/checkpoint_000015.ckpt \
    --test_batch_size 1 \
    --out_add 'true' --key_query_same 'true' --deformable_groups 8

python main_middlebury.py --dataset middlebury \
    --datapath $DATAPATH --trainlist ./filenames/middlebury_train.txt --testlist ./filenames/middlebury_val.txt \
    --epochs 600 --lrepochs "200, 600:10" \
    --model gwcnet-gc --logdir ./checkpoints/middlebury/hda_s3/ \
    --loadckpt ./checkpoints/sceneflow/hda/truetrue8/checkpoint_000015.ckpt \
    --test_batch_size 1 \
    --out_add 'true' --key_query_same 'true' --deformable_groups 8

