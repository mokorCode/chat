import numpy as np
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
np.set_printoptions(precision=None, suppress=True)

transform = transforms.Compose({
    transforms.ToTensor()
})

train_data = DataLoader(datasets.MNIST(
    root = './mnist',
    train = True,
    transform = transform,
    download = True
),
    batch_size = 32,
    shuffle = True
)


def cross_entropy_loss(y, t):
    batch_size = t.shape[0]
    h = 1e-4
    loss = -np.sum(np.log(y[np.arange(batch_size), t] + h)) / batch_size
    return loss

def softmax(x):
    max_value = np.max(x, keepdims=True, axis=1)
    return np.exp(x - max_value) / np.sum(np.exp(x - max_value), keepdims=True, axis=1)


false_y = np.array([[0, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0, 0, 0, 0, 0]])
false_t = np.array([1, 2])


class Affine:
    def __init__(self, w, b):
        self.x = None
        self.w = w
        self.b = b
        self.dw = None
        self.db = None
        self.origin_x_shape = None

    def forward(self, x):
        self.x = x
        self.origin_x_shape = x.shape
        self.x = x.reshape(x.shape[0], -1)
        y = self.x @ self.w
        return y
    
    def backward(self, dout):
        dx = dout @ self.w.T
        dw = self.x.T @ dout
        db = np.sum(dout, axis=0)
        self.db = db
        self.dw = dw
        dx = dx.reshape(self.origin_x_shape)
        return dx
    
class Relu:
    def __init__(self):
        self.mask = None

    def forward(self, x):
        self.mask = (x <= 0)
        dx = x.copy()
        dx[self.mask] = 0
        return dx
    
    def backward(self, dout):
        dx = dout.copy()
        dx[self.mask] = 0

        return dx

class SoftmaxWithLoss:
    def __init__(self):
        self.loss = None
        self.t = None
        self.y = None

    def forward(self, x, t):
        self.y = softmax(x)
        self.t = t
        self.loss = cross_entropy_loss(self.y, t)
        return self.loss
    
    def backward(self, dout=1):
        batch_size = self.y.shape[0]
        dx = self.y.copy()
        dx[np.arange(batch_size), self.t] -= 1
        dx /= batch_size
        return dx

def affineHeParamsGenerate(param, size1, size2):
    if param == 'w':
        return np.random.randn(size1, size2) * np.sqrt(2/size1)
    elif param == 'b':
        return np.zeros((1, size2))

class NetWork:
    def __init__(self, layers, last_layer):
        self.layers = layers
        self.last_layer = last_layer

    def forward(self, x, t):
        for layer in self.layers:
            x = layer.forward(x)
        loss = self.last_layer.forward(x, t)
        return loss

    def backward(self):
        dout = 1
        dout = self.last_layer.backward(dout)
        layers = reversed(self.layers)
        for layer in layers:
            dout = layer.backward(dout)

        return dout
    
    def update(self, learning_rate=0.01):
        for layer in self.layers:
            if layer.dw:
                layer.w -= learning_rate * layer.dw
            if layer.db:
                layer.b -= learning_rate * layer.db
    
    


def generateParams(int1, int2):
    return [affineHeParamsGenerate('w', int1, int2), affineHeParamsGenerate('b', int1, int2)]

net_work = NetWork([
    Affine(*generateParams(784, 392)),
    Relu(),
    Affine(*generateParams(392, 196)),
    Relu(),
    Affine(*generateParams(196, 98)),
    Relu(),
    Affine(*generateParams(98, 49)),
    Relu(),
    Affine(*generateParams(49, 10)),
], SoftmaxWithLoss())

net_work.forward(np.random.randn(1, 784), np.array([1]))
net_work.backward()
print(net_work.layers[0].dw)