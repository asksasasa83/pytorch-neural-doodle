##
## pytorch-neural-doodle/src/generate.py
##
## Created by Paul Warkentin <paul@warkentin.email> on 10/08/2018.
## Updated by Bastian Boll <mail@bbboll.com> on 31/08/2018.
##

import numpy as np
import os
import sys
import time

__exec_dir = sys.path[0]
while os.path.basename(__exec_dir) != "src":
	__exec_dir = os.path.dirname(__exec_dir)
	sys.path.insert(0, __exec_dir)

import torch

from utils.common.files import get_full_path
from utils.common.logging import logging_info
from utils.image import load
from utils.common.terminal import query_yes_no
from cli import parse_arguments

from models import VGG19
from loss import StyleLoss


if __name__ == "__main__":
	arguments = parse_arguments()

	# print some information
	logging_info("Generate a new image.")
	logging_info("Input style file:    {}".format(arguments.input_style_file))
	logging_info("Input map file:      {}".format(arguments.input_map_file))
	logging_info("Output filename:     {}".format(arguments.output_file))
	logging_info("Output map file:     {}".format(arguments.output_map_file))
	logging_info("Output content file: {}".format(arguments.output_content_file))
	logging_info("Content weight:      {}".format(arguments.content_weight))
	logging_info("Content layers:      {}".format(arguments.content_layers))
	logging_info("Style layers:        {}".format(arguments.style_layers))
	logging_info("Style weight:        {}".format(arguments.style_weight))
	logging_info("Map channel weight:  {}".format(arguments.map_channel_weight))

	should_continue = query_yes_no("Continue?", default="yes")
	if not should_continue:
		exit()

	# determine compute device
	if torch.cuda.is_available():
		device = torch.device("cuda")
	else:
		device = torch.device("cpu")

	# initialize model
	model = VGG19(input_channels=3)
	vgg_19_path = get_full_path("models", "vgg_19_imagenet", "vgg_19.minimum.pkl")
	if not os.path.isfile(vgg_19_path):
		logging_error("Please download the weights and biases of the VGG 19 network from " \
					  "http://download.tensorflow.org/models/vgg_19_2016_08_28.tar.gz, extract the archive and run the Python script "\
					  "`extract_vgg_19_weights.py`.")
	model.initialize(vgg_19_path)
	model.to(device)

	# load input data
	input_style = load(arguments.input_style_file, device=device)
	input_map   = load(arguments.input_map_file,   device=device)
	output_map  = load(arguments.output_map_file,  device=device)
	#output_content = load(arguments.output_content_file)

	# perform forward pass of model to extract response for content loss
	#content_response = model.forward(output_content)

	# perform forward pass of model to extract response for style loss
	style_response = model.forward(input_style, extract_layers=arguments.style_layers)

	# initialize style loss
	style_loss = StyleLoss(style_response, arguments.style_layers, stride=12)

	# TEST:
	activations = model.forward(input_map, extract_layers=arguments.style_layers)

	style_loss.loss(activations)

	# main loop
	for ii in range(arguments.num_phases):
		pass
