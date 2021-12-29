#!/usr/bin/env python

'''Generate models for affinity predictions'''

# variables: 


# GAP(0)
# PENALTY (0)
# HUBER (false)
# DELTA (0)
# RANKLOSS (0)
basemodel = '''layer {
  name: "data"
  type: "MolGridData"
  top: "data"
  top: "label"
  top: "affinity"
  include {
    phase: TEST
  }
  molgrid_data_param {
    source: "TESTFILE"
    batch_size: 50
    dimension: 23.5
    resolution: 0.5
    shuffle: false
    balanced: false
    has_affinity: true
    root_folder: "../../"
  }
}
layer {
  name: "data"
  type: "MolGridData"
  top: "data"
  top: "label"
  top: "affinity"
  include {
    phase: TRAIN
  }
  molgrid_data_param {
    source: "TRAINFILE"
    batch_size:  50
    dimension: 23.5
    resolution: 0.5
    shuffle: true
    balanced: true
    stratify_receptor: true
    stratify_affinity_min: 0
    stratify_affinity_max: 0
    stratify_affinity_step: 0
    has_affinity: true
    random_rotation: true
    random_translate: 2
    root_folder: "../../"
  }
}

layer {
  name: "unit1_pool"
  type: "Pooling"
  bottom: "data"
  top: "unit1_pool"
  pooling_param {
    pool: MAX
    kernel_size: 2
    stride: 2
  }
}
layer {
  name: "unit1_conv1"
  type: "Convolution"
  bottom: "unit1_pool"
  top: "unit1_conv1"
  convolution_param {
    num_output: 32
    pad: 1
    kernel_size: 3
    stride: 1
    weight_filler {
      type: "xavier"
    }
  }
}
layer {
  name: "unit1_relu1"
  type: "ReLU"
  bottom: "unit1_conv1"
  top: "unit1_conv1"
}
layer {
  name: "unit2_pool"
  type: "Pooling"
  bottom: "unit1_conv1"
  top: "unit2_pool"
  pooling_param {
    pool: MAX
    kernel_size: 2
    stride: 2
  }
}
layer {
  name: "unit2_conv1"
  type: "Convolution"
  bottom: "unit2_pool"
  top: "unit2_conv1"
  convolution_param {
    num_output: 64
    pad: 1
    kernel_size: 3
    stride: 1
    weight_filler {
      type: "xavier"
    }
  }
}
layer {
  name: "unit2_relu1"
  type: "ReLU"
  bottom: "unit2_conv1"
  top: "unit2_conv1"
}
layer {
  name: "unit3_pool"
  type: "Pooling"
  bottom: "unit2_conv1"
  top: "unit3_pool"
  pooling_param {
    pool: MAX
    kernel_size: 2
    stride: 2
  }
}
layer {
  name: "unit3_conv1"
  type: "Convolution"
  bottom: "unit3_pool"
  top: "unit3_conv1"
  convolution_param {
    num_output: 128
    pad: 1
    kernel_size: 3
    stride: 1
    weight_filler {
      type: "xavier"
    }
  }
}
layer {
  name: "unit3_relu1"
  type: "ReLU"
  bottom: "unit3_conv1"
  top: "unit3_conv1"
}

layer {
    name: "split"
    type: "Split"
    bottom: "unit3_conv1"
    top: "split"
}

layer {
  name: "output_fc"
  type: "InnerProduct"
  bottom: "split"
  top: "output_fc"
  inner_product_param {
    num_output: 2
    weight_filler {
      type: "xavier"
    }
  }
}
layer {
  name: "loss"
  type: "SoftmaxWithLoss"
  bottom: "output_fc"
  bottom: "label"
  top: "loss"
}

layer {
  name: "output"
  type: "Softmax"
  bottom: "output_fc"
  top: "output"
}
layer {
  name: "labelout"
  type: "Split"
  bottom: "label"
  top: "labelout"
  include {
    phase: TEST
  }
}

layer {
  name: "output_fc_aff"
  type: "InnerProduct"
  bottom: "split"
  top: "output_fc_aff"
  inner_product_param {
    num_output: 1
    weight_filler {
      type: "xavier"
    }
  }
}

layer {
  name: "rmsd"
  type: "AffinityLoss"
  bottom: "output_fc_aff"
  bottom: "affinity"
  top: "rmsd"
  affinity_loss_param {
    scale: 0.1
    gap: GAP
    penalty: PENALTY
    pseudohuber: HUBER
    delta: DELTA
  }
}

layer {
  name: "predaff"
  type: "Flatten"
  bottom: "output_fc_aff"
  top: "predaff"
}

layer {
  name: "affout"
  type: "Split"
  bottom: "affinity"
  top: "affout"
  include {
    phase: TEST
  }
}
'''


def makemodel(**kwargs):
    m = basemodel
    for (k,v) in kwargs.items():
        m = m.replace(k,str(v))
    return m
    


# GAP(0)
# PENALTY (0)
# HUBER (false)
# DELTA (0)
# RANKLOSS (0)

models = []
for gap in [0,1,2]:
    for penalty in [0,1,2,4]:
        for delta in [0,1,2,4,6]:    
            huber = "false" if delta == 0 else "true"
            model = makemodel(GAP=gap,PENALTY=penalty,HUBER=huber, DELTA=delta)
            m = 'affinity_g%d_p%d_h%d.model'%(gap,penalty, delta)
            models.append(m)
            out = open(m,'w')
            out.write(model)

for m in models:
    print("train.py -m %s -p ../types/all_0.5_0_ --keep_best -t 1000 -i 100000 --reduced -o all_%s"%(m,m.replace('.model','')))
