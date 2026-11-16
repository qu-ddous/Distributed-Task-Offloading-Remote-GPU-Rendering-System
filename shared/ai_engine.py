"""
GPUShare Core AI & Neural Vision Engine
Pure PyTorch implementation of CNN architectures, synthetic dataset generators,
and Google Lens style image inference.
No heavy external dependencies required (works with pure torch + PIL + numpy).
"""

import os
import time
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from PIL import Image

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# Default classes for 10-class vision models (CIFAR-10 / ImageNet subset)
DEFAULT_CLASSES = [
    "Airplane ✈️",
    "Automobile 🚗",
    "Bird 🐦",
    "Cat 🐱",
    "Deer 🦌",
    "Dog 🐶",
    "Frog 🐸",
    "Horse 🐴",
    "Ship 🚢",
    "Truck 🚚"
]

# ==========================================
# 1. CNN Model Architectures
# ==========================================

class SimpleCNN(nn.Module):
    """3-Stage Convolutional Neural Network with BatchNorm & MaxPool"""
    def __init__(self, num_classes: int = 10, in_channels: int = 3):
        super().__init__()
        self.features = nn.Sequential(
            # Block 1
            nn.Conv2d(in_channels, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2), # 32x32 -> 16x16 or 64x64 -> 32x32

            # Block 2
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),

            # Block 3
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((4, 4))
        )
        self.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(128 * 4 * 4, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(256, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feat = self.features(x)
        feat = torch.flatten(feat, 1)
        return self.classifier(feat)


class ResidualBlock(nn.Module):
    """Residual Block with Skip Connection"""
    def __init__(self, channels: int):
        super().__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(channels)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += residual
        return self.relu(out)


class ResNetLite(nn.Module):
    """Lightweight ResNet Architecture with Residual Blocks"""
    def __init__(self, num_classes: int = 10, in_channels: int = 3):
        super().__init__()
        self.in_block = nn.Sequential(
            nn.Conv2d(in_channels, 32, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True)
        )
        self.res1 = ResidualBlock(32)
        self.down1 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True)
        )
        self.res2 = ResidualBlock(64)
        self.down2 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True)
        )
        self.res3 = ResidualBlock(128)
        self.gap = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(128, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.in_block(x)
        x = self.res1(x)
        x = self.down1(x)
        x = self.res2(x)
        x = self.down2(x)
        x = self.res3(x)
        x = self.gap(x)
        x = torch.flatten(x, 1)
        return self.fc(x)


class DepthwiseSeparableConv(nn.Module):
    def __init__(self, in_ch: int, out_ch: int, stride: int = 1):
        super().__init__()
        self.depthwise = nn.Conv2d(in_ch, in_ch, 3, stride=stride, padding=1, groups=in_ch, bias=False)
        self.bn1 = nn.BatchNorm2d(in_ch)
        self.pointwise = nn.Conv2d(in_ch, out_ch, 1, stride=1, padding=0, bias=False)
        self.bn2 = nn.BatchNorm2d(out_ch)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.relu(self.bn1(self.depthwise(x)))
        x = self.relu(self.bn2(self.pointwise(x)))
        return x


class MobileNetLite(nn.Module):
    """Lightweight MobileNet with Depthwise Separable Convolutions"""
    def __init__(self, num_classes: int = 10, in_channels: int = 3):
        super().__init__()
        self.init_conv = nn.Sequential(
            nn.Conv2d(in_channels, 32, 3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True)
        )
        self.layers = nn.Sequential(
            DepthwiseSeparableConv(32, 64, stride=1),
            DepthwiseSeparableConv(64, 128, stride=2),
            DepthwiseSeparableConv(128, 128, stride=1),
            DepthwiseSeparableConv(128, 256, stride=2),
            DepthwiseSeparableConv(256, 256, stride=1)
        )
        self.gap = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(256, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.init_conv(x)
        x = self.layers(x)
        x = self.gap(x)
        x = torch.flatten(x, 1)
        return self.fc(x)


def get_model(architecture: str, num_classes: int = 10) -> nn.Module:
    arch = architecture.lower().replace("-", "_").replace(" ", "_")
    if "resnet" in arch:
        return ResNetLite(num_classes=num_classes)
    elif "mobilenet" in arch:
        return MobileNetLite(num_classes=num_classes)
    else:
        return SimpleCNN(num_classes=num_classes)


# ==========================================
# 2. Datasets: 100k Synthetic & Folder Loaders
# ==========================================

class Synthetic100kDataset(Dataset):
    """
    Simulated 100,000 Image Dataset generator for GPUShare Assignment benchmarks.
    Pre-allocates a bank of distinct class tensors for ultra-fast memory-cached streaming
    that saturates GPU VRAM and CUDA tensor cores at maximum throughput.
    """
    def __init__(self, num_samples: int = 100000, num_classes: int = 10, img_size: int = 32):
        self.num_samples = num_samples
        self.num_classes = num_classes
        self.img_size = img_size

        # Pre-generate distinct class prototypes in memory for ultra-fast DataLoader access
        self.prototypes: List[Tuple[torch.Tensor, int]] = []
        for c in range(num_classes):
            for _ in range(10):
                t = torch.randn(3, img_size, img_size) * 0.4
                t[:, 8:24, 8:24] += (c * 0.25)
                self.prototypes.append((t, c))

    def __len__(self) -> int:
        return self.num_samples

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        return self.prototypes[idx % len(self.prototypes)]


class FolderImageDataset(Dataset):
    """
    Loads real images from directory containing class subfolders (e.g. dataset/dogs/, dataset/cats/)
    or directly from a flat folder.
    """
    def __init__(self, root_dir: str, target_size: Tuple[int, int] = (64, 64)):
        self.root_path = Path(root_dir)
        self.target_size = target_size
        self.samples: List[Tuple[Path, int]] = []
        self.classes: List[str] = []

        subdirs = sorted([d for d in self.root_path.iterdir() if d.is_dir()])
        valid_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

        if subdirs:
            self.classes = [d.name for d in subdirs]
            class_to_idx = {cls_name: i for i, cls_name in enumerate(self.classes)}
            for d in subdirs:
                idx = class_to_idx[d.name]
                for f in d.iterdir():
                    if f.suffix.lower() in valid_exts:
                        self.samples.append((f, idx))
        else:
            # Flat folder
            self.classes = DEFAULT_CLASSES
            for i, f in enumerate(self.root_path.iterdir()):
                if f.suffix.lower() in valid_exts:
                    self.samples.append((f, i % len(self.classes)))

        if not self.samples:
            # Fallback if empty folder
            self.classes = DEFAULT_CLASSES

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        if not self.samples:
            return torch.zeros(3, *self.target_size), 0

        img_path, label = self.samples[idx]
        try:
            with Image.open(img_path) as im:
                im = im.convert("RGB").resize(self.target_size, Image.Resampling.BILINEAR)
                arr = np.array(im, dtype=np.float32) / 255.0
                tensor = torch.from_numpy(arr).permute(2, 0, 1)
                # Normalize roughly to [-1, 1]
                tensor = (tensor - 0.5) / 0.5
                return tensor, label
        except Exception:
            return torch.zeros(3, *self.target_size), label


# ==========================================
# 3. Image Preprocessing & Google Lens Predictor
# ==========================================

def preprocess_image_for_lens(image_path: str, target_size: Tuple[int, int] = (64, 64)) -> torch.Tensor:
    """Prepares an input image for neural network classification"""
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        img = img.resize(target_size, Image.Resampling.BILINEAR)
        arr = np.array(img, dtype=np.float32) / 255.0
        tensor = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0) # [1, 3, H, W]
        tensor = (tensor - 0.5) / 0.5
        return tensor


def run_google_lens_inference(
    model: nn.Module,
    image_path: str,
    device: torch.device,
    classes: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Executes Google Lens style visual classification on a single image.
    Returns predicted class, confidence, top-3 candidates, and inference time in ms.
    """
    if classes is None or not classes:
        classes = DEFAULT_CLASSES

    model.eval()
    model.to(device)

    start_time = time.perf_counter()

    tensor = preprocess_image_for_lens(image_path).to(device)

    with torch.no_grad():
        outputs = model(tensor)
        probabilities = torch.softmax(outputs, dim=1)[0]
        conf, pred_idx = torch.max(probabilities, dim=0)

        # Get top 3 candidates
        top_k = min(3, len(classes))
        top_probs, top_indices = torch.topk(probabilities, k=top_k)

    inference_ms = round((time.perf_counter() - start_time) * 1000, 2)

    top_candidates = []
    for prob, idx in zip(top_probs, top_indices):
        c_idx = idx.item()
        cls_name = classes[c_idx] if c_idx < len(classes) else f"Class #{c_idx}"
        top_candidates.append({
            "class_name": cls_name,
            "confidence": round(prob.item() * 100, 1)
        })

    main_class_idx = pred_idx.item()
    main_class_name = classes[main_class_idx] if main_class_idx < len(classes) else f"Class #{main_class_idx}"

    device_name = "Remote NVIDIA GPU (CUDA)" if device.type == "cuda" else "Server Host CPU"
    if device.type == "cuda":
        device_name = f"{torch.cuda.get_device_name(0)} (CUDA)"

    return {
        "success": True,
        "predicted_class": main_class_name,
        "confidence_percent": round(conf.item() * 100, 1),
        "top_candidates": top_candidates,
        "inference_latency_ms": inference_ms,
        "device_used": device_name,
        "image_filename": Path(image_path).name,
        "bounding_box": [15, 15, 70, 70] # Focus region for UI lens visual
    }
