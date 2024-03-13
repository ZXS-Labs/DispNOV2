#!/usr/bin/env bash
set -x
DATAPATH="/dssg/home/scs2010810793/data/benchmark/benchmark/middlebury-offi/trainingH/"
python main_middlebury_DispNO_range.py --dataset middleburyDispNO \
    --datapath $DATAPATH --trainlist ./filenames/middlebury_train.txt --testlist ./filenames/middlebury_val.txt \
    --epochs 600 --lrepochs "200, 600:10" \
    --model gwcnet-gc-dispno-range --logdir ./checkpoints/middlebury/DispNO_15_303/ \
    --loadckpt ./checkpoints/sceneflow/DispNO/truetrue8/checkpoint_000049.ckpt \
    --test_batch_size 1 \
    --out_add 'true' --key_query_same 'true' --deformable_groups 8 \
    --output_representation 'bimodal' --sampling 'dda' \
    --train_scale_min 4 --train_scale_max 7 --test_scale_min 5 --test_scale_max 5 \
