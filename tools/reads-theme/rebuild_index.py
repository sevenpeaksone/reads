import os, re, html, math, json, shutil

# 사이트 루트. 데일리 태스크는 /tmp/blog 에 clone 후 실행한다.
SITE = os.environ.get("SITE", "/tmp/blog")
# GitHub Pages 서브경로(절대 링크용). 루트 배포면 "" 로.
BASE_URL = "/reads"
# GoatCounter 방문자 수 코드. 가입 후 받은 코드(예: "sevenpeaks")만 넣으면 활성화된다.
# 비워두면 방문자 수 기능은 표시되지 않는다.
GOATCOUNTER_CODE = os.environ.get("GOATCOUNTER_CODE", "sevenpeaks")
READS_THEME_VERSION = "lime-v1"
THEME_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(THEME_DIR, "reads_theme.css"), encoding="utf-8") as theme_file:
    READS_THEME_CSS = theme_file.read()
CAT_ORDER = [("IT", "it"), ("과학", "science"), ("경제", "economy"), ("바이오", "bio"),
             ("철학/인문", "philosophy"), ("상담", "counseling"), ("세계", "world"), ("종교", "religion")]
CAT_NAME = {slug: name for name, slug in CAT_ORDER}

# 뉴스(해설) 섹션 — 블로그와 분리. /news/<slug>/ 아래에 게시.
NEWS_ORDER = [("경제", "economy"), ("정치/사회", "politics"),
              ("국제/세계", "world"), ("산업·IT/과학", "industry")]

HOME_PER_CAT = 5   # 홈에서 카테고리별로 보여줄 최신 글 수 (그리드 5열 = 한 줄)
CAT_PER_PAGE = 12  # 카테고리 보관 페이지 1장당 글 수

# 7Peaks 로고 (SVG 벡터 재현 — 다크 테마 네온 시안). /assets/logo.png 로 저장.
LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 104" fill="none" role="img" aria-label="7Peaks">
  <defs>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="1.7" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <g filter="url(#glow)" stroke="#5fe3f2" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" fill="none">
    <path d="M60 9 L110 95 L10 95 Z"/>
    <path d="M60 33 L90 85 L30 85 Z"/>
    <path d="M46 50 H74 L57 85"/>
  </g>
  <g fill="#9af0fb">
    <circle cx="60" cy="9" r="4"/><circle cx="110" cy="95" r="4"/><circle cx="10" cy="95" r="4"/>
    <circle cx="35" cy="52" r="4"/><circle cx="85" cy="52" r="4"/><circle cx="60" cy="95" r="4"/>
  </g>
</svg>"""

# 웹폰트(Pretendard) — OS 무관하게 일정한 한글 렌더링
FONT_LINK = ('<link rel="stylesheet" '
             'href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@latest/dist/web/static/pretendard-dynamic-subset.css">')

# ---------------------------------------------------------------- 목록 스타일
CSS = """
  :root { --bg:#0f1117; --card:#1a1d27; --line:#2a2e3a; --text:#e8eaf0; --muted:#9aa0ad;
    --it:#4f8cff; --philosophy:#b07cff; --economy:#2bb673; --bio:#ff7c7c; --counseling:#f0a532;
    --science:#20c4cf; --world:#c2883f; --religion:#6f86d6;
    --politics:#e0667a; --industry:#3fb6a8; }
  * { box-sizing:border-box; }
  body { margin:0; font-family:'Pretendard','Pretendard Variable','Apple SD Gothic Neo','Malgun Gothic',sans-serif;
    background:var(--bg); color:var(--text); -webkit-font-smoothing:antialiased; }
  a { color:inherit; }
  .hero { text-align:center; padding:64px 20px 44px; border-bottom:1px solid var(--line);
    background:linear-gradient(160deg,#161a2b,#0f1117); }
  .hero.sub { padding:46px 20px 32px; }
  .hero h1 { margin:0; font-size:34px; font-weight:800; letter-spacing:-.6px; }
  .hero.sub h1 { font-size:24px; }
  .hero h1 a { text-decoration:none; }
  .hero p { margin:12px 0 0; color:var(--muted); font-size:15px; }
  main { max-width:1200px; margin:0 auto; padding:36px 20px 80px; }
  .cat-section { margin-bottom:46px; }
  .cat-bar { display:flex; align-items:center; justify-content:space-between; margin:0 0 18px; }
  .cat-head { font-size:15px; font-weight:700; display:inline-block; padding:5px 14px;
    border-radius:20px; color:#fff; background:#3a4050; }
  .cat-head[data-cat=news]{background:#e0667a;}
  .cat-head[data-cat=blog]{background:#4f8cff;}
  .cat-head[data-cat=it]{background:var(--it);}
  .cat-head[data-cat=philosophy]{background:var(--philosophy);}
  .cat-head[data-cat=economy]{background:var(--economy);}
  .cat-head[data-cat=bio]{background:var(--bio);}
  .cat-head[data-cat=counseling]{background:var(--counseling);}
  .cat-head[data-cat=science]{background:var(--science);}
  .cat-head[data-cat=world]{background:var(--world);}
  .cat-head[data-cat=religion]{background:var(--religion);}
  .cat-head[data-cat=politics]{background:var(--politics);}
  .cat-head[data-cat=industry]{background:var(--industry);}
  .more-link { font-size:13px; color:var(--muted); text-decoration:none; white-space:nowrap; }
  .more-link:hover { color:var(--text); }
  .back { display:inline-block; margin-bottom:22px; color:var(--muted); text-decoration:none; font-size:14px; }
  .back:hover { color:var(--text); }

  /* 카드 그리드 (홈: 한 줄 5개 / 자동 반응형) */
  .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr)); gap:18px; }
  .card { display:flex; flex-direction:column; background:var(--card); border:1px solid var(--line);
    border-radius:14px; overflow:hidden; text-decoration:none; color:var(--text);
    transition:transform .14s ease, border-color .14s, box-shadow .14s; }
  .card:hover { transform:translateY(-4px); border-color:#3a4050; box-shadow:0 12px 30px rgba(0,0,0,.38); }
  .thumb { width:100%; aspect-ratio:16/10; object-fit:cover; display:block; background:#11141d; }
  .thumb.ph { display:flex; align-items:center; justify-content:center; }
  .thumb.ph span { font-weight:800; color:#fff; font-size:20px; letter-spacing:-.3px; opacity:.92; }
  .thumb.ph[data-cat=it]{background:linear-gradient(135deg,#1b2140,var(--it));}
  .thumb.ph[data-cat=philosophy]{background:linear-gradient(135deg,#241b40,var(--philosophy));}
  .thumb.ph[data-cat=economy]{background:linear-gradient(135deg,#10301f,var(--economy));}
  .thumb.ph[data-cat=bio]{background:linear-gradient(135deg,#3a1b1b,var(--bio));}
  .thumb.ph[data-cat=counseling]{background:linear-gradient(135deg,#3a2c12,var(--counseling));}
  .thumb.ph[data-cat=science]{background:linear-gradient(135deg,#10302f,var(--science));}
  .thumb.ph[data-cat=world]{background:linear-gradient(135deg,#2e2410,var(--world));}
  .thumb.ph[data-cat=religion]{background:linear-gradient(135deg,#191f3a,var(--religion));}
  .thumb.ph[data-cat=politics]{background:linear-gradient(135deg,#3a1820,var(--politics));}
  .thumb.ph[data-cat=industry]{background:linear-gradient(135deg,#10302c,var(--industry));}
  .card-body { padding:13px 15px 15px; display:flex; flex-direction:column; gap:8px; flex:1; }
  .badge { align-self:flex-start; font-size:11px; font-weight:700; color:#fff; padding:3px 10px; border-radius:20px; }
  .badge[data-cat=it]{background:var(--it);}
  .badge[data-cat=philosophy]{background:var(--philosophy);}
  .badge[data-cat=economy]{background:var(--economy);}
  .badge[data-cat=bio]{background:var(--bio);}
  .badge[data-cat=counseling]{background:var(--counseling);}
  .badge[data-cat=science]{background:var(--science);}
  .badge[data-cat=world]{background:var(--world);}
  .badge[data-cat=religion]{background:var(--religion);}
  .badge[data-cat=politics]{background:var(--politics);}
  .badge[data-cat=industry]{background:var(--industry);}
  .card-title { margin:0; font-size:15px; font-weight:600; line-height:1.45;
    display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
  .card-date { margin-top:auto; font-size:12px; color:var(--muted); }

  .pager { display:flex; flex-wrap:wrap; gap:8px; justify-content:center; margin-top:40px; }
  .pager a, .pager span { min-width:38px; text-align:center; padding:8px 12px; border-radius:9px;
    border:1px solid var(--line); font-size:14px; text-decoration:none; color:var(--text); background:var(--card); }
  .pager a:hover { border-color:#3a4050; }
  .pager .cur { background:#3a4050; border-color:#3a4050; font-weight:700; }
  .pager .dots { border:none; background:none; color:var(--muted); min-width:auto; padding:8px 4px; }

  /* 상단 카테고리 탭 + 검색 */
  .topnav { position:sticky; top:0; z-index:50; display:flex; align-items:center; gap:14px; flex-wrap:wrap;
    padding:10px 20px; background:rgba(15,17,23,.92); -webkit-backdrop-filter:blur(8px); backdrop-filter:blur(8px);
    border-bottom:1px solid var(--line); }
  .topnav .tn-brand { display:inline-flex; align-items:center; gap:9px; font-weight:800; font-size:16px;
    text-decoration:none; letter-spacing:-.3px; }
  .topnav .tn-logo { height:28px; width:auto; display:block; }
  .hero-logo { height:76px; width:auto; display:block; margin:0 auto 16px;
    filter:drop-shadow(0 0 12px rgba(95,227,242,.4)); }
  .topnav .tn-cats { display:flex; gap:4px; flex-wrap:wrap; }
  .topnav .tn-cats a { font-size:14px; text-decoration:none; color:var(--muted); padding:5px 10px; border-radius:8px; }
  .topnav .tn-cats a:hover { color:var(--text); background:var(--card); }
  .topnav #site-search { margin-left:auto; background:var(--card); border:1px solid var(--line); border-radius:9px;
    color:var(--text); padding:8px 12px; font-size:14px; min-width:150px; outline:none;
    font-family:inherit; }
  .topnav #site-search:focus { border-color:#3a4050; }
  #search-meta { color:var(--muted); font-size:14px; margin:0 0 18px; }

  footer { text-align:center; color:var(--muted); font-size:13px; padding:24px; border-top:1px solid var(--line); }
  .visit { margin-bottom:6px; font-size:12px; color:var(--muted); }
  .visit b { color:var(--text); font-weight:700; }

  /* 즐겨찾기 별 버튼 (카드 위) */
  .card { position:relative; }
  .fav { position:absolute; top:9px; right:9px; z-index:3; width:30px; height:30px; border-radius:50%;
    display:flex; align-items:center; justify-content:center; cursor:pointer; font-size:16px; line-height:1;
    color:#ffd24a; background:rgba(15,17,23,.62); border:1px solid rgba(255,255,255,.14);
    -webkit-backdrop-filter:blur(3px); backdrop-filter:blur(3px); transition:transform .12s, background .12s; }
  .fav:hover { transform:scale(1.12); background:rgba(15,17,23,.85); }
  .fav.on { background:#ffd24a; color:#1a1d27; border-color:#ffd24a; }

  /* 보기 설정 + 페이지당 카드수 컨트롤 바 */
  .prefs { display:flex; align-items:center; gap:14px; flex-wrap:wrap; margin:0 0 22px; }
  .prefs .seg { display:inline-flex; border:1px solid var(--line); border-radius:9px; overflow:hidden; }
  .prefs .seg button { background:var(--card); color:var(--muted); border:none; padding:7px 15px;
    font-size:13px; cursor:pointer; font-family:inherit; }
  .prefs .seg button.on { background:#3a4050; color:#fff; font-weight:700; }
  .prefs label { display:inline-flex; align-items:center; gap:7px; color:var(--muted); font-size:13px; }
  .prefs select { background:var(--card); border:1px solid var(--line); color:var(--text);
    border-radius:8px; padding:6px 10px; font-size:13px; font-family:inherit; outline:none; }
  .prefs .grow { margin-left:auto; }
  .prefs .fav-link { color:var(--muted); text-decoration:none; font-size:13px; }
  .prefs .fav-link:hover { color:#ffd24a; }

  /* 목록형 보기 */
  .grid.view-list { display:block; }
  .grid.view-list .card { flex-direction:row; margin-bottom:12px; align-items:stretch; }
  .grid.view-list .thumb { width:170px; flex:0 0 170px; height:auto; aspect-ratio:16/10; }
  .grid.view-list .thumb.ph { aspect-ratio:16/10; }
  .grid.view-list .card-body { flex:1; }
  .grid.view-list .card-title { -webkit-line-clamp:3; }
  @media(max-width:560px){ .grid.view-list .thumb{ width:110px; flex-basis:110px; } }

  #fav-empty { color:var(--muted); font-size:15px; padding:30px 0; }
  .fav-tools { display:flex; align-items:center; gap:10px; margin:0 0 18px; flex-wrap:wrap; }
  .fav-tools button { background:var(--card); color:var(--text); border:1px solid var(--line);
    border-radius:9px; padding:8px 14px; font-size:13px; cursor:pointer; font-family:inherit; }
  .fav-tools button:hover { border-color:#3a4050; }
  .fav-tools #fav-msg { color:var(--muted); font-size:13px; }

  /* ── 뉴스 전용: 헤드라인 리스트 (블로그 카드와 다른, 신문 느낌) */
  .news-list { display:flex; flex-direction:column; border-top:2px solid #e0667a; }
  .news-item { position:relative; display:flex; gap:16px; align-items:center;
    padding:15px 8px 15px 4px; border-bottom:1px solid var(--line);
    text-decoration:none; color:var(--text); transition:background .12s; }
  .news-item:hover { background:var(--card); }
  .news-thumb { width:108px; height:72px; flex:0 0 108px; border-radius:8px;
    object-fit:cover; background:#11141d; }
  .news-thumb.ph { display:flex; align-items:center; justify-content:center;
    color:#fff; font-weight:800; font-size:13px; text-align:center; padding:4px; }
  .news-thumb.ph[data-cat=economy]{background:linear-gradient(135deg,#10301f,var(--economy));}
  .news-thumb.ph[data-cat=politics]{background:linear-gradient(135deg,#3a1820,var(--politics));}
  .news-thumb.ph[data-cat=world]{background:linear-gradient(135deg,#2e2410,var(--world));}
  .news-thumb.ph[data-cat=industry]{background:linear-gradient(135deg,#10302c,var(--industry));}
  .news-body { flex:1; min-width:0; display:flex; flex-direction:column; gap:7px; }
  .news-meta { display:flex; align-items:center; gap:10px; font-size:12px; }
  .news-cat { color:#fff; padding:2px 9px; border-radius:4px; font-weight:700; font-size:11px;
    letter-spacing:.2px; background:#3a4050; }
  .news-cat[data-cat=economy]{background:var(--economy);}
  .news-cat[data-cat=politics]{background:var(--politics);}
  .news-cat[data-cat=world]{background:var(--world);}
  .news-cat[data-cat=industry]{background:var(--industry);}
  .news-time { color:var(--muted); }
  .news-time::before { content:"● "; color:#e0667a; font-size:9px; vertical-align:middle; }
  .news-title { font-size:16.5px; font-weight:700; line-height:1.42; letter-spacing:-.2px;
    display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
  .news-item:hover .news-title { color:#fff; }
  .news-item .fav { top:12px; right:6px; }
  @media(max-width:560px){ .news-thumb{ width:82px; flex-basis:82px; height:58px; } .news-title{ font-size:15px; } }
"""


CSS += "\n" + READS_THEME_CSS


def get_title(p):
    try:
        t = open(p, encoding="utf-8").read()
        m = re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S) or re.search(r"<title[^>]*>(.*?)</title>", t, re.S)
        if m:
            return re.sub(r"<[^>]+>", "", m.group(1)).strip()
    except Exception:
        pass
    return "(제목 없음)"


def fmt_label(slot):
    m = re.match(r"(\d{4}-\d{2}-\d{2})-(\d{2})", slot)
    return f"{m.group(1)} {m.group(2)}시" if m else slot


def collect(cat_order=CAT_ORDER, base_dir="posts"):
    data = []
    for cat, cslug in cat_order:
        base = os.path.join(SITE, base_dir, cslug)
        items = []
        if os.path.isdir(base):
            for d in sorted(os.listdir(base), reverse=True):
                idx = os.path.join(base, d, "index.html")
                if os.path.isfile(idx):
                    thumb_ok = os.path.isfile(os.path.join(base, d, "images", "thumbnail.png"))
                    items.append({"slot": d, "title": get_title(idx),
                                  "label": fmt_label(d), "thumb_ok": thumb_ok})
        data.append((cat, cslug, items))
    return data


def card(it, href, thumb_href, cat, cslug, id_prefix=""):
    if it["thumb_ok"]:
        cover = f'<img class="thumb" src="{thumb_href}" alt="{html.escape(it["title"])}" loading="lazy">'
    else:
        cover = f'<div class="thumb ph" data-cat="{cslug}"><span>{html.escape(cat)}</span></div>'
    fav_id = f"{id_prefix}{cslug}/{it['slot']}"
    return ('      <a class="card" href="{href}">\n'
            '        <span class="fav" data-id="{fid}" role="button" aria-label="즐겨찾기" title="즐겨찾기">☆</span>\n'
            '        {cover}\n'
            '        <div class="card-body">\n'
            '          <span class="badge" data-cat="{cslug}">{cat}</span>\n'
            '          <h3 class="card-title">{title}</h3>\n'
            '          <span class="card-date">{label}</span>\n'
            '        </div>\n'
            '      </a>').format(href=href, cover=cover, cslug=cslug, fid=fav_id,
                                 cat=html.escape(cat), title=html.escape(it["title"]), label=it["label"])


def goatcounter_script():
    if not GOATCOUNTER_CODE:
        return ""
    return (f'<script data-goatcounter="https://{GOATCOUNTER_CODE}.goatcounter.com/count" '
            'async src="//gc.zgo.at/count.js"></script>')


def news_card(it, href, thumb_href, cat, cslug):
    """뉴스 전용 헤드라인 리스트 항목(신문 느낌)."""
    if it["thumb_ok"]:
        cover = f'<img class="news-thumb" src="{thumb_href}" alt="" loading="lazy">'
    else:
        cover = f'<div class="news-thumb ph" data-cat="{cslug}">{html.escape(cat)}</div>'
    fid = f"news-{cslug}/{it['slot']}"
    return ('      <a class="news-item" href="{href}">\n'
            '        <span class="fav" data-id="{fid}" role="button" aria-label="즐겨찾기" title="즐겨찾기">☆</span>\n'
            '        {cover}\n'
            '        <div class="news-body">\n'
            '          <div class="news-meta"><span class="news-cat" data-cat="{cslug}">{cat}</span>'
            '<span class="news-time">{label}</span></div>\n'
            '          <div class="news-title">{title}</div>\n'
            '        </div>\n'
            '      </a>').format(href=href, fid=fid, cover=cover, cslug=cslug,
                                 cat=html.escape(cat), label=it["label"], title=html.escape(it["title"]))


def latest_per_cat(data):
    """각 카테고리의 최신 1편만 뽑아 최신순 정렬. (cat, cslug, item) 리스트."""
    out = [(cat, cslug, items[0]) for cat, cslug, items in data if items]
    out.sort(key=lambda x: x[2]["slot"], reverse=True)
    return out


def page(title, body):
    visit = '<div class="visit" id="visit-count"></div>' if GOATCOUNTER_CODE else ""
    return (f'<!DOCTYPE html>\n<html lang="ko" data-reads-theme="{READS_THEME_VERSION}">\n<head>\n'
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{html.escape(title)}</title>\n'
            f'{FONT_LINK}\n'
            f'<style>{CSS}</style>\n</head>\n<body>\n{body}\n'
            f'<footer>{visit}© 2026 7Peaks Reads · <a href="https://7peaks.io/ko/">7Peaks 홈페이지 ↗</a></footer>\n'
            f'{PREFS_JS}\n{VISIT_JS}\n{goatcounter_script()}\n</body>\n</html>')


def pager(p, pages):
    if pages <= 1:
        return ""
    href = lambda n: "./index.html" if n == 1 else f"./page{n}.html"
    parts = ['<nav class="pager">']
    if p > 1:
        parts.append(f'<a href="{href(p-1)}">← 이전</a>')
    # 처음·끝·현재 주변만 노출하고 나머지는 … 으로 생략
    nums = sorted({n for n in (1, 2, pages - 1, pages, p - 1, p, p + 1) if 1 <= n <= pages})
    prev = 0
    for n in nums:
        if n - prev > 1:
            parts.append('<span class="dots">…</span>')
        parts.append(f'<span class="cur">{n}</span>' if n == p else f'<a href="{href(n)}">{n}</a>')
        prev = n
    if p < pages:
        parts.append(f'<a href="{href(p+1)}">다음 →</a>')
    parts.append('</nav>')
    return "\n".join(parts)


def topnav_html():
    # 최상위 2대분류(블로그 / 뉴스) 중심으로 단순화. 개별 카테고리는 각 메인 안에서 탐색.
    return (
        '  <nav class="topnav" aria-label="Reads 탐색">\n'
        f'    <a class="tn-brand" href="{BASE_URL}/index.html">'
        f'<img class="tn-logo" src="{BASE_URL}/assets/7peaks-wordmark-light.svg" alt="7Peaks"><span>Reads</span></a>\n'
        '    <div class="tn-cats">\n'
        f'      <a href="{BASE_URL}/index.html">홈</a>\n'
        f'      <a href="{BASE_URL}/posts/index.html">블로그</a>\n'
        f'      <a href="{BASE_URL}/news/index.html">뉴스</a>\n'
        f'      <a href="{BASE_URL}/favorites.html">★ 즐겨찾기</a>\n'
        '      <a class="company-link" href="https://7peaks.io/ko/">7Peaks ↗</a>\n'
        '    </div>\n'
        '    <input id="site-search" type="search" placeholder="제목·카테고리 검색…" autocomplete="off" aria-label="검색">\n'
        '  </nav>\n')


SEARCH_WRAP = ('    <div id="search-wrap" hidden>\n'
               '      <p id="search-meta"></p>\n'
               '      <div id="search-results" class="grid"></div>\n'
               '    </div>\n')

SEARCH_JS = ('<script id="site-search-js">' + """
(function(){
  var input=document.getElementById('site-search');
  if(!input) return;
  var wrap=document.getElementById('search-wrap'),
      content=document.getElementById('page-content'),
      meta=document.getElementById('search-meta'),
      results=document.getElementById('search-results');
  var BASE="__BASE__", data=null;
  function esc(s){return (s||'').replace(/[&<>"]/g,function(c){return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'})[c];});}
  function load(cb){ if(data){cb();return;}
    fetch(BASE+'/search.json').then(function(r){return r.json();}).then(function(j){data=j;cb();}).catch(function(){data=[];cb();}); }
  function card(it){
    var cover = it.thumb ? '<img class="thumb" src="'+BASE+it.thumb+'" alt="" loading="lazy">'
      : '<div class="thumb ph" data-cat="'+it.cslug+'"><span>'+esc(it.cat)+'</span></div>';
    var star = window.__starMarkup ? window.__starMarkup(it.fid||(it.cslug+'/'+it.slot)) : '';
    return '<a class="card" href="'+BASE+it.url+'">'+star+cover+
      '<div class="card-body"><span class="badge" data-cat="'+it.cslug+'">'+esc(it.cat)+'</span>'+
      '<h3 class="card-title">'+esc(it.title)+'</h3><span class="card-date">'+esc(it.label)+'</span></div></a>';
  }
  function run(q){
    q=(q||'').trim().toLowerCase();
    if(!q){ wrap.hidden=true; if(content) content.hidden=false; return; }
    load(function(){
      var hits=data.filter(function(it){
        return (it.title||'').toLowerCase().indexOf(q)>=0 || (it.cat||'').toLowerCase().indexOf(q)>=0;
      });
      meta.textContent='“'+q+'” 검색결과 '+hits.length+'편';
      results.innerHTML = hits.length ? hits.map(card).join('') : '<p style="color:var(--muted)">결과가 없습니다.</p>';
      if(window.__refreshStars) window.__refreshStars();
      if(content) content.hidden=true; wrap.hidden=false;
    });
  }
  input.addEventListener('input',function(){run(input.value);});
})();
</script>""").replace("__BASE__", BASE_URL)


PREFS_JS = ('<script id="site-prefs-js">' + r"""
(function(){
  var BASE="__BASE__";
  var KV={view:'spk-view', per:'spk-perpage', favs:'spk-favs'};
  function lsget(k,d){ try{var v=localStorage.getItem(k);return v===null?d:v;}catch(e){return d;} }
  function lsset(k,v){ try{localStorage.setItem(k,v);}catch(e){} }
  function favs(){ try{return JSON.parse(lsget(KV.favs,'[]'))||[];}catch(e){return [];} }
  function saveFavs(a){ lsset(KV.favs, JSON.stringify(a)); }
  function getView(){ return lsget(KV.view,'card')==='list'?'list':'card'; }
  function getPer(){ var n=parseInt(lsget(KV.per,'12'),10); if(isNaN(n))n=12; return Math.min(15,Math.max(10,n)); }

  // ── 즐겨찾기 별
  window.__starMarkup=function(id){
    return '<span class="fav" data-id="'+id+'" role="button" aria-label="즐겨찾기" title="즐겨찾기">☆</span>';
  };
  function refreshStars(){
    var f=favs();
    document.querySelectorAll('.fav').forEach(function(el){
      var on=f.indexOf(el.dataset.id)>=0;
      el.classList.toggle('on',on); el.textContent=on?'★':'☆';
    });
  }
  window.__refreshStars=refreshStars;
  document.addEventListener('click',function(e){
    var s=e.target.closest && e.target.closest('.fav'); if(!s)return;
    e.preventDefault(); e.stopPropagation();
    var id=s.dataset.id, a=favs(), i=a.indexOf(id);
    if(i>=0)a.splice(i,1); else a.unshift(id);
    saveFavs(a); refreshStars();
    if(window.__onFavChange)window.__onFavChange();
  });

  // ── 보기/페이지당 컨트롤
  function applyView(v){
    document.querySelectorAll('.grid').forEach(function(g){ g.classList.toggle('view-list', v==='list'); });
  }
  function buildPager(grid){
    var page=1;
    var nav=document.createElement('nav'); nav.className='pager'; grid.after(nav);
    function render(){
      var cards=[].slice.call(grid.querySelectorAll('.card, .news-item'));
      var per=getPer(), pages=Math.max(1,Math.ceil(cards.length/per));
      if(page>pages)page=pages;
      cards.forEach(function(c,i){ c.style.display=(i>=(page-1)*per&&i<page*per)?'':'none'; });
      nav.innerHTML='';
      if(pages>1){
        var mk=function(label,p,cur,dis){
          if(cur){var sp=document.createElement('span');sp.className='cur';sp.textContent=label;nav.appendChild(sp);return;}
          if(dis)return;
          var a=document.createElement('a');a.href='#';a.textContent=label;
          a.addEventListener('click',function(e){e.preventDefault();page=p;render();window.scrollTo({top:0,behavior:'smooth'});});
          nav.appendChild(a);
        };
        mk('← 이전',page-1,false,page<=1);
        var nums=[],n; for(n=1;n<=pages;n++){ if(n===1||n===pages||Math.abs(n-page)<=1)nums.push(n); }
        var prev=0; nums.forEach(function(n){
          if(n-prev>1){var d=document.createElement('span');d.className='dots';d.textContent='…';nav.appendChild(d);}
          mk(String(n),n,n===page,false); prev=n;
        });
        mk('다음 →',page+1,false,page>=pages);
      }
    }
    window.__repaginate=render; render();
  }
  function init(){
    refreshStars();
    var pc=document.getElementById('page-content');
    if(!pc) return;
    var hasGrid=pc.querySelector('.grid');
    var pg=pc.querySelector('.grid[data-paginate], .news-list[data-paginate]');
    if(!hasGrid && !pg) return;   // 보기설정·페이지당 컨트롤이 필요 없는 페이지
    var bar=document.createElement('div'); bar.className='prefs';
    var perOpts=''; for(var n=10;n<=15;n++){ perOpts+='<option value="'+n+'"'+(n===getPer()?' selected':'')+'>'+n+'</option>'; }
    bar.innerHTML=
      (hasGrid?('<div class="seg" id="view-seg">'+
        '<button type="button" data-view="card">카드</button>'+
        '<button type="button" data-view="list">목록</button>'+
      '</div>'):'')+
      (pg?('<label>페이지당 <select id="perpage">'+perOpts+'</select> 개</label>'):'')+
      '<span class="grow"></span>'+
      '<a class="fav-link" href="'+BASE+'/favorites.html">★ 즐겨찾기</a>';
    pc.insertBefore(bar, pc.firstChild);
    var seg=bar.querySelector('#view-seg');
    if(seg){
      var paintSeg=function(v){ seg.querySelectorAll('button').forEach(function(b){ b.classList.toggle('on', b.dataset.view===v); }); };
      seg.addEventListener('click',function(e){ var b=e.target.closest('button'); if(!b)return;
        var v=b.dataset.view; lsset(KV.view,v); applyView(v); paintSeg(v); });
      applyView(getView()); paintSeg(getView());
    }
    if(pg){
      buildPager(pg);
      var sel=bar.querySelector('#perpage');
      sel.addEventListener('change',function(){ lsset(KV.per, sel.value); if(window.__repaginate)window.__repaginate(); });
    }
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init); else init();
})();
</script>""").replace("__BASE__", BASE_URL)

VISIT_JS = (('<script id="site-visit-js">' + r"""
(function(){
  var el=document.getElementById('visit-count'); if(!el)return;
  fetch('https://__CODE__.goatcounter.com/counter/TOTAL.json')
    .then(function(r){return r.json();})
    .then(function(j){ el.innerHTML='누적 방문 <b>'+(j.count||'0')+'</b>'; })
    .catch(function(){});
})();
</script>""").replace("__CODE__", GOATCOUNTER_CODE)) if GOATCOUNTER_CODE else ""


def search_entries(data, base_dir, id_prefix, section):
    out = []
    for cat, cslug, items in data:
        for it in items:
            out.append({
                "title": it["title"], "cat": cat, "cslug": cslug, "section": section,
                "label": it["label"], "slot": it["slot"],
                "fid": f"{id_prefix}{cslug}/{it['slot']}",
                "url": f"/{base_dir}/{cslug}/{it['slot']}/index.html",
                "thumb": (f"/{base_dir}/{cslug}/{it['slot']}/images/thumbnail.png" if it["thumb_ok"] else None),
            })
    return out


def build_search_index(*groups):
    out = []
    for g in groups:
        out.extend(g)
    out.sort(key=lambda x: x["slot"], reverse=True)
    open(os.path.join(SITE, "search.json"), "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False))
    return len(out)


def clean_category_pages(cslug, base_dir="posts"):
    """카테고리 폴더 바로 아래의 index.html / pageN.html 만 삭제(슬롯 폴더는 보존)."""
    base = os.path.join(SITE, base_dir, cslug)
    if not os.path.isdir(base):
        return
    for f in os.listdir(base):
        full = os.path.join(base, f)
        if os.path.isfile(full) and (f == "index.html" or re.match(r"page\d+\.html$", f)):
            os.remove(full)


# ---------------------------------------------------------------- 글 페이지 편의기능 주입
POST_CHROME_CSS = """<style id="site-chrome-css">
  #read-progress{position:fixed;top:0;left:0;height:3px;width:0;z-index:200;background:#2f57d6;transition:width .08s linear;}
  #site-nav{position:sticky;top:0;z-index:100;display:flex;align-items:center;gap:14px;
    padding:11px 20px;background:rgba(255,255,255,.92);-webkit-backdrop-filter:blur(6px);
    backdrop-filter:blur(6px);border-bottom:1px solid #e5e7eb;
    font-family:'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif;}
  #site-nav a{color:#2b2b2b;text-decoration:none;font-size:14px;font-weight:600;}
  #site-nav a:hover{color:#2f57d6;}
  #site-nav .nav-spacer{margin-left:auto;}
  #site-nav .nav-list{color:#555;font-weight:500;}
  #site-nav .read-time{color:#8a8f98;font-size:13px;font-weight:500;}
  #theme-toggle{border:1px solid #e5e7eb;background:#fff;color:#2b2b2b;border-radius:8px;
    padding:5px 11px;font-size:13px;cursor:pointer;font-family:inherit;}
  #theme-toggle:hover{border-color:#c7ccd6;}
  #to-top{position:fixed;right:22px;bottom:22px;z-index:100;width:46px;height:46px;border-radius:50%;
    border:1px solid #e5e7eb;background:#fff;color:#2f57d6;font-size:20px;line-height:1;cursor:pointer;
    box-shadow:0 4px 14px rgba(0,0,0,.14);display:none;}
  #to-top.show{display:flex;align-items:center;justify-content:center;}
  /* 다크 모드(본문): 글마다 클래스명이 달라도 동작하도록 컨테이너를 투명화해 어두운 body가 비치게 하고,
     글자는 밝게 강제. 내 사이트 chrome(네비/버튼)은 id 선택자로 다시 복구한다. */
  html.dark{background:#0f1117;}
  html.dark body{background:#0f1117 !important;color:#d7dae2 !important;}
  html.dark body :where(div,section,article,header,footer,main,aside,p,ul,ol,li,blockquote,figure,figcaption,table,thead,tbody,tr,td,th){
    background-color:transparent !important; background-image:none !important; border-color:#2a2e3a !important; }
  html.dark body :where(p,li,td,th,figcaption,blockquote,span,em){color:#ccd2dd !important;}
  html.dark body :where(h1,h2,h3,h4,h5,strong,b){color:#f4f6fa !important;}
  html.dark body :where(h2)::before{opacity:.9;}
  html.dark body a{color:#7aa2ff !important;}
  html.dark hr{border-color:#2a2e3a !important;}
  /* 사이트 chrome 복구 (id 우선순위로 위 일반 규칙을 덮는다) */
  html.dark #site-nav{background:rgba(18,21,29,.97) !important;border-bottom-color:#2a2e3a !important;}
  html.dark #site-nav a{color:#e8eaf0 !important;}
  html.dark #site-nav .nav-list,html.dark #site-nav .read-time{color:#aeb4c0 !important;}
  html.dark #theme-toggle{background:#1a1d27 !important;color:#e8eaf0 !important;border-color:#2a2e3a !important;}
  html.dark #to-top{background:#1a1d27 !important;color:#7aa2ff !important;border-color:#2a2e3a !important;}
  html.dark #read-progress{background:#7aa2ff !important;}
</style>"""

# The same local theme is embedded into each HTML file, so article publishing
# does not depend on an extra stylesheet request or a new hosting service.
POST_CHROME_CSS = POST_CHROME_CSS.replace("</style>", "\n" + READS_THEME_CSS + "\n</style>")

POST_CHROME_JS = """<script id="site-chrome-js">
(function(){
  var root=document.documentElement, KEY='spk-theme';
  try{ if(localStorage.getItem(KEY)==='dark') root.classList.add('dark'); }catch(e){}
  var tb=document.getElementById('theme-toggle');
  if(tb) tb.addEventListener('click',function(){
    root.classList.toggle('dark');
    try{ localStorage.setItem(KEY, root.classList.contains('dark')?'dark':'light'); }catch(e){}
  });
  var rt=document.getElementById('read-time');
  if(rt){ var txt=(document.body.innerText||'').replace(/\\s/g,'');
    rt.textContent='약 '+Math.max(1,Math.round(txt.length/500))+'분 읽기'; }
  var pb=document.getElementById('read-progress'), tt=document.getElementById('to-top');
  function onScroll(){ var h=document.documentElement;
    var sh=h.scrollHeight-h.clientHeight, p=sh>0?(h.scrollTop/sh*100):0;
    if(pb) pb.style.width=p+'%';
    if(tt) tt.classList.toggle('show', h.scrollTop>400); }
  window.addEventListener('scroll',onScroll,{passive:true}); onScroll();
  if(tt) tt.addEventListener('click',function(){window.scrollTo({top:0,behavior:'smooth'});});
})();
</script>"""

_OLD_CHROME_PATTERNS = [
    r'<style id="reads-article-theme"[^>]*>.*?</style>',
    r'<style id="site-nav-css">.*?</style>',
    r'<style id="site-chrome-css">.*?</style>',
    r'<nav id="site-nav"[^>]*>.*?</nav>',
    r'<div id="read-progress"></div>',
    r'<button id="to-top"[^>]*>.*?</button>',
    r'<script id="site-chrome-js">.*?</script>',
    r"<script>\s*\(function\(\)\{var b=document\.getElementById\('to-top'\).*?</script>",
    # goatcounter 태그도 반드시 제거해야 멱등이 된다. 없으면 실행할 때마다 1개씩 누적된다.
    r'<script[^>]*data-goatcounter=[^>]*>\s*</script>',
]


def _strip_chrome(t):
    for pat in _OLD_CHROME_PATTERNS:
        t = re.sub(pat, "", t, flags=re.S)
    return t


def ensure_post_chrome(cat_order=CAT_ORDER, base_dir="posts", list_suffix="목록"):
    """모든 글 index.html 에 상단 네비+테마토글+읽기시간+진행바+맨위로 버튼을 멱등 주입(업그레이드)."""
    count = 0
    for cat, cslug in cat_order:
        base = os.path.join(SITE, base_dir, cslug)
        if not os.path.isdir(base):
            continue
        for d in sorted(os.listdir(base)):
            f = os.path.join(base, d, "index.html")
            if not os.path.isfile(f):
                continue
            t = _strip_chrome(open(f, encoding="utf-8").read())
            if not t.strip():
                # Preserve pre-existing empty article files; presentation must
                # never invent or replace missing editorial content.
                continue
            if not re.search(r"<body\b", t, flags=re.I):
                # Two legacy posts are valid browser-rendered HTML fragments.
                # Supply a document shell without changing their body markup.
                first_block = re.search(r"<(?:div|article|main)\b", t, flags=re.I)
                if first_block is None:
                    continue
                fragment_head = re.sub(r"<!doctype[^>]*>", "", t[:first_block.start()], flags=re.I)
                t = ('<!DOCTYPE html><html lang="ko"><head>' + fragment_head
                     + '</head><body>' + t[first_block.start():] + '</body></html>')
            nav = ('<div id="read-progress"></div>\n'
                   '<nav id="site-nav" aria-label="글 탐색">'
                   f'<a class="nav-home" href="{BASE_URL}/index.html">'
                   f'<img class="reads-wordmark" src="{BASE_URL}/assets/7peaks-wordmark-light.svg" alt="7Peaks"><span>Reads</span></a>'
                   f'<a class="nav-list" href="{BASE_URL}/{base_dir}/{cslug}/index.html">{html.escape(cat)} {list_suffix}</a>'
                   '<span class="nav-spacer"></span>'
                   '<span class="read-time" id="read-time"></span>'
                   '<button id="theme-toggle" type="button">◐ 테마</button>'
                   '</nav>')
            t = re.sub(r"(<body\b)([^>]*>)",
                       lambda m: m.group(0) if 'data-reads-view=' in m.group(2)
                       else m.group(1) + ' data-reads-view="article"' + m.group(2), t, count=1)
            t = re.sub(r"(<body\b)([^>]*>)",
                       lambda m: m.group(0) if 'data-reads-theme=' in m.group(2)
                       else m.group(1) + f' data-reads-theme="{READS_THEME_VERSION}"' + m.group(2), t, count=1)
            if "</head>" in t:
                t = t.replace("</head>", POST_CHROME_CSS + "\n</head>", 1)
            t = re.sub(r"(<body[^>]*>)", r"\1\n" + nav.replace("\\", "\\\\"), t, count=1)
            if "</body>" in t:
                t = t.replace("</body>",
                              '<button id="to-top" aria-label="맨 위로">↑</button>\n'
                              + POST_CHROME_JS + "\n" + goatcounter_script() + "\n</body>", 1)
            open(f, "w", encoding="utf-8").write(t)
            count += 1
    return count


data = collect()
# 로고 에셋 폴더 보장 (실제 로고 파일 assets/logo.png 는 저장소에 커밋되어 있음)
os.makedirs(os.path.join(SITE, "assets"), exist_ok=True)
shutil.copyfile(os.path.join(THEME_DIR, "assets", "7peaks-wordmark-light.svg"),
                os.path.join(SITE, "assets", "7peaks-wordmark-light.svg"))
shutil.copyfile(os.path.join(THEME_DIR, "reads_theme.css"),
                os.path.join(SITE, "assets", "reads-theme.css"))
_svg_path = os.path.join(SITE, "assets", "logo.svg")
if os.path.exists(_svg_path):
    os.remove(_svg_path)  # 예전 SVG 잔재 제거
# 글이 있는 카테고리 슬러그 집합(네비/부제 노출 기준)
ACTIVE_SLUGS = {cslug for cat, cslug, items in data if items}
HERO_SUB = " · ".join(cat for cat, cslug, items in data if items) or "매일 새로운 이야기"

def cat_sections(data, base_prefix):
    """카테고리별 최신 HOME_PER_CAT개 카드 섹션. base_prefix 예: '.' (블로그 메인 기준)."""
    out = ""
    for cat, cslug, items in data:
        if not items:
            continue
        shown = items[:HOME_PER_CAT]
        cards = "\n".join(card(it, f"{base_prefix}/{cslug}/{it['slot']}/index.html",
                               f"{base_prefix}/{cslug}/{it['slot']}/images/thumbnail.png", cat, cslug)
                          for it in shown)
        more = (f'전체 {len(items)}편 보기 →' if len(items) > HOME_PER_CAT else '전체 보기 →')
        out += (f'    <section class="cat-section">\n'
                f'      <div class="cat-bar">\n'
                f'        <h2 class="cat-head" data-cat="{cslug}">{html.escape(cat)}</h2>\n'
                f'        <a class="more-link" href="{base_prefix}/{cslug}/">{more}</a>\n'
                f'      </div>\n'
                f'      <div class="grid home">\n{cards}\n      </div>\n'
                f'    </section>\n')
    return out


def latest_cards(data, base_prefix, id_prefix, n):
    """여러 카테고리 글을 최신순으로 합쳐 상위 n개 카드."""
    flat = [(cat, cslug, it) for cat, cslug, items in data for it in items]
    flat.sort(key=lambda x: x[2]["slot"], reverse=True)
    return "\n".join(
        card(it, f"{base_prefix}/{cslug}/{it['slot']}/index.html",
             f"{base_prefix}/{cslug}/{it['slot']}/images/thumbnail.png", cat, cslug, id_prefix=id_prefix)
        for cat, cslug, it in flat[:n])


# ---------------------------------------------------------------- 블로그 메인(/posts/index.html)
os.makedirs(os.path.join(SITE, "posts"), exist_ok=True)
blog_body = (topnav_html() +
             '  <div class="hero">\n'
             '    <p class="reads-eyebrow">BLOG</p>\n'
             '    <h1>블로그</h1>\n'
             '    <p>익숙한 주제를 깊이, 새로운 관점을 넓게.</p>\n'
             '  </div>\n'
             '  <main>\n'
             + SEARCH_WRAP +
             '    <div id="page-content">\n'
             '    <a class="back" href="../index.html">← 홈으로</a>\n'
             f'{cat_sections(data, ".")}    </div>\n'
             '  </main>\n'
             + SEARCH_JS)
open(os.path.join(SITE, "posts", "index.html"), "w", encoding="utf-8").write(
    page("블로그 - SevenPeaks Reads", blog_body))

# ---------------------------------------------------------------- 블로그 카테고리 보관 페이지
total_pages = 0
for cat, cslug, items in data:
    clean_category_pages(cslug)
    if not items:
        continue
    total = len(items)
    cards = "\n".join(card(it, f"./{it['slot']}/index.html",
                           f"./{it['slot']}/images/thumbnail.png", cat, cslug) for it in items)
    body = (topnav_html() +
            '  <div class="hero sub">\n'
            '    <h1><a href="../index.html">블로그</a></h1>\n'
            f'    <p><span class="cat-head" data-cat="{cslug}">{html.escape(cat)}</span> '
            f'전체 {total}편</p>\n'
            '  </div>\n'
            '  <main>\n'
            + SEARCH_WRAP +
            '    <div id="page-content">\n'
            '    <a class="back" href="../index.html">← 블로그 메인</a>\n'
            f'    <div class="grid" data-paginate="1">\n{cards}\n    </div>\n'
            '    </div>\n'
            '  </main>\n'
            + SEARCH_JS)
    open(os.path.join(SITE, "posts", cslug, "index.html"), "w", encoding="utf-8").write(
        page(f"{cat} - SevenPeaks Reads", body))
    total_pages += 1

# ---------------------------------------------------------------- 즐겨찾기 페이지
FAV_JS = ('<script id="fav-page-js">' + r"""
(function(){
  var BASE="__BASE__";
  function esc(s){return (s||'').replace(/[&<>"]/g,function(c){return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'})[c];});}
  function favs(){ try{return JSON.parse(localStorage.getItem('spk-favs')||'[]')||[];}catch(e){return [];} }
  var results=document.getElementById('fav-results'), empty=document.getElementById('fav-empty'), data=null;
  var NEWS_CATS=__NEWSCATS__, BLOG_CATS=__BLOGCATS__;
  function star(id){ return window.__starMarkup?window.__starMarkup(id):''; }
  function blogCard(it){
    var cover = it.thumb ? '<img class="thumb" src="'+BASE+it.thumb+'" alt="" loading="lazy">'
      : '<div class="thumb ph" data-cat="'+it.cslug+'"><span>'+esc(it.cat)+'</span></div>';
    return '<a class="card" href="'+BASE+it.url+'">'+star(it.fid)+cover+
      '<div class="card-body"><span class="badge" data-cat="'+it.cslug+'">'+esc(it.cat)+'</span>'+
      '<h3 class="card-title">'+esc(it.title)+'</h3><span class="card-date">'+esc(it.label)+'</span></div></a>';
  }
  function newsItem(it){
    var cover = it.thumb ? '<img class="news-thumb" src="'+BASE+it.thumb+'" alt="" loading="lazy">'
      : '<div class="news-thumb ph" data-cat="'+it.cslug+'">'+esc(it.cat)+'</div>';
    return '<a class="news-item" href="'+BASE+it.url+'">'+star(it.fid)+cover+
      '<div class="news-body"><div class="news-meta"><span class="news-cat" data-cat="'+it.cslug+'">'+esc(it.cat)+'</span>'+
      '<span class="news-time">'+esc(it.label)+'</span></div>'+
      '<div class="news-title">'+esc(it.title)+'</div></div></a>';
  }
  function getPer(){ var n=parseInt(localStorage.getItem('spk-perpage')||'12',10); if(isNaN(n))n=12; return Math.min(15,Math.max(10,n)); }
  function makePager(host, items, section){
    var per=getPer(), page=1;
    var listWrap=document.createElement('div');
    listWrap.className=(section==='news'?'news-list':'grid');
    var nav=document.createElement('nav'); nav.className='pager';
    host.appendChild(listWrap); host.appendChild(nav);
    function render(){
      var pages=Math.max(1,Math.ceil(items.length/per));
      if(page>pages)page=pages;
      var slice=items.slice((page-1)*per, page*per);
      listWrap.innerHTML=slice.map(section==='news'?newsItem:blogCard).join('');
      nav.innerHTML='';
      if(pages>1){
        var mk=function(label,p,cur,dis){
          if(cur){var s=document.createElement('span');s.className='cur';s.textContent=label;nav.appendChild(s);return;}
          if(dis)return;
          var a=document.createElement('a');a.href='#';a.textContent=label;
          a.addEventListener('click',function(e){e.preventDefault();page=p;render();});
          nav.appendChild(a);
        };
        mk('← 이전',page-1,false,page<=1);
        var nums=[],n; for(n=1;n<=pages;n++){ if(n===1||n===pages||Math.abs(n-page)<=1)nums.push(n); }
        var prev=0; nums.forEach(function(n){ if(n-prev>1){var d=document.createElement('span');d.className='dots';d.textContent='…';nav.appendChild(d);} mk(String(n),n,n===page,false); prev=n; });
        mk('다음 →',page+1,false,page>=pages);
      }
      if(window.__refreshStars)window.__refreshStars();
    }
    render();
  }
  function renderGroups(parent, section, cats){
    var f=favs(), any=false;
    cats.forEach(function(pair){
      var cslug=pair[0], cname=pair[1];
      var items=(data||[]).filter(function(it){ return it.section===section && it.cslug===cslug && f.indexOf(it.fid)>=0; });
      if(!items.length) return;
      any=true;
      var bar=document.createElement('div'); bar.className='cat-bar'; bar.style.margin='18px 0 10px';
      bar.innerHTML='<h3 class="cat-head" data-cat="'+cslug+'">'+esc(cname)+' <span style="opacity:.75">'+items.length+'</span></h3>';
      parent.appendChild(bar);
      var host=document.createElement('div');
      parent.appendChild(host);
      makePager(host, items, section);
    });
    return any;
  }
  function paint(){
    var f=favs();
    results.innerHTML='';
    if(!f.length){ empty.hidden=false; if(window.__refreshStars)window.__refreshStars(); return; }
    empty.hidden=true; var wrote=false;
    var newsSec=document.createElement('section'); newsSec.style.marginBottom='30px';
    newsSec.innerHTML='<h2 class="cat-head" data-cat="news" style="font-size:17px;padding:6px 16px">뉴스</h2>';
    if(renderGroups(newsSec,'news',NEWS_CATS)){ results.appendChild(newsSec); wrote=true; }
    var blogSec=document.createElement('section');
    blogSec.innerHTML='<h2 class="cat-head" data-cat="blog" style="font-size:17px;padding:6px 16px">블로그</h2>';
    if(renderGroups(blogSec,'blog',BLOG_CATS)){ results.appendChild(blogSec); wrote=true; }
    if(!wrote){ results.innerHTML='<p style="color:var(--muted);padding:20px 0">즐겨찾기한 글을 찾을 수 없습니다.</p>'; }
    if(window.__refreshStars)window.__refreshStars();
  }
  window.__onFavChange=paint;

  // ── 가져오기 / 내보내기
  var msgEl=document.getElementById('fav-msg');
  function msg(t){ if(msgEl) msgEl.textContent=t; }
  var expBtn=document.getElementById('fav-export');
  if(expBtn) expBtn.addEventListener('click',function(){
    var arr=favs();
    if(!arr.length){ msg('내보낼 즐겨찾기가 없습니다.'); return; }
    var blob=new Blob([JSON.stringify(arr,null,0)],{type:'application/json'});
    var url=URL.createObjectURL(blob), a=document.createElement('a');
    var d=new Date(), p=function(n){return (n<10?'0':'')+n;};
    a.href=url; a.download='sevenpeaks-favorites-'+d.getFullYear()+p(d.getMonth()+1)+p(d.getDate())+'.json';
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function(){URL.revokeObjectURL(url);},1000);
    msg('내보내기 완료 ('+arr.length+'개)');
  });
  var fi=document.getElementById('fav-import'), impBtn=document.getElementById('fav-import-btn');
  if(impBtn && fi){
    impBtn.addEventListener('click',function(){ fi.click(); });
    fi.addEventListener('change',function(){
      var f=fi.files&&fi.files[0]; if(!f){ return; }
      var r=new FileReader();
      r.onload=function(){
        try{
          var arr=JSON.parse(r.result);
          if(!Array.isArray(arr)) throw 0;
          var cur=favs(), added=0;
          arr.forEach(function(id){ if(typeof id==='string' && id && cur.indexOf(id)<0){ cur.push(id); added++; } });
          localStorage.setItem('spk-favs', JSON.stringify(cur));
          msg('가져오기 완료: '+added+'개 추가 (총 '+cur.length+'개)');
          paint();
        }catch(e){ msg('가져오기 실패 — 올바른 즐겨찾기 파일이 아닙니다.'); }
        fi.value='';
      };
      r.readAsText(f);
    });
  }

  fetch(BASE+'/search.json').then(function(r){return r.json();}).then(function(j){data=j;paint();}).catch(function(){paint();});
})();
</script>""")
FAV_JS = (FAV_JS.replace("__BASE__", BASE_URL)
          .replace("__NEWSCATS__", json.dumps([[cslug, cat] for cat, cslug in NEWS_ORDER], ensure_ascii=False))
          .replace("__BLOGCATS__", json.dumps([[cslug, cat] for cat, cslug in CAT_ORDER], ensure_ascii=False)))

fav_body = (topnav_html() +
            '  <div class="hero sub">\n'
            '    <p class="reads-eyebrow">SAVED STORIES</p>\n'
            '    <h1>즐겨찾기</h1>\n'
            '    <p>다시 읽고 싶은 글을 모아둡니다.</p>\n'
            '  </div>\n'
            '  <main>\n'
            + SEARCH_WRAP +
            '    <div id="page-content">\n'
            '    <a class="back" href="./index.html">← 홈으로</a>\n'
            '    <div class="fav-tools">\n'
            '      <button type="button" id="fav-export">내보내기</button>\n'
            '      <button type="button" id="fav-import-btn">가져오기</button>\n'
            '      <input type="file" id="fav-import" accept="application/json,.json" hidden>\n'
            '      <span id="fav-msg"></span>\n'
            '    </div>\n'
            '    <p id="fav-empty" hidden>아직 즐겨찾기한 글이 없습니다. 카드 오른쪽 위의 ☆ 를 눌러 추가하세요.</p>\n'
            '    <div id="fav-results"></div>\n'
            '    </div>\n'
            '  </main>\n'
            + SEARCH_JS + FAV_JS)
open(os.path.join(SITE, "favorites.html"), "w", encoding="utf-8").write(
    page("즐겨찾기 - SevenPeaks Reads", fav_body))

# ================================================================ 뉴스(해설) 섹션
news_data = collect(NEWS_ORDER, "news")
os.makedirs(os.path.join(SITE, "news"), exist_ok=True)
news_sub = " · ".join(cat for cat, cslug, items in news_data if items) or "주요 이슈를 짚어드립니다"

# 뉴스 랜딩(/news/index.html) — 주제별로 최신 몇 편을 헤드라인 리스트로
news_sections = ""
for cat, cslug, items in news_data:
    if not items:
        continue
    shown = items[:HOME_PER_CAT]
    rows = "\n".join(news_card(it, f"./{cslug}/{it['slot']}/index.html",
                               f"./{cslug}/{it['slot']}/images/thumbnail.png", cat, cslug)
                     for it in shown)
    more = (f'전체 {len(items)}편 보기 →' if len(items) > HOME_PER_CAT else '전체 보기 →')
    news_sections += (f'    <section class="cat-section">\n'
                      f'      <div class="cat-bar">\n'
                      f'        <h2 class="cat-head" data-cat="{cslug}">{html.escape(cat)}</h2>\n'
                      f'        <a class="more-link" href="./{cslug}/">{more}</a>\n'
                      f'      </div>\n'
                      f'      <div class="news-list">\n{rows}\n      </div>\n'
                      f'    </section>\n')
if not news_sections:
    news_sections = ('    <p style="color:var(--muted);padding:24px 0">아직 등록된 뉴스 해설이 없습니다. '
                     '곧 매일 업데이트됩니다.</p>\n')

news_home_body = (topnav_html() +
                  '  <div class="hero">\n'
                  '    <p class="reads-eyebrow">NEWS</p>\n'
                  '    <h1>뉴스 해설</h1>\n'
                  '    <p>오늘의 이슈를 맥락과 함께 읽습니다.</p>\n'
                  '  </div>\n'
                  '  <main>\n'
                  + SEARCH_WRAP +
                  f'    <div id="page-content">\n'
                  '    <a class="back" href="../index.html">← 홈</a>\n'
                  f'{news_sections}    </div>\n'
                  '  </main>\n'
                  + SEARCH_JS)
open(os.path.join(SITE, "news", "index.html"), "w", encoding="utf-8").write(
    page("뉴스 - SevenPeaks Reads", news_home_body))

# 뉴스 카테고리 보관 페이지(/news/<slug>/index.html)
news_pages = 0
for cat, cslug, items in news_data:
    clean_category_pages(cslug, "news")
    if not items:
        continue
    total = len(items)
    rows = "\n".join(news_card(it, f"./{it['slot']}/index.html",
                               f"./{it['slot']}/images/thumbnail.png", cat, cslug) for it in items)
    body = (topnav_html() +
            '  <div class="hero sub">\n'
            '    <h1><a href="../index.html">뉴스</a></h1>\n'
            f'    <p><span class="cat-head" data-cat="{cslug}">{html.escape(cat)}</span> '
            f'전체 {total}편</p>\n'
            '  </div>\n'
            '  <main>\n'
            + SEARCH_WRAP +
            '    <div id="page-content">\n'
            '    <a class="back" href="../index.html">← 뉴스 메인</a>\n'
            f'    <div class="news-list" data-paginate="1">\n{rows}\n    </div>\n'
            '    </div>\n'
            '  </main>\n'
            + SEARCH_JS)
    open(os.path.join(SITE, "news", cslug, "index.html"), "w", encoding="utf-8").write(
        page(f"{cat} 뉴스 - SevenPeaks Reads", body))
    news_pages += 1

# ================================================================ 통합 메인(/index.html)
# 상단: 뉴스 — 주제별 최신 1편씩(헤드라인 리스트) / 하단: 블로그 — 주제별 최신 1편씩(카드)
news_rows = "\n".join(
    news_card(it, f"./news/{cslug}/{it['slot']}/index.html",
              f"./news/{cslug}/{it['slot']}/images/thumbnail.png", cat, cslug)
    for cat, cslug, it in latest_per_cat(news_data))
blog_cards = "\n".join(
    card(it, f"./posts/{cslug}/{it['slot']}/index.html",
         f"./posts/{cslug}/{it['slot']}/images/thumbnail.png", cat, cslug)
    for cat, cslug, it in latest_per_cat(data))
root_news_block = (
    '    <section class="cat-section">\n'
    '      <div class="cat-bar">\n'
    '        <h2 class="cat-head" data-cat="news">뉴스</h2>\n'
    '        <a class="more-link" href="./news/index.html">뉴스 더보기 →</a>\n'
    '      </div>\n'
    + (f'      <div class="news-list">\n{news_rows}\n      </div>\n' if news_rows
       else '      <p style="color:var(--muted)">준비 중입니다.</p>\n')
    + '    </section>\n')
root_blog_block = (
    '    <section class="cat-section">\n'
    '      <div class="cat-bar">\n'
    '        <h2 class="cat-head" data-cat="blog">블로그</h2>\n'
    '        <a class="more-link" href="./posts/index.html">블로그 더보기 →</a>\n'
    '      </div>\n'
    + (f'      <div class="grid home">\n{blog_cards}\n      </div>\n' if blog_cards
       else '      <p style="color:var(--muted)">준비 중입니다.</p>\n')
    + '    </section>\n')
root_body = (topnav_html() +
             '  <div class="hero">\n'
             '    <p class="reads-eyebrow">NEWS &amp; STORIES</p>\n'
             '    <h1>오늘의 뉴스.<br>새로운 관점.</h1>\n'
             '    <p>세상의 흐름과 깊이 있는 이야기를 전합니다.</p>\n'
             '  </div>\n'
             '  <main>\n'
             + SEARCH_WRAP +
             f'    <div id="page-content">\n{root_news_block}{root_blog_block}    </div>\n'
             '  </main>\n'
             + SEARCH_JS)
open(os.path.join(SITE, "index.html"), "w", encoding="utf-8").write(
    page("SevenPeaks Reads", root_body))

# ---------------------------------------------------------------- 마무리(공통)
injected = ensure_post_chrome()
injected += ensure_post_chrome(NEWS_ORDER, "news", "뉴스")
n_search = build_search_index(
    search_entries(data, "posts", "", "blog"),
    search_entries(news_data, "news", "news-", "news"))
print(f"index rebuilt (home + {total_pages} blog cat pages + news + {news_pages} news cat pages); "
      f"search.json={n_search} posts; post-chrome injected into {injected} posts")
