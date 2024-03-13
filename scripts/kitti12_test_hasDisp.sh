#!/usr/bin/env bash
set -x
DATAPATH="/dssg/home/scs2010810793/data/benchmark/benchmark/kitti/2012/"
python main_kitti_test_hasDisp.py --datapath $DATAPATH --testlist ./filenames/kitti12_train_all.txt --model gwcnet-gc \
 --loadckpt ./checkpoints/kitti12/hda_s1/truetrue8/checkpoint_000283_best.ckpt \
 --out_add 'true' --key_query_same 'true' --deformable_groups 8
