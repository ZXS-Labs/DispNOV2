from __future__ import print_function
import torch
import torch.nn as nn
import torch.utils.data
from torch.autograd import Variable
import torch.nn.functional as F
from models.submodule import *
import math
from deform_conv import DeformConv, ModulatedDeformConv
from models.attention import *

def conv3x3(in_planes, out_planes, stride=1, groups=1, dilation=1):
    """3x3 convolution with padding"""
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride,
                     padding=dilation, groups=groups, bias=False, dilation=dilation)


def conv1x1(in_planes, out_planes, stride=1):
    """1x1 convolution"""
    return nn.Conv2d(in_planes, out_planes, kernel_size=1, stride=stride, bias=False)

class DeformConv2d(nn.Module):
    """A single (modulated) deformable conv layer"""

    def __init__(self, in_channels,
                 out_channels,
                 kernel_size=3,
                 stride=1,
                 dilation=2,
                 groups=1,
                 deformable_groups=2,
                 modulation=True,
                 double_mask=True,
                 bias=False):
        super(DeformConv2d, self).__init__()

        self.modulation = modulation
        self.deformable_groups = deformable_groups
        self.kernel_size = kernel_size
        self.double_mask = double_mask

        if self.modulation:
            self.deform_conv = ModulatedDeformConv(in_channels,
                                                   out_channels,
                                                   kernel_size=kernel_size,
                                                   stride=stride,
                                                   padding=dilation,
                                                   dilation=dilation,
                                                   groups=groups,
                                                   deformable_groups=deformable_groups,
                                                   bias=bias)
        else:
            self.deform_conv = DeformConv(in_channels,
                                          out_channels,
                                          kernel_size=kernel_size,
                                          stride=stride,
                                          padding=dilation,
                                          dilation=dilation,
                                          groups=groups,
                                          deformable_groups=deformable_groups,
                                          bias=bias)

        k = 3 if self.modulation else 2

        offset_out_channels = deformable_groups * k * kernel_size * kernel_size

        # Group-wise offset leraning when deformable_groups > 1
        self.offset_conv = nn.Conv2d(in_channels, offset_out_channels, kernel_size=kernel_size,
                                     stride=stride, padding=dilation, dilation=dilation,
                                     groups=deformable_groups, bias=True)

        # Initialize the weight for offset_conv as 0 to act like regular conv
        nn.init.constant_(self.offset_conv.weight, 0.)
        nn.init.constant_(self.offset_conv.bias, 0.)

    def forward(self, x):
        if self.modulation:
            offset_mask = self.offset_conv(x)

            offset_channel = self.deformable_groups * 2 * self.kernel_size * self.kernel_size
            offset = offset_mask[:, :offset_channel, :, :]

            mask = offset_mask[:, offset_channel:, :, :]
            mask = mask.sigmoid()  # [0, 1]

            if self.double_mask:
                mask = mask * 2  # initialize as 1 to work as regular conv

            out = self.deform_conv(x, offset, mask)

        else:
            offset = self.offset_conv(x)
            out = self.deform_conv(x, offset)

        return out

class DeformSimpleBottleneck(nn.Module):
    """Used for cost aggregation"""

    def __init__(self, inplanes, planes, stride=1, downsample=None, groups=1,
                 base_width=64, norm_layer=None,
                 mdconv_dilation=2,
                 deformable_groups=2,
                 modulation=True,
                 double_mask=True,
                 ):
        super(DeformSimpleBottleneck, self).__init__()
        if norm_layer is None:
            norm_layer = nn.BatchNorm2d
        width = int(planes * (base_width / 64.)) * groups
        # Both self.conv2 and self.downsample layers downsample the input when stride != 1
        self.conv1 = conv1x1(inplanes, width)
        self.bn1 = norm_layer(width)
        self.conv2 = DeformConv2d(width, width, stride=stride,
                                  dilation=mdconv_dilation,
                                  deformable_groups=deformable_groups,
                                  modulation=modulation,
                                  double_mask=double_mask)
        self.bn2 = norm_layer(width)
        self.conv3 = conv1x1(width, planes)
        self.bn3 = norm_layer(planes)
        self.relu = nn.ReLU(inplace=True)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        identity = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        if self.downsample is not None:
            identity = self.downsample(x)

        out += identity
        out = self.relu(out)

        return out

class feature_extraction(nn.Module):
    def __init__(self, concat_feature=False, concat_feature_channel=12, out_add=True, key_query_same=True, deformable_groups=2):
        super(feature_extraction, self).__init__()
        self.concat_feature = concat_feature
        self.out_add = out_add
        self.key_query_same = key_query_same
        self.deformable_groups = deformable_groups
        self.inplanes = 32
        self.firstconv = nn.Sequential(convbn(3, 32, 3, 2, 1, 1),
                                       nn.ReLU(inplace=True),
                                       convbn(32, 32, 3, 1, 1, 1),
                                       nn.ReLU(inplace=True),
                                       convbn(32, 32, 3, 1, 1, 1),
                                       nn.ReLU(inplace=True))

        self.layer1 = self._make_layer(BasicBlock, 32, 3, 1, 1, 1)
        self.layer2 = self._make_layer(BasicBlock, 64, 16, 2, 1, 1)
        self.layer3 = self._make_layer(BasicBlock, 128, 3, 1, 1, 1)
        self.layer4 = self._make_layer(BasicBlock, 128, 3, 1, 1, 2)
        dilations=(3, 5, 15)
        in_features = 128
        out_features = 128
        self.conv1 = nn.Sequential(nn.AdaptiveAvgPool2d((1, 1)),
                                   nn.Conv2d(in_features, out_features, kernel_size=1, padding=0, stride=1, dilation=1,
                                             bias=False),
                                   nn.BatchNorm2d(out_features))

        self.conv2 = nn.Sequential(nn.AvgPool2d(kernel_size=3, stride=1, padding=1),
                                   nn.Conv2d(in_features, out_features, kernel_size=3, dilation=dilations[0],
                                             padding=dilations[0], bias=False),
                                   nn.BatchNorm2d(out_features))

        self.conv3 = nn.Sequential(nn.AvgPool2d(kernel_size=5, stride=1, padding=2),
                                   nn.Conv2d(in_features, out_features, kernel_size=3, dilation=dilations[1],
                                             padding=dilations[1], bias=False),
                                   nn.BatchNorm2d(out_features))

        self.conv4 = nn.Sequential(nn.AvgPool2d(kernel_size=15, stride=1, padding=7),
                                   nn.Conv2d(in_features, out_features, kernel_size=3, dilation=dilations[2],
                                             padding=dilations[2], bias=False),
                                   nn.BatchNorm2d(out_features))
        if self.concat_feature:
            self.lastconv = nn.Sequential(convbn(320, 128, 3, 1, 1, 1),
                                          nn.ReLU(inplace=True),
                                          nn.Conv2d(128, concat_feature_channel, kernel_size=1, padding=0, stride=1,
                                                    bias=False))
        self.dcn = DeformSimpleBottleneck(320, 320, deformable_groups=self.deformable_groups)
        self.horizon_attention = Horizon_attention_module(True, True, 320, 128)
    def _make_layer(self, block, planes, blocks, stride, pad, dilation):
        downsample = None
        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.inplanes, planes * block.expansion,
                          kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(planes * block.expansion), )

        layers = []
        layers.append(block(self.inplanes, planes, stride, downsample, pad, dilation))
        self.inplanes = planes * block.expansion
        for i in range(1, blocks):
            layers.append(block(self.inplanes, planes, 1, None, pad, dilation))

        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.firstconv(x)
        x = self.layer1(x)
        l2 = self.layer2(x)
        l3 = self.layer3(l2)
        l4 = self.layer4(l3)
        _, _, h, w = l4.shape

        x1 = torch.cat((l2, l3, l4), 1) 
        x2 = self.horizon_attention(x1)
        gwc_feature_ = self.dcn(x2)
        if not self.concat_feature:
            return {"gwc_feature": gwc_feature_}
        else:
            concat_feature = self.lastconv(gwc_feature_)
            return {"gwc_feature": gwc_feature_, "concat_feature": concat_feature}


class hourglass(nn.Module):
    def __init__(self, in_channels):
        super(hourglass, self).__init__()

        self.conv1 = nn.Sequential(convbn_3d(in_channels, in_channels * 2, 3, 2, 1),
                                   nn.ReLU(inplace=True))

        self.conv2 = nn.Sequential(convbn_3d(in_channels * 2, in_channels * 2, 3, 1, 1),
                                   nn.ReLU(inplace=True))

        self.conv3 = nn.Sequential(convbn_3d(in_channels * 2, in_channels * 4, 3, 2, 1),
                                   nn.ReLU(inplace=True))

        self.conv4 = nn.Sequential(convbn_3d(in_channels * 4, in_channels * 4, 3, 1, 1),
                                   nn.ReLU(inplace=True))

        self.conv5 = nn.Sequential(
            nn.ConvTranspose3d(in_channels * 4, in_channels * 2, 3, padding=1, output_padding=1, stride=2, bias=False),
            nn.BatchNorm3d(in_channels * 2))

        self.conv6 = nn.Sequential(
            nn.ConvTranspose3d(in_channels * 2, in_channels, 3, padding=1, output_padding=1, stride=2, bias=False),
            nn.BatchNorm3d(in_channels))

        self.redir1 = convbn_3d(in_channels, in_channels, kernel_size=1, stride=1, pad=0)
        self.redir2 = convbn_3d(in_channels * 2, in_channels * 2, kernel_size=1, stride=1, pad=0)

    def forward(self, x):
        conv1 = self.conv1(x)
        conv2 = self.conv2(conv1)

        conv3 = self.conv3(conv2)
        conv4 = self.conv4(conv3)

        conv5 = F.relu(self.conv5(conv4) + self.redir2(conv2), inplace=True)
        conv6 = F.relu(self.conv6(conv5) + self.redir1(x), inplace=True)

        return conv6


class GwcNet(nn.Module):
    def __init__(self, maxdisp, out_add, key_query_same, deformable_groups, use_concat_volume=True):
        super(GwcNet, self).__init__()
        self.maxdisp = maxdisp
        self.use_concat_volume = use_concat_volume
        self.out_add = out_add
        self.key_query_same = key_query_same
        self.deformable_groups = deformable_groups
        self.num_groups = 40

        if self.use_concat_volume:
            self.concat_channels = 12
            self.feature_extraction = feature_extraction(concat_feature=True,
                                                         concat_feature_channel=self.concat_channels, out_add=self.out_add, key_query_same=self.key_query_same, deformable_groups=self.deformable_groups)
        else:
            self.concat_channels = 0
            self.feature_extraction = feature_extraction(concat_feature=False, out_add=self.out_add, key_query_same=self.key_query_same, deformable_groups=self.deformable_groups)

        self.dres0 = nn.Sequential(convbn_3d(self.num_groups + self.concat_channels * 2, 32, 3, 1, 1),
                                   nn.ReLU(inplace=True),
                                   convbn_3d(32, 32, 3, 1, 1),
                                   nn.ReLU(inplace=True))

        self.dres1 = nn.Sequential(convbn_3d(32, 32, 3, 1, 1),
                                   nn.ReLU(inplace=True),
                                   convbn_3d(32, 32, 3, 1, 1))

        self.dres2 = hourglass(32)

        self.dres3 = hourglass(32)

        self.dres4 = hourglass(32)

        self.classif0 = nn.Sequential(convbn_3d(32, 32, 3, 1, 1),
                                      nn.ReLU(inplace=True),
                                      nn.Conv3d(32, 1, kernel_size=3, padding=1, stride=1, bias=False))

        self.classif1 = nn.Sequential(convbn_3d(32, 32, 3, 1, 1),
                                      nn.ReLU(inplace=True),
                                      nn.Conv3d(32, 1, kernel_size=3, padding=1, stride=1, bias=False))

        self.classif2 = nn.Sequential(convbn_3d(32, 32, 3, 1, 1),
                                      nn.ReLU(inplace=True),
                                      nn.Conv3d(32, 1, kernel_size=3, padding=1, stride=1, bias=False))

        self.classif3 = nn.Sequential(convbn_3d(32, 32, 3, 1, 1),
                                      nn.ReLU(inplace=True),
                                      nn.Conv3d(32, 1, kernel_size=3, padding=1, stride=1, bias=False))

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
            elif isinstance(m, nn.Conv3d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.kernel_size[2] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()
            elif isinstance(m, nn.BatchNorm3d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()
            elif isinstance(m, nn.Linear):
                m.bias.data.zero_()

    def forward(self, left, right, s = None, o_shape = None):
        features_left = self.feature_extraction(left)
        features_right = self.feature_extraction(right)

        gwc_volume = build_gwc_piancha_volume(features_left["gwc_feature"], features_right["gwc_feature"], self.maxdisp // 4,
								     self.num_groups)
        if self.use_concat_volume:
            concat_volume = build_concat_volume(features_left["concat_feature"], features_right["concat_feature"],
                                                self.maxdisp // 4)
            volume = torch.cat((gwc_volume, concat_volume), 1)
        else:
            volume = gwc_volume

        cost0 = self.dres0(volume)
        cost0 = self.dres1(cost0) + cost0

        out1 = self.dres2(cost0)
        out2 = self.dres3(out1)
        out3 = self.dres4(out2)

        if self.training:
            cost0 = self.classif0(cost0)
            cost1 = self.classif1(out1)
            cost2 = self.classif2(out2)
            cost3 = self.classif3(out3)

            cost0 = F.upsample(cost0, [self.maxdisp, left.size()[2], left.size()[3]], mode='trilinear')
            cost0 = torch.squeeze(cost0, 1)
            pred0 = F.softmax(cost0, dim=1)
            pred0 = disparity_regression(pred0, self.maxdisp)

            cost1 = F.upsample(cost1, [self.maxdisp, left.size()[2], left.size()[3]], mode='trilinear')
            cost1 = torch.squeeze(cost1, 1)
            pred1 = F.softmax(cost1, dim=1)
            pred1 = disparity_regression(pred1, self.maxdisp)

            cost2 = F.upsample(cost2, [self.maxdisp, left.size()[2], left.size()[3]], mode='trilinear')
            cost2 = torch.squeeze(cost2, 1)
            pred2 = F.softmax(cost2, dim=1)
            pred2 = disparity_regression(pred2, self.maxdisp)

            cost3 = F.upsample(cost3, [self.maxdisp, left.size()[2], left.size()[3]], mode='trilinear')
            cost3 = torch.squeeze(cost3, 1)
            pred3 = F.softmax(cost3, dim=1)
            pred3 = disparity_regression(pred3, self.maxdisp)
            return [pred0, pred1, pred2, pred3]
        else:
            cost3 = self.classif3(out3)
            cost3 = F.upsample(cost3, [self.maxdisp, left.size()[2], left.size()[3]], mode='trilinear')
            cost3 = torch.squeeze(cost3, 1)
            pred3 = F.softmax(cost3, dim=1)
            pred3 = disparity_regression(pred3, self.maxdisp)
            pred = pred3 * (s / 4)
            pred = torch.unsqueeze(pred, 1)
            pred = F.upsample(pred, [o_shape[0][0], o_shape[0][1]], mode='bilinear')
            pred = torch.squeeze(pred, 1)
            return [pred]


def GwcNet_GC(d, out_add, key_query_same, deformable_groups,):
    return GwcNet(d, out_add, key_query_same, deformable_groups, use_concat_volume=True)

