# encoding: utf-8
"""
经过更改，20181116
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader
from torch.utils.data import TensorDataset
from torch.autograd import Variable as var
from sklearn.metrics import r2_score

def get_data(x, y, batch_size, shuffle):
    dataset = TensorDataset(x, y)
    return DataLoader(dataset, batch_size, shuffle=shuffle, num_workers=4)


def train_model(model, x_train, y_train, x_valid, y_valid,xgb_model,epochs, batch_size, lr, weight_decay, use_gpu):
    if use_gpu:
        model = model.cuda()
    metric_log = defaultdict(list)

    train_data = get_data(x_train, y_train, batch_size, True)
    if x_valid is not None:
        valid_data = get_data(x_valid, y_valid, batch_size, False)
    else:
        valid_data = None

    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    criterion = nn.MSELoss()

    for e in range(epochs):
        # 训练模型
        model.train()
        for data in train_data:
            x, y = data
            if use_gpu:
                x = x.cuda()
                y = y.cuda()
            # forward
            out = model(x)
            
            out_numpy = out.data.cpu().numpy()
            y_pre = xgb_model.predict(out_numpy)
            
            y_pre = torch.from_numpy(y_pre).view(batch_size, 1)
            y_pre = y_pre.cuda()
            loss = criterion(y_pre, y)
            # backward
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        metric_log['train_rmse'].append(get_rmse(model, x_train, y_train, use_gpu))

        # 测试模型
        if x_valid is not None:
            metric_log['valid_rmse'].append(get_rmse(model, x_valid, y_valid, use_gpu))
            print_str = 'epoch: {}, train rmse: {:.3f}, valid rmse: {:.3f}' \
                .format(e + 1, metric_log['train_rmse'][-1], metric_log['valid_rmse'][-1])
        else:
            print_str = 'epoch: {}, train rmse: {:.3f}'.format(e + 1, metric_log['train_rmse'][-1])
        if (e + 1) % 10 == 0:
            print(print_str)
            print()

    # 可视化
    figsize = (10, 5)
    fig = plt.figure(figsize=figsize)
    plt.plot(metric_log['train_rmse'], color='red', label='train')
    if valid_data is not None:
        plt.plot(metric_log['valid_rmse'], color='blue', label='valid')
    plt.legend(loc='best')
    plt.xlabel('epochs')
    plt.ylabel('loss')
    plt.show()


def get_rmse(model, feature, label, use_gpu):
    if use_gpu:
        feature = feature.cuda()
        label = feature.cuda()
    model.eval()
    mse_loss = nn.MSELoss()
    with torch.no_grad():
        encoded, decoded = model(feature)
    # clipped_pred = pred.clamp(1, float('inf'))
    rmse = (mse_loss(decoded, label)).sqrt()
    return rmse.item()


def pred(net, test_data, test_features):
    net = net.eval()
    net = net.cpu()
    with torch.no_grad():
        preds = net(test_features)
    preds = np.exp(preds.numpy())
    test_data['SalePrice'] = pd.Series(preds.reshape(1, -1)[0])
    submission = pd.concat([test_data['Id'], test_data['SalePrice']], axis=1)
    submission.to_csv('submission.csv', index=False)

def auto_train(model, x_train, y_train, x_valid, y_valid,epochs, batch_size, lr, weight_decay, use_gpu):
    if use_gpu:
        model = model.cuda()
    metric_log = defaultdict(list)

    train_data = get_data(x_train, y_train, batch_size, True)
    if x_valid is not None:
        valid_data = get_data(x_valid, y_valid, batch_size, False)
    else:
        valid_data = None

    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    criterion = nn.MSELoss()

    for e in range(epochs):
        # 训练模型
        model.train()
        for data in train_data:
            x, y = data
            if use_gpu:
                x = x.cuda()
                y = x.cuda()
            # forward
            encoded, decoded = model(x)
            
            loss = criterion(decoded, y)
            # backward
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        metric_log['train_rmse'].append(get_rmse(model, x_train, y_train, use_gpu))

        # 测试模型
        if x_valid is not None:
            metric_log['valid_rmse'].append(get_rmse(model, x_valid, y_valid, use_gpu))
            print_str = 'epoch: {}, train rmse: {:.3f}, valid rmse: {:.3f}' \
                .format(e + 1, metric_log['train_rmse'][-1], metric_log['valid_rmse'][-1])
        else:
            print_str = 'epoch: {}, train rmse: {:.3f}'.format(e + 1, metric_log['train_rmse'][-1])
        if (e + 1) % 10 == 0:
            print(print_str)
            print()

    # 可视化
    figsize = (10, 5)
    fig = plt.figure(figsize=figsize)
    plt.plot(metric_log['train_rmse'], color='red', label='train')
    if valid_data is not None:
        plt.plot(metric_log['valid_rmse'], color='blue', label='valid')
    plt.legend(loc='best')
    plt.xlabel('epochs')
    plt.ylabel('loss')
    plt.show()

def auto_pre(net, test_data):
    net = net.eval()
    net = net.cpu()
    with torch.no_grad():
        encoded, decoded = net(test_data)
    encoded = encoded.data.numpy()
    return encoded

def xgb_train(model, x_train, y_train, x_valid, y_valid):
    #metric_log = defaultdict(list)
    
    model.fit(x_train, y_train)
    y_train_pre = model.predict(x_train)
    
    y_valid_pre = model.predict(x_valid)
    
    r2_loss_train = r2_score(y_train, y_train_pre)
    r2_loss_valid = r2_score(y_valid, y_valid_pre)
    
    print('xgb 训练误差为：', r2_loss_train)
    print('\n')
    print('xgb 验证误差为：', r2_loss_valid)