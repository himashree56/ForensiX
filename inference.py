import torch
import cv2
import numpy as np
from torchvision import transforms
from safetensors.torch import load_file

IMG_SIZE = 224

class VisionMambaLite(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = torch.nn.Sequential(
            torch.nn.Conv2d(3, 32, 3, stride=2, padding=1),
            torch.nn.BatchNorm2d(32),
            torch.nn.ReLU(),
            torch.nn.Conv2d(32, 64, 3, stride=2, padding=1),
            torch.nn.BatchNorm2d(64),
            torch.nn.ReLU(),
            torch.nn.Conv2d(64, 128, 3, stride=2, padding=1),
            torch.nn.BatchNorm2d(128),
            torch.nn.ReLU(),
        )
        self.pool = torch.nn.AdaptiveAvgPool2d(1)
        self.head = torch.nn.Linear(128, 1)

    def forward(self, x):
        x = self.backbone(x)
        x = self.pool(x).squeeze(-1).squeeze(-1)
        return self.head(x).squeeze()

def load_model(device="cpu"):
    import os
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model.safetensors")
    model = VisionMambaLite().to(device)
    state = load_file(model_path)
    model.load_state_dict(state)
    model.eval()
    return model

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std =[0.229, 0.224, 0.225]
    )
])

@torch.no_grad()
def predict_frame(frame, model, device="cpu"):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
    frame = transform(frame).unsqueeze(0).to(device)
    score = torch.sigmoid(model(frame)).item()
    return score
