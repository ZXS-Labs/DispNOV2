#!/usr/bin/env bash
set -x
DATAPATH="/dssg/home/scs2010810793/data/benchmark/benchmark/kitti/2015/"
python main_kitti_test.py --datapath $DATAPATH --testlist ./filenames/kiti15_test.txt --model gwcnet-gc --loadckpt ./checkpoints/kitti15/hda_s3/truetrue8/checkpoint_000254_best.ckpt --out_add 'true' --key_query_same 'true' --deformable_groups 8
