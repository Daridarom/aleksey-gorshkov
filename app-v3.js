(() => {
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => [...root.querySelectorAll(s)];
  let content = { timeline: [], knowledge: [], projects: [], connections: {} };
  let feed = { items: [] };

  async function loadJSON(path) {
    const response = await fetch(`${path}?v=3`, { cache: 'no-store' });
    if (!response.ok) throw new Error(`${path}: ${response.status}`);
    return response.json();
  }

  function safe(text = '') {
    return String(text)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  function renderTimeline() {
    const root = $('#timeline');
    root.innerHTML = content.timeline.map(item => `
      <article class="timeline-item">
        <div class="timeline-year">${safe(item.year)}</div>
        <div>
          <h3>${safe(item.title)}</h3>
          <p>${safe(item.text)}</p>
          <div class="timeline-tags">${item.tags.map(t => `<span>${safe(t)}</span>`).join('')}</div>
        </div>
      </article>`).join('');
  }

  function renderKnowledge(category = 'Все') {
    const root = $('#knowledgeGrid');
    const items = category === 'Все' ? content.knowledge : content.knowledge.filter(x => x.category === category);
    root.innerHTML = items.map((item, index) => `
      <button class="knowledge-card ${item.wide ? 'wide' : ''}" data-knowledge="${safe(item.id)}" style="--card-color:${safe(item.color)}">
        <div class="knowledge-meta"><span>${safe(item.category)}</span><span>0${index + 1}</span></div>
        <h3>${safe(item.title)}</h3>
        <p>${safe(item.summary)}</p>
        <div class="status-row">${item.status.map(s => `<span>${safe(s)}</span>`).join('')}</div>
      </button>`).join('') || '<div class="loading-card">Пока здесь нет материалов.</div>';

    $$('[data-knowledge]').forEach(button => button.addEventListener('click', () => {
      const item = content.knowledge.find(x => x.id === button.dataset.knowledge);
      if (item) openContent(item.category, item.title, item.body, item.why, item.tags);
    }));
  }

  function renderKnowledgeFilters() {
    const root = $('#knowledgeFilters');
    const categories = ['Все', ...new Set(content.knowledge.map(x => x.category))];
    root.innerHTML = categories.map((name, i) => `<button class="library-filter ${i === 0 ? 'active' : ''}" data-knowledge-filter="${safe(name)}">${safe(name)}</button>`).join('');
    $$('[data-knowledge-filter]').forEach(button => button.addEventListener('click', () => {
      $$('[data-knowledge-filter]').forEach(x => x.classList.remove('active'));
      button.classList.add('active');
      renderKnowledge(button.dataset.knowledgeFilter);
    }));
  }

  function renderProjects() {
    const root = $('#projectsGrid');
    root.innerHTML = content.projects.map(item => `
      <article class="project-card">
        <div class="project-top"><span>${safe(item.period)}</span><span>${safe(item.role)}</span></div>
        <h3>${safe(item.title)}</h3>
        <p>${safe(item.summary)}</p>
        <button data-project="${safe(item.id)}">Посмотреть связи ↗</button>
      </article>`).join('');
    $$('[data-project]').forEach(button => button.addEventListener('click', () => {
      const item = content.projects.find(x => x.id === button.dataset.project);
      if (!item) return;
      openContent('проект', item.title, item.summary, `Моя роль: ${item.role}. Период: ${item.period}.`, item.tags);
    }));
  }

  function renderFeed(filter = 'Все') {
    const root = $('#feedGrid');
    const items = filter === 'Все' ? feed.items : feed.items.filter(x => x.source === filter);
    root.innerHTML = items.map(item => `
      <article class="feed-card ${item.featured ? 'featured' : ''}">
        <div class="feed-source"><span>${safe(item.source)}</span><span>${safe(item.date)}</span></div>
        <h3>${safe(item.title)}</h3>
        <p>${safe(item.summary)}</p>
        <a href="${safe(item.url)}" ${item.url.startsWith('http') ? 'target="_blank" rel="noreferrer"' : ''}>Открыть ↗</a>
      </article>`).join('') || '<div class="loading-card">В этом источнике пока нет записей.</div>';
  }

  function renderFeedFilters() {
    const root = $('#sourcePills');
    const names = ['Все', ...new Set(feed.items.map(x => x.source))];
    root.innerHTML = names.map((name, i) => `<button class="source-pill ${i === 0 ? 'active' : ''}" data-feed-filter="${safe(name)}">${safe(name)}</button>`).join('');
    $$('[data-feed-filter]').forEach(button => button.addEventListener('click', () => {
      $$('[data-feed-filter]').forEach(x => x.classList.remove('active'));
      button.classList.add('active');
      renderFeed(button.dataset.feedFilter);
    }));
  }

  function setupMap() {
    $$('.map-node').forEach(button => button.addEventListener('click', () => {
      $$('.map-node').forEach(x => x.classList.remove('active'));
      button.classList.add('active');
      const value = content.connections[button.dataset.node] || ['Связь', 'Этот узел пока развивается.'];
      $('#mapDetail').innerHTML = `<small>${safe(value[0])}</small><strong>${safe(value[1])}</strong>`;
    }));
  }

  function openContent(meta, title, body, why, tags = []) {
    $('#dialogMeta').textContent = meta;
    $('#dialogTitle').textContent = title;
    $('#dialogBody').textContent = body;
    $('#dialogWhy').textContent = why;
    $('#dialogTags').innerHTML = tags.map(t => `<span>${safe(t)}</span>`).join('');
    $('#contentDialog').showModal();
  }

  function buildSearchIndex() {
    const index = [];
    content.knowledge.forEach(item => index.push({ type: 'знание', title: item.title, text: `${item.summary} ${item.body} ${item.why} ${item.tags.join(' ')}`, anchor: '#knowledge' }));
    content.projects.forEach(item => index.push({ type: 'проект', title: item.title, text: `${item.summary} ${item.role} ${item.tags.join(' ')}`, anchor: '#projects' }));
    content.timeline.forEach(item => index.push({ type: 'этап', title: item.title, text: `${item.year} ${item.text} ${item.tags.join(' ')}`, anchor: '#me' }));
    feed.items.forEach(item => index.push({ type: 'сейчас', title: item.title, text: `${item.source} ${item.summary}`, anchor: item.url || '#now' }));
    return index;
  }

  function tokenize(query) {
    return query.toLowerCase().replace(/[.,!?;:()«»"']/g, ' ').split(/\s+/).filter(x => x.length > 2);
  }

  function yasenSearch(query) {
    const words = tokenize(query);
    const index = buildSearchIndex();
    const synonyms = {
      'дети': ['воспитание', 'педагогика', 'киноуроки'],
      'школа': ['воспитание', 'педагогика', 'киноуроки'],
      'ии': ['ai', 'инструменты', 'автоматизация'],
      'нейросеть': ['ai', 'инструменты'],
      'природа': ['экология', 'территория'],
      'космос': ['космизм', 'рко'],
      'люди': ['сообщества', 'команда', 'связи']
    };
    const expanded = [...words];
    words.forEach(w => { if (synonyms[w]) expanded.push(...synonyms[w]); });

    return index.map(item => {
      const hay = `${item.title} ${item.text}`.toLowerCase();
      const score = expanded.reduce((sum, word) => sum + (hay.includes(word) ? 1 : 0), 0);
      return { ...item, score };
    }).filter(x => x.score > 0).sort((a,b) => b.score - a.score).slice(0, 6);
  }

  function showYasenResults(query) {
    const root = $('#yasenResults');
    const results = yasenSearch(query);
    if (!query.trim()) {
      root.innerHTML = '<div class="yasen-empty">Спроси что-нибудь. Ясень лучше работает с человеческими словами, чем с пустотой 🙂</div>';
      return;
    }
    if (!results.length) {
      root.innerHTML = `<div class="yasen-empty">По запросу «${safe(query)}» Ясень пока ничего уверенного не нашёл. Это полезный сигнал: возможно, такую ветку стоит добавить в библиотеку.</div>`;
      return;
    }
    root.innerHTML = results.map(item => `
      <button type="button" class="yasen-result" data-yasen-anchor="${safe(item.anchor)}">
        <small>${safe(item.type)}</small>
        <strong>${safe(item.title)}</strong>
        <span>${safe(item.text.slice(0, 155))}${item.text.length > 155 ? '…' : ''}</span>
      </button>`).join('');
    $$('[data-yasen-anchor]').forEach(button => button.addEventListener('click', () => {
      const anchor = button.dataset.yasenAnchor;
      $('#yasenDialog').close();
      if (anchor.startsWith('#')) $(anchor)?.scrollIntoView({ behavior: 'smooth' });
      else window.open(anchor, '_blank', 'noopener');
    }));
  }

  function setupYasen() {
    const dialog = $('#yasenDialog');
    $$('[data-yasen-open]').forEach(button => button.addEventListener('click', () => {
      dialog.showModal();
      setTimeout(() => $('#yasenInput').focus(), 60);
    }));

    $('#yasenForm').addEventListener('submit', event => {
      if (event.submitter?.value === 'close') return;
      event.preventDefault();
      showYasenResults($('#yasenInput').value);
    });

    $$('[data-yasen-query]').forEach(button => button.addEventListener('click', () => {
      $('#yasenInput').value = button.dataset.yasenQuery;
      showYasenResults(button.dataset.yasenQuery);
    }));

    dialog.addEventListener('click', event => {
      if (event.target === dialog) dialog.close();
    });
    $('#contentDialog').addEventListener('click', event => {
      if (event.target === $('#contentDialog')) $('#contentDialog').close();
    });
  }

  async function init() {
    try {
      [content, feed] = await Promise.all([loadJSON('content-v3.json'), loadJSON('feed-v3.json')]);
      renderTimeline();
      renderKnowledgeFilters();
      renderKnowledge();
      renderProjects();
      renderFeedFilters();
      renderFeed();
      setupMap();
      setupYasen();
    } catch (error) {
      console.error(error);
      $('#feedGrid').innerHTML = '<div class="loading-card">Не удалось загрузить динамические данные. Обновите страницу.</div>';
    }
  }

  init();
})();
