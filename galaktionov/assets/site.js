/* Личный архив В. Г. Галактионова — удобства поверх статической страницы. */
(function () {
  'use strict';
  var doc = document.documentElement;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) { /* приватный режим */ } }
  };

  /* ---------- Toast ---------- */
  var toastEl = $('#toast'), toastTimer;
  function toast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove('show'); }, 3200);
  }

  /* ---------- Меню ---------- */
  var menuBtn = $('#menuBtn'), panel = $('#menuPanel');
  function setMenu(open) {
    if (!menuBtn) return;
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    panel.classList.toggle('open', open);
  }
  if (menuBtn) {
    menuBtn.addEventListener('click', function () { setMenu(menuBtn.getAttribute('aria-expanded') !== 'true'); });
    $$('.main-nav a', panel).forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && panel.classList.contains('open')) { setMenu(false); menuBtn.focus(); }
    });
  }

  /* ---------- Размер шрифта и контраст ---------- */
  var sizes = ['-1', '0', '1', '2', '3'];
  function currentSize() { return doc.dataset.size || '0'; }
  function setSize(v) {
    doc.dataset.size = v;
    store.set('gk-size', v);
    var labels = { '-1': 'Шрифт уменьшен', '0': 'Обычный шрифт', '1': 'Шрифт крупнее', '2': 'Шрифт крупный', '3': 'Шрифт очень крупный' };
    toast(labels[v]);
  }
  var plus = $('#fontPlus'), minus = $('#fontMinus'), hc = $('#contrastBtn');
  if (plus) plus.addEventListener('click', function () { var i = sizes.indexOf(currentSize()); if (i < sizes.length - 1) setSize(sizes[i + 1]); else toast('Это самый крупный шрифт'); });
  if (minus) minus.addEventListener('click', function () { var i = sizes.indexOf(currentSize()); if (i > 0) setSize(sizes[i - 1]); else toast('Это самый мелкий шрифт'); });
  if (hc) {
    hc.setAttribute('aria-pressed', doc.classList.contains('hc') ? 'true' : 'false');
    hc.addEventListener('click', function () {
      var on = !doc.classList.contains('hc');
      doc.classList.toggle('hc', on);
      hc.setAttribute('aria-pressed', on ? 'true' : 'false');
      store.set('gk-contrast', on ? '1' : '0');
      toast(on ? 'Высокий контраст включён' : 'Обычные цвета');
    });
  }

  /* ---------- Истории: раскрытие, ссылки, «Поделиться» ---------- */
  function storyUrl(id) { return location.href.split('#')[0] + '#' + id; }
  function openStory(id, scroll) {
    var el = document.getElementById(id);
    if (el && el.classList.contains('mrow')) { var md = $('details', el); if (md) md.open = true; if (scroll) el.scrollIntoView({ block: 'start' }); return true; }
    if (!el || !el.classList.contains('story')) return false;
    var d = $('details', el);
    if (d) d.open = true;
    if (scroll) el.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
    return true;
  }
  $$('.story-body').forEach(function (d) {
    d.addEventListener('toggle', function () {
      var art = d.closest('.story');
      art.classList.toggle('is-open', d.open);
      if (d.open && history.replaceState) history.replaceState(null, '', '#' + art.id);
    });
  });
  $$('[data-open-story]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var id = a.getAttribute('data-open-story');
      if (openStory(id, true)) { e.preventDefault(); if (history.pushState) history.pushState(null, '', '#' + id); }
    });
  });
  function handleHash() {
    var id = decodeURIComponent(location.hash.slice(1));
    if (id) openStory(id, true);
  }
  window.addEventListener('hashchange', handleHash);
  if (location.hash) setTimeout(handleHash, 60);

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    return new Promise(function (resolve, reject) {
      var ta = document.createElement('textarea');
      ta.value = text; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy') ? resolve() : reject(); } catch (e) { reject(e); }
      document.body.removeChild(ta);
    });
  }
  function copyLink(id) {
    var url = storyUrl(id);
    copyText(url).then(function () { toast('Ссылка на историю скопирована'); }, function () { toast('Скопируйте ссылку: ' + url); });
  }
  $$('[data-copy]').forEach(function (b) { b.addEventListener('click', function () { copyLink(b.getAttribute('data-copy')); }); });
  $$('[data-share]').forEach(function (b) {
    b.addEventListener('click', function () {
      var id = b.getAttribute('data-share');
      var data = { title: b.getAttribute('data-title') + ' — Владимир Галактионов', url: storyUrl(id) };
      if (navigator.share) {
        navigator.share(data).catch(function (err) { if (err && err.name !== 'AbortError') copyLink(id); });
      } else { copyLink(id); }
    });
  });

  /* ---------- Свернуть историю (кнопка в конце текста) ---------- */
  $$('[data-close]').forEach(function (b) {
    b.addEventListener('click', function () {
      var art = document.getElementById(b.getAttribute('data-close'));
      var d = $('details', art); if (d) d.open = false;
      art.scrollIntoView({ block: 'start' });
      var s = $('summary', art); if (s) s.focus({ preventScroll: true });
    });
  });

  /* ---------- Кнопка «Наверх» ---------- */
  var ft = $('#floatTop');
  if (ft) {
    var onScroll = function () { ft.classList.toggle('show', window.scrollY > window.innerHeight * 2); };
    window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
  }

  /* ---------- Печать ---------- */
  var openedForPrint = [];
  $$('[data-print]').forEach(function (b) {
    b.addEventListener('click', function () {
      var art = document.getElementById(b.getAttribute('data-print'));
      document.body.classList.add('print-one');
      art.classList.add('print-target');
      window.print();
    });
  });
  window.addEventListener('beforeprint', function () {
    $$('.story-body').forEach(function (d) {
      var art = d.closest('.story');
      var needed = !document.body.classList.contains('print-one') || art.classList.contains('print-target');
      if (needed && !d.open) { d.open = true; openedForPrint.push(d); }
    });
  });
  window.addEventListener('afterprint', function () {
    openedForPrint.forEach(function (d) { d.open = false; });
    openedForPrint = [];
    document.body.classList.remove('print-one');
    $$('.print-target').forEach(function (a) { a.classList.remove('print-target'); });
  });

  /* ---------- Просмотр фото ---------- */
  var lb = $('#lightbox'), lbImg = $('#lbImg'), lbCap = $('#lbCaption'), lbCount = $('#lbCount');
  var photos = [];
  try { photos = JSON.parse($('#photoData').textContent); } catch (e) { photos = []; }
  var idx = 0, lastFocus = null;
  var webpOk = (function () { try { return document.createElement('canvas').toDataURL('image/webp').indexOf('data:image/webp') === 0; } catch (e) { return false; } })();
  function esc(s) { var d = document.createElement('div'); d.textContent = s || ''; return d.innerHTML; }
  function show(i) {
    if (!photos.length) return;
    idx = (i + photos.length) % photos.length;
    var p = photos[idx];
    lbImg.src = webpOk ? p.webp : p.jpg;
    lbImg.alt = p.alt;
    lbCount.textContent = 'Фото ' + (idx + 1) + ' из ' + photos.length;
    var src = p.url ? ' · <a href="' + esc(p.url) + '" target="_blank" rel="noopener noreferrer">' + esc(p.org) + ' ↗</a>' : '';
    lbCap.innerHTML = '<strong>' + esc(p.title) + '</strong>' + esc(p.caption) +
      '<span class="lb-credit">' + esc(p.date) + ' · ' + esc(p.credit) + src + '</span>';
    [idx + 1, idx - 1].forEach(function (n) { var q = photos[(n + photos.length) % photos.length]; var im = new Image(); im.src = webpOk ? q.webp : q.jpg; });
  }
  function openLb(id) {
    if (!lb || typeof lb.showModal !== 'function') return false;
    var i = 0;
    photos.forEach(function (p, n) { if (p.id === id) i = n; });
    lastFocus = document.activeElement;
    show(i);
    lb.showModal();
    $('#lbClose').focus();
    return true;
  }
  function closeLb() { if (lb.open) lb.close(); }
  if (lb) {
    lb.addEventListener('close', function () { lbImg.removeAttribute('src'); if (lastFocus) lastFocus.focus(); });
    $('#lbClose').addEventListener('click', closeLb);
    $('#lbPrev').addEventListener('click', function () { show(idx - 1); });
    $('#lbNext').addEventListener('click', function () { show(idx + 1); });
    lb.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { e.preventDefault(); show(idx - 1); }
      else if (e.key === 'ArrowRight') { e.preventDefault(); show(idx + 1); }
    });
    lb.addEventListener('click', function (e) { if (e.target === lb || e.target.classList.contains('lb-stage')) closeLb(); });
    var sx = null, sy = null;
    var stage = $('.lb-stage', lb);
    stage.addEventListener('touchstart', function (e) { sx = e.touches[0].clientX; sy = e.touches[0].clientY; }, { passive: true });
    stage.addEventListener('touchend', function (e) {
      if (sx === null) return;
      var dx = e.changedTouches[0].clientX - sx, dy = e.changedTouches[0].clientY - sy;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) show(idx + (dx < 0 ? 1 : -1));
      sx = sy = null;
    });
  }
  $$('.photo-open').forEach(function (b) {
    b.addEventListener('click', function () {
      if (!openLb(b.getAttribute('data-photo'))) {
        var p = photos.filter(function (x) { return x.id === b.getAttribute('data-photo'); })[0];
        if (p) window.open(p.jpg, '_blank', 'noopener');
      }
    });
  });
})();
