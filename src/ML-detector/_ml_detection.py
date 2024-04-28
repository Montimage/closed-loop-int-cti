#!/usr/bin/env python3
# coding=utf-8

import pandas as pd
import numpy as np
import os


# List of features
METRICS = ['diffLen', 'len']

# directory containing this script
__DIR__ = os.path.dirname(os.path.realpath(__file__))

# structure of model: DecisionTreeClassifier
# https://scikit-learn.org/stable/auto_examples/tree/plot_unveil_tree_structure.html#sphx-glr-auto-examples-tree-plot-unveil-tree-structure-py
MODEL = pd.read_pickle( os.path.join(__DIR__, "./dt.model" ))


def detector(data):
    mtrafic = pd.DataFrame( data )
    #filtre out the unecessary metrics
    mtrafic = mtrafic[ METRICS ]
    #print( mtrafic )
    data = np.asarray(mtrafic).astype('float')
    
    output = MODEL.predict( data )
    #print( output )
    return output