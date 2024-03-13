#!/usr/bin/env bash
set -x
DATAPATH="/dssg/home/scs2010810793/data/benchmark/benchmark/scenceflow/"
python main_scene.py --dataset sceneflow \
    --datapath $DATAPATH --trainlist ./filenames/sceneflow_train.txt --testlist ./filenames/sceneflow_test.txt \
    --epochs 16 --lrepochs "10,12,14,16,18,20:2" \
    --model gwcnet-gc --logdir ./checkpoints/sceneflow/hda/ \
    --out_add 'true' --key_query_same 'true' --deformable_groups 8 \
