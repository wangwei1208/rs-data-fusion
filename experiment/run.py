import sys
sys.path.append('..')

import os
os.environ['KERAS_BACKEND'] = 'tensorflow'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import argparse
from functools import partial
import json
from keras import optimizers
from pathlib import Path

import tensorflow as tf
from keras.backend import tensorflow_backend as K

from toolbox.data import load_set
from toolbox.model import get_model
from toolbox.experiment import Experiment

parser = argparse.ArgumentParser()
parser.add_argument('config', type=Path)
args = parser.parse_args()
param = json.load(args.config.open())

# Model
scale = param['scale']
build_model = partial(get_model(param['model']['name']),
                      **param['model']['params'])
if 'optimizer' in param:
    optimizer = getattr(optimizers, param['optimizer']['name'].lower())
    optimizer = optimizer(**param['optimizer']['params'])
else:
    optimizer = 'adam'

# Data
load_set = partial(load_set,
                   lr_sub_size=param['lr_sub_size'],
                   lr_sub_stride=param['lr_sub_stride'])

with tf.Session(config=tf.ConfigProto(
                    intra_op_parallelism_threads=2)) as sess:
    K.set_session(sess)
    # Training
    expt = Experiment(scale=param['scale'], load_set=load_set,
                      build_model=build_model, optimizer=optimizer,
                      save_dir=param['save_dir'])
    print('training process...')
    expt.train(train_set=param['train_set'], val_set=param['val_set'],
               epochs=param['epochs'], resume=True)

    # Evaluation
    print('evaluation process...')
    for test_set in param['test_sets']:
        expt.test(test_set=test_set)
