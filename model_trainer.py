import torch
import torch.nn as nn
import torch.onnx as onnx
import numpy as np

# 10 input features, 4 classes
class GearboxNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
           nn.Linear(10, 32),
           nn.ReLU(),
           nn.Linear(32, 16),
           nn.ReLU(),
           nn.Linear(16, 4)
        )

    def forward(self, x):
        logits = self.net(x)
        probs = torch.softmax(logits, dim=1)
        conf, indices = torch.max(probs, 1)
        return indices.float(), conf

model = GearboxNet()

# Fake synthetic training data for realism
X = []
Y = []
def add(mode, base_fft):
    for _ in range(300):
        fft = np.array([b + np.random.uniform(-0.05, 0.05) for b in base_fft])
        if mode == 0:
            temp = np.random.uniform(53, 58)
            torque = np.random.uniform(300, 330)
        elif mode == 1:
            temp = np.random.uniform(58, 65)
            torque = np.random.uniform(300, 340)
        elif mode == 2:
            temp = np.random.uniform(60, 68)
            torque = np.random.uniform(280, 330)
        elif mode == 3:
            temp = np.random.uniform(56, 62)
            torque = np.random.uniform(270, 330)
        x = np.concatenate([fft, [temp, torque]])
        X.append(x)
        Y.append(mode)

add(0, [0.2, 0.25,0.3,0.4,0.45,0.3,0.25,0.2])
add(1, [0.2,0.3,0.6,1.1,0.9,0.5,0.3,0.25])
add(2, [0.25,0.35,1.3,0.7,1.5,0.6,0.35,0.25])
add(3, [0.3,0.35,0.4,0.7,1.4,0.8,0.45,0.3])

X = torch.tensor(np.array(X), dtype=torch.float32)
Y = torch.tensor(np.array(Y), dtype=torch.long)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

for epoch in range(200):
    optimizer.zero_grad()
    logits = model.net(X)
    loss = criterion(logits, Y)
    loss.backward()
    optimizer.step()

dummy = torch.randn(1,10)
onnx.export(model, dummy, "gearbox_model.onnx", input_names=['input'], output_names=['class', 'confidence'])
print("Saved gearbox_model.onnx")
