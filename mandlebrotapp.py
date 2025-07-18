import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import random
from scipy.ndimage import sobel, map_coordinates
import os
from scipy.ndimage import gaussian_filter
from tkinter import messagebox  # Make sure this import is at the top if not already
import zipfile
import os
from tkinter import filedialog, messagebox

#Globals!!
gallery_images = []

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

def julia(width, height, zoom, center_x, center_y, max_iter=200, c=-0.7+0.27015j):
    x = np.linspace(center_x - zoom, center_x + zoom, width)
    y = np.linspace(center_y - zoom, center_y + zoom, height)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    M = np.zeros(Z.shape, dtype=float)
    for i in range(max_iter):
        mask = np.abs(Z) < 100
        Z[mask] = Z[mask] ** 2 + c
        M[mask] += 1 - np.exp(-np.abs(Z[mask]))
    return M / M.max()

def burning_ship(width, height, zoom, center_x, center_y, max_iter=200):
    x = np.linspace(center_x - zoom, center_x + zoom, width)
    y = np.linspace(center_y - zoom, center_y + zoom, height)
    X, Y = np.meshgrid(x, y)
    C = X + 1j * Y
    Z = np.zeros_like(C)
    M = np.zeros(C.shape, dtype=float)
    for i in range(max_iter):
        Z = (np.abs(Z.real) + 1j * np.abs(Z.imag))**2 + C
        mask = np.abs(Z) < 100
        M[mask] += 1 - np.exp(-np.abs(Z[mask]))
    return M / M.max()

fractal_types = {
    "Mandelbrot": mandelbrot,
    "Julia": julia,
    "Burning Ship": burning_ship,
}   

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

from tkinter import messagebox  # Make sure this import is at the top if not already

def clear_gallery():
    if messagebox.askyesno("Clear Gallery", "Are you sure you want to clear the gallery? This cannot be undone."):
        global gallery_images
        for widget in gallery_frame.winfo_children():
            widget.destroy()
        gallery_images.clear()


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
    fractal_func = fractal_types[fractal_var.get()]


    if fractal_var.get() == "Julia":
        try:
            real = float(julia_real_var.get())
            imag = float(julia_imag_var.get())
            c = complex(real, imag)
        except ValueError:
            c = complex(random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0))

        fractal = fractal_func(width, height, zoom, center_x, center_y, max_iter, c=c)
    else:
        fractal = fractal_func(width, height, zoom, center_x, center_y, max_iter)

    fractal = apply_effect(fractal, effect)
    image_pil = make_pil_image(fractal, cmap_choice)
    last_image_pil = image_pil.copy()

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
        "title": f"{fractal_var.get()} | Zoom {zoom:.2f} | C=({center_x:.2f},{center_y:.2f}) | {effect}",

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
    cmap_choice = random.choice(['plasma', 'inferno', 'turbo', 'viridis'])
    effect = random.choice(['none', 'edges', 'invert', 'posterize', 'swirl', 'rotate'])
    fractal_choice = random.choice(list(fractal_types.keys()))
    fractal_var.set(fractal_choice)
    fractal_func = fractal_types[fractal_choice]
    if fractal_choice == "Julia":
        seed_text = julia_seed_var.get()
        if seed_text:
            try:
                c = complex(seed_text)
            except ValueError:
                c = complex(random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0))
        else:
            c = complex(random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0))
    
        fractal = fractal_func(width, height, zoom, center_x, center_y, max_iter, c=c)
    else:
        fractal = fractal_func(width, height, zoom, center_x, center_y, max_iter)

    fractal = apply_effect(fractal, effect)
    image_pil = make_pil_image(fractal, cmap_choice)
    last_image_pil = image_pil.copy()

    try:
        icon_path = "last_icon.ico"
        icon_ico = last_image_pil.resize((64, 64))
        icon_ico.save(icon_path, format='ICO')
        root.iconbitmap(icon_path)
    except Exception as e:
        print(f"Couldn't set window icon: {e}")


    update_main_view()
    update_gallery()


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
        btn.grid(row=i // 3, column=i % 3, padx=4, pady=4)

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
control_frame = tk.LabelFrame(right_panel, text="🛠 Controls", bg="#2b2b2b", fg="white", font=("Arial", 18, "bold"))
control_frame.pack(padx=10, pady=10, fill="x")

# Type
tk.Label(control_frame, text="🧠 Fractal Type", bg="#2b2b2b", fg="white").pack(anchor="w")
fractal_var = tk.StringVar(value="Mandelbrot")
fractal_menu = ttk.Combobox(control_frame, textvariable=fractal_var, state="readonly")
fractal_menu['values'] = ["Mandelbrot", "Julia", "Burning Ship"]
fractal_menu.pack(fill="x", pady=(0, 10))

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

# === Scrollable Gallery Container with LabelFrame ===
gallery_labelframe = tk.LabelFrame(right_panel, text="Session Gallery",
                                  bg="#2b2b2b", fg="white",
                                  font=("Arial", 18, "bold"))
gallery_labelframe.pack(fill="both", expand=False, pady=10, padx=10)

gallery_canvas = tk.Canvas(gallery_labelframe, bg="#2b2b2b", highlightthickness=0, height=340)
gallery_canvas.pack(side="left", fill="both", expand=True, padx=(5,0), pady=5)

scrollbar = ttk.Scrollbar(gallery_labelframe, orient="vertical", command=gallery_canvas.yview)
scrollbar.pack(side="right", fill="y", pady=5, padx=(0,5))

gallery_canvas.configure(yscrollcommand=scrollbar.set)

gallery_frame = tk.Frame(gallery_canvas, bg="#2b2b2b")
gallery_canvas.create_window((0, 0), window=gallery_frame, anchor="nw")

def on_gallery_configure(event):
    gallery_canvas.configure(scrollregion=gallery_canvas.bbox("all"))

gallery_frame.bind("<Configure>", on_gallery_configure)

julia_seed_var = tk.StringVar()
def validate_int(P):
    if P == "" or (P.isdigit() or (P.startswith('-') and P[1:].isdigit())):
        return True
    return False

vcmd = root.register(validate_int)

# --- Julia Seed Input (Real + Imaginary) ---
julia_real_var = tk.StringVar(value="-0.7")
julia_imag_var = tk.StringVar(value="0.27015")

seed_frame = tk.Frame(control_frame, bg="#2e2e2e")
seed_frame.pack(pady=5)

tk.Label(seed_frame, text="Julia Seed:", bg="#2e2e2e", fg="white").grid(row=0, column=0, columnspan=4, sticky="w")

tk.Entry(seed_frame, textvariable=julia_real_var, width=6, bg="#3a3a3a", fg="white", insertbackground="white", relief="flat").grid(row=1, column=0, padx=(0, 2))
tk.Label(seed_frame, text="+", bg="#2e2e2e", fg="white").grid(row=1, column=1)
tk.Entry(seed_frame, textvariable=julia_imag_var, width=6, bg="#3a3a3a", fg="white", insertbackground="white", relief="flat").grid(row=1, column=2, padx=(2, 0))
tk.Label(seed_frame, text="i", bg="#2e2e2e", fg="white").grid(row=1, column=3)

clear_button = tk.Button(control_frame, text="Clear Gallery", command=clear_gallery, bg="#444", fg="white", relief="flat")
clear_button.pack(pady=5, fill="x")


# === Globals ===
last_image_pil = None
session_gallery = []

generate_image()
root.mainloop()


# why do python programmers wear glasses?
# Because they can't C.

