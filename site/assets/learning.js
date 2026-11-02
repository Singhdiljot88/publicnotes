(() => {
  'use strict';
  const grid = document.getElementById('library-grid');
  if (grid) {
    const form = document.getElementById('library-filters');
    const query = document.getElementById('library-query');
    const series = document.getElementById('library-series');
    const theme = document.getElementById('library-theme');
    const count = document.getElementById('library-count');
    const empty = document.getElementById('library-empty');
    const more = document.getElementById('library-more');
    const cards = Array.from(grid.querySelectorAll('.library-card'));
    let limit = 24;
    const params = new URLSearchParams(location.search);
    query.value = params.get('q') || '';
    if (Array.from(series.options).some(o => o.value === params.get('series'))) series.value = params.get('series');
    if (Array.from(theme.options).some(o => o.value === params.get('theme'))) theme.value = params.get('theme');
    const apply = () => {
      const terms = query.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
      const matches = cards.filter(card => (series.value === 'all' || card.dataset.series === series.value) &&
        (theme.value === 'all' || card.dataset.theme === theme.value) && terms.every(term => card.dataset.query.includes(term)));
      cards.forEach(card => { card.hidden = true; });
      matches.slice(0, limit).forEach(card => { card.hidden = false; });
      count.textContent = `${matches.length} ${matches.length === 1 ? 'note matches' : 'notes match'} · showing ${Math.min(matches.length, limit)}`;
      empty.hidden = matches.length !== 0;
      more.hidden = matches.length <= limit;
      const next = new URLSearchParams();
      if (query.value.trim()) next.set('q', query.value.trim());
      if (series.value !== 'all') next.set('series', series.value);
      if (theme.value !== 'all') next.set('theme', theme.value);
      history.replaceState(null, '', location.pathname + (next.size ? '?' + next.toString() : ''));
    };
    [query, series, theme].forEach(control => control.addEventListener(control === query ? 'input' : 'change', () => { limit = 24; apply(); }));
    form.addEventListener('submit', event => { event.preventDefault(); apply(); });
    form.addEventListener('reset', () => { setTimeout(() => { limit = 24; apply(); }, 0); });
    more.addEventListener('click', () => {
      const previous = new Set(cards.filter(card => !card.hidden));
      limit += 24;
      apply();
      const next = cards.find(card => !card.hidden && !previous.has(card));
      next?.querySelector('a')?.focus();
    });
    apply();
  }
  document.getElementById('copy-feed')?.addEventListener('click', async () => {
    const status = document.getElementById('feed-status');
    try {
      await navigator.clipboard.writeText('https://publicnotes.org/feed.xml');
      status.textContent = 'Feed address copied.';
    } catch {
      status.textContent = 'Copy this address: https://publicnotes.org/feed.xml';
    }
  });
})();
