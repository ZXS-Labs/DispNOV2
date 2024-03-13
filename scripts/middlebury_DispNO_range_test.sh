#!/usr/bin/env bash
set -x
DATAPATH="/dssg/home/scs2010810793/data/benchmark/benchmark/middlebury-offi/trainingH/"
python main_middlebury_DispNO_range_test.py --datapath $DATAPATH --testlist ./filenames/middlebury_test.txt --model gwcnet-gc-dispno-range \
 --loadckpt ./checkpoints/middlebury/DispNO_15_303/truetrue8/checkpoint_000571_best.ckpt \
 --logdir ./checkpoints/middlebury/test_DispNO_15_303 --dataset middleburyDispNO \
 --out_add 'true' --key_query_same 'true' --deformable_groups 8 \
 --output_representation 'bimodal' --sampling 'dda' --epochs 1 --lrepochs "10,12,14,16:2" \
 --scale_min 5 --scale_max 5 \
