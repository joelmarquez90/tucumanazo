#!/usr/bin/env python3
"""
cut_characters.py — Recorta walk frames de assets/characters.png.

Uso: cd /Users/joel/workspace/tucumanazo && python3 tools/cut_characters.py

Output:
  assets/sprites/enemy_walk_0..7.png  (row 0 — camisa blanca)
  assets/sprites/player_walk_0..7.png (row 1 — pelo gris)
"""
from PIL import Image
import numpy as np
import os

def tight_crop(arr):
    alpha = arr[:, :, 3]
    rows = np.any(alpha > 30, axis=1)
    cols = np.any(alpha > 30, axis=0)
    if not rows.any():
        return arr
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    return arr[rmin:rmax+1, cmin:cmax+1]

def save(arr, path):
    Image.fromarray(arr, 'RGBA').save(path)
    h, w = arr.shape[:2]
    print(f"  → {path} ({w}×{h}px)")

img = Image.open('assets/characters.png').convert('RGBA')
arr = np.array(img)
H, W = arr.shape[:2]
COLS, ROWS = 8, 2
cell_w, cell_h = W // COLS, H // ROWS

print(f"Sheet: {W}×{H}px, cells: {cell_w}×{cell_h}px")
os.makedirs('assets/sprites', exist_ok=True)

prefixes = {0: 'enemy_walk', 1: 'player_walk'}

for row in range(ROWS):
    prefix = prefixes[row]
    for col in range(COLS):
        x0, y0 = col * cell_w, row * cell_h
        cell = arr[y0:y0+cell_h, x0:x0+cell_w].copy()
        cropped = tight_crop(cell)
        save(cropped, f'assets/sprites/{prefix}_{col}.png')

print("\nListo.")
