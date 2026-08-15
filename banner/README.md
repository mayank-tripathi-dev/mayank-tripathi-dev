# Terminal Banner Generator

This directory contains the Python pipeline used to generate the 1-bit Floyd-Steinberg dithered animated terminal profile banner (`dark.svg` and `light.svg`).

## Architecture

* **`generate.py`**: Processing script using Pillow & NumPy. Crops input portrait, applies contrast enhancement, performs 1-bit Floyd-Steinberg dithering, saves `.npy` matrix data, and exports standalone theme-aware SVGs (`dark.svg` and `light.svg`).
* **`data/`**: Source-of-truth 2D NumPy array matrix (`portrait_dots.npy`).
* **`input/`**: Input headshot portrait reference (`portrait.jpg`).
* **`output/`**: Final generated SVGs (`dark.svg` and `light.svg`).

## How to Regenerate

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python generate.py
```
