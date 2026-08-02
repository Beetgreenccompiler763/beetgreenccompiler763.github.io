# -*- coding: utf-8 -*-
"""يبني أغلفة المشاريع من لقطات الشاشة الحقيقية."""
from PIL import Image, ImageDraw, ImageFilter
import os, colorsys

# حط لقطات الشاشة الخام في فولدر اسمه screenshots جنب الملف ده
UP = "screenshots"
OUT = "."

# slug: (خلفية متدرجة), [(ملف, أعلى القص)]
JOBS = {
 "newshop": (("#e9ede0", "#b9c4a3"), [("94b9e910-1000119048.jpg", 252), ("409d42a8-1000119049.jpg", 68)]),
 "egyup":   (("#ece9fb", "#c3bbee"), [("63017bed-1000119050.jpg", 252), ("836bc64e-1000119051.jpg", 68)]),
 "noor":    (("#f0e6ee", "#c9a8c0"), [("a77d3534-1000119045.jpg", 252)]),
 "selim":   (("#efe2d6", "#c49a72"), [("78c8b5fd-1000119046.jpg", 252), ("13959cf5-1000119047.jpg", 68)]),
 "natiga":  (("#f2ead9", "#cdbb98"), [("386454a6-1000118958.jpg", 100)]),
 "book":    (("#efe4d4", "#c0a279"), [("75b21287-1000119043.jpg", 252), ("bf68ecfc-1000119044.jpg", 252)]),
}

W, H = 2400, 1500
BOTTOM_CROP = 2496          # فوق شريط الإيماءات
BEZEL = 14                  # سُمك إطار الجهاز
RADIUS = 34


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def gradient(size, c1, c2):
    """تدرّج قطري ناعم."""
    w, h = size
    small = Image.new("RGB", (w // 8, h // 8))
    px = small.load()
    a, b = hexrgb(c1), hexrgb(c2)
    sw, sh = small.size
    for y in range(sh):
        for x in range(sw):
            t = (x / sw * 0.55 + y / sh * 0.45)
            px[x, y] = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
    return small.resize((w, h), Image.BICUBIC)


def rounded(img, r):
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, img.size[0] - 1, img.size[1] - 1], r, fill=255)
    out = img.convert("RGBA")
    out.putalpha(mask)
    return out


def device(shot, target_h):
    """يلف اللقطة في إطار جهاز داكن بحواف دائرية."""
    scr_h = target_h - BEZEL * 2
    scr_w = int(shot.width * scr_h / shot.height)
    screen = rounded(shot.resize((scr_w, scr_h), Image.LANCZOS), RADIUS - 5)

    frame = Image.new("RGBA", (scr_w + BEZEL * 2, target_h), (0, 0, 0, 0))
    body = Image.new("RGB", frame.size, (28, 25, 22))
    frame.paste(rounded(body, RADIUS), (0, 0))
    frame.paste(screen, (BEZEL, BEZEL), screen)
    return frame


def shadow(size, r, blur=46, alpha=118):
    s = Image.new("RGBA", (size[0] + blur * 3, size[1] + blur * 3), (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle(
        [blur * 1.5, blur * 1.5, blur * 1.5 + size[0], blur * 1.5 + size[1]], r, fill=(24, 18, 12, alpha))
    return s.filter(ImageFilter.GaussianBlur(blur))


for slug, (colors, shots) in JOBS.items():
    src = []
    for fname, top in shots:
        p = os.path.join(UP, fname)
        if not os.path.exists(p):
            print("!! missing", fname)
            continue
        im = Image.open(p).convert("RGB")
        src.append(im.crop((0, top, im.width, min(BOTTOM_CROP, im.height))))
    if not src:
        continue

    canvas = gradient((W, H), *colors).convert("RGBA")
    # وهج ناعم أعلى اليسار
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([-460, -560, 1180, 700], fill=(255, 255, 255, 62))
    canvas = Image.alpha_composite(canvas, glow.filter(ImageFilter.GaussianBlur(190)))

    if len(src) == 2:
        h_back, h_front = 1130, 1252
        back = device(src[1], h_back)
        front = device(src[0], h_front)
        gap = 54
        total = back.width + front.width + gap
        x0 = (W - total) // 2
        # الخلفي (يسار), الأمامي (يمين) — الترتيب البصري لـRTL
        for img, x, y, a in [(back, x0, (H - h_back) // 2 + 30, 96),
                             (front, x0 + back.width + gap, (H - h_front) // 2, 128)]:
            sh = shadow(img.size, RADIUS, alpha=a)
            canvas.alpha_composite(sh, (x - (sh.width - img.width) // 2,
                                        y - (sh.height - img.height) // 2 + 34))
            canvas.alpha_composite(img, (x, y))
    else:
        h = 1290
        d = device(src[0], h)
        x, y = (W - d.width) // 2, (H - h) // 2
        sh = shadow(d.size, RADIUS, alpha=130)
        canvas.alpha_composite(sh, (x - (sh.width - d.width) // 2,
                                    y - (sh.height - d.height) // 2 + 38))
        canvas.alpha_composite(d, (x, y))

    rgb = canvas.convert("RGB")
    rgb.resize((1600, 1000), Image.LANCZOS).save(f"{OUT}/cover-{slug}.webp", "WEBP", quality=88, method=6)
    rgb.resize((880, 550), Image.LANCZOS).save(f"{OUT}/thumb-{slug}.webp", "WEBP", quality=84, method=6)
    print("✓", slug, len(src), "shot(s)",
          os.path.getsize(f"{OUT}/cover-{slug}.webp") // 1024, "KB")
