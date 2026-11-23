"""兩階段檢查：
1. facts.md 的每個數字都必須出現在它標示的 wiki 頁（事實 ← wiki）。
2. index.html 中每個帶小數點的數字、以及 data-fact 標註的數字，都必須出現在 facts.md（簡報 ← 事實）。
用法：python3 slides/check_facts.py [--html slides/index.html]
"""
import re, sys, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACTS = os.path.join(ROOT, 'slides', 'facts.md')
WIKI = os.path.join(ROOT, 'wiki')


def norm(s):
    # 統一負號與空白，方便比對
    return s.replace('−', '-').replace(' ', ' ')


def load_facts():
    rows = []
    for line in open(FACTS, encoding='utf-8'):
        if not re.match(r'\|\s*F\d+', line):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        fid, claim, nums, page, src = cells[:5]
        rows.append((fid, claim, [n.strip() for n in nums.split(';') if n.strip()], page, src))
    return rows


def check_facts_vs_wiki(rows):
    errors = 0
    for fid, claim, nums, page, src in rows:
        path = os.path.join(WIKI, page)
        if not os.path.exists(path):
            print(f'[FAIL] {fid}: wiki 頁不存在 {page}')
            errors += 1
            continue
        text = norm(open(path, encoding='utf-8').read())
        for n in nums:
            if norm(n) not in text:
                print(f'[FAIL] {fid}: 「{n}」不在 {page}')
                errors += 1
    return errors


def check_html_vs_facts(rows, html_path):
    fact_nums = set()
    for _, _, nums, _, _ in rows:
        for n in nums:
            fact_nums.update(re.findall(r'\d+\.\d+', norm(n)))
    raw = open(html_path, encoding='utf-8').read()
    # 去掉 <style> 與 <script> 中非資料的部分：script 內的資料陣列也要檢查，所以只去 style
    body = re.sub(r'<style.*?</style>', '', raw, flags=re.S)
    # 忽略 CSS / SVG 幾何屬性中的數字
    body = re.sub(r'\s(?:d|viewBox|points|transform|x|y|x1|x2|y1|y2|cx|cy|r|rx|width|height|stroke-width|opacity|offset|font-size|stop-opacity)="[^"]*"', ' ', body)
    # script 中只檢查標了 /*fact*/ 的資料區塊
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', body, flags=re.S)
    body_noscript = re.sub(r'<script.*?</script>', '', body, flags=re.S)
    text = html.unescape(re.sub(r'<[^>]+>', ' ', body_noscript))
    data_blocks = []
    for s in scripts:
        data_blocks += re.findall(r'/\*fact\*/(.*?)/\*end\*/', s, flags=re.S)
    scan = norm(text) + ' ' + ' '.join(data_blocks)
    scan = re.sub(r'§\s*[\dA-Z.\-]+', ' ', scan)  # 章節編號（§3.1.3、§IV-A1）不是資料
    candidates = re.findall(r'\d+\.\d+', scan)
    allow = {'1.0', '2.0'}  # 非資料用途（如「LiDAR 2.0」等）時才加入
    errors = 0
    seen = set()
    for c in candidates:
        if c in fact_nums or c in allow or c in seen:
            continue
        seen.add(c)
        print(f'[FAIL] 簡報中的數字 {c} 不在 facts.md')
        errors += 1
    # 每頁投影片必須有出處註記
    slides = re.findall(r'<section class="slide[^"]*"(.*?)</section>', raw, flags=re.S)
    for i, s in enumerate(slides, 1):
        if re.search(r'\d+\.\d+', re.sub(r'<script.*?</script>', '', s, flags=re.S)) and 'class="src"' not in s:
            print(f'[FAIL] 第 {i} 頁有數字但沒有出處註記（class="src"）')
            errors += 1
    return errors, len(slides)


if __name__ == '__main__':
    rows = load_facts()
    e1 = check_facts_vs_wiki(rows)
    print(f'事實 ← wiki：{len(rows)} 條事實，{e1} 個錯誤')
    if '--html' in sys.argv:
        hp = sys.argv[sys.argv.index('--html') + 1]
        e2, n = check_html_vs_facts(rows, hp)
        print(f'簡報 ← 事實：{n} 頁投影片，{e2} 個錯誤')
        e1 += e2
    sys.exit(1 if e1 else 0)
