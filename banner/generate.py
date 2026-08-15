import os
import numpy as np
from PIL import Image, ImageEnhance

# Ensure directories exist
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Path to portrait image
IMAGE_PATH = "/home/Mayank/Downloads/WhatsApp Image 2026-08-16 at 12.22.41 AM.jpeg"

def process_portrait(image_path, grid_w=64, grid_h=80):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")

    img = Image.open(image_path).convert("L")
    w, h = img.size

    # Focus crop on face & upper body
    crop_w = min(w, h * 3 // 4)
    crop_h = crop_w * 4 // 3
    left = (w - crop_w) // 2
    top = int(h * 0.05)
    right = left + crop_w
    bottom = top + crop_h
    img_cropped = img.crop((left, top, right, bottom))

    # Save processed input copy
    img_cropped.save(os.path.join(INPUT_DIR, "portrait.jpg"))

    # Enhance contrast
    enhancer = ImageEnhance.Contrast(img_cropped)
    img_enhanced = enhancer.enhance(1.4)

    # Resize to dot grid
    img_resized = img_enhanced.resize((grid_w, grid_h), Image.Resampling.LANCZOS)
    arr = np.array(img_resized, dtype=float)

    # Floyd-Steinberg 1-bit Dithering
    height, width = arr.shape
    for y in range(height):
        for x in range(width):
            old_p = arr[y, x]
            new_p = 255.0 if old_p > 125.0 else 0.0
            arr[y, x] = new_p
            err = old_p - new_p
            if x + 1 < width:
                arr[y, x + 1] += err * (7.0 / 16.0)
            if y + 1 < height:
                if x - 1 >= 0:
                    arr[y + 1, x - 1] += err * (3.0 / 16.0)
                arr[y + 1, x] += err * (5.0 / 16.0)
                if x + 1 < width:
                    arr[y + 1, x + 1] += err * (1.0 / 16.0)

    binary_matrix = (arr > 128).astype(np.uint8)
    np.save(os.path.join(DATA_DIR, "portrait_dots.npy"), binary_matrix)
    return binary_matrix

def generate_svg(binary_matrix, mode="dark"):
    grid_h, grid_w = binary_matrix.shape

    # Dimensions
    svg_w = 880
    svg_h = 360

    # Color Palette definitions
    if mode == "dark":
        bg_color = "#0B0F19"
        window_border = "#1E293B"
        header_bg = "#111827"
        text_primary = "#F8FAFC"
        text_muted = "#94A3B8"
        accent_cyan = "#22D3EE"
        accent_emerald = "#10B981"
        accent_purple = "#A78BFA"
        portrait_dot_fill = "#22D3EE"
        portrait_bg = "#0A101F"
        card_bg = "#131C2E"
        grid_line = "#1E293B"
    else: # light mode
        bg_color = "#F8FAFC"
        window_border = "#CBD5E1"
        header_bg = "#F1F5F9"
        text_primary = "#0F172A"
        text_muted = "#64748B"
        accent_cyan = "#0284C7"
        accent_emerald = "#059669"
        accent_purple = "#7C3AED"
        portrait_dot_fill = "#0284C7"
        portrait_bg = "#FFFFFF"
        card_bg = "#F1F5F9"
        grid_line = "#E2E8F0"

    # Generate Portrait Dot Path
    start_x = 35
    start_y = 65
    box_w = 200
    box_h = 265

    dx = box_w / grid_w
    dy = box_h / grid_h

    path_items = []
    r = min(dx, dy) * 0.42

    for y in range(grid_h):
        for x in range(grid_w):
            if binary_matrix[y, x]:
                cx = start_x + (x + 0.5) * dx
                cy = start_y + (y + 0.5) * dy
                path_items.append(f"M {cx-r:.2f},{cy:.2f} A {r:.2f},{r:.2f} 0 1,0 {cx+r:.2f},{cy:.2f} A {r:.2f},{r:.2f} 0 1,0 {cx-r:.2f},{cy:.2f}")

    d_portrait = " ".join(path_items)

    # Info Column Coordinates
    info_x = 265
    info_y_start = 85

    info_data = [
        ("NAME", "Mayank Tripathi", accent_cyan),
        ("ROLE", "Backend &amp; Systems Engineer", text_primary),
        ("EDUCATION", "B.Tech CSE · Final Year (AKGEC)", text_primary),
        ("STATUS", "Building + Learning + Shipping", accent_emerald),
        ("LANG", "C++ · Python · JavaScript · TypeScript", text_primary),
        ("BACKEND", "Node.js · Express · REST APIs · WebSockets", text_primary),
        ("DATABASE", "PostgreSQL · MongoDB · Redis", text_primary),
        ("INFRA", "Docker · Kubernetes · AWS · Arch Linux", accent_purple),
    ]

    info_rows_svg = ""
    curr_y = info_y_start
    for label, val, color in info_data:
        info_rows_svg += f'''
        <text x="{info_x}" y="{curr_y}" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="11" font-weight="700" fill="{text_muted}" letter-spacing="1.5">{label}</text>
        <text x="{info_x + 95}" y="{curr_y}" font-family="'JetBrains Mono', 'Fira Code', monospace" font-size="12" font-weight="600" fill="{color}">{val}</text>
        '''
        curr_y += 28

    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="100%" height="100%">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700;800&amp;display=swap');
      
      .terminal-bg {{ fill: {bg_color}; stroke: {window_border}; stroke-width: 1.5; }}
      .header-bg {{ fill: {header_bg}; border-bottom: 1px solid {window_border}; }}
      .title-text {{ font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 700; fill: {text_primary}; }}
      .header-tag {{ font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; fill: {accent_cyan}; letter-spacing: 1.2px; }}

      /* Pulse animation */
      @keyframes pulse {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.4; transform: scale(0.9); }}
      }}
      .online-dot {{ animation: pulse 2s infinite ease-in-out; transform-origin: 840px 22px; }}

      /* Morphing Logos Cycle Animation */
      @keyframes logoCycle1 {{
        0%, 28% {{ opacity: 1; transform: translateY(0); }}
        33%, 95% {{ opacity: 0; transform: translateY(6px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
      }}
      @keyframes logoCycle2 {{
        0%, 28% {{ opacity: 0; transform: translateY(-6px); }}
        33%, 61% {{ opacity: 1; transform: translateY(0); }}
        66%, 100% {{ opacity: 0; transform: translateY(6px); }}
      }}
      @keyframes logoCycle3 {{
        0%, 61% {{ opacity: 0; transform: translateY(-6px); }}
        66%, 95% {{ opacity: 1; transform: translateY(0); }}
        100% {{ opacity: 0; transform: translateY(6px); }}
      }}

      .logo-1 {{ animation: logoCycle1 12s infinite ease-in-out; }}
      .logo-2 {{ animation: logoCycle2 12s infinite ease-in-out; }}
      .logo-3 {{ animation: logoCycle3 12s infinite ease-in-out; }}

      /* Travelling dots animation */
      @keyframes travelDot1 {{
        0% {{ cx: 280px; cy: 65px; opacity: 0; }}
        20% {{ opacity: 0.8; }}
        80% {{ opacity: 0.8; }}
        100% {{ cx: 840px; cy: 65px; opacity: 0; }}
      }}
      @keyframes travelDot2 {{
        0% {{ cx: 280px; cy: 320px; opacity: 0; }}
        20% {{ opacity: 0.8; }}
        80% {{ opacity: 0.8; }}
        100% {{ cx: 840px; cy: 320px; opacity: 0; }}
      }}
      .traveller-1 {{ animation: travelDot1 4s infinite linear; }}
      .traveller-2 {{ animation: travelDot2 6s infinite linear 1.5s; }}
    </style>

    <linearGradient id="cyanGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{accent_cyan}" stop-opacity="0.9" />
      <stop offset="100%" stop-color="{accent_emerald}" stop-opacity="0.9" />
    </linearGradient>

    <linearGradient id="portraitGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{portrait_dot_fill}" stop-opacity="1.0" />
      <stop offset="100%" stop-color="{accent_emerald}" stop-opacity="0.85" />
    </linearGradient>
  </defs>

  <!-- Outer Window -->
  <rect x="2" y="2" width="{svg_w-4}" height="{svg_h-4}" rx="12" ry="12" class="terminal-bg" />

  <!-- Window Header Bar -->
  <path d="M 2 14 A 12 12 0 0 1 14 2 L {svg_w-14} 2 A 12 12 0 0 1 {svg_w-2} 14 L {svg_w-2} 40 L 2 40 Z" fill="{header_bg}" stroke="{window_border}" stroke-width="1" />
  <line x1="2" y1="40" x2="{svg_w-2}" y2="40" stroke="{window_border}" stroke-width="1.5" />

  <!-- Window Control Buttons -->
  <circle cx="22" cy="21" r="5.5" fill="#FF5F56" />
  <circle cx="38" cy="21" r="5.5" fill="#FFBD2E" />
  <circle cx="54" cy="21" r="5.5" fill="#27C93F" />

  <!-- Terminal Title -->
  <text x="{svg_w//2}" y="25" text-anchor="middle" class="title-text">backend.sh --live</text>

  <!-- Status Indicator -->
  <circle cx="830" cy="21" r="4" fill="{accent_emerald}" class="online-dot" />
  <text x="840" y="25" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="700" fill="{accent_emerald}">ONLINE</text>

  <!-- Panel Dividers -->
  <!-- Left Panel Background -->
  <rect x="20" y="55" width="225" height="285" rx="8" ry="8" fill="{portrait_bg}" stroke="{grid_line}" stroke-width="1" />
  <text x="32" y="73" class="header-tag">VISUAL.MAP</text>
  <line x1="20" y1="80" x2="245" y2="80" stroke="{grid_line}" stroke-width="1" />

  <!-- Portrait Dithered Dots -->
  <g transform="translate(0, 25)">
    <path d="{d_portrait}" fill="url(#portraitGrad)" />
  </g>

  <!-- Right Panel Container -->
  <rect x="255" y="55" width="605" height="285" rx="8" ry="8" fill="{card_bg}" stroke="{grid_line}" stroke-width="1" />
  <text x="270" y="73" class="header-tag">SYSTEM.INFO</text>
  <line x1="255" y1="80" x2="860" y2="80" stroke="{grid_line}" stroke-width="1" />

  <!-- Info Key-Values -->
  {info_rows_svg}

  <!-- Morphing Tech Logos (Linux, Docker, Kubernetes) in Top Right of Info Card -->
  <g transform="translate(805, 53)">
    <!-- Border box for Morphing Logo -->
    <rect x="0" y="0" width="44" height="24" rx="4" fill="{bg_color}" stroke="{window_border}" stroke-width="1" />

    <!-- 1. Linux Logo (Tux / Terminal prompt) -->
    <g class="logo-1" transform="translate(12, 4)">
      <!-- Linux Tux icon SVG path -->
      <path d="M10,2 C7,2 5,4 5,7 C5,8.5 4,9.5 3,10 C2,10.5 1,11 1,12 C1,13.5 3,14 4,14 C5,14 6,15 7,15 C8,15 9,14 10,14 C11,14 12,15 13,15 C14,15 15,14 16,14 C17,14 19,13.5 19,12 C19,11 18,10.5 17,10 C16,9.5 15,8.5 15,7 C15,4 13,2 10,2 Z" fill="{accent_cyan}" />
      <circle cx="8" cy="6" r="1" fill="{bg_color}" />
      <circle cx="12" cy="6" r="1" fill="{bg_color}" />
      <path d="M8.5,8.5 Q10,10 11.5,8.5" stroke="{bg_color}" stroke-width="1" fill="none" />
    </g>

    <!-- 2. Docker Logo (Whale) -->
    <g class="logo-2" transform="translate(10, 4)">
      <!-- Docker Whale SVG path -->
      <path d="M1,10 Q2,7 6,7 Q7,4 10,4 L10,6 L13,6 L13,4 L16,4 L16,7 Q20,7 21,10 Q22,12 18,13 Q10,14 1,10 Z" fill="{accent_cyan}" />
      <rect x="5" y="4.5" width="2" height="2" fill="{accent_cyan}" />
      <rect x="8" y="2" width="2" height="2" fill="{accent_cyan}" />
      <rect x="11" y="2" width="2" height="2" fill="{accent_cyan}" />
      <rect x="14" y="2" width="2" height="2" fill="{accent_cyan}" />
    </g>

    <!-- 3. Kubernetes Logo (Helm Wheel) -->
    <g class="logo-3" transform="translate(12, 4)">
      <!-- K8s Wheel SVG path -->
      <circle cx="10" cy="8" r="6" stroke="{accent_purple}" stroke-width="1.5" fill="none" />
      <circle cx="10" cy="8" r="2" fill="{accent_purple}" />
      <line x1="10" y1="2" x2="10" y2="14" stroke="{accent_purple}" stroke-width="1.2" />
      <line x1="4" y1="5" x2="16" y2="11" stroke="{accent_purple}" stroke-width="1.2" />
      <line x1="4" y1="11" x2="16" y2="5" stroke="{accent_purple}" stroke-width="1.2" />
    </g>
  </g>

  <!-- Travelling Dots Animation -->
  <circle class="traveller-1" cx="280" cy="65" r="1.5" fill="{accent_cyan}" />
  <circle class="traveller-2" cx="280" cy="320" r="1.5" fill="{accent_emerald}" />
</svg>'''

    output_file = os.path.join(OUTPUT_DIR, f"{mode}.svg")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {mode}.svg successfully ({len(svg_content)} bytes).")

if __name__ == "__main__":
    print("Processing portrait and dithering...")
    matrix = process_portrait(IMAGE_PATH)
    print("Generating SVGs...")
    generate_svg(matrix, mode="dark")
    generate_svg(matrix, mode="light")
    print("Done!")
