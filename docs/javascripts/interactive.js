// Two-pane catalog used on the Skills and Delegation pages.
//   Left: cards (.ea-card). Opening a card selects it and loads the matching
//   <template data-detail="slug"> into the right-hand viewer.
//   Filter chips (.ea-chip[data-tag]) narrow the list by data-tags.
// Copy buttons (.ea-copy) copy the text of the next <pre> element.
// Runs on first load and after Material instant navigation (document$).

(function () {
  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      try {
        var ta = document.createElement('textarea');
        ta.value = text; ta.setAttribute('readonly', '');
        ta.style.position = 'fixed'; ta.style.opacity = '0';
        document.body.appendChild(ta); ta.select();
        document.execCommand('copy'); document.body.removeChild(ta);
        resolve();
      } catch (e) { reject(e); }
    });
  }

  function flash(btn) {
    if (btn._prev === undefined) btn._prev = btn.textContent;
    btn.classList.add('is-copied');
    btn.textContent = 'Скопійовано';
    clearTimeout(btn._timer);
    btn._timer = setTimeout(function () {
      btn.classList.remove('is-copied');
      btn.textContent = btn._prev;
    }, 1800);
  }

  // One delegated listener for every copy button, including cloned ones.
  document.addEventListener('click', function (ev) {
    var btn = ev.target.closest && ev.target.closest('.ea-copy');
    if (!btn) return;
    var pre = btn.nextElementSibling;
    while (pre && pre.tagName !== 'PRE') pre = pre.nextElementSibling;
    if (!pre) return;
    copyText(pre.textContent.trim()).then(function () { flash(btn); }, function () {});
  });

  function initApp(root) {
    var store = {};
    root.querySelectorAll('.ea-details template[data-detail]').forEach(function (t) {
      store[t.getAttribute('data-detail')] = t;
    });
    var cards = Array.prototype.slice.call(root.querySelectorAll('.ea-card'));
    var viewer = root.querySelector('[data-ea-viewer]');
    if (!viewer) return;
    var vEmpty = viewer.querySelector('.ea-viewer__empty');
    var vContent = viewer.querySelector('.ea-viewer__content');
    var vTitle = viewer.querySelector('.ea-viewer__bar');
    var vDetail = viewer.querySelector('.ea-viewer__detail');
    var isMobile = function () { return window.matchMedia('(max-width: 76.1875em)').matches; };

    function select(card, skipScroll) {
      var slug = card.getAttribute('data-slug');
      var title = card.querySelector('.ea-card__title');
      vTitle.textContent = title ? title.textContent : '';
      var tpl = store[slug];
      vDetail.replaceChildren(tpl ? tpl.content.cloneNode(true) : document.createDocumentFragment());
      vDetail.scrollTop = 0;
      vEmpty.hidden = true;
      vContent.hidden = false;
      cards.forEach(function (c) { c.classList.toggle('is-active', c === card); });
      if (!skipScroll && isMobile()) viewer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function setOpen(card, open) {
      card.querySelector('.ea-card__head').setAttribute('aria-expanded', open ? 'true' : 'false');
      var body = card.querySelector('.ea-card__body');
      if (body) body.hidden = !open;
      card.classList.toggle('is-open', open);
    }

    cards.forEach(function (card) {
      var head = card.querySelector('.ea-card__head');
      head.addEventListener('click', function () {
        var open = head.getAttribute('aria-expanded') === 'true';
        cards.forEach(function (c) { setOpen(c, false); });
        if (!open) { setOpen(card, true); select(card, false); }
      });
    });

    // Deep link: #skill-slug opens that card; otherwise the first one.
    var hash = (window.location.hash || '').replace('#', '');
    var initial = cards.filter(function (c) { return c.getAttribute('data-slug') === hash; })[0] || cards[0];
    if (initial) { setOpen(initial, true); select(initial, true); }

    var chips = Array.prototype.slice.call(root.querySelectorAll('.ea-filter .ea-chip'));
    var active = new Set();
    var allChip = root.querySelector('.ea-filter .ea-chip[data-tag=""]');
    function apply() {
      cards.forEach(function (c) {
        var tags = (c.getAttribute('data-tags') || '').split(' ');
        var show = active.size === 0 || Array.from(active).some(function (t) { return tags.indexOf(t) !== -1; });
        c.parentElement.style.display = show ? '' : 'none';
      });
      if (allChip) allChip.classList.toggle('is-active', active.size === 0);
    }
    chips.forEach(function (ch) {
      ch.addEventListener('click', function () {
        var tag = ch.getAttribute('data-tag');
        if (tag === '') { active.clear(); chips.forEach(function (c) { c.classList.remove('is-active'); }); }
        else if (active.has(tag)) { active.delete(tag); ch.classList.remove('is-active'); }
        else { active.add(tag); ch.classList.add('is-active'); }
        apply();
      });
    });
    apply();
  }

  function init() {
    document.querySelectorAll('.ea-app[data-ea-app]').forEach(function (root) {
      if (root._eaReady) return;
      root._eaReady = true;
      initApp(root);
    });
  }

  function schedule() {
    if (window.requestAnimationFrame) window.requestAnimationFrame(init);
    else window.setTimeout(init, 0);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', schedule, { once: true });
  else schedule();
  if (window.document$) window.document$.subscribe(schedule);
})();
