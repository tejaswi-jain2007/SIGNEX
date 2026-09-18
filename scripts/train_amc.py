"""
NTRO SIGINT AMC Model Training Script
Trains 1D ResNet-18 on synthetic RF signal corpus and saves weights to models/amc_resnet18.pt.
Supports GPU acceleration (CUDA) and mixed precision.
"""

import os
import sys
import time

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader

from ntro_sigint.ml.dataset import create_synthetic_dataset, MODULATION_CLASSES
from ntro_sigint.ml.amc_classifier import ResNet18_1D


def train_model(
    epochs: int = 5,
    batch_size: int = 64,
    lr: float = 1e-3,
    samples_per_class: int = 150,
    save_path: str = "models/amc_resnet18.pt"
):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[AMC TRAIN] Training device: {device}")

    # Generate synthetic training set across 0 to 20 dB SNR
    print(f"[AMC TRAIN] Generating synthetic dataset ({samples_per_class} per class)...")
    X, Y = create_synthetic_dataset(
        num_samples_per_class=samples_per_class,
        snr_range=(5.0, 20.0),
        window_len=1024
    )

    # Train / Val split (80 / 20)
    n_total = len(X)
    indices = np.random.permutation(n_total)
    split = int(0.8 * n_total)
    train_idx, val_idx = indices[:split], indices[split:]

    x_train, y_train = torch.tensor(X[train_idx]), torch.tensor(Y[train_idx])
    x_val, y_val = torch.tensor(X[val_idx]), torch.tensor(Y[val_idx])

    train_loader = DataLoader(TensorDataset(x_train, y_train), batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(TensorDataset(x_val, y_val), batch_size=batch_size, shuffle=False)

    model = ResNet18_1D(num_classes=len(MODULATION_CLASSES)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)

    print(f"[AMC TRAIN] Starting training loop ({epochs} epochs)...")
    t_start = time.time()

    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        correct = 0
        total = 0

        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * batch_x.size(0)
            preds = torch.argmax(outputs, dim=1)
            correct += (preds == batch_y).sum().item()
            total += batch_y.size(0)

        train_acc = (correct / total) * 100.0
        avg_loss = train_loss / total

        # Validation
        model.eval()
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for vx, vy in val_loader:
                vx, vy = vx.to(device), vy.to(device)
                vout = model(vx)
                vpreds = torch.argmax(vout, dim=1)
                val_correct += (vpreds == vy).sum().item()
                val_total += vy.size(0)

        val_acc = (val_correct / val_total) * 100.0
        print(f"  Epoch [{epoch}/{epochs}] Loss: {avg_loss:.4f} | Train Acc: {train_acc:.1f}% | Val Acc: {val_acc:.1f}%")

    total_time = time.time() - t_start
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    torch.save(model.state_dict(), save_path)
    print(f"[AMC TRAIN] Complete in {total_time:.2f}s! Saved weights to: {save_path}")


if __name__ == "__main__":
    train_model(epochs=12, samples_per_class=200, lr=1e-3, batch_size=64)
