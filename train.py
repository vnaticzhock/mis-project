import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from dbhelper import dbhelper
from itertools import chain

from torchfm.model.fm import FactorizationMachineModel

cursor = dbhelper().cursor


class CommentDataset(Dataset):
    def __init__(self):
        cursor.execute('SELECT rest_index, user_id, rating FROM comments;')
        result = cursor.fetchall()

        user_id = [tup[1] for tup in result]

        self.user_id_mapper = {k: v for v, k in enumerate(user_id)}
        self.len = len(result)
        self.x = [(x1, x2) for x1, x2, _ in result]
        self.y = [y for _, _, y in result]

    def __getitem__(self, index):
        return self.x[index], self.y[index]

    def __len__(self):
        return self.len


class TransNet(nn.modules):
    def __init__(self):
        super(TransNet, self).__init__()

        self.source = nn.Sequential(
            nn.Conv2d(3, 64, 3, 1, 1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2, 2, 0),

            nn.Conv2d(64, 128, 3, 1, 1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2, 2, 0),

            nn.Conv2d(128, 256, 3, 1, 1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.MaxPool2d(4, 4, 0),
        )

        self.target = nn.Sequential(
            nn.Conv2d(3, 64, 3, 1, 1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2, 2, 0),

            nn.Conv2d(64, 128, 3, 1, 1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2, 2, 0),

            nn.Conv2d(128, 256, 3, 1, 1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.MaxPool2d(4, 4, 0),
        )

        self.fm = FactorizationMachineModel(3, 88)

    def forward(self, x):
        rest_index, user_id = x[0], x[1]
        cursor.execute(
            'SELECT * FROM comments WHERE rest_index = %s', (rest_index,))
        result1 = set(cursor.fetchall())

        cursor.execute('SELECT * FROM comments WHERE user_id = %s', (user_id,))
        result2 = set(cursor.fetchall())

        target = result1.intersection(result2)
        source_rest = "。".join([tup[3] for tup in result1.difference(target)])
        source_user = "。".join([tup[3] for tup in result2.difference(target)])

        # 換成 word embeddings
