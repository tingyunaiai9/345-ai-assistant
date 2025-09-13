
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import os
import cv2
import numpy as np

from PIL import Image

class LeNet(nn.Module):
    def __init__(self, num_classes=10):
        super(LeNet, self).__init__()
        self.layer1 = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2))
        self.layer2 = nn.Sequential(
            nn.Conv2d(16, 32, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2))
        self.layer3 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2))
        self.fc = nn.Linear(3 * 3 * 64, num_classes)

    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = self.layer3(out)
        out = out.reshape(out.size(0), -1)
        out = self.fc(out)
        return out

def image_classification(file):
    """
    TODO
    """

    def pre_process(img, device):
        img = cv2.resize(img, (28, 28))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        img = img / 255
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(device)
        img = img.float()
        img = img.unsqueeze(0)
        if img.ndimension() == 3:
            img = img.unsqueeze(0)
        return img

    def inference(model, img):
        device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        img = pre_process(img, device)
        model.to(device)
        model.eval()
        with torch.no_grad():
            preds = model(img)
            label = preds[0].argmax()
        return label

    # 处理 file 路径
    if hasattr(file, 'name'):
        img_path = file.name
    else:
        img_path = file
    if not os.path.exists(img_path):
        return "图片文件不存在"
    img = cv2.imread(img_path)
    if img is None:
        return "无法读取图片文件"

    # 加载模型
    model_path = 'lenet.pth'
    if not os.path.exists(model_path):
        return f"模型文件不存在: {model_path}"
    load_dict = torch.load(model_path, map_location=torch.device('cpu'))
    if isinstance(load_dict, dict) and 'state_dict' in load_dict:
        state_dict = load_dict['state_dict']
    else:
        state_dict = load_dict
    model = LeNet(num_classes=10)
    model.load_state_dict(state_dict)

    label = inference(model, img)
    # return f"Classification result: {label.item()}"
    return f"{label.item()}"
