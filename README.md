# 🖨️ Minecraft Printer

> **Captures every single frame of your Minecraft game and prints it to your physical printer. In real time. Every frame. Yes, really.**

---

## 🤔 What is this?

This is a Python script that:

1. Finds your open Minecraft window
2. Takes a screenshot of it
3. **Sends it to your printer**
4. Repeats this forever until you run out of paper, ink, money, or the will to live

A second window opens alongside it titled **"Check here you dumbass"** which tracks exactly how much damage you're doing — pages printed, ink wasted in mL, and trees killed.

---

## 📋 Requirements

### Software
- Python 3.8+
- Minecraft (the actual game, you own it right?)
- A working printer driver installed on your PC

### Python packages

```bash
pip install mss pillow pygetwindow pywin32
```

| Package | What it does |
|---|---|
| `mss` | Fast screen capture |
| `pillow` | Image processing + printer rendering |
| `pygetwindow` | Finds your Minecraft window |
| `pywin32` | Talks directly to the Windows print spooler (no dialogs) |

> `tkinter` is already built into Python. You don't need to install it.

---

## 🚀 Usage

1. **Launch Minecraft** and get into a world
2. **Run the script:**

```bash
python minecraft_printer.py
```

3. Two things will happen:
   - A stats window called **"Check here you dumbass"** will open showing your damage in real time
   - Your printer will immediately start printing every frame of Minecraft

4. Press **STOP THE MADNESS** in the stats window (or close it) to stop

---

## ⚙️ Configuration

At the top of `minecraft_printer.py`:

```python
CAPTURE_FPS = 1  # frames (pages) per second
```

| FPS | Pages / minute | Pages / hour | Reams / day |
|-----|---------------|--------------|-------------|
| 1   | 60            | 3,600        | 172         |
| 5   | 300           | 18,000       | 864         |
| 10  | 600           | 36,000       | 1,728       |

You can also change the Minecraft window search keyword:

```python
MINECRAFT_TITLE_KEYWORD = "minecraft"
```

---

## 🖨️ How printing works (no dialogs!)

On **Windows**, the script uses `win32print` and `win32ui` to send images directly to the GDI print spooler. No "how would you like to print" popups. No dialogs. No questions. It just prints.

On **macOS / Linux**, it uses `lpr` which is equally silent.

Each printed page is stamped with:
- The frame number
- The timestamp
- The filename, as a reminder of your choices

---

## 📊 The Stats Window

The window titled **"Check here you dumbass"** tracks:

- 🖨️ Pages printed
- 💧 Estimated ink used (mL)
- 📄 Sheets of paper consumed
- 🌳 Trees murdered (yes, it calculates this)
- 📦 Frames currently queued to print

---

## ❓ FAQ

**Q: Will this void my printer warranty?**
A: Almost certainly.

**Q: What if I run out of paper?**
A: The queue will back up and print the rest when you reload paper. This script does not care about you or your paper supply.

**Q: Is this legal?**
A: Printing screenshots of a game you own is fine. What's not fine is whatever you're about to do to your printer.

**Q: Can I increase the FPS?**
A: You can. You shouldn't. But you can.

**Q: Why does this exist?**
A: No good reason.

---

## ⚠️ Warnings

- This **will** go through your ink cartridges extremely fast
- This **will** eat through paper at an alarming rate
- Printing grayscale instead of color in your printer settings will save ink
- Reducing print quality/DPI in your printer settings will also help
- Nothing will truly save you

---

---

## 🌲 Note on the environment

At 1 FPS, you will consume approximately **1 tree every 13 hours** of playtime (based on ~8,333 pages per tree). Please consider this before running the script during a long Minecraft session.

---

*Built with Python, mss, Pillow, pywin32, and an utter disregard for paper.*

---

> ## ⬇️ IF YOU ARE DOWNLOADING THIS WITHOUT A PRINTER, WHAT ARE YOU DOING!?!?!?!
