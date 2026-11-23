"""Wiki lint：壞連結、壞錨點、孤兒頁、未列入 index、無出處數字（啟發式）、過時標記。
用法：python3 tools/lint.py [repo 根目錄]
"""
import re, os, sys, collections
root = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))); wiki = os.path.join(root, 'wiki')
pages = {}
for d, _, fs in os.walk(wiki):
    for f in fs:
        if f.endswith('.md'):
            p = os.path.join(d, f); pages[os.path.relpath(p, wiki)] = open(p, encoding='utf-8').read()
link_re = re.compile(r'\]\(([^)#\s]+\.md)(#[^)]*)?\)')
inbound = collections.Counter(); broken = []; badanchor = []
def slug(h):
    h = h.strip().lower()
    h = re.sub(r'[^\w一-鿿\- ]', '', h)
    return h.replace(' ', '-')
heads = {k: {slug(m) for m in re.findall(r'^#+\s+(.*)$', v, re.M)} for k, v in pages.items()}
for src, txt in pages.items():
    for m in link_re.finditer(txt):
        tgt = os.path.normpath(os.path.join(os.path.dirname(src), m.group(1)))
        if tgt not in pages: broken.append((src, m.group(1)))
        else:
            inbound[tgt] += 1
            if m.group(2) and m.group(2)[1:] not in heads[tgt]: badanchor.append((src, m.group(1)+m.group(2)))
print('== pages:', len(pages))
print('== broken links:'); [print('  ', s, '->', t) for s, t in sorted(set(broken))]
print('== bad anchors:'); [print('  ', s, '->', t) for s, t in sorted(set(badanchor))]
print('== orphans (no inbound except index/log):')
for p in sorted(pages):
    if p in ('index.md', 'log.md'): continue
    srcs = [s for s, t in pages.items() if s not in ('index.md','log.md') and re.search(re.escape(os.path.basename(p)), t)]
    if not srcs: print('  ', p)
print('== not in index:')
for p in sorted(pages):
    if p in ('index.md','log.md'): continue
    if p not in pages['index.md']: print('  ', p)
# numbers without a nearby source on the same line (heuristic)
src_re = re.compile(r'(Table|Fig\.|§|Eq\.|表|出處|來源|SECOND|PointPillars|PV-RCNN|Voxel R-CNN|CasA|NV3D|VoxelNeXt|LION|整理|README|附錄|A\.\d)')
print('== lines with 2-decimal numbers but no source marker:')
for p, t in sorted(pages.items()):
    if p == 'log.md': continue
    for i, line in enumerate(t.splitlines(), 1):
        if re.search(r'\d+\.\d\d', line) and not src_re.search(line) and not line.strip().startswith('|'):
            print(f'   {p}:{i}: {line.strip()[:110]}')

print('== stale markers (待 ingest / 待確認 / 待補 / 待查證):')
for p, t in sorted(pages.items()):
    if p == 'log.md': continue
    for i, line in enumerate(t.splitlines(), 1):
        if re.search(r'待\s*ingest|待確認|待補|待查證', line):
            print(f'   {p}:{i}: {line.strip()[:110]}')
