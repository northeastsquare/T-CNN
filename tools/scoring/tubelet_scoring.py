#!/usr/bin/env python

import argparse
import sys
import os
sys.path.insert(1, '.')
sys.path.insert(1, './External/caffe-official/python')
from vdetlib.utils.protocol import proto_load, proto_dump, track_proto_from_annot_proto
from vdetlib.utils.common import caffe_net
from vdetlib.vdet.dataset import imagenet_vdet_class_idx, imagenet_det_200_class_idx
from vdetlib.vdet.tubelet_cls import scoring_tracks, rcnn_scoring

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('vid_file')
    parser.add_argument('annot_file')
    parser.add_argument('track_file')
    parser.add_argument('net_file')
    parser.add_argument('param_file')
    parser.add_argument('rcnn_model')
    parser.add_argument('save_file')
    parser.add_argument('--cls')
    parser.add_argument('--job', type=int)
    args = parser.parse_args()

    vid_proto = proto_load(args.vid_file)
    annot_proto = proto_load(args.annot_file)
    if args.track_file == 'None':
        track_proto = track_proto_from_annot_proto(annot_proto)
    else:
        track_proto = proto_load(args.track_file)

    vid_name = vid_proto['video']
    assert vid_name == annot_proto['video']
    assert vid_name == track_proto['video']
    cls_index = imagenet_vdet_class_idx[args.cls]

    net = caffe_net(args.net_file, args.param_file, args.job-1)
    rcnn_sc = lambda vid_proto, track_proto, net, class_idx: \
        rcnn_scoring(vid_proto, track_proto, net, class_idx, args.rcnn_model)
    rcnn_sc.__name__ = "rcnn_{}".format(
        os.path.splitext(os.path.basename(args.param_file))[0])

    score_proto = scoring_tracks(vid_proto, track_proto, annot_proto,
        rcnn_sc, net, cls_index)
    proto_dump(score_proto, args.save_file)