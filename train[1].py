# -*- coding: utf-8 -*-
"""Untitled5.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kwUg96Gdmu2YMs43jd4LicIiGO_6dyI5
"""

cd /content/

ls -a

rm -rf .ipynb_checkpoints

import os
import cv2
import time
import random
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, datasets
from torchvision.datasets import ImageFolder
from sklearn.model_selection import train_test_split
from PIL import Image


path = 'train'
print(path)

batch_size = 32

data_transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.RandomRotation(10, resample=Image.BICUBIC, expand=False, center=(55, 5)),
    transforms.RandomResizedCrop(224),
    transforms.ColorJitter(brightness=0.1, contrast=0, saturation=0, hue=0.1),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize((.5, .5, .5), (.5, .5, .5))
])

dataset = datasets.ImageFolder(path, transform=data_transform)
print(len(dataset))
train_dataset,test_dataset = train_test_split(dataset, test_size=0.2, random_state=42)

testLoader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size)

trainLoader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size,shuffle=True)
valLoader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size,shuffle=True)


print("data process...")
print("split train = %d"  % (len(train_dataset)))
print("split test = %d" % (len(test_dataset)))
print('-------------------------------------------------')

def train(model):

    learning_rate = 0.001
    decay=0.9
    num_epochs = 100
    num_classes = 3
    
    loss_function = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    avg_loss = 0
    cnt = 0
    current_loss = 0.0
    loss_values = []
    train_acc=0
    total=0
    
    for epoch in range(0, num_epochs):
        #print(f'Starting epoch {epoch+1}')
        current_loss = 0.0
        start = time.time()
        for i, data in enumerate(trainLoader):
            images, labels = data
            images = images.to(device)
            labels = labels.to(device)
                
            # Forward + Backward + Optimize
            optimizer.zero_grad()
            
            outputs = model(images)
            loss = loss_function(outputs,labels)
            
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            train_acc+=(predicted == labels).sum().item()
            
            avg_loss += loss.data
            cnt += 1
            
            loss.backward()
            optimizer.step()
            current_loss+=loss.item()
        
        print("[Epoch: %d] train loss: %f, avg_loss: %f" % (epoch+1,loss.data, avg_loss/cnt))
        # wandb.log({"loss": loss.data})
        # wandb.log({"Avg loss": avg_loss/cnt})
        
        end = time.time()
        torch.cuda.synchronize()
        print('Use time:',end-start)
        
        if epoch % 20 ==0:
            learning_rate=learning_rate*decay
        loss_values.append(current_loss / len(trainLoader))
    print('train_acc : {:.5f}'.format( 100.0 * train_acc / total))
    

    
    
    correct, total = 0, 0
    # result = {}
    with torch.no_grad():
    
        for i, data in enumerate(testLoader):
  
            # Get inputs
            images, labels = data
            images = images.cuda()
            labels = labels.cuda()
            # Generate outputs
            outputs = model(images)

            # Set total and torch
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
  
        # Print accuracy
        print('Accuracy %f %%' % (100.0 * correct / total))
        print('-----------------------------------------------')
        # wandb.log({"Accuracy": 100.0 * correct / total})
        
    print('Saving trained model...')
    torch.save(model.state_dict(), 'cls_breast')

if __name__ == '__main__':
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print('Device:', device)
    
    model= models.vgg16(pretrained=True)
    model = model.to(device)
    
    print("Start Training!!")
    train(model)
    print('-----------------------------------------------')

