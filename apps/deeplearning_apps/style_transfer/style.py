import argparse
import os
import sys
import time
import re
import cv2

import numpy as np
import torch
from torch.optim import Adam
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision import transforms
import torch.onnx
from transformer_net import TransformerNet



from utility import load_image, save_image



device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')



def load_model(model_path):
    print('load model')
    with torch.no_grad():
        style_model = TransformerNet()
        state_dict = torch.load(model_path)
        # remove saved deprecated running_* keys in InstanceNorm from the checkpoint
        for k in list(state_dict.keys()):
            if re.search(r'in\d+\.running_(mean|var)$', k):
                del state_dict[k]
        style_model.load_state_dict(state_dict)
        style_model.to(device)
        style_model.eval()
        return style_model



def stylize(style_model, content_image, output_image):
    content_image = load_image(content_image)
    content_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Lambda(lambda x: x.mul(255))
    ])
    content_image = content_transform(content_image)
    if len(content_image.shape) > 2 and content_image.shape[0] == 4:
        #convert the image from RGBA2RGB
        content_image = content_image[:3,:,:]
    content_image = content_image.unsqueeze(0).to(device)

    

    with torch.no_grad():
        print(content_image.shape)
        output = style_model(content_image).cpu()

    save_image(output_image, output[0])
