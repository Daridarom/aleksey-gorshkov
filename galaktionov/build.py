#!/usr/bin/env python3
"""Собирает index.html из content/site.json.

Как пополнять архив:
  1. Добавьте историю, событие хронологии, встречу или фото в content/site.json.
     Фото кладите в assets/photos/<id>-<ширина>.webp и .jpg (см. tools/photos.py).
  2. Запустите:  python3 build.py
  3. Откройте index.html в браузере и проверьте.

Страница остаётся статической: всё содержимое есть в HTML и читается без JavaScript.
Скрипт assets/site.js только добавляет удобства: увеличение фото, поделиться, поиск, шрифт.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "content" / "site.json").read_text(encoding="utf-8"))
SRC = DATA["sources"]
PHOTOS = {p["id"]: p for p in DATA["photos"]}
THEMES = {t["id"]: t["title"] for t in DATA["themes"]}
STORIES = {s["id"]: s for s in DATA["stories"]}
MEETS = {m["id"]: m for m in DATA["meetings"]}

NBSP_WORDS = r"(?:в|и|с|к|о|у|а|я|на|не|по|за|из|от|до|во|со|об|ко|но|же|ли)"


def esc(s):
    return html.escape(s or "", quote=True)


def t(s):
    """Экранирование + неразрывные пробелы после коротких слов и перед тире."""
    s = esc(s)
    s = re.sub(r"(?<![\wА-Яа-яЁё])(" + NBSP_WORDS + r") ", r"\1&nbsp;", s, flags=re.I)
    s = s.replace(" — ", "&nbsp;— ")
    return s


def src_link(key, cls="src"):
    s = SRC[key]
    if "small" in cls and s.get("short"):
        label = s["short"]
    else:
        label = s["org"] + (", " + s["date"] if s.get("date") else "")
    return (f'<a class="{cls}" href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">'
            f'{t(label)}<span class="ext" aria-hidden="true"> ↗</span>'
            f'<span class="visually-hidden"> (откроется в новой вкладке)</span></a>')


def picture(pid, sizes_attr, cls="", eager=False, open_lightbox=True):
    p = PHOTOS[pid]
    base = f"assets/photos/{pid}"
    ws = p["sizes"]
    webp = ", ".join(f"{base}-{w}.webp {w}w" for w in ws)
    jpg = ", ".join(f"{base}-{w}.jpg {w}w" for w in ws)
    fallback = f"{base}-{ws[-1] if len(ws) == 1 else ws[0]}.jpg"
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    focus = f' style="object-position:{p["focus"]}"' if p.get("focus") else ""
    img = (f'<picture><source type="image/webp" srcset="{webp}" sizes="{sizes_attr}">'
           f'<img class="{cls}" src="{fallback}" srcset="{jpg}" sizes="{sizes_attr}" '
           f'width="{p["w"]}" height="{p["h"]}" alt="{esc(p["alt"])}" {load} decoding="async"{focus}></picture>')
    if open_lightbox:
        return (f'<button class="photo-open" type="button" data-photo="{pid}" '
                f'aria-label="Открыть фото крупно: {esc(p["title"])}">{img}'
                f'<span class="zoom-hint" aria-hidden="true">Увеличить</span></button>')
    return img


def credit_line(pid):
    p = PHOTOS[pid]
    if p.get("source"):
        s = SRC[p["source"]]
        return (f'<a class="src small" href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">'
                f'{t(p["credit"])}<span class="ext" aria-hidden="true"> ↗</span>'
                f'<span class="visually-hidden"> (публикация откроется в новой вкладке)</span></a>')
    return t(p["credit"])


def figure(pid, sizes_attr, cls="", eager=False):
    p = PHOTOS[pid]
    if p["h"] > p["w"]:
        cls += " portrait"
    return (f'<figure class="doc-photo {cls}">{picture(pid, sizes_attr, eager=eager)}'
            f'<figcaption><span class="cap-title">{t(p["title"])}.</span> {t(p["caption"])} '
            f'<span class="cap-credit">{credit_line(pid)}</span></figcaption></figure>')


# ---------------------------------------------------------------- sections

def header():
    nav = [("life", "О человеке"), ("stories", "Истории"), ("timeline", "Хронология"),
           ("meetings", "Встречи"), ("photos", "Фото"), ("video", "Видео"), ("sources", "Источники")]
    links = "".join(f'<a href="#{i}">{n}</a>' for i, n in nav)
    return f'''<header class="site-header" id="top">
  <div class="wrap header-row">
    <a class="brand" href="#home"><span class="brand-name">Владимир Галактионов</span><span class="brand-sub">личный архив · ребёнок блокадного Ленинграда</span></a>
    <button class="menu-btn" id="menuBtn" type="button" aria-expanded="false" aria-controls="menuPanel"><span class="menu-icon" aria-hidden="true"></span>Меню</button>
    <div class="menu-panel" id="menuPanel">
      <nav class="main-nav" aria-label="Разделы сайта">{links}</nav>
      <div class="reading-tools" role="group" aria-label="Настройки чтения">
        <span class="tools-label">Текст</span>
        <button type="button" class="tool" id="fontMinus" aria-label="Уменьшить шрифт">А−</button>
        <button type="button" class="tool" id="fontPlus" aria-label="Увеличить шрифт">А+</button>
        <button type="button" class="tool" id="contrastBtn" aria-pressed="false">Контраст</button>
      </div>
    </div>
  </div>
</header>'''


def hero():
    i = DATA["intro"]
    return f'''<section class="hero" id="home" aria-labelledby="heroTitle">
  <div class="wrap hero-grid">
    <figure class="hero-photo">{picture("hero-2020s", "(max-width: 760px) 100vw, 46vw", eager=True)}
      <figcaption>{t(PHOTOS["hero-2020s"]["caption"])} {t(PHOTOS["hero-2020s"]["credit"])}.</figcaption>
    </figure>
    <div class="hero-text">
      <p class="eyebrow">Персональный архив</p>
      <h1 id="heroTitle">Владимир Георгиевич <span>Галактионов</span></h1>
      <p class="hero-dates">Родился 18&nbsp;апреля 1941&nbsp;года в&nbsp;Ленинграде</p>
      <p class="hero-lead">{t(i["lead"])}</p>
      <div class="hero-actions">
        <a class="btn primary" href="#life">Читать историю</a>
        <a class="btn ghost" href="#photos">Фотографии</a>
        <a class="btn ghost" href="#video">Видео</a>
      </div>
    </div>
  </div>
</section>'''


def about():
    i = DATA["intro"]
    paras = "".join(f"<p>{t(p)}</p>" for p in i["paragraphs"])
    q = i["quote"]
    facts = "".join(
        f'<li><strong>{t(f["value"])}</strong><span>{t(f["label"])}</span>'
        f'<a class="fact-src" href="{esc(SRC[f["source"]]["url"])}" target="_blank" rel="noopener noreferrer">источник ↗</a></li>'
        for f in i["facts"])
    return f'''<section class="section about" id="life" aria-labelledby="lifeTitle">
  <div class="wrap">
    <p class="kicker">О человеке</p>
    <h2 id="lifeTitle">Жизнь, которая началась в&nbsp;блокаду</h2>
    <div class="about-grid">
      <div class="about-text prose">{paras}
        <blockquote class="pull"><p>«{t(q["text"])}»</p><footer>— {t(q["who"])}. {src_link(q["source"])}</footer></blockquote>
      </div>
      {figure("blago-2015-portrait", "(max-width: 760px) 100vw, 48vw", "about-photo")}
    </div>
    <ul class="facts">{facts}</ul>
  </div>
</section>'''


def featured():
    cards = []
    for s in DATA["stories"]:
        if not s.get("featured"):
            continue
        quote = s.get("pull")
        body = (f'<p class="teaser-quote">«{t(quote["text"])}»</p>' if quote else f'<p class="teaser-lead">{t(s["lead"])}</p>')
        media = ""
        if s["id"] == "officers":
            media = f'<div class="teaser-media">{picture("officers-2022-2", "(max-width: 760px) 100vw, 25vw", open_lightbox=False)}</div>'
        cards.append(f'''<li class="teaser{' has-media' if media else ''}">{media}
  <div class="teaser-body"><p class="teaser-meta">{t(THEMES[s["theme"]])} · {t(s["years"])}</p>
  <h3><a href="#{s["id"]}" data-open-story="{s["id"]}">{t(s["title"])}</a></h3>{body}
  <span class="teaser-more" aria-hidden="true">Читать →</span></div></li>''')
    return f'''<section class="section featured" id="episodes" aria-labelledby="epTitle">
  <div class="wrap">
    <p class="kicker">Главные эпизоды</p>
    <h2 id="epTitle">С&nbsp;чего начать чтение</h2>
    <ul class="teasers">{"".join(cards)}</ul>
  </div>
</section>'''


def timeline():
    periods = []
    for n, per in enumerate(DATA["timeline"], 1):
        evs = []
        for e in per["events"]:
            srcs = ", ".join(src_link(k, "src small") for k in e["sources"])
            story = ""
            if e.get("story"):
                label = "История →" if (e["story"] in STORIES or e["story"] in MEETS) else "Смотреть →"
                story = f' <a class="ev-story" href="#{e["story"]}" data-open-story="{e["story"]}">{label}</a>'
            evs.append(f'<li><p class="ev-date">{t(e["date"])}</p><p class="ev-text">{t(e["text"])}{story}</p>'
                       f'<p class="ev-src">{srcs}</p></li>')
        photo = figure(per["photo"], "(max-width: 760px) 100vw, 34vw", "period-photo") if per.get("photo") else ""
        periods.append(f'''<li class="period" id="{per["id"]}">
  <div class="period-head"><p class="period-num">Часть {n}</p><p class="period-years">{t(per["years"])}</p>
    <h3>{t(per["title"])}</h3><p class="period-summary">{t(per["summary"])}</p>{photo}</div>
  <ol class="events">{"".join(evs)}</ol>
</li>''')
    return f'''<section class="section timeline" id="timeline" aria-labelledby="tlTitle">
  <div class="wrap">
    <p class="kicker">Хронология</p>
    <h2 id="tlTitle">Три части одной жизни</h2>
    <p class="section-lead">Только даты, подтверждённые публикациями. У&nbsp;каждого события — ссылка на&nbsp;источник.</p>
    <ol class="periods">{"".join(periods)}</ol>
  </div>
</section>'''


def story_article(s):
    paras = "".join(f"<p>{t(p)}</p>" for p in s["paragraphs"])
    pull = ""
    if s.get("pull"):
        pull = f'<blockquote class="pull small"><p>«{t(s["pull"]["text"])}»</p><footer>{src_link(s["pull"]["source"])}</footer></blockquote>'
    srcs = "".join(f"<li>{src_link(k)}<span class='src-title'>{t(SRC[k]['title'])}</span></li>" for k in s["sources"])
    photo = figure(s["photo"], "(max-width: 760px) 100vw, 40vw", "story-photo") if s.get("photo") else ""
    cls = "story featured-story" if s.get("featured") else "story"
    return f'''<article class="{cls}" id="{s["id"]}" data-theme="{s["theme"]}">
  <header class="story-head"><p class="story-meta"><span class="theme-tag">{t(THEMES[s["theme"]])}</span> <span class="years">{t(s["years"])}</span></p>
    <h3>{t(s["title"])}</h3><p class="story-lead">{t(s["lead"])}</p></header>
  {photo}
  <details class="story-body"><summary><span class="sum-open">Читать историю</span><span class="sum-close">Свернуть</span></summary>
    <div class="prose reading">{paras}{pull}
      <div class="story-sources"><p class="label">Источники</p><ul>{srcs}</ul></div>
      <div class="story-actions inner">
        <button type="button" class="act" data-copy="{s["id"]}">Скопировать ссылку</button>
        <button type="button" class="act" data-print="{s["id"]}">Распечатать историю</button>
      </div>
    </div>
  </details>
  <button type="button" class="share-btn" data-share="{s["id"]}" data-title="{esc(s["title"])}"><span aria-hidden="true">↗</span> Поделиться</button>
</article>'''


def stories():
    feat = "".join(story_article(x) for x in DATA["stories"] if x.get("featured"))
    rest = "".join(story_article(x) for x in DATA["stories"] if not x.get("featured"))
    return f'''<section class="section stories" id="stories" aria-labelledby="stTitle">
  <div class="wrap">
    <p class="kicker">Главные эпизоды</p>
    <h2 id="stTitle">Истории жизни</h2>
    <p class="section-lead">Пересказы по&nbsp;проверенным публикациям и&nbsp;воспоминаниям самого Владимира Георгиевича. Под каждой историей — источник; ссылкой на&nbsp;любую можно поделиться.</p>
    <div class="featured-stories">{feat}</div>
    <h3 class="group-title">Ещё истории</h3>
    <div class="story-list">{rest}</div>
  </div>
</section>'''


def meetings():
    cards = "".join(story_article(m) for m in DATA["meetings"])
    return f'''<section class="section meetings" id="meetings" aria-labelledby="mtTitle">
  <div class="wrap">
    <p class="kicker">Встречи поколений</p>
    <h2 id="mtTitle">Со&nbsp;школьниками, студентами и&nbsp;юнармейцами</h2>
    <p class="section-lead">Телемосты, уроки мужества, музейные встречи и&nbsp;памятные вечера — по&nbsp;годам, у&nbsp;каждой встречи свой источник.</p>
    <div class="story-list meet-list">{cards}</div>
  </div>
</section>'''


def placed_photos():
    ids = {"hero-2020s", "blago-2015-portrait"}
    ids |= {p["photo"] for p in DATA["timeline"] if p.get("photo")}
    ids |= {x["photo"] for x in DATA["stories"] + DATA["meetings"] if x.get("photo")}
    return ids


def gallery():
    items = []
    placed = placed_photos()
    total = sum(1 for p in DATA["photos"] if p.get("publish"))
    for p in DATA["photos"]:
        if not p.get("publish") or p["id"] in placed:
            continue
        items.append(f'''<li class="g-item"><figure>{picture(p["id"], "(max-width: 560px) 100vw, (max-width: 1000px) 50vw, 33vw")}
  <figcaption><span class="g-date">{t(p["date"])}</span><span class="g-title">{t(p["title"])}</span>
  <span class="g-cap">{t(p["caption"])}</span><span class="g-credit">{credit_line(p["id"])}</span></figcaption></figure></li>''')
    n = len(items)
    return f'''<section class="section photos" id="photos" aria-labelledby="phTitle">
  <div class="wrap">
    <p class="kicker">Фотоальбом</p>
    <h2 id="phTitle">Фотографии</h2>
    <p class="section-lead">Всего на&nbsp;сайте {total} снимков, каждый — один раз: семейные фото стоят в&nbsp;историях и&nbsp;хронологии, снимки встреч — у&nbsp;своих встреч, а&nbsp;здесь — остальные. Нажмите на&nbsp;любое фото, чтобы увеличить и&nbsp;листать все {total}.</p>
    <ul class="gallery">{"".join(items)}</ul>
    <aside class="note-card">
      <h3>Ещё 20 снимков — у&nbsp;РИА Новости</h3>
      <p>Фотоочерк 2019&nbsp;года: дом на&nbsp;Английском проспекте, детский портрет, семья, Пискарёвское кладбище. Снимки принадлежат фотобанку РИА Новости и&nbsp;открываются на&nbsp;его сайте.</p>
      <p class="note-links">{src_link("ria")}</p>
    </aside>
  </div>
</section>'''


def video():
    v = DATA["video"]
    more = "".join(f'<li><a href="{esc(SRC[m["source"]]["url"])}" target="_blank" rel="noopener noreferrer"><strong>{t(m["title"])}</strong>'
                   f'<span>{t(m["note"])}</span><span class="ext" aria-hidden="true">↗</span></a></li>' for m in v["more"])
    audio_url = esc(SRC["voice"]["url"])
    audio = "".join(f'<li><a href="{audio_url}" target="_blank" rel="noopener noreferrer"><span class="a-num">{i:02d}</span>{t(a)}</a></li>'
                    for i, a in enumerate(v["audio"], 1))
    return f'''<section class="section video" id="video" aria-labelledby="vdTitle">
  <div class="wrap">
    <p class="kicker">Видео и голос</p>
    <h2 id="vdTitle">Услышать рассказ свидетеля</h2>
    <div class="video-grid">
      <div class="player">
        <div class="player-frame"><iframe src="https://rutube.ru/play/embed/{v["rutube_id"]}/" title="{esc(v["title"])} — Владимир Георгиевич Галактионов, RUTUBE" loading="lazy" allow="clipboard-write; autoplay; encrypted-media; fullscreen; picture-in-picture" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe></div>
        <p class="player-note">{t(v["note"])} Если плеер не загрузился — <a href="{esc(SRC["rutube"]["url"])}" target="_blank" rel="noopener noreferrer">откройте запись на&nbsp;RUTUBE ↗</a></p>
      </div>
      <div class="video-more"><h3>Другие записи и&nbsp;сюжеты</h3><ul class="more-list">{more}</ul></div>
    </div>
    <div class="audio">
      <h3>Воспоминания от&nbsp;первого лица</h3>
      <p>{t(v["audio_intro"])}</p>
      <ol class="audio-list">{audio}</ol>
    </div>
  </div>
</section>'''


def research():
    return '''<section class="section research" id="archive" aria-labelledby="rsTitle">
  <div class="wrap research-grid">
    <div>
      <p class="kicker">Исследования</p>
      <h2 id="rsTitle">«Герои самопожертвования»</h2>
    </div>
    <div class="prose">
      <p>Владимир Георгиевич участвует в&nbsp;работе по&nbsp;увековечиванию памяти героев самопожертвования. Это отдельное направление его деятельности, а&nbsp;не&nbsp;часть личной биографии.</p>
      <p>В&nbsp;рамках совместного исследовательского проекта подготовлен цифровой реестр на&nbsp;456 позиций, архив оригиналов и&nbsp;расшифровки. Данные проходят независимую проверку и&nbsp;не&nbsp;публикуются здесь как установленные факты.</p>
      <p class="muted">Семейные фотографии, записи интервью, афиши встреч и&nbsp;письма можно добавить в&nbsp;архив. Для каждого предмета сохраняются дата, автор, место, контекст и&nbsp;разрешение на&nbsp;публикацию.</p>
    </div>
  </div>
</section>'''


def sources():
    items = "".join(
        f'<li><a href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer"><span class="s-org">{t(s["org"])}</span>'
        f'<span class="s-title">{t(s["title"])}</span>{("<span class=s-date>" + t(s["date"]) + "</span>") if s.get("date") else ""}</a></li>'
        for k, s in SRC.items())
    return f'''<section class="section sources" id="sources" aria-labelledby="srTitle">
  <div class="wrap">
    <p class="kicker">Источники</p>
    <h2 id="srTitle">Откуда эти сведения</h2>
    <ol class="source-list">{items}</ol>
    <div class="accuracy prose">
      <h3>Об&nbsp;источниках и&nbsp;точности</h3>
      <p>Тексты сайта — собственные пересказы по&nbsp;открытым публикациям; полные чужие статьи не&nbsp;копируются. Публикация фотографий согласована с&nbsp;Владимиром Георгиевичем; у&nbsp;каждого снимка указаны автор и&nbsp;первая публикация. Семейные фото — из&nbsp;его архива.</p>
      <p>В&nbsp;названии союза и&nbsp;в&nbsp;ряде публикаций встречается «900 дней»; фактическая продолжительность блокады Ленинграда — 872&nbsp;дня. Это различие сохранено намеренно.</p>
    </div>
  </div>
</section>'''


def footer():
    return f'''<footer class="site-footer">
  <div class="wrap footer-row">
    <div><strong>Владимир Георгиевич Галактионов</strong><p>Личный архив · рабочая редакция от&nbsp;{t(DATA["meta"]["edition"])}</p></div>
    <a class="to-top" href="#home">Наверх ↑</a>
  </div>
</footer>
<dialog class="lightbox" id="lightbox" aria-label="Просмотр фотографии">
  <div class="lb-inner">
    <div class="lb-bar"><p class="lb-count" id="lbCount"></p><button type="button" class="lb-close" id="lbClose" aria-label="Закрыть просмотр">Закрыть ✕</button></div>
    <div class="lb-stage"><button type="button" class="lb-nav prev" id="lbPrev" aria-label="Предыдущее фото">‹</button>
      <img id="lbImg" alt=""><button type="button" class="lb-nav next" id="lbNext" aria-label="Следующее фото">›</button></div>
    <div class="lb-caption" id="lbCaption"></div>
  </div>
</dialog>
<div class="toast" id="toast" role="status" aria-live="polite"></div>'''


def lightbox_data():
    out = []
    for p in DATA["photos"]:
        if not p.get("publish"):
            continue
        big = f"assets/photos/{p['id']}-{p['sizes'][-1]}"
        out.append({"id": p["id"], "webp": big + ".webp", "jpg": big + ".jpg", "alt": p["alt"],
                    "title": p["title"], "caption": p["caption"], "date": p["date"], "credit": p["credit"],
                    "url": SRC[p["source"]]["url"] if p.get("source") else "",
                    "org": SRC[p["source"]]["org"] if p.get("source") else ""})
    return json.dumps(out, ensure_ascii=False).replace("</", "<\\/")


def page():
    m = DATA["meta"]
    return f'''<!DOCTYPE html>
<html lang="ru" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(m["title"])}</title>
<meta name="description" content="{esc(m["description"])}">
<meta name="robots" content="noindex,follow">
<meta name="theme-color" content="#f6f1e7">
<meta property="og:type" content="profile">
<meta property="og:locale" content="ru_RU">
<meta property="og:site_name" content="Личный архив Владимира Галактионова">
<meta property="og:title" content="Владимир Георгиевич Галактионов — ребёнок блокадного Ленинграда">
<meta property="og:description" content="{esc(m["description"])}">
<meta property="og:url" content="{esc(m["url"])}">
<meta property="og:image" content="{esc(m["og_image"])}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Владимир Георгиевич Галактионов">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="assets/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<link rel="preload" href="assets/fonts/Lora-Variable.woff" as="font" type="font/woff" crossorigin>
<link rel="stylesheet" href="assets/site.css">
<script>document.documentElement.classList.replace('no-js','js');try{{var s=localStorage.getItem('gk-size'),c=localStorage.getItem('gk-contrast');if(s)document.documentElement.dataset.size=s;if(c==='1')document.documentElement.classList.add('hc')}}catch(e){{}}</script>
<script src="assets/site.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Перейти к&nbsp;содержанию</a>
{header()}
<main id="main">
{hero()}
{about()}
{stories()}
{timeline()}
{meetings()}
{gallery()}
{video()}
{research()}
{sources()}
</main>
{footer()}
<script type="application/json" id="photoData">{lightbox_data()}</script>
</body>
</html>
'''


def write_sources_csv():
    import csv
    with open(ROOT / "sources.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Код", "Организация", "Публикация", "Дата", "URL", "Где используется"])
        for k, s in SRC.items():
            used = [st["id"] for st in DATA["stories"] + DATA["meetings"] if k in st["sources"]]
            used += [p["id"] for p in DATA["photos"] if p.get("source") == k]
            w.writerow([k, s["org"], s["title"], s.get("date", ""), s["url"], ", ".join(used)])


if __name__ == "__main__":
    write_sources_csv()
    out = page()
    (ROOT / "index.html").write_text(out, encoding="utf-8")
    print(f"index.html: {len(out):,} байт, историй: {len(DATA['stories'])}, фото: {sum(1 for p in DATA['photos'] if p.get('publish'))}")
