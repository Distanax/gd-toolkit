r"""Mode/speed/orb statistics for rated reference levels.

Usage: python analysis/analyze_refs.py [REFS_DIR]   (default: refs/, which is git-ignored;
the exported references live in C:\Work\ClaudeProjects\gd_levels\ref_*.gmd)
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # repo root, so `toolkit` imports when run directly

from toolkit.gdparse import load_gmd
import glob, collections, os
SPEEDP = {200:0.5, 201:1, 202:2, 203:3, 1334:4}
HDR_SPEED = {'0':1, '1':0.5, '2':2, '3':3, '4':4}
UPS = {0.5:251.16, 1:311.58, 2:387.42, 3:468.0, 4:576.0}
MODEP = {12:'cube',13:'ship',47:'ball',111:'ufo',660:'wave',745:'robot',1331:'spider',1933:'swing'}
HDR_MODE = {'0':'cube','1':'ship','2':'ball','3':'ufo','4':'wave','5':'robot','6':'spider','7':'swing'}
ORBS = {36:'yellow',84:'blue',141:'pink',1022:'green',1330:'black',1333:'red',1594:'toggle',1704:'greendash',1751:'pinkdash',3004:'spider',3027:'teleport'}
PADS = {35:'yellow',67:'blue',140:'pink',1332:'red',3005:'spider'}
GRAV = {10:'grav-normal',11:'grav-flip',2926:'grav-toggle'}
SIZE = {99:'normal-size',101:'mini'}
DUAL = {286:'dual-on',287:'dual-off'}
MIRROR={45:'mirror-on',46:'mirror-off'}
SPIKES = {8,39,103,392,9,61,243,244,366,367,368,446,447,667,989,991,720,421,422,1715,1714,1716,1717,1718,1719,1720,1721,1722,1723,1724,1725,1726,1727,1728,1729,1730,1731,1732,1733,135,177,178,179,1889,1890,1891,1892}
SAWS = {88,89,98,183,184,185,186,187,188,397,398,399,678,679,680,740,741,742,918,919,1582,1619,1620,1701,1702,1703,1705,1706,1707,1708,1709,1710,1734,1735,1736}

def timeline(hdr, objs):
    sp = sorted((o['_x'], SPEEDP[o['_id']]) for o in objs if o['_id'] in SPEEDP)
    speed = HDR_SPEED.get(hdr.get('kA4','0'),1)
    pts = [(0.0, 0.0, speed)]   # (x, t, speed from here)
    for x, s in sp:
        x0, t0, s0 = pts[-1]
        if x < x0: continue
        pts.append((x, t0 + (x - x0) / UPS[s0], s))
    def t_of(x):
        for i in range(len(pts)-1, -1, -1):
            if x >= pts[i][0]:
                x0, t0, s0 = pts[i]; return t0 + (x - x0) / UPS[s0]
        return 0
    return t_of, pts

def main(refs_dir='refs'):
    files = sorted(glob.glob(os.path.join(refs_dir, '*.gmd')))
    if not files:
        print(f'No reference levels in {refs_dir!r}: skipping analysis.')
        return
    for f in sorted(files):
        meta, hdr, objs = load_gmd(f)
        t_of, pts = timeline(hdr, objs)
        endx = max((o['_x'] for o in objs if o['_id'] in SPIKES|set(ORBS)|set(PADS)|set(MODEP)), default=0)
        print('='*90); print(meta['k2'], '| song', meta['k45'], '| start', HDR_MODE.get(hdr.get('kA2','0')), HDR_SPEED.get(hdr.get('kA4','0')), '| gameplay ends ~%.0fs' % t_of(endx))
        # events
        ev = []
        for o in objs:
            i = o['_id']
            for table in (MODEP, GRAV, SIZE, DUAL, MIRROR):
                if i in table: ev.append((t_of(o['_x']), table[i], o['_y']))
            if i in SPEEDP: ev.append((t_of(o['_x']), f'speed {SPEEDP[i]}x', o['_y']))
        ev.sort()
        # collapse duplicates within 0.05s
        last = None; out = []
        for t, name, y in ev:
            if last and abs(t - last[0]) < 0.05 and name == last[1]: continue
            out.append((t, name)); last = (t, name)
        print('  transitions:', ' | '.join(f'{t:.1f}s {n}' for t, n in out))
        c = collections.Counter()
        for o in objs:
            i = o['_id']
            if i in ORBS: c['orb:'+ORBS[i]] += 1
            elif i in PADS: c['pad:'+PADS[i]] += 1
            elif i in SPIKES: c['spike'] += 1
            elif i in SAWS: c['saw'] += 1
        print('  counts:', dict(c))

    print('\n\nSEGMENT STATS (mode or speed change = new segment)')
    import statistics
    for f in sorted(files):
        meta, hdr, objs = load_gmd(f)
        t_of, pts = timeline(hdr, objs)
        endx = max((o['_x'] for o in objs if o['_id'] in SPIKES|set(ORBS)|set(PADS)|set(MODEP)), default=0)
        T = t_of(endx)
        ts = sorted({round(t_of(o['_x']),1) for o in objs if o['_id'] in MODEP or o['_id'] in SPEEDP})
        ts = [t for t in ts if 0.5 < t < T]
        # merge changes within 0.3s
        m=[]
        for t in ts:
            if not m or t-m[-1]>0.3: m.append(t)
        segs=[b-a for a,b in zip([0]+m, m+[T])]
        modes = collections.Counter(MODEP[o['_id']] for o in objs if o['_id'] in MODEP)
        inter = [t_of(o['_x']) for o in objs if o['_id'] in ORBS or o['_id'] in PADS]
        print(f"{meta['k2']:18s} len {T:5.1f}s  segments {len(segs):3d}  median {statistics.median(segs):4.1f}s  max {max(segs):4.1f}s  orbs+pads/s {len(inter)/T:4.2f}  modes {dict(modes)}")


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'refs')
