# Vision-Mamba Deepfake Detection

This model detects deepfake content from face images or video frames.

## Input
- RGB image (224x224)
- Normalized with ImageNet mean/std

## Output
- Sigmoid score ∈ [0,1]
- >0.65 → FAKE
- <0.35 → REAL

## Architecture
- Lightweight CNN backbone
- Vision-Mamba–style gated head
- Trained on DFDC face crops

## Usage
Load `model.safetensors` using safetensors or PyTorch.
