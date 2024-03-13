#!/usr/bin/env bash
set -x
DATAPATH="/dssg/home/scs2010810793/data/benchmark/benchmark/UnrealStereo4K/"
python main_UnrealStereo.py --dataset UnrealStereo \
    --datapath $DATAPATH --trainlist ./filenames/UnrealStereo_train.txt --testlist ./filenames/UnrealStereo_val.txt \
    --epochs 300 --lrepochs "200, 600:10" \
    --model gwcnet-gc --logdir ./checkpoints/UnrealStereo/hda_s1 \
    --loadckpt ./checkpoints/sceneflow/hda/truetrue8/checkpoint_000015.ckpt \
    --test_batch_size 1 \
    --out_add 'true' --key_query_same 'true' --deformable_groups 8

python main_UnrealStereo.py --dataset UnrealStereo \
    --datapath $DATAPATH --trainlist ./filenames/UnrealStereo_train.txt --testlist ./filenames/UnrealStereo_val.txt \
    --epochs 300 --lrepochs "200, 600:10" \
    --model gwcnet-gc --logdir ./checkpoints/UnrealStereo/hda_s2 \
    --loadckpt ./checkpoints/sceneflow/hda/truetrue8/checkpoint_000015.ckpt \
    --test_batch_size 1 \
    --out_add 'true' --key_query_same 'true' --deformable_groups 8

python main_UnrealStereo.py --dataset UnrealStereo \
    --datapath $DATAPATH --trainlist ./filenames/UnrealStereo_train.txt --testlist ./filenames/UnrealStereo_val.txt \
    --epochs 300 --lrepochs "200, 600:10" \
    --model gwcnet-gc --logdir ./checkpoints/UnrealStereo/hda_s3 \
    --loadckpt ./checkpoints/sceneflow/hda/truetrue8/checkpoint_000015.ckpt \
    --test_batch_size 1 \
    --out_add 'true' --key_query_same 'true' --deformable_groups 8

