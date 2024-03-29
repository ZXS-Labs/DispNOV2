#!/usr/bin/env bash
set -x
DATAPATH="/dssg/home/scs2010810793/data/benchmark/benchmark/scenceflow/"
python main_scene_DispNO_test.py --dataset sceneflowDispNO \
    --datapath $DATAPATH --trainlist ./filenames/sceneflow_train.txt --testlist ./filenames/sceneflow_test.txt \
    --epochs 1 --lrepochs "10,12,14,16:2" \
    --model gwcnet-gc-dispno-costGar --logdir ./checkpoints/sceneflow/test_DispNO_costGar \
    --loadckpt ./checkpoints/sceneflow/DispNO_costGar/truetrue8/checkpoint_000049.ckpt \
    --out_add true --key_query_same true --deformable_groups 8 \
    --output_representation 'bimodal' --sampling 'dda' --scale_min 5 --scale_max 5 \
