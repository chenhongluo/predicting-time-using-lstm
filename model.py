# -*- coding: utf-8 -*-

# Author: chl

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
import json

torch.manual_seed(1)

train_filename = ""
test_filename = ""
info_filename = ""

hidden_dim = 200

# user_dim = 200
# group_dim = 10
# app_dim = 10
# queue_dim = 10
# partition_dim = 10
infos = torch.Tensor(json.load(info_filename))

with open(train_filename) as f:
    train_data = json.load(f)

with open(test_filename) as f:
    test_data = json.load(f)

request_len = [1]
embedding_len = [0,1,2,3,4]
nums = infos[11:16,2]
dims = [200,10,10,10,10]

input_size = len(request_len)
for i in embedding_len:
    input_size += dims[i]


# Prepare data:

def prepare_sequence(seq,embedings):
    t = torch.zeros(input_size)
    for j,i in enumerate(request_len):
        t[j] = seq[7+i]
    s = len(request_len)
    for j,i in enumerate(embedding_len):
        t[s:s+dims[i]] = embedings[i][seq[11+i]]
    return t

######################################################################
# Create the model:


class LSTMTagger(nn.Module):

    def __init__(self, tagset_size):
        super(LSTMTagger, self).__init__()
        self.hidden_dim = hidden_dim

        self.embeddings = []
        for i in range(5):
            self.embeddings.append(nn.Embedding(nums[i], dims[i]))

        # The LSTM takes word embeddings as inputs, and outputs hidden states
        # with dimensionality hidden_dim.
        self.lstm = nn.LSTM(input_size, hidden_dim)

        # The linear layer that maps from hidden state space to tag space
        self.hidden2tag = nn.Linear(hidden_dim, tagset_size)

    def forward(self, seq):
        embeds = torch.cat([prepare_sequence(seq[i],self.embeddings) for i in range(len(seq))]).cuda()
        lstm_out, _ = self.lstm(embeds.view(len(seq), 1, -1))
        predict_times = self.hidden2tag(lstm_out.view(len(seq)))
        return predict_times

######################################################################
# Train the model:

model = LSTMTagger(1).cuda()
def train(model,epoch_num):
    loss_function = nn.MSELoss()
    optimizer = optim.SGD(model.parameters(), lr=0.1)

    for epoch in range(epoch_num):  # again, normally you would NOT do 300 epochs, it is toy data
        for u, v in train_data:
            model.zero_grad()
            if len(v) != 0:
                predict_times = model(v)
            true_times = torch.zeros([len(v)])
            for i in range(len(train_data)):
                true_times[i] = v[18]
            true_times.cuda()
            loss = loss_function(predict_times,true_times)
            loss.backward()
            optimizer.step()
    return model

def test(model):
    loss_function = nn.MSELoss()
    loss = 0
    with torch.no_grad():
        for u, v in test_data:
            if len(v) != 0:
                predict_times = model(v)
            true_times = torch.zeros([len(v)])
            for i in range(len(train_data)):
                true_times[i] = v[18]
            true_times.cuda()
            loss += loss_function(predict_times,true_times)
    return loss