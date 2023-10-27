import argparse

import numpy
import cupy as np

from common.util import (print_args, load, save, to_gpu)
from common.models import Convolutional
from common.optimizer import Adam
from common.trainer import Trainer
from common.dataloader import DataLoader

from dataset.mnist import load_mnist

np.cuda.set_allocator(np.cuda.MemoryPool().malloc)


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lr', type=float, default=0.001)
    parser.add_argument('--epochs', type=int, default=16)
    parser.add_argument('--batch-size', type=int, default=128)
    parser.add_argument('--hidden-size', type=int, nargs='+', default=[16, 64, 128, 64, 16])
    parser.add_argument('--weight-init-std', type=str, default='xavier')
    parser.add_argument('--loads', action='store_true')
    parser.add_argument('--saves', action='store_true')
    parser.add_argument('--weight', type=str, default='./data/Conv/weight.pkl')
    parser.add_argument('--seed', type=int, default=0)

    return parser.parse_args()


if __name__ == '__main__':
    opt = vars(parse_opt())
    print_args(opt)
    lr, goal_epoch, batch_size, hidden_size_list, weight_init_std, loads, saves, weight, seed = \
        (opt['lr'], opt['epochs'], opt['batch_size'], opt['hidden_size'],
         opt['weight_init_std'], opt['loads'], opt['saves'], opt['weight'], opt['seed'])

    numpy.random.seed(seed)
    np.random.seed(seed)

    (x_train, t_train), (x_test, t_test) = load_mnist(flatten=False)
    x_train, t_train, x_test, t_test = to_gpu(x_train, t_train, x_test, t_test)
    train_loader = DataLoader(x_train, t_train, batch_size)
    test_loader = DataLoader(x_test, t_test, batch_size)

    channel, input_size, class_number = x_train[1], x_train.shape[2], 10
    if loads:
        model, optimizer = load(weight)
    else:
        model = Convolutional()
        optimizer = Adam(model=model, lr=lr)

    trainer = Trainer(model, optimizer)
    trainer.train(train_loader, test_loader, epochs=goal_epoch, batch_size=batch_size)

    if saves:
        save(weight, model, optimizer)