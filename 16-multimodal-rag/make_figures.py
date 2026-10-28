"""Draw the three figures used in this lesson.

Fernhill's documents are text, so we drew three simple manual figures for this lesson. Each one holds facts that are
written ONLY in the drawing, nowhere in the text:

- display-bracket.png    Ridge 500 manual: fitting the display bracket (a diagram with a torque value)
- battery-capacity.png   Battery guide: capacity left after charge cycles (a chart)
- carrier-load.png       Metro 300 manual: loading the rear carrier (a side view)

Run from the repository root:  python 16-multimodal-rag/make_figures.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FOLDER = Path(__file__).parent / "figures"
WIDTH, HEIGHT = 1600, 1100
SCALE = 2  # draw at twice the size, then shrink: smoother lines
INK = (30, 30, 30)
GREY = (120, 120, 120)
PAPER = (252, 251, 248)


def font(size):
    return ImageFont.load_default(size=size * SCALE)


def new_figure(header, caption):
    image = Image.new("RGB", (WIDTH * SCALE, HEIGHT * SCALE), PAPER)
    draw = ImageDraw.Draw(image)
    draw.text((s(60), s(40)), header, font=font(30), fill=GREY)
    draw.line([s(60), s(90), s(WIDTH - 60), s(90)], fill=GREY, width=s(2))
    draw.text((s(60), s(HEIGHT - 80)), caption, font=font(34), fill=INK)
    return image, draw


def s(value):
    return value * SCALE


def box(draw, x0, y0, x1, y1, width=4):
    draw.rectangle([s(x0), s(y0), s(x1), s(y1)], outline=INK, width=s(width))


def line(draw, points, width=4, colour=INK):
    draw.line([(s(x), s(y)) for x, y in points], fill=colour, width=s(width), joint="curve")


def text(draw, x, y, words, size=34, colour=INK):
    draw.text((s(x), s(y)), words, font=font(size), fill=colour)


def callout(draw, number, x, y):
    draw.ellipse([s(x - 24), s(y - 24), s(x + 24), s(y + 24)], fill=INK)
    draw.text((s(x), s(y)), str(number), font=font(30), fill=PAPER, anchor="mm")


def save(image, name):
    small = image.resize((WIDTH, HEIGHT), Image.LANCZOS)
    small.save(FOLDER / name)
    print("Saved", FOLDER / name)


def display_bracket():
    image, draw = new_figure("RIDGE 500 OWNER'S MANUAL  ·  FITTING THE DISPLAY",
                             "Figure 7. Fitting the display bracket (FH-5110-A) to the handlebar.")
    # the handlebar and the stem
    box(draw, 120, 560, 1480, 620)
    box(draw, 900, 520, 1040, 660)
    line(draw, [(970, 660), (970, 820)], width=6)
    text(draw, 1060, 680, "stem", 30, GREY)
    # the bracket clamped round the bar, with the display on top
    box(draw, 560, 530, 760, 650, width=6)
    box(draw, 520, 300, 800, 470, width=6)
    box(draw, 550, 325, 770, 445, width=2)
    line(draw, [(660, 470), (660, 530)], width=6)
    text(draw, 585, 365, "display", 34, GREY)
    # two clamp screws under the bracket
    for x in (600, 720):
        line(draw, [(x, 650), (x, 720)], width=8)
        draw.ellipse([s(x - 16), s(712), s(x + 16), s(744)], outline=INK, width=s(4))
    # the cable to the stem
    line(draw, [(800, 400), (860, 400), (860, 540), (900, 540)], width=3, colour=GREY)
    # labels, written next to the parts they name
    line(draw, [(584, 740), (470, 800)], width=2)
    text(draw, 120, 790, "clamp screws (2): 3 Nm", 36)
    text(draw, 120, 840, "2.5 mm hex key", 36)
    line(draw, [(520, 360), (430, 300)], width=2)
    text(draw, 120, 260, "slide on until it clicks", 34)
    line(draw, [(860, 470), (1180, 470)], width=2)
    text(draw, 1190, 450, "cable to the right", 34)
    text(draw, 1190, 495, "of the stem", 34)
    save(image, "display-bracket.png")


def battery_capacity():
    image, draw = new_figure("BATTERY AND CHARGING GUIDE  ·  HOW A BATTERY AGES",
                             "Figure 2. Capacity left after full charge cycles (Fernhill lab test, 20 °C).")
    cycles = [0, 200, 400, 600, 800, 1000]
    capacity = [100, 95, 90, 86, 82, 78]
    left, right, top, bottom = 220, 1460, 160, 860   # the plot area; the y axis runs from 60% to 100%

    def point(cycle, percent):
        x = left + (right - left) * cycle / 1000
        y = bottom - (bottom - top) * (percent - 60) / 40
        return x, y

    line(draw, [(left, top), (left, bottom), (right, bottom)], width=4)
    for percent in (60, 70, 80, 90, 100):
        x, y = point(0, percent)
        line(draw, [(left - 12, y), (left, y)], width=3)
        text(draw, left - 110, y - 20, f"{percent}%", 30, GREY)
    for cycle in cycles:
        x, y = point(cycle, 60)
        line(draw, [(x, bottom), (x, bottom + 12)], width=3)
        text(draw, x - 30, bottom + 20, str(cycle), 30, GREY)
    text(draw, 700, bottom + 60, "full charge cycles", 30, GREY)
    # the warranty limit of the 2026 policy, dashed
    x0, y70 = point(0, 70)
    for start in range(left, right, 40):
        line(draw, [(start, y70), (start + 22, y70)], width=3, colour=GREY)
    text(draw, 1130, y70 + 14, "warranty limit 70%", 30, GREY)
    # the measured capacity, with a dot and a value at every point
    line(draw, [point(c, p) for c, p in zip(cycles, capacity)], width=6)
    for c, p in zip(cycles, capacity):
        x, y = point(c, p)
        draw.ellipse([s(x - 12), s(y - 12), s(x + 12), s(y + 12)], fill=INK)
        text(draw, x - 30, y - 62, f"{p}%", 32)
    save(image, "battery-capacity.png")


def carrier_load():
    image, draw = new_figure("METRO 300 OWNER'S MANUAL  ·  CARRYING LUGGAGE",
                             "Figure 4. Loading the rear carrier: side view.")
    # the rear wheel, the frame and the saddle
    draw.ellipse([s(780), s(430), s(1220), s(870)], outline=INK, width=s(6))
    draw.ellipse([s(980), s(630), s(1020), s(670)], fill=INK)
    line(draw, [(1000, 650), (760, 420), (560, 650)], width=6)
    line(draw, [(760, 420), (720, 300)], width=6)
    box(draw, 640, 270, 800, 300)
    # the carrier and its stays
    box(draw, 820, 360, 1300, 384, width=6)
    line(draw, [(1280, 384), (1000, 650)], width=5)
    line(draw, [(840, 384), (780, 440)], width=5)
    # a pannier bag hanging from the carrier (one each side; the near one is shown)
    draw.rectangle([s(870), s(400), s(1070), s(580)], fill=PAPER, outline=INK, width=s(4))
    text(draw, 912, 470, "pannier", 30, GREY)
    # the load arrow
    line(draw, [(1060, 180), (1060, 340)], width=6)
    line(draw, [(1040, 310), (1060, 340), (1080, 310)], width=6)
    callout(draw, 1, 1140, 210)
    callout(draw, 2, 1390, 500)
    line(draw, [(1366, 500), (1070, 500)], width=2)
    text(draw, 120, 880, "1   Maximum load on the carrier: 25 kg", 36)
    text(draw, 120, 935, "2   Up to 2 pannier bags, one each side", 36)
    save(image, "carrier-load.png")


FOLDER.mkdir(exist_ok=True)
display_bracket()
battery_capacity()
carrier_load()
