import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import random
from scipy.ndimage import sobel, map_coordinates
import os

# === Mandelbrot Calculation ===
def mandelbrot(width, height, zoom, center_x, center_y, max_iter=200):
    x = np.linspace(center_x - zoom, center_x + zoom, width)
    y = np.linspace(center_y - zoom, center_y + zoom, height)
    X, Y = np.meshgrid(x, y)
    C = X + 1j * Y
    Z = np.zeros_like(C)
    M = np.zeros(C.shape, dtype=float)
    for i in range(max_iter):
        mask = np.abs(Z) < 100
        Z[mask] = Z[mask] ** 2 + C[mask]
        M[mask] += 1 - np.exp(-np.abs(Z[mask]))
    return M / M.max()

# === Effects ===
def apply_effect(image, effect):
    if effect == 'edges':
        dx = sobel(image, axis=0)
        dy = sobel(image, axis=1)
        return np.hypot(dx, dy)
    elif effect == 'invert':
        return 1 - image
    elif effect == 'posterize':
        levels = 4
        return np.floor(image * levels) / levels
    elif effect == 'swirl':
        coords = np.indices(image.shape).astype(float)
        center = np.array(image.shape)[:, None, None] / 2
        angle = np.hypot(*(coords - center)) / 30
        coords[0] += np.sin(angle) * 5
        coords[1] += np.cos(angle) * 5
        return map_coordinates(image, coords, order=1, mode='reflect')
    elif effect == 'rotate':
        return np.rot90(image, k=random.randint(1, 3))
    return image

# === Convert numpy array to image ===
def make_pil_image(image, cmap):
    fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
    ax.imshow(image, cmap=cmap)
    ax.axis('off')
    fig.tight_layout(pad=0)
    buf = BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf)

# === Generate New Fractal ===
def generate_image():
    global last_image_pil, session_gallery

    width, height = 600, 600
    zoom = zoom_slider.get()
    center_x = centerx_slider.get()
    center_y = centery_slider.get()
    max_iter = 250
    cmap_choice = cmap_var.get()
    effect = effect_var.get()

    mandel = mandelbrot(width, height, zoom, center_x, center_y, max_iter)
    mandel = apply_effect(mandel, effect)
    image_pil = make_pil_image(mandel, cmap_choice)
    last_image_pil = image_pil.copy()

    # Set window icon to latest image
    try:
        icon_path = "last_icon.ico"
        icon_ico = last_image_pil.resize((64, 64))
        icon_ico.save(icon_path, format='ICO')
        root.iconbitmap(icon_path)
    except Exception as e:
        print(f"Couldn't set window icon: {e}")

    session_gallery.append({
        "image": image_pil,
        "thumb": image_pil.resize((100, 100), Image.ANTIALIAS),
        "title": f"Zoom {zoom:.2f} | C=({center_x:.2f},{center_y:.2f}) | {effect}",
    })

    update_main_view()
    update_gallery()

def generate_random_image():
    global last_image_pil, session_gallery

    width, height = 600, 600
    zoom = random.uniform(0.2, 2.0)
    center_x = random.uniform(-2.0, 1.0)
    center_y = random.uniform(-1.5, 1.5)
    max_iter = 250
    cmap_choice = random.choice(['plasma', 'inferno', 'turbo', 'twilight', 'viridis'])
    effect = random.choice(['none', 'edges', 'invert', 'posterize', 'swirl', 'rotate'])

    mandel = mandelbrot(width, height, zoom, center_x, center_y, max_iter)
    mandel = apply_effect(mandel, effect)
    image_pil = make_pil_image(mandel, cmap_choice)
    last_image_pil = image_pil.copy()

    # Set icon etc. (same as generate_from_settings)
    try:
        icon_path = "last_icon.ico"
        icon_ico = last_image_pil.resize((64, 64))
        icon_ico.save(icon_path, format='ICO')
        root.iconbitmap(icon_path)
    except Exception as e:
        print(f"Couldn't set window icon: {e}")

    session_gallery.append({
        "image": image_pil,
        "thumb": image_pil.resize((100, 100), Image.ANTIALIAS),
        "title": f"Random | Zoom {zoom:.2f} | C=({center_x:.2f},{center_y:.2f}) | {effect}",
    })

    update_main_view()
    update_gallery()

def update_main_view(index=None):
    global last_image_pil
    if index is not None:
        last_image_pil = session_gallery[index]["image"]
        title_text.set(session_gallery[index]["title"])
    img = ImageTk.PhotoImage(last_image_pil)
    canvas.config(image=img)
    canvas.image = img

def update_gallery():
    for widget in gallery_frame.winfo_children():
        widget.destroy()
    for i, entry in enumerate(session_gallery):
        thumb_img = ImageTk.PhotoImage(entry["thumb"])
        btn = tk.Button(gallery_frame, image=thumb_img, command=lambda i=i: update_main_view(i))
        btn.image = thumb_img
        btn.grid(row=i // 3, column=i % 3, padx=2, pady=2)

def save_image():
    if last_image_pil:
        file = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file:
            last_image_pil.save(file)

# === GUI ===
root = tk.Tk()
root.title("🎨 Fractal Studio 2025")
root.configure(bg="#1e1e1e")
root.state('zoomed')
root.bind("<Escape>", lambda e: root.state('normal'))

# Style setup
style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", background="#2b2b2b", foreground="white")
style.configure("TButton", background="#444", foreground="white")
style.configure("TScale", troughcolor="#3a3a3a", background="#2b2b2b")

# === Layout ===
main_frame = tk.Frame(root, bg="#2b2b2b")
main_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

right_panel = tk.Frame(root, bg="#2b2b2b")
right_panel.pack(side="right", fill="y", padx=5, anchor="n")

# === Main Canvas ===
title_text = tk.StringVar()
title_label = tk.Label(main_frame, textvariable=title_text, font=("Arial", 12, "bold"), bg="#2b2b2b", fg="white")
title_label.pack(pady=(0, 4))

canvas = tk.Label(main_frame, bg="#2b2b2b")
canvas.pack(expand=True, fill="both")

# === Buttons ===
tk.Button(right_panel, text="🎨 Generate Random", command=generate_random_image,
          font=("Arial", 14), bg="#444", fg="white").pack(pady=10, fill="x", padx=10)

tk.Button(right_panel, text="🧪 Generate with Settings", command=generate_image,
          font=("Arial", 14), bg="#333", fg="white").pack(pady=5, fill="x", padx=10)

tk.Button(right_panel, text="💾 Save Image", command=save_image,
          font=("Arial", 14), bg="#444", fg="white").pack(pady=10, fill="x", padx=10)

# === Controls ===
control_frame = tk.LabelFrame(right_panel, text="🛠 Controls", bg="#2b2b2b", fg="white", font=("Arial", 12, "bold"))
control_frame.pack(padx=10, pady=10, fill="x")

# Zoom
tk.Label(control_frame, text="🔍 Zoom", bg="#2b2b2b", fg="white").pack(anchor="w")
zoom_slider = ttk.Scale(control_frame, from_=0.2, to=2.0, orient="horizontal")
zoom_slider.set(1.0)
zoom_slider.pack(fill="x")

# Center X/Y
tk.Label(control_frame, text="↔ Center X", bg="#2b2b2b", fg="white").pack(anchor="w")
centerx_slider = ttk.Scale(control_frame, from_=-2.0, to=1.0, orient="horizontal")
centerx_slider.set(-0.5)
centerx_slider.pack(fill="x")

tk.Label(control_frame, text="↕ Center Y", bg="#2b2b2b", fg="white").pack(anchor="w")
centery_slider = ttk.Scale(control_frame, from_=-1.5, to=1.5, orient="horizontal")
centery_slider.set(0.0)
centery_slider.pack(fill="x")

# Colormap
tk.Label(control_frame, text="🎨 Colormap", bg="#2b2b2b", fg="white").pack(anchor="w")
cmap_var = tk.StringVar(value="plasma")
cmap_frame = tk.Frame(control_frame, bg="#2b2b2b")
cmap_frame.pack()
for cmap in ["plasma", "inferno", "turbo", "twilight", "viridis"]:
    tk.Radiobutton(cmap_frame, text=cmap, variable=cmap_var, value=cmap,
                   bg="#2b2b2b", fg="white", selectcolor="#444").pack(side="left", padx=2)

# Effect
tk.Label(control_frame, text="✨ Effect", bg="#2b2b2b", fg="white").pack(anchor="w")
effect_var = tk.StringVar(value="none")
effect_frame = tk.Frame(control_frame, bg="#2b2b2b")
effect_frame.pack()
for effect in ["none", "edges", "invert", "posterize", "swirl", "rotate"]:
    tk.Radiobutton(effect_frame, text=effect, variable=effect_var, value=effect,
                   bg="#2b2b2b", fg="white", selectcolor="#444").pack(side="left", padx=2)

# === Gallery ===
# === Scrollable Gallery Container ===
gallery_container = tk.Frame(right_panel, bg="#2b2b2b")
gallery_container.pack(fill="both", expand=False, pady=(0,10), padx=10)

gallery_canvas = tk.Canvas(gallery_container, bg="#2b2b2b", highlightthickness=0, height=340)
gallery_canvas.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(gallery_container, orient="vertical", command=gallery_canvas.yview)
scrollbar.pack(side="right", fill="y")

gallery_canvas.configure(yscrollcommand=scrollbar.set)

# Frame inside canvas to hold thumbnails
gallery_frame = tk.Frame(gallery_canvas, bg="#2b2b2b")
gallery_canvas.create_window((0, 0), window=gallery_frame, anchor="nw")

def on_gallery_configure(event):
    gallery_canvas.configure(scrollregion=gallery_canvas.bbox("all"))

gallery_frame.bind("<Configure>", on_gallery_configure)

# === Globals ===
last_image_pil = None
session_gallery = []

generate_image()
root.mainloop()
