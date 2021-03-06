#!/usr/bin/env python
# coding: utf-8

# ## 03 Feature Extraction

# Imports

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import clear_output
import torch
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
import fnmatch
import yaml
import sys


# Check GPU availability
from chosen_gpu import get_freer_gpu
device = torch.device(get_freer_gpu()) 
print("Configured device: ", device)

# 1. Loading Data
par = sys.argv[1]
file = sys.argv[2]
task = sys.argv[3]
model_name = "cnn"
drift = "drift"

X = np.load('../data/preprocessed_np/round2/{par}/{drift}/{file}_{task}_X.npy'.format(par=par,drift = drift,file=file, task=task), allow_pickle=True)
y = np.load('../data/preprocessed_np/round2/{par}/{drift}/{file}_{task}_y.npy'.format(par=par,drift = drift,file=file, task=task), allow_pickle=True)


# 1.1 Check shape
# [# stim, # electrod, # datapoint]
print(X.shape)
print(y.shape)


# 1.2 Plot
# ### Plot to see wheter eegs have drift or not
# print(X[100][0].shape)
# fig, ax = plt.subplots(16,1,figsize=(20,50),sharex=True)

# for i in range(data.shape[1]):
#     ax[i].plot(X[100][i])


# 2. Reserve data for Real TEST
# - test_size: 0.1
# - 10% of data is reserved for the real test --> X_test, y_test
# - 90% will be again divided into (train,test,val) --> X_model, y_model

# <img src="img/Split.jpg" width=300 height=300 />

# 2.1 Reserve some data for REAL TEST
from sklearn.model_selection import train_test_split

X_model, X_real_test, y_model, y_real_test = train_test_split( X, y, test_size=0.1, random_state=42, stratify= y)


# Check if number of classes is equal
def check_split(X1, X2, y1, y2, name1, name2):
    unique1, count1 = np.unique(y1, return_counts=True)
    unique2, count2 = np.unique(y2, return_counts=True)

    assert count1[0] == count1[1] == count1[2]
    assert count2[0] == count2[1] == count2[2]

    print('='*20,name1,'='*20)
    print(f"Shape of X_{name1}: ", X1.shape)
    print(f"Shape of y_{name1}: ",y1.shape)
    print(f"Classes of y_{name1}: ",unique1)
    print(f"Counts of y_{name1} classes: ",count1)
    print('='*20,name2,'='*20)
    print(f"Shape of X_{name2}: ",X2.shape)
    print(f"Shape of y_{name2}: ",y2.shape)
    print(f"Classes of y_{name2}: ",unique2)
    print(f"Counts of y_{name2} classes: ",count2)

check_split(X_model, X_real_test, y_model, y_real_test,'model','real test')


# 3. Prepare Train Val Test Data 

# - 10 can be thought of as totally new eeg records and will be used as the real evaluation of our model.
# - For X : Chunking eeg to lengh of 10 data point in each stimuli's eeg
# - For y(lebels) : Filled the lebels in y because we chunk X ( 1 stimuli into 6 chunk). We have 500 labels before but now we need 500 x 6 = 3000 labels

# 3.1 Chunking

import sys
np.set_printoptions(threshold=sys.maxsize)

def chunk_data(data, size):
    data_keep = data.shape[2] - (data.shape[2]%size)
    data = data[:,:,:data_keep]
    data = data.reshape(-1,data.shape[1],data.shape[2]//size,size)
    data = np.transpose(data, (0, 2, 1, 3)  )
    return data

def filled_y(y, chunk_num):
    yy = np.array([[i] *chunk_num for i in  y ]).ravel()
    return yy

chunk_size = 10

print('=================== X ==================')
print(f'Oringinal X shape {X_model.shape}')
X = chunk_data(X_model, chunk_size)
print(f'Chunked X : {X.shape}') # (#stim, #chunks, #electrodes, #datapoint per chunk)
chunk_per_stim = X.shape[1]
X = X.reshape(-1,16,chunk_size)
print(f'Reshape X to : {X.shape}')
print('=================== y ==================')
print(f'Shape of y : {y_model.shape}')
y_filled = filled_y(y_model, chunk_per_stim)
y = y_filled
print(f'Shape of new y : {y.shape}')


# 3.2 Train Test Val Split and Prepare X and y in correct shape
# 
# - For X, pytorch (if set batch_first) LSTM requires to be (batch, seq_len, features).  Thus, for us, it should be (100, 75, 16).
# - For y, nothing is special
# - So let's convert our numpy to pytorch, and then reshape using view

# 3.2.1 Train Test Val Split
X_train, X_val_test, y_train, y_val_test = train_test_split( X, y, test_size=0.3, random_state=42, stratify= y)
check_split(X_train, X_val_test, y_train, y_val_test,'train','val_test')

X_val, X_test, y_val, y_test = train_test_split( X_val_test, y_val_test, test_size=0.33, random_state=42, stratify= y_val_test)
check_split(X_val, X_test, y_val, y_test ,'val','test')


# 3.2.2 Convert to torch
def check_torch_shape(torch_X, torch_y, name):
    print('='*20,name,'='*20)
    print(f"Shape of torch_X_{name}: ",torch_X.shape)
    print(f"Shape of torch_y_{name}: ",torch_y.shape)    

torch_X_train = torch.from_numpy(X_train)
torch_y_train = torch.from_numpy(y_train)
check_torch_shape(torch_X_train,torch_X_train,'train')

torch_X_val = torch.from_numpy(X_val)
torch_y_val = torch.from_numpy(y_val)
check_torch_shape(torch_X_val,torch_y_val,'val')

torch_X_test = torch.from_numpy(X_test)
torch_y_test = torch.from_numpy(y_test)
check_torch_shape(torch_X_test,torch_y_test,'test')


# 3.2.3 Reshape

# CNN requires the input shape as (batch, channel, height, width)

torch_X_train_reshaped = torch_X_train.reshape(torch_X_train.shape[0],torch_X_train.shape[1],1,torch_X_train.shape[2])
print("Converted torch_X_train to ", torch_X_train_reshaped.size())

torch_X_val_reshaped = torch_X_val.reshape(torch_X_val.shape[0],torch_X_val.shape[1],1,torch_X_val.shape[2])
print("Converted torch_X_val to ", torch_X_val_reshaped.size())

torch_X_test_reshaped = torch_X_test.reshape(torch_X_test.shape[0],torch_X_test.shape[1],1,torch_X_test.shape[2])
print("Converted torch_X_test to ", torch_X_test_reshaped.size())


# 4. Dataset and DataLoader

from torch.utils.data import TensorDataset

BATCH_SIZE = 128 #keeping it binary so it fits GPU

#Train set loader
train_dataset = TensorDataset(torch_X_train_reshaped, torch_y_train)
train_iterator = torch.utils.data.DataLoader(dataset=train_dataset, 
                                           batch_size=BATCH_SIZE, 
                                           shuffle=True)
#Val set loader
val_dataset = TensorDataset(torch_X_val_reshaped, torch_y_val)
valid_iterator = torch.utils.data.DataLoader(dataset=val_dataset, 
                                           batch_size=BATCH_SIZE, 
                                           shuffle=True)
#Test set loader
test_dataset = TensorDataset(torch_X_test_reshaped, torch_y_test)
test_iterator = torch.utils.data.DataLoader(dataset=test_dataset, 
                                           batch_size=BATCH_SIZE, 
                                           shuffle=True)


# 5. Training for Feature Extraction 

# 5.1 Define functions for calculating time, plotting and counting model params

def epoch_time(start_time, end_time):
    elapsed_time = end_time - start_time
    elapsed_mins = int(elapsed_time / 60)
    elapsed_secs = int(elapsed_time - (elapsed_mins * 60))
    return elapsed_mins, elapsed_secs

def do_plot(train_losses, valid_losses):
    plt.figure(figsize=(25,5))
#     clear_output(wait=True)
    plt.plot(train_losses, label='Train Loss')
    plt.plot(valid_losses, label='Valid Loss')
    plt.title('Train and Val loss')
    plt.legend()
    plt.show()

#Count the parameters for writing papers
def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


# 5.2 Define model parameters
# - Count model parameters
# - optimizer
# - loss function
# - GPU
from models import EEGEncoder

model_EEGEncoder = EEGEncoder()
model_EEGEncoder = model_EEGEncoder.float() #define precision as float to reduce running time
models = [model_EEGEncoder]

for model in models:
    print(f'The model {type(model).__name__} has {count_parameters(model):,} trainable parameters')# Train the model


# 5.3 Train the model
from train import train
from evaluate import evaluate

import torch.optim as optim

best_valid_loss = float('inf')
train_losses    = []
valid_losses    = []

learning_rate = 0.0001
N_EPOCHS      = 1000          ## best is 10k
criterion     = nn.CrossEntropyLoss()
optimizer     = torch.optim.Adam(model.parameters(), lr=learning_rate)


for model in models:
    model = model.to(device)
criterion = criterion.to(device)

model.is_debug = False
iteration = 0
classes = np.array(('Red', 'Green', 'Blue'))
for i, model in enumerate(models):
    print(f"Training {type(model).__name__}")

    start_time = time.time()

    for epoch in range(N_EPOCHS):
        start_time = time.time()

        train_loss, train_acc, train_predicted    = train(model, train_iterator, optimizer, criterion, device)
        valid_loss, valid_acc, valid_predicted, _ = evaluate(model, valid_iterator, criterion, classes, device)

        train_losses.append(train_loss)
        valid_losses.append(valid_loss)

        end_time = time.time()

        epoch_mins, epoch_secs = epoch_time(start_time, end_time)

        iteration     += 1

        if (epoch+1) % 50 == 0:
            clear_output(wait=True)
            print(f'Epoch: {epoch+1:02}/{N_EPOCHS}  |',end='')
            print(f'\tTrain Loss: {train_loss:.5f}  | Train Acc: {train_acc:.2f}%  |', end='')
            print(f'\t Val. Loss: {valid_loss:.5f}  | Val. Acc: {valid_acc:.2f}%')
            do_plot(train_losses, valid_losses)


        if valid_loss < best_valid_loss:
            best_valid_loss = valid_loss
            #print("Model:{} saved.".format(type(model).__name__))
            torch.save(model.state_dict(), "../model/feature_extraction/round2/{par}/{model_name}/{drift}/EEG_ENCODER_{task}.pt.tar".format(par=par, model_name=model_name,drift=drift,task=task))
            best_model_index = i


# 6. Evaluation [Test set]
# using test set

def squeeze_to_list(_tmp):
    from functools import reduce
    import operator
    xx = [ i.cpu().detach().numpy().ravel().tolist() for i in _tmp]
    xx = reduce(operator.concat, xx)
    return xx


# Define classes

classes = np.array(('Red', 'Green', 'Blue'))
model = EEGEncoder()
model = model.float()
model = model.to(device)
model.load_state_dict(torch.load('../model/feature_extraction/round2/{par}/{model_name}/{drift}/EEG_ENCODER_{task}.pt.tar'.format(par=par,model_name=model_name,drift=drift,task=task)))

test_loss, test_acc , predicted, actual_labels, acc_class_test = evaluate(model, test_iterator, criterion, classes, device, test = True)
print(f'Test Loss: {test_loss:.3f} | Test Acc: {test_acc:.2f}%')
print("---------------")
print(" (Actual y , Predicted y)")

y_test_t = squeeze_to_list(actual_labels)
y_hat_test_t = squeeze_to_list(predicted)

out_test = zip(y_test_t, y_hat_test_t)

# 7. Evaluation [Real Test]
X_real_test = chunk_data(X_real_test, chunk_size)
chunk_per_stim = X_real_test.shape[1]
X_real_test = X_real_test.reshape(-1,16,chunk_size)
y_filled_real_test = filled_y(y_real_test, chunk_per_stim)

print("Chucked X_test: ",X_real_test.shape )
print("y_filled_test: ",y_filled_real_test.shape )

torch_X_real_test = torch.from_numpy(X_real_test)
torch_y_real_test = torch.from_numpy(y_filled_real_test)
check_torch_shape(torch_X_real_test,torch_y_real_test,'test')

print("Shape of torch_X: ",torch_X_real_test.shape)
print("Shape of torch_y: ",torch_y_real_test.shape)

torch_X_real_test_reshaped = torch_X_real_test.reshape(torch_X_real_test.shape[0],torch_X_real_test.shape[1],1,torch_X_real_test.shape[2])
print("Converted X to ", torch_X_real_test_reshaped.size())

real_test_dataset = TensorDataset(torch_X_real_test_reshaped, torch_y_real_test)
#Test set loader
real_test_iterator = torch.utils.data.DataLoader(dataset=real_test_dataset, 
                                          batch_size=BATCH_SIZE, 
                                          shuffle=True)

model = EEGEncoder()
model = model.float()
model = model.to(device)
model.load_state_dict(torch.load('../model/feature_extraction/round2/{par}/{model_name}/{drift}/EEG_ENCODER_{task}.pt.tar'.format(par=par,model_name=model_name,drift=drift,task=task)))

test_loss, real_test_acc , predicted, actual_labels, acc_class_real_test = evaluate(model, real_test_iterator, criterion, classes, device, test=True)
print(f'Test Loss: {test_loss:.3f} | Test Acc: {real_test_acc:.2f}%')
print("---------------")
print(" (Actual y , Predicted y)")

y_test_rt    = squeeze_to_list(actual_labels)
y_hat_test_rt = squeeze_to_list(predicted)

out_real_test = zip(y_test_rt, y_hat_test_rt)
print(list(out_real_test))

# 8. Extracted Features
X_train_val = np.concatenate((X_train,X_val))
y_train_val = np.concatenate((y_train,y_val))

print(X_train_val.shape)
print(y_train_val.shape)

torch_X_train_val = torch.from_numpy(X_train_val)
torch_y_train_val = torch.from_numpy(y_train_val)
check_torch_shape(torch_X_train_val,torch_y_train_val,'train_val')

torch_X_train_val_reshaped = torch_X_train_val.reshape(torch_X_train_val.shape[0],torch_X_train_val.shape[1],1,torch_X_train_val.shape[2])
print("Converted X to ", torch_X_train_val_reshaped.size())

# save extracted features
eeg_encode = model_EEGEncoder.get_latent(torch_X_train_val_reshaped.to(device).float())
eeg_extracted_features = eeg_encode.detach().cpu().numpy()


# 9. SAVE
# Save Real Test
np.save("../data/participants/{par}/{task}/X_real_test".format(par=par,task=task),X_real_test)
np.save("../data/participants/{par}/{task}/y_real_test".format(par=par,task=task),y_filled_real_test)

# Save Train
np.save("../data/participants/{par}/{task}/X_train".format(par=par,task=task),X_train)
np.save("../data/participants/{par}/{task}/y_train".format(par=par,task=task),y_train)

# Save Test
np.save("../data/participants/{par}/{task}/X_test".format(par=par,task=task),X_test)
np.save("../data/participants/{par}/{task}/y_test".format(par=par,task=task),y_test)

# Save Val
np.save("../data/participants/{par}/{task}/X_val".format(par=par,task=task),X_val)
np.save("../data/participants/{par}/{task}/y_val".format(par=par,task=task),y_val)

# Save Extracted Features
np.save('../data/participants/{par}/{task}/extracted_features_X'.format(par=par,task=task), eeg_extracted_features )
np.save('../data/participants/{par}/{task}/extracted_features_y'.format(par=par,task=task), y_train_val)


# 10. Results
with open(f"../results/classification_results_{sys.argv[3]}.txt", "a") as myfile:
    myfile.write(f'================= {sys.argv[1]} ================\n')
    myfile.write(f" Train Acc: {train_acc} \n Valid Acc: {valid_acc} \n Test Acc: {test_acc} \n Real test Acc: {real_test_acc} \n")
    myfile.write("------- Acc per class for test ------- \n")
    for v,k in acc_class_test.items():
        myfile.write(f"{v}: {k[0]} \n")
    myfile.write("---- Acc per class for real test ----- \n")
    for v,k in acc_class_real_test.items():
        myfile.write(f"{v}: {k[0]} \n")

with open(f"../results/classification_results_{sys.argv[3]}.csv", "a") as myfile:
    task = sys.argv[3]
    myfile.write(f"{sys.argv[1]},{train_acc},{valid_acc},{test_acc},{real_test_acc},")
    for v,k in acc_class_test.items():
        myfile.write(f"{k[0]},")
    for v,k in acc_class_real_test.items():
        myfile.write(f"{k[0]},")
    myfile.write("\n")
