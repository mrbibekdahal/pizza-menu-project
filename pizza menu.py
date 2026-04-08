
import os
import sys
import csv
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk


def locate_images_folder():
    for d in ("images", "pizza_images"):
        if os.path.isdir(d):
            return d
    os.makedirs("images", exist_ok=True)
    return "images"

def load_prices(csv_file):
    prices = {}
    try:
        with open(csv_file, newline="") as f:
            rdr = csv.reader(f)
            first = next(rdr, None)
            if first and len(first) >= 2 and first[0].lower() == "pizza" and first[1].lower() == "price":
                pass
            else:
                try:
                    prices[first[0].strip()] = float(first[1])
                except:
                    pass
            for row in rdr:
                if len(row) < 2:
                    continue
                try:
                    prices[row[0].strip()] = float(row[1])
                except:
                    continue
    except FileNotFoundError:
        messagebox.showerror("Error", f"Cannot open {csv_file}")
    return prices

def load_images(prices, images_folder):
    images, thumbs = {}, {}
    for code in prices:
        pil = None
        for ext in (".jpg", ".jpeg", ".png"):
            path = os.path.join(images_folder, code + ext)
            if os.path.exists(path):
                pil = Image.open(path)
                break
        if pil is None:
            pil = Image.new("RGB", (200, 200), color="gray")
        images[code] = ImageTk.PhotoImage(pil.resize((100, 100)))
        thumbs[code] = ImageTk.PhotoImage(pil.resize((80, 80)))
    return images, thumbs

def build_toolbar(root, on_show, on_clear, on_quit):
    colours = {
        "Show All Pizzas": "#cce7ff",
        "Clear All Pizzas": "#99cfff",
        "Add New": "#4aa8ff",
        "Delete": "#f0f0f0",
        "Quit": "#b3e5ff"
    }
    frm = tk.Frame(root, bg="lightgray", height=40)
    frm.grid(row=0, column=0, columnspan=2, sticky="ew")
    buttons = {}
    for txt, cmd in (
        ("Show All Pizzas", on_show),
        ("Clear All Pizzas", on_clear),
        ("Add New", lambda: print("Add New button activated")),
        ("Delete", lambda: print("Delete button activated")),
        ("Quit", on_quit),
    ):
        b = tk.Button(frm, text=txt, command=cmd,
                     bg=colours[txt], activebackground=colours[txt])
        b.pack(side="left", padx=4, pady=4)
        buttons[txt] = b
    return buttons

def build_frame(root, row, col, color, colspan=1):
    frm = tk.Frame(root, bg=color)
    frm.grid(row=row, column=col, columnspan=colspan, sticky="nsew")
    frm.grid_propagate(False)
    return frm

def populate_display(ctx):
    MAX_COLS = 4
    for w in ctx['display_frame'].winfo_children():
        w.destroy()
    row = col = 0
    for code, img in ctx['images'].items():
        btn = tk.Button(ctx['display_frame'], image=img,
                        command=lambda c=code: show_detail(c, ctx))
        btn.grid(row=row, column=col, padx=5, pady=5)
        col += 1
        if col >= MAX_COLS:
            col = 0
            row += 1

def show_detail(code, ctx):
    ctx['selected_code'][0] = code
    for w in ctx['detail_frame'].winfo_children():
        w.destroy()
    img = ctx['images'][code]
    tk.Label(ctx['detail_frame'], image=img, bg="black").pack(pady=10)
    tk.Label(ctx['detail_frame'], text=code, fg="white", bg="black").pack()
    tk.Label(ctx['detail_frame'], text=f"Price: £{ctx['prices'][code]:.2f}", fg="white", bg="black").pack(pady=5)
    qty = tk.IntVar(value=1)
    ttk.Spinbox(ctx['detail_frame'], from_=1, to=20, textvariable=qty, width=5).pack(pady=5)
    tk.Button(ctx['detail_frame'], text="Add to Cart", bg="white", fg="black",
              command=lambda: add_to_cart(code, qty.get(), ctx)).pack(pady=5)
    tk.Button(ctx['detail_frame'], text="Cancel", bg="white", fg="black",
              command=lambda: clear_detail(ctx)).pack()

def clear_detail(ctx):
    for w in ctx['detail_frame'].winfo_children():
        w.destroy()
    ctx['selected_code'][0] = None

def add_to_cart(code, qty, ctx):
    for i, (c, q) in enumerate(ctx['cart']):
        if c == code:
            ctx['cart'][i] = (c, q + qty)
            break
    else:
        ctx['cart'].append((code, qty))
    clear_detail(ctx)
    update_order(ctx)

def update_order(ctx):
    for w in ctx['order_items'].winfo_children():
        w.destroy()
    if not ctx['cart']:
        return
    tk.Label(ctx['order_items'], text="Your order details:", bg="green", font=("Arial", 10, "bold"))\
        .grid(row=0, column=0, columnspan=8, sticky="w", padx=5, pady=(5, 10))
    for idx, (code, qty) in enumerate(ctx['cart']):
        r, col = 1 + idx // 8, idx % 8
        cell = tk.Frame(ctx['order_items'], bg="green")
        cell.grid(row=r, column=col, padx=10, pady=5, sticky="n")
        thumb = ctx['thumbs'][code]
        tk.Label(cell, image=thumb, bg="green").pack()
        tk.Label(cell, text=code, bg="green").pack()
        tk.Label(cell, text=f"Qty: {qty}", bg="green").pack()
        total = ctx['prices'][code] * qty
        tk.Label(cell, text=f"Total: £{total:.2f}", bg="green").pack()
    grand = sum(ctx['prices'][c] * q for c, q in ctx['cart'])
    tk.Label(ctx['order_items'], text=f"Grand Total: £{grand:.2f}", bg="green", font=("Arial", 12, "bold"))\
        .grid(row=r+1, column=0, columnspan=8, sticky="w", padx=5, pady=10)

def cancel_order(ctx):
    ctx['cart'].clear()
    show_order_message("Your cart is empty", ctx)

def confirm_order(ctx):
    ctx['cart'].clear()
    show_order_message("Order successfully placed!", ctx)

def show_order_message(msg, ctx):
    for w in ctx['order_items'].winfo_children():
        w.destroy()
    tk.Label(ctx['order_items'], text=msg, bg="green", font=("Arial", 12, "bold")).pack(pady=20)

def on_clear_all(ctx, buttons):
    if not ctx['images_shown'][0]:
        return
    for f in (ctx['display_frame'], ctx['detail_frame'], ctx['order_items']):
        for w in f.winfo_children():
            w.destroy()
    ctx['display_frame'].config(bg="red")
    ctx['detail_frame'].config(bg="black")
    ctx['order_items'].config(bg="green")
    ctx['cart'].clear()
    ctx['images_shown'][0] = False
    buttons['Show All Pizzas'].config(state="normal")
    buttons['Clear All Pizzas'].config(state="disabled")

def on_show_pizzas(ctx, buttons):
    if ctx['images_shown'][0]:
        return
    populate_display(ctx)
    ctx['images_shown'][0] = True
    buttons['Show All Pizzas'].config(state="disabled")
    buttons['Clear All Pizzas'].config(state="normal")

def on_quit(root):
    if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
        root.destroy()

def main():
    root = tk.Tk()
    root.title("Online Pizza Store")
    root.geometry("1024x768")
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=3)
    root.grid_columnconfigure(1, weight=1)

    images_folder = locate_images_folder()
    prices = load_prices("pizza_prices.csv")
    images, thumbs = load_images(prices, images_folder)

    display_frame = build_frame(root, 1, 0, "red")
    detail_frame = build_frame(root, 1, 1, "black")
    order_frame = build_frame(root, 2, 0, "green", colspan=2)
    order_items = tk.Frame(order_frame, bg="green")
    order_items.pack(fill="both", expand=True)
    ctrl = tk.Frame(order_frame, bg="green")
    ctrl.pack(fill="x", pady=5)

    # Context dict holds shared state cleanly
    ctx = {
        'prices': prices,
        'images': images,
        'thumbs': thumbs,
        'cart': [],
        'selected_code': [None],
        'images_shown': [False],
        'display_frame': display_frame,
        'detail_frame': detail_frame,
        'order_items': order_items
    }

    tk.Button(ctrl, text="Cancel Order", bg="#cce7ff",
              command=lambda: cancel_order(ctx)).pack(side="left", padx=10)
    tk.Button(ctrl, text="Confirm Order", bg="#99cfff",
              command=lambda: confirm_order(ctx)).pack(side="right", padx=10)

    buttons = build_toolbar(root,
        lambda: on_show_pizzas(ctx, buttons),
        lambda: on_clear_all(ctx, buttons),
        lambda: on_quit(root)
    )

    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Tests skipped.")
    else:
        main()
# The code is a simple pizza ordering application using Tkinter.
# It allows users to view pizzas, add them to a cart, and place an order.