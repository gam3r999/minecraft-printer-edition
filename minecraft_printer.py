"""
╔══════════════════════════════════════════════════════════════════╗
║             M I N E C R A F T   P R I N T E R                   ║
║                                                                  ║
║  Captures every frame from your real Minecraft window and        ║
║  sends each one to your physical printer. Every. Single. One.    ║
║                                                                  ║
║  Requirements:                                                   ║
║    pip install mss pillow pygetwindow pywin32                    ║
║    (tkinter is built into Python already)                        ║
║                                                                  ║
║  You will also need:                                             ║
║    - A real printer                                              ║
║    - A lot of paper                                              ║
║    - No regard for the environment                               ║
║    - Minecraft actually running                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import platform
import threading
import subprocess
import tempfile
from collections import deque

# ── dependency check ──────────────────────────────────────────────────────────
missing = []
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    missing.append("pillow")

try:
    import mss
except ImportError:
    missing.append("mss")

try:
    import pygetwindow as gw
except ImportError:
    missing.append("pygetwindow")

if missing:
    print(f"\n❌  Missing packages: {', '.join(missing)}")
    print(f"    Run:  pip install {' '.join(missing)}\n")
    sys.exit(1)

import tkinter as tk
from tkinter import font as tkfont

# ── config ────────────────────────────────────────────────────────────────────

# How many frames per second to capture (and print). 
# At 1 FPS you'll use ~1 page/sec. At 10 FPS you'll run out of paper
# and friends in under a minute.
CAPTURE_FPS = 1  # 👈 change this if you enjoy suffering faster

# Minecraft window title — the script looks for a window whose title
# contains this string (case-insensitive).
MINECRAFT_TITLE_KEYWORD = "minecraft"

# ── globals ───────────────────────────────────────────────────────────────────

pages_printed   = 0
ink_estimate_ml = 0.0
print_queue     = deque()
queue_lock      = threading.Lock()
stop_event      = threading.Event()

stats_label     = None   # set once the Tk window is ready
root_window     = None

# ── printer helpers ───────────────────────────────────────────────────────────

def estimate_ink_ml(img: Image.Image) -> float:
    """Wildly rough estimate: ~0.015 mL ink for a fully-covered page."""
    rgb = img.convert("RGB")
    pixels = list(rgb.getdata())
    non_white = sum(1 for r, g, b in pixels if r + g + b < 720)
    return (non_white / len(pixels)) * 0.015


def send_to_printer(pil_img: Image.Image):
    """Print a PIL image silently — no dialogs, no popups, no questions."""
    global pages_printed, ink_estimate_ml

    system = platform.system()
    try:
        if system == "Windows":
            _print_windows_silent(pil_img)
        elif system == "Darwin":
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                tmp = f.name
            pil_img.save(tmp, "PNG", dpi=(150, 150))
            subprocess.Popen(["lpr", tmp],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
            threading.Timer(5.0, lambda: os.path.exists(tmp) and os.unlink(tmp)).start()
        else:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                tmp = f.name
            pil_img.save(tmp, "PNG", dpi=(150, 150))
            subprocess.Popen(["lpr", tmp],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
            threading.Timer(5.0, lambda: os.path.exists(tmp) and os.unlink(tmp)).start()
    except Exception as e:
        print(f"[printer] error: {e}")

    pages_printed   += 1
    ink_estimate_ml += estimate_ink_ml(pil_img)
    update_stats_label()


def _print_windows_silent(pil_img: Image.Image):
    """
    Draw directly to the Windows printer DC using win32print + win32ui.
    No temp files. No PowerShell. No dialogs. Ever.
    Goes straight to the spooler in memory.
    """
    try:
        import win32print
        import win32ui
        from PIL import ImageWin
    except ImportError:
        print("[printer] pywin32 missing — run: pip install pywin32")
        return

    printer_name = win32print.GetDefaultPrinter()

    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(printer_name)

    page_w = hdc.GetDeviceCaps(110)  # HORZRES  — printable width in pixels
    page_h = hdc.GetDeviceCaps(111)  # VERTRES  — printable height in pixels

    # Scale image to fit the page, preserving aspect ratio
    img_w, img_h = pil_img.size
    scale  = min(page_w / img_w, page_h / img_h)
    draw_w = int(img_w * scale)
    draw_h = int(img_h * scale)
    x_off  = (page_w - draw_w) // 2
    y_off  = (page_h - draw_h) // 2

    hdc.StartDoc("Minecraft Frame")
    hdc.StartPage()

    dib = ImageWin.Dib(pil_img)
    dib.draw(hdc.GetHandleOutput(),
             (x_off, y_off, x_off + draw_w, y_off + draw_h))

    hdc.EndPage()
    hdc.EndDoc()
    hdc.DeleteDC()


def printer_worker():
    """Background thread: drain print_queue one job at a time."""
    while not stop_event.is_set():
        job = None
        with queue_lock:
            if print_queue:
                job = print_queue.popleft()
        if job is not None:
            send_to_printer(job)
        else:
            time.sleep(0.05)


# ── stats window ──────────────────────────────────────────────────────────────

def update_stats_label():
    """Push updated numbers into the Tk label (thread-safe via after())."""
    if root_window and stats_label:
        root_window.after(0, _refresh_label)


def _refresh_label():
    if stats_label:
        trees = pages_printed / 8333  # ~8333 pages per tree (rough)
        stats_label.config(
            text=(
                f"  🖨️  Pages printed:       {pages_printed}\n"
                f"  💧  Ink wasted:          {ink_estimate_ml:.3f} mL\n"
                f"  📄  Paper wasted:        {pages_printed} sheets\n"
                f"  🌳  Trees murdered:      {trees:.5f}\n\n"
                f"  Queue waiting to print: {len(print_queue)} frames\n\n"
                f"  Capture rate:           {CAPTURE_FPS} FPS\n"
                f"  (i.e. {CAPTURE_FPS * 60} pages/minute)\n\n"
                f"  Why are you doing this?\n"
            )
        )


def launch_stats_window():
    """Run the 'papers wasted' Tk window in the main thread."""
    global root_window, stats_label

    root_window = tk.Tk()
    root_window.title("Check here you dumbass")
    root_window.configure(bg="#1a1a1a")
    root_window.resizable(False, False)

    header = tk.Label(
        root_window,
        text="📊  PAPERS WASTED DASHBOARD  📊",
        bg="#1a1a1a",
        fg="#ff4444",
        font=("Courier New", 15, "bold"),
        pady=10,
        padx=20,
    )
    header.pack()

    sep = tk.Label(root_window, text="─" * 44, bg="#1a1a1a", fg="#555555",
                   font=("Courier New", 11))
    sep.pack()

    stats_label = tk.Label(
        root_window,
        text="  Waiting for Minecraft...",
        bg="#1a1a1a",
        fg="#00ff99",
        font=("Courier New", 13),
        justify="left",
        padx=20,
        pady=10,
    )
    stats_label.pack()

    sep2 = tk.Label(root_window, text="─" * 44, bg="#1a1a1a", fg="#555555",
                    font=("Courier New", 11))
    sep2.pack()

    warning = tk.Label(
        root_window,
        text=(
            "⚠️  Every frame of Minecraft you see\n"
            "    is being sent to your printer.\n"
            "    This is your fault."
        ),
        bg="#1a1a1a",
        fg="#ffaa00",
        font=("Courier New", 11, "italic"),
        pady=8,
        padx=20,
    )
    warning.pack()

    quit_btn = tk.Button(
        root_window,
        text="  STOP THE MADNESS  ",
        bg="#cc0000",
        fg="white",
        font=("Courier New", 12, "bold"),
        relief="flat",
        cursor="pirate",
        command=lambda: (stop_event.set(), root_window.destroy()),
        pady=6,
        padx=10,
    )
    quit_btn.pack(pady=12)

    root_window.protocol("WM_DELETE_WINDOW", lambda: (stop_event.set(), root_window.destroy()))
    root_window.mainloop()


# ── minecraft capture ─────────────────────────────────────────────────────────

# Browser suffixes that mean this is a website tab, not the actual game
BROWSER_SUFFIXES = (
    "- google chrome",
    "- chromium",
    "- mozilla firefox",
    "- firefox",
    "- microsoft edge",
    "- opera",
    "- brave",
    "- safari",
    "- vivaldi",
    "- arc",
)

def find_minecraft_window():
    """
    Return the actual Minecraft game window — nothing else.

    Rules:
      1. Title must start with 'Minecraft' (not just contain it).
      2. Title must NOT end with a browser name (e.g. "- Google Chrome").
         This stops it from printing your Claude/wiki/YouTube tab.
      3. Window must be at least 640x480 — the game is never smaller than that.
      4. Window must not be minimised (width/height > 0).
    """
    try:
        windows = gw.getAllWindows()
        for w in windows:
            title = (w.title or "").strip().lower()

            # Rule 1 — must start with minecraft
            if not title.startswith(MINECRAFT_TITLE_KEYWORD):
                continue

            # Rule 2 — must not be a browser tab
            if any(title.endswith(suffix) for suffix in BROWSER_SUFFIXES):
                continue

            # Rule 3 — must be a real game-sized window
            if w.width < 640 or w.height < 480:
                continue

            # Rule 4 — must not be minimised
            if w.width == 0 or w.height == 0:
                continue

            return w
    except Exception:
        pass
    return None


def add_frame_number(img: Image.Image, frame_num: int, timestamp: str) -> Image.Image:
    """Stamp the frame number and timestamp onto the image before printing."""
    draw = ImageDraw.Draw(img)
    text = f"FRAME #{frame_num}  |  {timestamp}  |  minecraft_printer.py"
    # white text with black shadow
    draw.text((11, 11), text, fill=(0, 0, 0))
    draw.text((10, 10), text, fill=(255, 255, 255))
    return img


def capture_loop():
    """Continuously capture Minecraft frames and queue them for printing."""
    frame_num     = 0
    interval      = 1.0 / CAPTURE_FPS
    last_capture  = 0.0
    warned_once   = False

    print("[capture] Looking for Minecraft window…")

    with mss.mss() as sct:
        while not stop_event.is_set():
            now = time.time()
            if now - last_capture < interval:
                time.sleep(0.01)
                continue
            last_capture = now

            # Find Minecraft window every frame (it may move/resize)
            win = find_minecraft_window()
            if win is None:
                if not warned_once:
                    print("[capture] Minecraft window not found. "
                          "Launch Minecraft and make sure its window is visible.")
                    warned_once = True
                time.sleep(1.0)
                continue

            warned_once = False

            try:
                # Grab the region matching the Minecraft window
                region = {
                    "top":    win.top,
                    "left":   win.left,
                    "width":  max(win.width,  1),
                    "height": max(win.height, 1),
                }
                raw = sct.grab(region)
                img = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
            except Exception as e:
                print(f"[capture] screenshot error: {e}")
                time.sleep(0.5)
                continue

            frame_num += 1
            ts = time.strftime("%H:%M:%S")
            stamped = add_frame_number(img.copy(), frame_num, ts)

            with queue_lock:
                print_queue.append(stamped)

            print(
                f"[capture] Frame {frame_num:>6}  |  "
                f"queue: {len(print_queue):>3}  |  "
                f"printed: {pages_printed}  |  "
                f"ink: {ink_estimate_ml:.3f} mL"
            )
            update_stats_label()


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    print(__doc__)
    print(f"[info] Printing silently via GDI (no dialogs)")
    print(f"[info] Capture rate  : {CAPTURE_FPS} FPS")
    print(f"[info] That's roughly {CAPTURE_FPS * 60} pages per minute.")
    print(f"[info] Or {CAPTURE_FPS * 3600} pages per hour.")
    print(f"[info] Good luck.\n")

    # Start printer worker thread
    pt = threading.Thread(target=printer_worker, daemon=True)
    pt.start()

    # Start capture thread
    ct = threading.Thread(target=capture_loop, daemon=True)
    ct.start()

    # Stats window runs on the main thread (Tk requirement)
    launch_stats_window()

    # Tk window closed — signal everything to stop
    stop_event.set()
    print("\n[info] Stopped.")
    print(f"[info] Total pages printed : {pages_printed}")
    print(f"[info] Total ink wasted    : {ink_estimate_ml:.3f} mL")
    print(f"[info] Trees harmed        : {pages_printed / 8333:.5f}")
    print("[info] I hope it was worth it.")


if __name__ == "__main__":
    main()
