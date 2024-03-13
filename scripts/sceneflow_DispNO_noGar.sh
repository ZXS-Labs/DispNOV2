#!/usr/bin/env bash 
set -x
DATAPATH="/dssg/home/scs2010810793/data/benchmark/benchmark/scenceflow/"
python main_scene_DispNO.py --dataset sceneflowDispNO \
    --datapath $DATAPATH --trainlist ./filenames/sceneflow_train.txt --testlist ./filenames/sceneflow_test.txt \
    --epochs 50 --lrepochs "10,12,14,16,18,20,32,40,48:2" \
    --model gwcnet-gc-dispno-noGar --logdir ./checkpoints/sceneflow/DispNO_noGar/ \
    --out_add 'true' --key_query_same 'true' --deformable_groups 8 \
    --output_representation 'bimodal' --sampling 'dda' --scale_min 4 --scale_max 7 \

