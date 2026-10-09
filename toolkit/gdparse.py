import re, base64, gzip, zlib, html
def load_gmd(path):
    s = open(path, encoding='utf-8', errors='replace').read()
    def tag(k):
        m = re.search(r'<k>%s</k><(\w+)>(.*?)</\1>' % k, s, re.S)
        return html.unescape(m.group(2)) if m else None
    raw = tag('k4')
    meta = {k: tag(k) for k in ('k2', 'k45', 'k8', 'k1')}
    data = raw.strip()
    if data.startswith('H4sI') or data.startswith('eJ'):
        b = base64.urlsafe_b64decode(data + '=' * (-len(data) % 4))
        try: data = gzip.decompress(b).decode()
        except Exception: data = zlib.decompress(b).decode()
    parts = data.split(';')
    header = parts[0]
    objs = []
    for p in parts[1:]:
        if not p: continue
        f = p.split(',')
        o = {}
        for i in range(0, len(f) - 1, 2):
            o[f[i]] = f[i + 1]
        try:
            o['_id'] = int(o.get('1', 0)); o['_x'] = float(o.get('2', 0)); o['_y'] = float(o.get('3', 0))
        except ValueError:
            continue
        objs.append(o)
    hd = header.split(',')
    hdr = {hd[i]: hd[i + 1] for i in range(0, len(hd) - 1, 2)}
    return meta, hdr, objs
