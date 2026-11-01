(function () {
  // mobile menu
  var mb = document.querySelector('.menu-btn'), nav = document.getElementById('sitenav');
  if (mb && nav) mb.addEventListener('click', function () {
    var open = nav.classList.toggle('open'); mb.setAttribute('aria-expanded', open);
  });

  // share
  if (navigator.share) document.documentElement.classList.add('has-share');
  document.querySelectorAll('.share').forEach(function (box) {
    var url = box.dataset.url, title = box.dataset.title;
    var n = box.querySelector('.share-native');
    if (n) n.addEventListener('click', function () { navigator.share({ title: title, url: url }).catch(function () {}); });
    var c = box.querySelector('.share-copy');
    if (c) c.addEventListener('click', function () {
      var done = function () { c.textContent = 'Link copied'; setTimeout(function () { c.textContent = 'Copy link'; }, 2000); };
      if (navigator.clipboard) navigator.clipboard.writeText(url).then(done, function () { prompt('Copy this link', url); });
      else prompt('Copy this link', url);
    });
  });

  // hub filter + search
  var grid = document.getElementById('note-grid');
  if (grid) {
    var cards = [].slice.call(grid.querySelectorAll('.note-card'));
    var input = document.getElementById('note-search'), count = document.getElementById('result-count');
    var theme = 'all';
    var apply = function () {
      var q = (input.value || '').toLowerCase().trim(), shown = 0;
      cards.forEach(function (c) {
        var ok = (theme === 'all' || c.dataset.theme === theme) && (!q || c.dataset.search.indexOf(q) !== -1);
        c.hidden = !ok; if (ok) shown++;
      });
      count.textContent = 'Showing ' + shown + (shown === 1 ? ' note' : ' notes');
    };
    document.querySelectorAll('.chip').forEach(function (ch) {
      ch.addEventListener('click', function () {
        document.querySelectorAll('.chip').forEach(function (x) { x.classList.remove('active'); });
        ch.classList.add('active'); theme = ch.dataset.filter; apply();
      });
    });
    input.addEventListener('input', apply);
    var h = location.hash.match(/^#theme-(\d+)$/);
    if (h) { var b = document.querySelector('.chip[data-filter="' + h[1] + '"]'); if (b) b.click(); }
  }

  // glossary search
  var gs = document.getElementById('gl-search');
  if (gs) gs.addEventListener('input', function () {
    var q = gs.value.toLowerCase().trim();
    document.querySelectorAll('.term').forEach(function (t) { t.hidden = q && t.dataset.search.indexOf(q) === -1; });
    document.querySelectorAll('.letter').forEach(function (l) { l.hidden = !!q; });
  });

  // quiz
  var quiz = document.querySelector('.quiz');
  if (quiz) {
    var total = +quiz.dataset.total, answered = 0, right = 0;
    quiz.querySelectorAll('.q').forEach(function (q) {
      var opts = q.querySelectorAll('.opt');
      opts.forEach(function (o) {
        o.addEventListener('click', function () {
          var ok = o.dataset.correct === '1';
          opts.forEach(function (x) { x.disabled = true; if (x.dataset.correct === '1') x.classList.add('right'); });
          if (!ok) o.classList.add('wrong');
          q.querySelector('.explain').hidden = false;
          answered++; if (ok) right++;
          if (answered === total) {
            var s = document.querySelector('.quiz-score');
            s.querySelector('.score-text').textContent = 'You scored ' + right + ' out of ' + total + '. ' +
              (right === total ? 'Perfect!' : right >= total - 1 ? 'Nearly there.' : 'Read the linked notes and try again.');
            s.hidden = false; s.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        });
      });
    });
  }
})();
