"""THE WORLD — Friday, 27 November 2026.
A dense broadsheet of the day's world news, drawn with pure Python stdlib.
Writes entry.png (1024x1024) to MAKEFUN_OUTPUT_DIR or the current directory.
"""
import os
import struct
import zlib
from binascii import crc32

W, H = 1024, 1024
PAPER = (247, 243, 234)
NAVY = (20, 33, 61)
RED = (178, 34, 34)
INK = (28, 28, 28)
GREY = (110, 108, 100)
WHITE = (250, 248, 244)
GOLD = (197, 146, 44)
TEAL = (31, 120, 110)
SKY = (88, 140, 178)

buf = bytearray(W * H * 3)


def fill(color):
    r, g, b = color
    for i in range(0, len(buf), 3):
        buf[i] = r
        buf[i + 1] = g
        buf[i + 2] = b


def px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = color


def rect(x, y, w, h, color):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        r, g, b = color
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            buf[i] = r
            buf[i + 1] = g
            buf[i + 2] = b


def hline(x0, x1, y, color):
    for x in range(max(0, x0), min(W, x1)):
        px(x, y, color)


def vline(x, y0, y1, color):
    for y in range(max(0, y0), min(H, y1)):
        px(x, y, color)


def line(x0, y0, x1, y1, color):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        px(x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def circle(cx, cy, r, color, fillc=True):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
            if fillc:
                if d <= r * r:
                    px(xx, yy, color)
            else:
                if abs(d - r * r) <= r:
                    px(xx, yy, color)


def tri(x0, y0, x1, y1, x2, y2, color):
    # filled triangle via scanline fill
    ys = sorted([(y0, x0), (y1, x1), (y2, x2)])
    (ya, xa), (yb, xb), (yc, xc) = ys
    def interp(y, y_a, x_a, y_b, x_b):
        if y_b == y_a:
            return x_a
        return x_a + (x_b - x_a) * (y - y_a) / (y_b - y_a)
    for y in range(ya, yc + 1):
        if y < yb:
            xa_ = interp(y, ya, xa, yb, xb)
            xb_ = interp(y, ya, xa, yc, xc)
        else:
            xa_ = interp(y, yb, xb, yc, xc)
            xb_ = interp(y, ya, xa, yc, xc)
        for x in range(int(min(xa_, xb_)), int(max(xa_, xb_)) + 1):
            px(x, y, color)


# 5x7 bitmap font. Each glyph is 35 chars: 7 rows of 5 bits, '1' = ink.
FONT = {
'A': '01110100011000111111100011000110001',
'B': '11110100011000111110100011000111110',
'C': '01110100011000010000100001000101110',
'D': '11110100011000110001100011000111110',
'E': '11111100001000011110100001000011111',
'F': '11111100001000011110100001000010000',
'G': '01110100011000010111100011000101111',
'H': '10001100011000111111100011000110001',
'I': '01110001000010000100001000010001110',
'J': '00111000100001000010000101001001100',
'K': '10001100101010011000101001001010001',
'L': '10000100001000010000100001000011111',
'M': '10001110111010110101100011000110001',
'N': '10001110011010110011100011000110001',
'O': '01110100011000110001100011000101110',
'P': '11110100011000111110100001000010000',
'Q': '01110100011000110001101011001001101',
'R': '11110100011000111110101001001010001',
'S': '01111100001000001110000010000111110',
'T': '11111001000010000100001000010000100',
'U': '10001100011000110001100011000101110',
'V': '10001100011000110001100010101000100',
'W': '10001100011000110101101011101110001',
'X': '10001100010101000100010101000110001',
'Y': '10001100010101000100001000010000100',
'Z': '11111000010001000100010001000011111',
'0': '01110100011001110101110011000101110',
'1': '00100011000010000100001000010001110',
'2': '01110100010000100110010001000011111',
'3': '11111000100010000010000011000101110',
'4': '00010001100101010010111110001000010',
'5': '11111100001111000001000011000101110',
'6': '01110100001000011110100011000101110',
'7': '11111000010001000100010000100001000',
'8': '01110100011000101110100011000101110',
'9': '01110100011000101111000010000101110',
' ': '00000000000000000000000000000000000',
'.': '00000000000000000000000000110001100',
',': '00000000000000000000011000010001000',
':': '00000011000110000000011000110000000',
';': '00000011000110000000011000010001000',
'!': '00100001000010000100001000000000100',
'?': '01110100010000100110001000000000100',
'-': '00000000000000001110000000000000000',
'(': '00010001000100001000010000010000010',
')': '01000001000001000010000100010001000',
'/': '00001000100010000100010001000010000',
'%': '11001110100001000100010000101110011',
'$': '00100011111010001110001011111000100',
'&': '01100100101010001000101011001001101',
'+': '00000001000010001110001000010000000',
'=': '00000000001111100000111110000000000',
'"': '01010010100101000000000000000000000',
"'": '00100001000100000000000000000000000',
}


def char_w(scale):
    return 6 * scale


def text_w(s, scale):
    return len(s) * char_w(scale)


def draw_text(s, x, y, scale, color):
    """Draw uppercase text; unknown chars become space."""
    cx = x
    for ch in s.upper():
        g = FONT.get(ch, FONT[' '])
        for r in range(7):
            row = g[r * 5:(r + 1) * 5]
            for c in range(5):
                if row[c] == '1':
                    rect(cx + c * scale, y + r * scale, scale, scale, color)
        cx += char_w(scale)
    return cx


def text_lines(s, max_w, scale):
    """Word-wrap text to lines fitting max_w pixels."""
    words = s.split()
    lines = []
    cur = ''
    for w_ in words:
        trial = (cur + ' ' + w_).strip()
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def para(s, x, y, max_w, scale, color, leading=None):
    """Draw wrapped paragraph; return y below the last line."""
    if leading is None:
        leading = 7 * scale + 3
    for ln in text_lines(s, max_w, scale):
        draw_text(ln, x, y, scale, color)
        y += leading
    return y


def center_text(s, y, scale, color, x0=0, x1=W):
    draw_text(s, x0 + (x1 - x0 - text_w(s, scale)) // 2, y, scale, color)


# Dotted world map: 36 rows x 72 cols, '#' = land. Equirectangular, rough.
MAP = [
"." * 72,
"." * 72,
"." * 24 + "#" * 4 + "." * 44,
"." * 7 + "#" * 14 + "." * 3 + "#" * 5 + "." * 6 + "#" * 5 + "." * 3 + "#" * 23 + "." * 6,
"." * 6 + "#" * 17 + "." + "#" * 5 + "." * 5 + "#" * 9 + "." + "#" * 24 + "." * 4,
"." * 5 + "#" * 19 + "." * 10 + "#" * 10 + "#" * 25 + "." * 3,
"." * 4 + "#" * 20 + "." * 10 + "#" * 9 + "." * 2 + "#" * 23 + "." * 4,
"." * 4 + "#" * 19 + "." * 12 + "#" * 7 + "." * 4 + "#" * 23 + "." * 3,
"." * 5 + "#" * 18 + "." * 12 + "#" * 6 + "." * 6 + "#" * 19 + "." * 6,
"." * 6 + "#" * 16 + "." * 14 + "#" * 5 + "." * 7 + "#" * 17 + "." * 7,
"." * 7 + "#" * 15 + "." * 15 + "#" * 5 + "." * 7 + "#" * 15 + "." * 8,
"." * 8 + "#" * 13 + "." * 14 + "#" * 10 + "." * 5 + "#" * 13 + "." * 9,
"." * 9 + "#" * 11 + "." * 14 + "#" * 12 + "." * 4 + "#" * 12 + "." * 10,
"." * 10 + "#" * 9 + "." * 15 + "#" * 12 + "." * 5 + "#" * 10 + "." * 11,
"." * 11 + "#" * 7 + "." * 17 + "#" * 11 + "." * 6 + "#" * 8 + "." * 12,
"." * 12 + "#" * 5 + "." * 18 + "#" * 10 + "." * 8 + "#" * 6 + "." * 13,
"." * 14 + "#" * 4 + "." * 18 + "#" * 9 + "." * 11 + "#" * 5 + "." * 11,
"." * 15 + "#" * 3 + "." * 18 + "#" * 8 + "." * 13 + "#" * 5 + "." * 10,
"." * 16 + "#" * 3 + "." * 18 + "#" * 7 + "." * 14 + "#" * 6 + "." * 8,
"." * 19 + "#" * 5 + "." * 12 + "#" * 6 + "." * 16 + "#" * 5 + "." * 9,
"." * 20 + "#" * 7 + "." * 10 + "#" * 6 + "." * 29,
"." * 21 + "#" * 6 + "." * 11 + "#" * 4 + "." * 17 + "#" * 8 + "." * 5,
"." * 21 + "#" * 7 + "." * 10 + "#" * 4 + "." * 17 + "#" * 8 + "." * 5,
"." * 22 + "#" * 6 + "." * 10 + "#" * 3 + "." * 19 + "#" * 6 + "." * 6,
"." * 22 + "#" * 5 + "." * 33 + "#" * 6 + "." * 6,
"." * 23 + "#" * 4 + "." * 45,
"." * 23 + "#" * 3 + "." * 46,
"." * 24 + "#" * 2 + "." * 42 + "#" * 2 + "." * 2,
"." * 24 + "#" * 2 + "." * 46,
"." * 68 + "#" + "." * 3,
"." * 72,
"." * 72,
"." * 72,
"." * 72,
"." * 72,
"." * 72,
]


def draw_map(x, y, cell, color, hot=None):
    """Draw dotted map; hot = list of (col, row) cells to draw in RED."""
    hot = set(hot or [])
    for r, row in enumerate(MAP):
        for c, ch in enumerate(row):
            if ch == '#':
                col = RED if (c, r) in hot else color
                circle(x + c * cell + cell // 2, y + r * cell + cell // 2,
                       max(1, cell // 2 - 1), col)


# ---- story icons: white pictogram on a coloured 44x44 tile ----
def tile(x, y, color):
    rect(x, y, 44, 44, color)


def icon_burst(x, y, color):
    tile(x, y, color)
    cx, cy = x + 22, y + 22
    for ang in range(0, 360, 30):
        import math
        a = math.radians(ang)
        line(cx, cy, cx + int(15 * math.cos(a)), cy + int(15 * math.sin(a)), WHITE)
    circle(cx, cy, 6, WHITE)


def icon_storm(x, y, color):
    tile(x, y, color)
    circle(x + 16, y + 16, 7, WHITE)
    circle(x + 26, y + 14, 8, WHITE)
    circle(x + 30, y + 20, 6, WHITE)
    rect(x + 10, y + 20, 26, 6, WHITE)
    tri(x + 24, y + 26, x + 18, y + 40, x + 24, y + 40, WHITE)
    tri(x + 20, y + 26, x + 26, y + 40, x + 20, y + 40, WHITE)


def icon_bars(x, y, color):
    tile(x, y, color)
    rect(x + 9, y + 28, 6, 9, WHITE)
    rect(x + 19, y + 20, 6, 17, WHITE)
    rect(x + 29, y + 12, 6, 25, WHITE)
    line(x + 7, y + 38, x + 38, y + 38, WHITE)


def icon_target(x, y, color):
    tile(x, y, color)
    circle(x + 22, y + 22, 13, WHITE, fillc=False)
    circle(x + 22, y + 22, 6, WHITE, fillc=False)
    circle(x + 22, y + 22, 2, WHITE)
    line(x + 22, y + 6, x + 22, y + 12, WHITE)
    line(x + 22, y + 32, x + 22, y + 38, WHITE)
    line(x + 6, y + 22, x + 12, y + 22, WHITE)
    line(x + 32, y + 22, x + 38, y + 22, WHITE)


def icon_flags(x, y, color):
    tile(x, y, color)
    line(x + 12, y + 8, x + 12, y + 38, WHITE)
    line(x + 30, y + 8, x + 30, y + 38, WHITE)
    rect(x + 12, y + 8, 12, 8, WHITE)
    rect(x + 30, y + 8, 12, 8, (197, 146, 44))
    line(x + 8, y + 38, x + 36, y + 38, WHITE)


def icon_ballot(x, y, color):
    tile(x, y, color)
    rect(x + 10, y + 18, 24, 18, WHITE)
    rect(x + 14, y + 12, 16, 5, WHITE)
    line(x + 16, y + 28, x + 21, y + 33, NAVY)
    line(x + 21, y + 33, x + 30, y + 22, NAVY)


def icon_mega(x, y, color):
    tile(x, y, color)
    tri(x + 8, y + 14, x + 8, y + 30, x + 30, y + 22, WHITE)
    rect(x + 30, y + 16, 6, 12, WHITE)
    line(x + 14, y + 32, x + 14, y + 38, WHITE)
    line(x + 20, y + 32, x + 20, y + 38, WHITE)


def icon_pawn(x, y, color):
    tile(x, y, color)
    circle(x + 22, y + 12, 6, WHITE)
    tri(x + 14, y + 36, x + 30, y + 36, x + 22, y + 18, WHITE)
    rect(x + 12, y + 36, 20, 4, WHITE)


def icon_ship(x, y, color):
    tile(x, y, color)
    tri(x + 8, y + 28, x + 36, y + 28, x + 32, y + 38, WHITE)
    rect(x + 12, y + 12, 8, 12, WHITE)
    rect(x + 22, y + 16, 8, 8, WHITE)
    line(x + 16, y + 6, x + 16, y + 12, WHITE)


def icon_factory(x, y, color):
    tile(x, y, color)
    rect(x + 8, y + 22, 14, 16, WHITE)
    rect(x + 24, y + 16, 12, 22, WHITE)
    rect(x + 28, y + 6, 4, 12, WHITE)
    circle(x + 30, y + 4, 3, (197, 146, 44))
    line(x + 8, y + 38, x + 38, y + 38, WHITE)


def icon_star(x, y, color):
    tile(x, y, color)
    cx, cy = x + 22, y + 22
    pts = []
    import math
    for i in range(10):
        a = math.radians(-90 + i * 36)
        r = 15 if i % 2 == 0 else 6
        pts.append((cx + int(r * math.cos(a)), cy + int(r * math.sin(a))))
    for i in range(10):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % 10]
        line(x0, y0, x1, y1, WHITE)
    circle(cx, cy, 3, WHITE)


def icon_tricolour(x, y, color):
    tile(x, y, color)
    rect(x + 10, y + 8, 8, 28, WHITE)
    rect(x + 18, y + 8, 8, 28, (197, 146, 44))
    rect(x + 26, y + 8, 8, 28, RED)


# ---- stories: 1 lead + 12 cards + 9 briefs + 1 sport = 23 ----
LEAD_KICKER = "LEAD - MIDDLE EAST"
LEAD_HEAD = "DRONE STRIKE KILLS TWO ITALIANS IN KUWAIT"
LEAD_DEK = ("Tehran denies any role as Rome demands answers after the strike "
            "kills two Italian workers.")
LEAD_FACT = "REPORTED 27 NOVEMBER - IRAN DENIES RESPONSIBILITY"

CARDS = [
    ("GAZA", "ISRAEL KILLS 10 IN GAZA",
     "Hamas weighs a reply; 16 schoolchildren killed this month.",
     icon_burst, RED),
    ("USA", "STORM CHAOS AT THANKSGIVING",
     "Macy's 100th parade postponed; 500,000+ lose power.",
     icon_storm, NAVY),
    ("MARKETS", "BLACK FRIDAY: $1 TRILLION IN SIGHT",
     "US holiday sales to top $1tn first time; $12.9bn online today.",
     icon_bars, GOLD),
    ("AFRICA", "300+ RUSSIANS KILLED IN MALI",
     "Moscow-backed forces suffer heavy losses supporting the junta.",
     icon_target, RED),
    ("S. AMERICA", "LULA SNUBS MILEI",
     "Brazil pulls its ambassador and bars Argentina's president from the inauguration.",
     icon_flags, TEAL),
    ("EUROPE", "UK MIGRATION AT 29-YEAR LOW",
     "Net migration falls to its lowest since 1997, outside the pandemic.",
     icon_ballot, NAVY),
    ("USA", "TRUMP CALLS GDP 'FAKE'",
     "President demands a probe after growth is revised up to 4.3%.",
     icon_mega, RED),
    ("CHESS", "GUKESH, SINDAROV DRAW MARATHON",
     "Game 3 of the world title match ends in a draw after a long fight.",
     icon_pawn, GOLD),
    ("EUROPE", "TANKER SINKS OFF IBIZA",
     "Diesel tanker carrying 7,000 tonnes capsizes; one crew member dead.",
     icon_ship, SKY),
    ("MIDDLE EAST", "REFINERY ATTACK IN SAUDI ARABIA",
     "Strike on the Jazan refinery kills a Nepali worker and injures several.",
     icon_factory, RED),
    ("OCEANIA", "NZ COALITION KEEPS 67 SEATS",
     "Final count confirms a slim majority after 400,000 special votes.",
     icon_star, TEAL),
    ("EUROPE", "FRANCE FACES VOTE DEBACLE",
     "Mainstream parties risk a presidential rout with no clear candidate.",
     icon_tricolour, NAVY),
]

BRIEFS = [
    "EBOLA IN CONGO PASSES 12,000 CASES AS UNREST DRIVES RESPONDERS OUT",
    "NEPAL DECLARES 4,000 MISSING LANDSLIDE VICTIMS DEAD",
    "EU LEADERS DISCUSS NEW FINANCIAL AID FOR UKRAINE",
    "NORTH KOREA'S KIM VOWS MORE NUCLEAR WEAPONS",
    "DEPARDIEU TO STAND TRIAL OVER ALLEGED 2018 RAPE",
    "INDIA'S TOP COURT RULES ON PMLA ATTACHMENT BENCH",
    "MUSK: EVERY US CHILD TO GET TWO SPACEX SHARES",
    "AUSTRALIA BRACES FOR A SEVERE BUSHFIRE SEASON",
    "BELGIUM OPENS EUROPE'S BIGGEST SATELLITE FACTORY",
]

SPORT = ("NEW ZEALAND 77-1 AT LUNCH, DAY ONE OF THE SECOND TEST V INDIA IN "
         "CHRISTCHURCH. THE BEARS STUNNED THE LIONS ON THANKSGIVING.")

NUMBERS = [
    ("$1.01T", "HOLIDAY SALES"),
    ("300+", "KILLED IN MALI"),
    ("12,000", "EBOLA CASES"),
    ("500K+", "WITHOUT POWER"),
    ("80M", "TRAVELLING"),
]

HOT = [(45, 12), (43, 12), (36, 15), (26, 20), (36, 8), (68, 27),
       (37, 10), (44, 15), (36, 9)]


def draw_masthead():
    rect(0, 0, W, 86, NAVY)
    rect(0, 86, W, 4, RED)
    center_text("THE WORLD", 12, 6, WHITE)
    center_text("FRIDAY, 27 NOVEMBER 2026 - THE WORLD'S NEWS IN ONE IMAGE",
                62, 2, (200, 205, 220))


def draw_lead_graphic(x, y, w, h):
    rect(x, y, w, h, NAVY)
    # skyline silhouette
    for bx, bw, bh in [(0, 26, 60), (28, 20, 90), (50, 24, 70), (76, 18, 110),
                       (96, 26, 80), (124, 20, 100), (146, 22, 64)]:
        rect(x + bx, y + h - bh - 18, bw, bh, (12, 20, 42))
    # windows
    for wy in range(y + h - 100, y + h - 20, 12):
        for wx in range(x + 4, x + w - 8, 12):
            if (wx * 7 + wy * 13) % 5 == 0:
                rect(wx, wy, 3, 4, GOLD)
    # drone + burst
    cx, cy = x + w - 44, y + 34
    circle(cx - 12, cy - 8, 4, WHITE)
    circle(cx + 12, cy - 8, 4, WHITE)
    circle(cx - 12, cy + 8, 4, WHITE)
    circle(cx + 12, cy + 8, 4, WHITE)
    rect(cx - 8, cy - 4, 16, 8, WHITE)
    line(cx - 12, cy - 8, cx + 12, cy + 8, WHITE)
    line(cx + 12, cy - 8, cx - 12, cy + 8, WHITE)
    circle(x + 30, y + 30, 10, (230, 90, 40))
    circle(x + 30, y + 30, 5, GOLD)
    rect(x, y + h - 18, w, 18, RED)
    center_text("KUWAIT - THE GULF", y + h - 14, 1, WHITE, x, x + w)


def draw_lead():
    draw_text(LEAD_KICKER, 8, 100, 2, RED)
    para(LEAD_HEAD, 8, 126, 444, 3, INK, leading=27)
    para(LEAD_DEK, 8, 188, 444, 2, INK, leading=18)
    draw_text(LEAD_FACT, 8, 252, 1, GREY)
    draw_lead_graphic(460, 98, 168, 194)


def draw_map_section():
    draw_text("THE WORLD ON 27 NOVEMBER", 636, 100, 2, NAVY)
    draw_map(660, 124, 4, NAVY, hot=HOT)
    center_text("SIX CONTINENTS - ONE DAY - 23 STORIES", 278, 1, GREY, 636, 1016)


def draw_cards():
    for i, (kicker, head, summary, icon, color) in enumerate(CARDS):
        cx = 8 + (i % 4) * 252
        cy = 312 + (i // 4) * 142
        rect(cx, cy, 244, 134, WHITE)
        rect(cx, cy, 244, 4, color)
        for bx in range(cx, cx + 244):
            px(bx, cy + 134, GREY)
        for by in range(cy, cy + 134):
            px(cx + 243, by, GREY)
        icon(cx + 8, cy + 12, color)
        draw_text(kicker, cx + 60, cy + 16, 1, RED)
        draw_text("27 NOV", cx + 60, cy + 30, 1, GREY)
        y = para(head, cx + 8, cy + 62, 228, 2, INK, leading=18)
        para(summary, cx + 8, y + 4, 228, 1, GREY, leading=10)


def draw_briefs():
    draw_text("IN BRIEF", 8, 738, 2, NAVY)
    hline(8, 1016, 760, NAVY)
    for i, b in enumerate(BRIEFS):
        bx = 8 + (i % 3) * 340
        by = 770 + (i // 3) * 48
        rect(bx, by + 2, 6, 6, RED)
        para(b, bx + 14, by, 312, 1, INK, leading=10)


def draw_footer():
    rect(0, 916, W, 100, NAVY)
    draw_text("SPORT", 16, 928, 2, RED)
    para(SPORT, 16, 948, 560, 2, WHITE, leading=18)
    vline(592, 928, 1004, (90, 100, 130))
    for i, (num, label) in enumerate(NUMBERS):
        nx = 608 + i * 82
        draw_text(num, nx, 928, 2, WHITE)
        para(label, nx, 950, 78, 1, (200, 205, 220), leading=10)


def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(buf[y * W * 3:(y + 1) * W * 3])
    comp = zlib.compress(bytes(raw), 6)

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", crc32(typ + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    fill(PAPER)
    draw_masthead()
    draw_lead()
    draw_map_section()
    hline(8, 1016, 300, NAVY)
    draw_cards()
    draw_briefs()
    draw_footer()
    out = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.getcwd()
    os.makedirs(out, exist_ok=True)
    write_png(os.path.join(out, "entry.png"))


if __name__ == "__main__":
    main()
