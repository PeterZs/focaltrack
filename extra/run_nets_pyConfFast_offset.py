import tensorflow as tf
import numpy as np
import cv2
import pdb
import pickle
import matplotlib.pyplot as plt
import pickle
import json
import os, glob
import copy
from utils import *
import time

#####################################################################
##  Write down the net we want to use
#####################################################################
netName = "pyConfLensFlowNetFast_offset"
method = "experiment"
dataset = [
	"6-0001g-1",
	"6-0001g-2",
	"6-0001g-3",
	"6-0002g-1",
	"6-0002g-2",
	"6-0005g-1",
	"6-0005g-2",
	"6-0006g-1",
	"6-0006g-2",
	"6-0006g-3",
	"6-0007g-1",
	"6-0007g-2",
	"6-0008g-1",
	"6-0008g-2",
	"6-0009g-1",
	"6-0009g-2",
	"6-0010g-1",
	"6-0010g-2",
	"6-0010g-3",
]
#####################################################################

exec("from "+netName+" import KEY_RANGE")
exec("from "+netName+" import "+netName)

# # import the data
for i in range(len(dataset)):
	fileName = "./"+method+"_data"+"/pyConfLensFlowNetFast/"+dataset[i]+".pickle"
	# fileName = "./experiment_data/"+netName+"/0.pickle"
	with open(fileName,'rb') as f:
		data = pickle.load(f)

	if i == 0:
		I = data['I']
		Loc = data['Loc']
		Z_f = data['Z_f']
	else:
		I = np.concatenate((I,data['I']),axis=0)
		Loc = np.concatenate((Loc, data['Loc']),axis=0)
		Z_f = Z_f + data['Z_f']
pdb.set_trace()
#####################################################################
# 

#####################################################################
##  Determine the initial configuration
#####################################################################
# just some basic tryouts

######## READ INITIAL FROM FILES ########################
# we use the training result of pyLensFlowNet as initialization
cfg_file = "./opt_results/pyConfLensFlowNetFast_ext/"+\
	"1x1t-text34-py4-setup5-one-sequential-regularize-nothreshold.pickle"
	# "initial_nothreshold.pickle"
	# "1x1t-text34-setup3-py5-sparse-w2r-stochastic.pickle"

with open(cfg_file,'rb') as f:
	cfg_data = pickle.load(f)
cfg = cfg_data['cfg']

# compute training time
time_train = cfg_data['time']
total_time = 0
total_episode = 0
for i in range(len(time_train)):
	for j in range(len(time_train[i])):
		total_time += time_train[i][j]
		total_episode += 1

print('Total time: ', total_time)
print('Total episode', total_episode)

# adding noise to the data
if cfg[0]['noise_var'] > 0:
	for i in range(I.shape[0]):
		I[i,:,:,:] = gauss_noise(\
			I[i,:,:,:], mu=0,var=cfg['noise_var'])

# range of output
depth = np.reshape(Loc[:,2,:],-1)
DEPTH_RANGE = [depth.min(),depth.max()]
KEY_RANGE['Z'] = DEPTH_RANGE
KEY_RANGE['Z_gt'] = DEPTH_RANGE
KEY_RANGE['Z_valid'] = DEPTH_RANGE
KEY_RANGE['Z_gt_valid'] = DEPTH_RANGE

# initailization
ff = eval(netName+"(cfg)")

# # find the file to save
# os.chdir('./opt_results/'+cfg[0]['netName']+'/')

pdb.set_trace()

ff.visual_mean_var(I, Loc, Z_f, conf_thre=0)
# ff.visual_err_conf_map(I, Loc, Z_f, log=True)
# ff.sparsification_map(I, Loc, Z_f)
# ff.AUC_map(I, Loc, Z_f)
# pdb.set_trace()

start_time = time.time()
for i in range(I.shape[0]):
	# input images
	Z_gt = Loc[i,2,int((Loc.shape[2]-1)/2)]
	Z_map_gt = np.ones(I[i,:,:,0].shape) * Z_gt
	ff.input_images(I[i,:,:,:], Z_map_gt, Z_f[i])


	# show the depth map
	ff.regular_output(conf_thre=0.99)

	# validate the image pyramid
	# ff.validate_pyramid()

	cv2.waitKey(1)
print((I.shape[0])/(time.time()-start_time))