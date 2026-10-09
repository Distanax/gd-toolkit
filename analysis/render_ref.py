"""Strip render of a reference level between two times.

Usage: python analysis/render_ref.py LEVEL.gmd T0 T1 OUT.png
"""
import sys, os, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # repo root, so `toolkit` imports when run directly
from PIL import Image, ImageDraw
from analysis.analyze_refs import *  # noqa: timeline + object-ID tables
def render_ref(path, t0, t1, out, scale=0.3, ymax=480):
    meta, hdr, objs = load_gmd(path)
    t_of, pts = timeline(hdr, objs)
    sel = [o for o in objs if t0 <= t_of(o['_x']) <= t1 and -60 <= o['_y'] <= ymax + 60]
    xs = [o['_x'] for o in sel]
    x0, x1 = min(xs), max(xs)
    W, H = int((x1 - x0) * scale) + 40, int(ymax * scale) + 40
    img = Image.new('RGB', (W, H), (20, 20, 28)); d = ImageDraw.Draw(img)
    X = lambda x: 20 + (x - x0) * scale; Y = lambda y: H - 20 - y * scale
    d.line([0, Y(0), W, Y(0)], fill=(90, 90, 110))
    # second markers
    s = int(t0) + 1
    for o in sorted(sel, key=lambda o: o['_x']):
        pass
    tx = []
    lastsec = None
    for o in sorted(objs, key=lambda o: o['_x']):
        t = t_of(o['_x'])
        if t0 <= t <= t1 and int(t) != lastsec:
            lastsec = int(t); d.line([X(o['_x']), 0, X(o['_x']), H], fill=(40, 40, 55)); d.text((X(o['_x']) + 2, 2), f'{lastsec}s', fill=(130, 130, 150))
    r = 15 * scale
    for o in sel:
        i, x, y = o['_id'], X(o['_x']), Y(o['_y'])
        if i in SPIKES: d.polygon([(x - r, y + r), (x + r, y + r), (x, y - r)], fill=(255, 60, 60))
        elif i in SAWS: d.ellipse([x - r * 1.5, y - r * 1.5, x + r * 1.5, y + r * 1.5], outline=(255, 60, 60))
        elif i in ORBS: d.ellipse([x - r, y - r, x + r, y + r], fill={'yellow': (255, 230, 0), 'blue': (60, 160, 255), 'pink': (255, 100, 220), 'green': (60, 255, 90), 'black': (200, 200, 200), 'red': (255, 120, 0)}.get(ORBS[i], (255, 255, 255)))
        elif i in PADS: d.rectangle([x - r, y + r * 0.4, x + r, y + r], fill={'yellow': (255, 230, 0), 'blue': (60, 160, 255), 'pink': (255, 100, 220), 'red': (255, 120, 0)}.get(PADS[i], (255, 255, 255)))
        elif i in MODEP or i in SPEEDP or i in GRAV or i in SIZE or i in DUAL:
            d.rectangle([x - r * .4, y - r * 2, x + r * .4, y + r * 2], outline=(80, 255, 140), width=2)
            d.text((x - 8, y - r * 2 - 12), (MODEP.get(i) or (f"{SPEEDP[i]}x" if i in SPEEDP else (GRAV.get(i) or SIZE.get(i) or DUAL.get(i))))[:6], fill=(80, 255, 140))
        elif i == 1 or (o.get('_id') in range(1, 9)) or i in (2, 3, 4, 5, 6, 7, 40, 62, 63, 64, 65, 66, 68, 195, 196, 467, 468, 469, 470, 471, 1203, 1204, 1205, 1206):
            d.rectangle([x - r, y - r, x + r, y + r], outline=(200, 200, 220))
        else:
            d.point((x, y), fill=(70, 70, 90))
    img.save(out); return out, W, H
if __name__ == '__main__':
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    p, t0, t1, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
    if not os.path.exists(p):
        print(f'Reference level {p!r} not found (refs/*.gmd are not in the repo): skipping render.')
        sys.exit(0)
    print(render_ref(p, t0, t1, out))
