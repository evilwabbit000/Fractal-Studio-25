import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image
import colorsys
import math
import numpy as np
from multiprocessing import Pool, cpu_count

def powerColor(distance, exp, const, scale):
    color = distance**exp
    rgb = colorsys.hsv_to_rgb(const + scale * color, 1 - 0.6 * color, 0.9)
    return tuple(round(i * 255) for i in rgb)

def mandelbrot(x, y, precision):
    oldX = x
    oldY = y
    for i in range(precision + 1):
        a = x*x - y*y  # Real component of z^2
        b = 2 * x * y  # Imaginary component of z^2
        x = a + oldX  # Real component of new z
        y = b + oldY  # Imaginary component of new z
        if x*x + y*y > 4:
            break
    return i

def process_row(args):
    row, width, height, minX, maxX, minY, maxY, yRange, xRange, precision, exp, const, scale = args
    row_colors = []
    y = maxY - row * yRange / height
    for col in range(width):
        x = minX + col * xRange / width
        i = mandelbrot(x, y, precision)
        if i < precision:
            distance = (i + 1) / (precision + 1)
            rgb = powerColor(distance, exp, const, scale)
        else:
            rgb = (0, 0, 0)  # Points inside the Mandelbrot set
        row_colors.append(rgb)
    return row, row_colors

def generate_image(width, aspect_ratio, precision, exp, const, scale, output_filename):
    height = round(width / aspect_ratio)
    x = -0.65
    y = 0
    xRange = 3.4
    yRange = xRange / aspect_ratio
    minX = x - xRange / 2
    maxX = x + xRange / 2
    minY = y - yRange / 2
    maxY = y + yRange / 2

    img = Image.new('RGB', (width, height), color='green')
    pixels = img.load()

    args = [(row, width, height, minX, maxX, minY, maxY, yRange, xRange, precision, exp, const, scale) for row in range(height)]

    # Use multiprocessing to speed up the process
    with Pool(cpu_count()) as pool:
        for row, row_colors in pool.map(process_row, args):
            for col, rgb in enumerate(row_colors):
                pixels[col, row] = rgb
            print(f"{row + 1} / {height} rows completed")

    img.save(output_filename)
    img.show()
    print(f"Image saved as {output_filename}")

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Ask the user for input
    width = simpledialog.askinteger("Input", "Enter the width (in pixels):", minvalue=1)
    aspect_ratio = simpledialog.askfloat("Input", "Enter the aspect ratio (width/height):", minvalue=0.01)
    precision = simpledialog.askinteger("Input", "Enter the precision (number of iterations):", minvalue=1)
    exp = simpledialog.askfloat("Input", "Enter the exponent for color calculation:", minvalue=0.0)
    const = simpledialog.askfloat("Input", "Enter the constant for color calculation:", minvalue=0.0)
    scale = simpledialog.askfloat("Input", "Enter the scale for color calculation:", minvalue=0.0)
    output_filename = simpledialog.askstring("Input", "Enter the output filename (with extension, e.g., output.jpg):")

    if width and aspect_ratio and precision and exp and const and scale and output_filename:
        try:
            generate_image(width, aspect_ratio, precision, exp, const, scale, output_filename)
            messagebox.showinfo("Success", f"Image saved as {output_filename}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    else:
        messagebox.showwarning("Input Error", "Please provide all inputs")

if __name__ == "__main__":
    main()
