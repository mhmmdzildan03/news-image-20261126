"""Broadsheet front page for Thursday 26 November 2026.

Draws a one-page newspaper front page with 27 stories, all verified as
26 November 2026 news: 3 illustrated lead cards, a 5-card grid, a dot
map, 19 one-line stories, a day-in-numbers strip, a UTC timeline strip,
a date-check box and a region ticker. Stdlib + Pillow only; fully
deterministic (no randomness, no timestamps, no network).
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 26

PAPER = (247, 242, 231)      # warm newsprint
INK = (24, 24, 24)           # near-black text
SOFT = (74, 74, 66)          # muted grey text
RULE = (24, 24, 24)
RED = (163, 22, 33)          # accent red
BLUE = (38, 70, 110)         # deep blue for map / chess
SKY = (91, 102, 112)         # storm grey
SKY_DARK = (58, 66, 76)
GOLD = (176, 132, 34)
CARD = (255, 253, 247)       # card paper, slightly lighter than page
CARD_LINE = (196, 188, 172)
DUSK = (43, 48, 84)          # Mumbai dusk sky
DUSK_LOW = (120, 74, 66)     # dusk horizon

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def _exists(name):
    import os
    return os.path.exists(FONT_DIR + "/" + name)


def font(kind, size):
    base = {"serif": "DejaVuSerif.ttf", "serif_b": "DejaVuSerif-Bold.ttf",
            "serif_i": "DejaVuSerif-Italic.ttf", "sans": "DejaVuSans.ttf",
            "sans_b": "DejaVuSans-Bold.ttf"}[kind]
    if kind == "serif_i" and not _exists(base):
        base = "DejaVuSerif.ttf"
    return ImageFont.truetype(FONT_DIR + "/" + base, size)


def wrap(d, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, x, y, text, fnt, max_w, fill=INK, leading=None, max_lines=None):
    lines = wrap(d, text, fnt, max_w)
    if max_lines:
        lines = lines[:max_lines]
    lh = leading or int(fnt.size * 1.28)
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def hline(d, x0, x1, y, fill=RULE, width=1):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def section_label(d, x, y, text):
    fnt = font("sans_b", 11)
    d.text((x, y), text, font=fnt, fill=RED)
    return y + 15


# ---------------------------------------------------------------- art panels

def art_parade(d, x, y, w, h):
    """Storm-grey sky, rain, a grounded balloon, empty avenue."""
    # sky bands, darker at top
    for i in range(5):
        d.rectangle([x, y + i * h // 5, x + w, y + (i + 1) * h // 5],
                    fill=(SKY[0] - i * 6, SKY[1] - i * 6, SKY[2] - i * 6))
    # low clouds
    for cx, cy, cw, ch in [(8, 12, 90, 26), (120, 6, 110, 30), (230, 16, 80, 24)]:
        d.ellipse([x + cx, y + cy, x + cx + cw, y + cy + ch], fill=(70, 78, 88))
        d.ellipse([x + cx + 18, y + cy - 8, x + cx + cw - 10, y + cy + ch - 8],
                  fill=(70, 78, 88))
    # rain streaks, slanted
    for rx in range(6, w, 16):
        for ry in range(34, h - 40, 26):
            d.line([(x + rx, y + ry), (x + rx - 5, y + ry + 14)],
                   fill=(190, 198, 205), width=2)
    # street
    d.rectangle([x, y + h - 34, x + w, y + h], fill=(52, 54, 58))
    d.rectangle([x, y + h - 34, x + w, y + h - 30], fill=(120, 122, 126))
    # sagging balloon, half-deflated on the avenue
    bx, by = x + w // 2 - 52, y + h - 96
    d.ellipse([bx, by, bx + 104, by + 52], fill=(196, 58, 64))
    d.ellipse([bx + 8, by + 4, bx + 96, by + 30], fill=(214, 92, 96))
    d.polygon([(bx + 10, by + 48), (bx + 96, by + 48), (bx + 70, by + 62),
               (bx + 34, by + 62)], fill=(150, 40, 46))
    # lamp posts, unlit
    for lx in (x + 18, x + w - 26):
        d.line([(lx, y + h - 34), (lx, y + h - 78)], fill=(30, 30, 32), width=3)
        d.line([(lx, y + h - 78), (lx + 12, y + h - 78)], fill=(30, 30, 32), width=3)
        d.ellipse([lx + 8, y + h - 76, lx + 16, y + h - 68], fill=(30, 30, 32))
    # postponed ribbon
    d.rectangle([x, y + 8, x + 118, y + 28], fill=RED)
    d.text((x + 8, y + 11), "POSTPONED", font=font("sans_b", 11), fill=(255, 255, 255))


def art_chess(d, x, y, w, h):
    """Mini board, white king vs black king, score badge."""
    d.rectangle([x, y, x + w, y + h], fill=(233, 226, 205))
    sq = 24
    n = 5
    ox, oy = x + (w - n * sq) // 2, y + 2
    light, dark = (238, 232, 210), (96, 122, 84)
    for r in range(n):
        for c in range(n):
            col = light if (r + c) % 2 == 0 else dark
            d.rectangle([ox + c * sq, oy + r * sq, ox + (c + 1) * sq, oy + (r + 1) * sq],
                        fill=col)

    def king(kx, ky, col):
        d.ellipse([kx - 11, ky - 5, kx + 11, ky + 15], fill=col,
                  outline=(60, 60, 60), width=2)
        d.ellipse([kx - 7, ky - 13, kx + 7, ky], fill=col,
                  outline=(60, 60, 60), width=2)
        d.line([(kx, ky - 20), (kx, ky - 6)], fill=(60, 60, 60), width=3)
        d.line([(kx - 5, ky - 15), (kx + 5, ky - 15)], fill=(60, 60, 60), width=3)

    def pawn(px, py, col):
        d.ellipse([px - 7, py - 3, px + 7, py + 10], fill=col,
                  outline=(60, 60, 60), width=1)
        d.ellipse([px - 4, py - 10, px + 4, py - 2], fill=col,
                  outline=(60, 60, 60), width=1)

    king(ox + 12, oy + 12, (250, 250, 245))          # white king, top left
    king(ox + 4 * sq + 12, oy + 4 * sq + 12, (28, 28, 30))  # black king, bottom right
    pawn(ox + sq + 12, oy + 2 * sq + 12, (250, 250, 245))
    pawn(ox + 3 * sq + 12, oy + sq + 12, (28, 28, 30))
    # score badge
    d.rectangle([x + w - 66, y + h - 30, x + w - 8, y + h - 8], fill=INK)
    d.text((x + w - 58, y + h - 27), "1 – 1", font=font("sans_b", 12),
           fill=(255, 255, 255))


def art_mumbai(d, x, y, w, h):
    """Dusk sky, skyline silhouette, Gateway arch, candle flames."""
    for i in range(6):
        t = i / 5
        col = tuple(int(DUSK[k] + (DUSK_LOW[k] - DUSK[k]) * t) for k in range(3))
        d.rectangle([x, y + i * h // 6, x + w, y + (i + 1) * h // 6], fill=col)
    # low sun glow
    d.ellipse([x + w - 78, y + 18, x + w - 38, y + 58], fill=(226, 168, 92))
    # skyline silhouette
    base = y + h - 30
    heights = [46, 30, 58, 38, 66, 44, 34, 52, 40, 62, 36, 48]
    bw = w // len(heights)
    for i, hh in enumerate(heights):
        d.rectangle([x + i * bw, base - hh, x + (i + 1) * bw - 2, base],
                    fill=(22, 24, 44))
    # Gateway of India arch, centre
    ax, ay = x + w // 2 - 26, base - 74
    d.rectangle([ax, ay + 26, ax + 52, base], fill=(22, 24, 44))
    d.pieslice([ax - 4, ay - 6, ax + 56, ay + 56], 180, 360, fill=(22, 24, 44))
    d.rectangle([ax + 20, ay + 48, ax + 32, base], fill=PAPER)
    d.pieslice([ax + 16, ay + 38, ax + 36, ay + 58], 180, 360, fill=PAPER)
    # water line + candle flames
    d.rectangle([x, base, x + w, y + h], fill=(30, 34, 58))
    for fx in range(x + 24, x + w - 20, 42):
        d.ellipse([fx - 2, y + h - 22, fx + 2, y + h - 12], fill=(240, 180, 70))
        d.ellipse([fx - 4, y + h - 12, fx + 4, y + h - 8], fill=(240, 180, 70))
    d.text((x + 8, y + 8), "18 YEARS", font=font("sans_b", 12), fill=(240, 200, 120))


# ---------------------------------------------------------------- page parts

def masthead(d):
    y = 16
    hline(d, MARGIN, W - MARGIN, y, width=2)
    small = font("sans_b", 10)
    d.text((MARGIN, y + 6), "THURSDAY, 26 NOVEMBER 2026", font=small, fill=INK)
    right = "DAY 330 OF 2026  ·  27 STORIES"
    d.text((W - MARGIN - d.textlength(right, font=small), y + 6), right,
           font=small, fill=INK)
    name = font("serif_b", 46)
    title = "The Thursday Broadsheet"
    d.text(((W - d.textlength(title, font=name)) / 2, y + 22), title,
           font=name, fill=INK)
    strap = font("serif_i", 13)
    line = "Twenty-seven stories from a single Thursday — every one verified to the day."
    d.text(((W - d.textlength(line, font=strap)) / 2, y + 74), line,
           font=strap, fill=SOFT)
    hline(d, MARGIN, W - MARGIN, y + 96, width=2)
    hline(d, MARGIN, W - MARGIN, y + 100, width=1)
    return y + 108


LEADS = [
    dict(num=1, kicker="NEW YORK · THANKSGIVING", art=art_parade,
         head="Thanksgiving without the parade: Macy's 100th pushed to Saturday",
         deck="First weather postponement in a century as a nor'easter brings "
              "60 mph gusts; NBC airs the 2025 parade on Thursday instead."),
    dict(num=2, kicker="GENEVA · WORLD CHESS CHAMPIONSHIP", art=art_chess,
         head="Game 3: level at 1–1 as Sindarov takes White",
         deck="Two draws in, the title fight restarts at 3pm CET — Gukesh says "
              "he felt “always under control”."),
    dict(num=3, kicker="MUMBAI · 26/11", art=art_mumbai,
         head="Eighteen years on, Mumbai remembers 26/11",
         deck="Tributes at dawn for the 166 lives lost in the 2008 attacks; "
              "the city pauses, then carries on."),
]

GRID = [
    dict(num=4, kicker="BRUSSELS · EU SUMMIT",
         head="EU leaders hold special summit",
         body="A one-day special summit as the bloc weighs its next moves on "
              "Ukraine and budgets."),
    dict(num=5, kicker="DELHI · CONSTITUTION DAY",
         head="India marks 77 years of its Constitution",
         body="Samvidhan Divas: the Constitution adopted in 1949 is honoured "
              "across the country."),
    dict(num=6, kicker="DELHI · EDUCATION",
         head="IITs to add 6,000 tech seats",
         body="New places in robotics, AI and space technology from 2027."),
    dict(num=7, kicker="KATHMANDU · NEIGHBOURS",
         head="India–Nepal ₹15,000-crore package",
         body="Development and connectivity assistance after talks between "
              "Modi and PM Balendra Shah."),
    dict(num=8, kicker="DELHI · SPACE",
         head="India's space economy: $9bn to $45bn",
         body="Minister Jitendra Singh sets a ten-year target for the sector."),
]

# 19 one-liners, numbered 9–27. Regional tally:
# EUROPE 1 · AMERICAS 4 · MIDDLE EAST 2 · ASIA 11 · OCEANIA 1
ONE_LINERS = [
    # ASIA (11)
    "Nayi Chetna's fifth edition fights gender violence",
    "SAMAVESH, e-Anudan portals to speed welfare aid",
    "Supreme Court seeks reply on protest detentions",
    "India urges human control over AI in warfare",
    "Ranchi police detain anti-tree-cutting protesters",
    "Flipkart CEO Krishnamurthy to step down in Dec",
    "Indian banks wrote off ₹1.44 lakh crore in FY26",
    "Cabinet clears ₹4,288-crore Kamarajar terminal",
    "Cabinet clears ₹2,014-crore Silchar airport",
    "Tamil Nadu signs ₹58,000-crore investment MoUs",
    "Congress wins most Zila Pramukh posts, Rajasthan",
    # AMERICAS (4)
    "Wolbachia mosquitoes cut Brazil infections 68%",
    "Fort Hood survivors lose final appeal on execution",
    "Coast Guard hunts six after Gulf of Mexico crash",
    "US shelves business-deals-for-peace Ukraine plan",
    # MIDDLE EAST (2)
    "India condemns Riyadh tower attack; 2 hurt",
    "Houthis strike Saudi Arabia's Ras Tanura refinery",
    # EUROPE (1)
    "BBC, Met Office launch weather coverage tie-up",
    # OCEANIA (1)
    "Australia inks Pacific pact as China taunts",
]

NUMBERS = [
    ("100", "years of the Macy's parade"),
    ("60 mph", "forecast gusts in New York"),
    ("18", "years since the 26/11 attacks"),
    ("6,000", "new IIT tech seats"),
    ("68%", "Brazil infections cut by mosquitoes"),
    ("₹58,000 cr", "Tamil Nadu investment MoUs"),
]

TIMELINE = [
    ("00:00", "Mumbai's 26/11 tributes begin at dawn"),
    ("04:00", "Macy's confirms the parade moves to Saturday"),
    ("06:00", "EU special summit opens in Brussels"),
    ("13:30", "NBC re-airs the 2025 parade (8:30am ET)"),
    ("14:00", "Chess Game 3 starts in Geneva (3pm CET)"),
]

DATE_CHECK = ("Shenzhou-24 · Samara refineries · Nvidia −7% · US tariff plan · "
              "Rosstat ~500,000 deaths · Senegal CAS · Venezuela $237.5bn · "
              "Petrobras $122bn · Bangladesh wage +36% · Hasina return bid · "
              "Sooryavanshi 204 · IPL register · Iowa blast — all 23–25 Nov. "
              "Earlier still: ICJ Rohingya verdict (19 Nov) · BepiColombo (21 Nov) · "
              "Huawei verdict.")


def lead_card(d, x, y, w, h, lead):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=CARD_LINE, width=1)
    art_h = 128
    lead["art"](d, x + 1, y + 1, w - 2, art_h)
    ty = y + art_h + 10
    d.text((x + 12, ty), lead["kicker"], font=font("sans_b", 10), fill=RED)
    ty += 16
    ty = draw_wrapped(d, x + 12, ty, lead["head"], font("serif_b", 17),
                      w - 24, leading=20, max_lines=3)
    ty += 4
    draw_wrapped(d, x + 12, ty, lead["deck"], font("sans", 11.5),
                 w - 24, leading=15, max_lines=4)


def grid_card(d, x, y, w, h, item):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=CARD_LINE, width=1)
    ty = y + 9
    d.text((x + 10, ty), item["kicker"], font=font("sans_b", 9), fill=RED)
    ty += 15
    ty = draw_wrapped(d, x + 10, ty, item["head"], font("serif_b", 12.5),
                      w - 20, leading=15, max_lines=3)
    ty += 3
    draw_wrapped(d, x + 10, ty, item["body"], font("sans", 10),
                 w - 20, leading=13, max_lines=3)


def draw_map(d, x, y, w, h):
    """Schematic dotted world map with numbered pins 1–8."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 236, 240),
                outline=CARD_LINE, width=1)
    # continents as rough polygons in a 100 x 50 space
    continents = [
        [(4, 8), (18, 4), (30, 6), (34, 12), (28, 18), (22, 26), (14, 24), (8, 18)],
        [(26, 30), (34, 30), (38, 38), (32, 48), (27, 40)],
        [(46, 8), (54, 5), (58, 10), (54, 14), (48, 14)],
        [(46, 18), (56, 18), (60, 26), (54, 38), (48, 32), (44, 24)],
        [(58, 4), (82, 4), (96, 10), (92, 20), (80, 24), (72, 30), (64, 22), (58, 14)],
        [(82, 36), (92, 36), (94, 42), (84, 44)],
    ]
    sx, sy = (w - 16) / 100.0, (h - 40) / 50.0
    for poly in continents:
        pts = [(x + 8 + px * sx, y + 6 + py * sy) for px, py in poly]
        d.polygon(pts, fill=(176, 184, 192), outline=(140, 148, 158))
    # pins: (story number, map x, map y) — spread so neighbours never touch
    pins = [(1, 24, 12), (2, 51, 12), (3, 69, 25), (4, 46, 7),
            (5, 74, 17), (6, 78, 21), (7, 80, 15), (8, 72, 20)]
    for num, px, py in pins:
        cx, cy = x + 8 + px * sx, y + 6 + py * sy
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED,
                  outline=(255, 255, 255), width=1)
        num_f = font("sans_b", 8)
        tw = d.textlength(str(num), font=num_f)
        d.text((cx - tw / 2, cy - 5), str(num), font=num_f, fill=(255, 255, 255))
    legend = "1 New York · 2 Geneva · 3 Mumbai · 4 Brussels · 5, 6 & 8 Delhi · 7 Kathmandu"
    lf = font("sans", 9.5)
    draw_wrapped(d, x + 8, y + h - 30, legend, lf, w - 16, leading=12)


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    y = masthead(d)

    # --- three lead cards
    lead_w = (W - 2 * MARGIN - 2 * 12) // 3
    lead_h = 288
    for i, lead in enumerate(LEADS):
        lead_card(d, MARGIN + i * (lead_w + 12), y, lead_w, lead_h, lead)
    y += lead_h + 10

    # --- five-card grid
    y = section_label(d, MARGIN, y, "ALSO TODAY — FIVE MORE")
    grid_w = (W - 2 * MARGIN - 4 * 10) // 5
    grid_h = 126
    for i, item in enumerate(GRID):
        grid_card(d, MARGIN + i * (grid_w + 10), y, grid_w, grid_h, item)
    y += grid_h + 10

    # --- map + one-liners
    y = section_label(d, MARGIN, y, "WHERE IT HAPPENED")
    d.text((340, y - 15), "THE REST OF THE DAY — 19 STORIES",
           font=font("sans_b", 11), fill=RED)
    map_w = 292
    col_x = [340, 676]
    col_w = 322
    item_f = font("sans", 10.5)
    num_f = font("sans_b", 10.5)
    # measure the one-liner block first so it can never collide with the
    # numbers strip below, however the lines wrap
    probe = Image.new("RGB", (8, 8))
    pd = ImageDraw.Draw(probe)
    block_h = 0
    for col in range(2):
        items = ONE_LINERS[col * 10:(col + 1) * 10]
        ch = 4
        for text in items:
            ch += len(wrap(pd, text, item_f, col_w - 26)) * 13 + 4
        block_h = max(block_h, ch)
    map_h = max(236, block_h)
    draw_map(d, MARGIN, y, map_w, map_h)
    for col in range(2):
        items = ONE_LINERS[col * 10:(col + 1) * 10]
        iy = y + 4
        for j, text in enumerate(items):
            num = 9 + col * 10 + j
            d.text((col_x[col], iy), str(num) + ".", font=num_f, fill=RED)
            lines = wrap(d, text, item_f, col_w - 26)
            ly = iy
            for ln in lines:
                d.text((col_x[col] + 26, ly), ln, font=item_f, fill=INK)
                ly += 13
            iy = ly + 4
    y += map_h + 10

    # --- day in numbers
    hline(d, MARGIN, W - MARGIN, y, width=1)
    y += 6
    d.text((MARGIN, y), "THE DAY IN NUMBERS", font=font("sans_b", 11), fill=RED)
    y += 18
    stat_w = (W - 2 * MARGIN) // 6
    for i, (num, cap) in enumerate(NUMBERS):
        sx = MARGIN + i * stat_w
        d.text((sx, y), num, font=font("serif_b", 21), fill=INK)
        draw_wrapped(d, sx, y + 26, cap, font("sans", 9.5), stat_w - 12,
                     fill=SOFT, leading=12, max_lines=2)
    y += 52
    hline(d, MARGIN, W - MARGIN, y, width=1)

    # --- UTC timeline
    y += 7
    d.text((MARGIN, y), "THURSDAY IN UTC", font=font("sans_b", 11), fill=RED)
    tl = "   ·   ".join("%s  %s" % (t, s) for t, s in TIMELINE)
    draw_wrapped(d, MARGIN + 132, y, tl, font("sans", 10.5),
                 W - MARGIN - (MARGIN + 132), leading=14, max_lines=2)
    y += 34

    # --- date-check box
    box_h = 46
    d.rectangle([MARGIN, y, W - MARGIN, y + box_h], outline=CARD_LINE, width=1)
    d.text((MARGIN + 10, y + 5), "DATE-CHECK — LEFT OUT BECAUSE THEY ARE NOT 26 NOVEMBER",
           font=font("sans_b", 10), fill=RED)
    draw_wrapped(d, MARGIN + 10, y + 21, DATE_CHECK, font("sans", 9.5),
                 W - 2 * MARGIN - 20, leading=12, max_lines=2)
    y += box_h + 8

    # --- region ticker
    hline(d, MARGIN, W - MARGIN, y, width=2)
    tick = "EUROPE 3  ·  AMERICAS 5  ·  MIDDLE EAST 2  ·  ASIA 16  ·  OCEANIA 1   —   27 STORIES, ONE THURSDAY"
    tf = font("sans_b", 12)
    d.text(((W - d.textlength(tick, font=tf)) / 2, y + 6), tick, font=tf, fill=INK)
    hline(d, MARGIN, W - MARGIN, y + 26, width=2)

    return img


def main():
    img = render()
    img.save("entry.png")


if __name__ == "__main__":
    main()
