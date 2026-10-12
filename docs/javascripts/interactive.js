// Two-pane catalog (.ea-app[data-ea-app]) on the Scenarios page.
//   Left: cards (.ea-card). Clicking a card selects it and fills the
//   right-hand viewer. The first card (or the one named in the URL hash)
//   opens on load.
//   Cards expand to show a short description. The viewer has two tabs:
//   «Промпт» (default) and «Детальний опис».
//     Descriptions are Markdown-rendered <section data-detail="slug"> blocks
//     in the hidden .ea-details container after the app; the selected one is
//     moved into the viewer and moved back on the next selection, so code
//     copy buttons and ids stay intact.
//     Prompts are base64 text in <script type="text/plain" data-prompt>
//     inside an inert <template class="ea-prompts">.
//   Filter chips (.ea-chip[data-tag]) narrow the list by data-tags.
// Copy buttons:
//   .ea-copy[data-copy-b64="id1 id2"]  copies base64 prompts joined by a blank line;
//   .ea-copy[data-copy-target="id"]    copies the <pre> inside #id;
//   .ea-copy                           copies the next <pre> sibling.
// Runs on first load and after Material instant navigation (document$).

(function () {
  function b64ToUtf8(b64) {
    var bin = atob(b64.replace(/\s+/g, ''));
    var bytes = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return new TextDecoder('utf-8').decode(bytes);
  }

  // Finds <script data-prompt="id"> in the page or inside inert templates.
  function promptById(id) {
    var s = document.querySelector('script[data-prompt="' + id + '"]');
    if (!s) {
      var tpls = document.querySelectorAll('template.ea-prompts');
      for (var i = 0; i < tpls.length && !s; i++) {
        s = tpls[i].content.querySelector('script[data-prompt="' + id + '"]');
      }
    }
    return s ? b64ToUtf8(s.textContent.trim()) : '';
  }

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
        var copied = document.execCommand('copy');
        document.body.removeChild(ta);
        if (copied) resolve();
        else reject(new Error('Copy unavailable'));
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

  // Shows the text for manual copying when the clipboard is unavailable.
  function showManual(btn, text) {
    var holder = btn.parentElement;
    var pre = holder.querySelector('pre.ea-manual');
    if (!pre) {
      pre = document.createElement('pre');
      pre.className = 'ea-manual';
      pre.tabIndex = 0;
      pre.appendChild(document.createElement('code'));
      holder.appendChild(pre);
    }
    pre.firstChild.textContent = text;
    pre.focus();
  }

  // One delegated listener for every copy button, including cloned ones.
  document.addEventListener('click', function (ev) {
    var btn = ev.target.closest && ev.target.closest('.ea-copy');
    if (!btn || btn.hasAttribute('data-copy-current')) return;
    var status = btn.parentElement.querySelector('.ea-copy-status');
    var b64 = btn.getAttribute('data-copy-b64');
    if (b64) {
      var text = b64.split(/\s+/).map(promptById).filter(Boolean).join('\n\n');
      copyText(text).then(function () {
        flash(btn);
        if (status) status.textContent = 'Повний текст скопійовано. Вставте його в новий чат.';
      }, function () {
        showManual(btn, text);
        if (status) status.textContent = 'Копіювання недоступне. Виділіть текст нижче й скопіюйте вручну.';
      });
      return;
    }
    var target = btn.getAttribute('data-copy-target');
    var pre = target ? document.getElementById(target) : btn.nextElementSibling;
    if (!target) while (pre && pre.tagName !== 'PRE') pre = pre.nextElementSibling;
    if (target && pre) pre = pre.querySelector('pre');
    if (!pre) return;
    copyText(pre.textContent.trim()).then(function () {
      flash(btn);
      if (status) status.textContent = 'Повний текст скопійовано.';
    }, function () {
      var details = pre.closest('details');
      if (details) details.open = true;
      if (status) status.textContent = 'Копіювання недоступне. Виділіть текст нижче й скопіюйте вручну.';
      pre.focus();
    });
  });

  function initApp(root) {
    var store = {};
    root.querySelectorAll('template.ea-prompts').forEach(function (t) {
      t.content.querySelectorAll('script[data-prompt]').forEach(function (s) {
        store[s.getAttribute('data-prompt')] = { raw: s.textContent.trim(), text: null };
      });
    });
    function promptText(slug) {
      var e = store[slug]; if (!e) return '';
      if (e.text == null) e.text = b64ToUtf8(e.raw);
      return e.text;
    }

    var shelf = root.nextElementSibling;
    if (!shelf || !shelf.classList.contains('ea-details')) shelf = document.querySelector('.ea-details');
    var details = {};
    if (shelf) shelf.querySelectorAll('[data-detail]').forEach(function (d) {
      details[d.getAttribute('data-detail')] = d;
    });

    var cards = Array.prototype.slice.call(root.querySelectorAll('.ea-card'));
    var viewer = root.querySelector('[data-ea-viewer]');
    if (!viewer) return;
    var vEmpty = viewer.querySelector('.ea-viewer__empty');
    var vContent = viewer.querySelector('.ea-viewer__content');
    var vTitle = viewer.querySelector('.ea-viewer__title');
    var vDetail = viewer.querySelector('[data-pane="detail"]');
    var vPre = viewer.querySelector('[data-pane="prompt"]');
    var vCode = viewer.querySelector('.ea-viewer__code');
    var vCopy = viewer.querySelector('[data-copy-current]');
    var tabs = Array.prototype.slice.call(viewer.querySelectorAll('.ea-vtab'));
    var current = null;
    var shown = null;
    var isMobile = function () { return window.matchMedia('(max-width: 76.1875em)').matches; };

    function showView(view) {
      tabs.forEach(function (t) {
        var on = t.getAttribute('data-view') === view;
        t.classList.toggle('is-active', on);
        t.setAttribute('aria-selected', on ? 'true' : 'false');
      });
      if (view === 'prompt' && current) {
        if (vCode.getAttribute('data-for') !== current) {
          vCode.textContent = promptText(current);
          vCode.setAttribute('data-for', current);
        }
        vPre.scrollTop = 0;
      }
      vPre.hidden = view !== 'prompt';
      vDetail.hidden = view !== 'detail';
    }

    function select(card, skipScroll) {
      var slug = card.getAttribute('data-slug');
      current = slug;
      var title = card.querySelector('.ea-card__title');
      var emoji = card.querySelector('.ea-card__emoji');
      vTitle.textContent = (emoji ? emoji.textContent + '  ' : '') + (title ? title.textContent : '');
      if (shown && shelf) shelf.appendChild(shown);
      shown = details[slug] || null;
      if (shown) vDetail.appendChild(shown);
      vDetail.scrollTop = 0;
      vEmpty.hidden = true;
      vContent.hidden = false;
      showView('prompt');
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
        if (open && card.getAttribute('data-slug') === current) return;
        setOpen(card, true);
        if (history.replaceState) history.replaceState(null, '', '#' + card.getAttribute('data-slug'));
        select(card, false);
      });
    });
    tabs.forEach(function (t) {
      t.addEventListener('click', function () { showView(t.getAttribute('data-view')); });
    });

    if (vCopy) vCopy.addEventListener('click', function () {
      if (!current) return;
      copyText(promptText(current)).then(function () { flash(vCopy); }, function () {
        showView('prompt');
        vPre.tabIndex = 0; vPre.focus();
      });
    });

    // Deep link: #slug opens that card; otherwise the first one.
    var hash = decodeURIComponent((window.location.hash || '').replace('#', ''));
    var byHash = cards.filter(function (c) { return c.getAttribute('data-slug') === hash; })[0];
    var initial = byHash || cards[0];
    if (initial) { setOpen(initial, true); select(initial, true); }
    if (byHash) root.scrollIntoView({ block: 'start' });

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

  // Left navigation toggle (wide screens). The choice is a per-viewer
  // convenience kept in localStorage; the page works without it.
  var NAV_KEY = 'ea-nav-collapsed';
  function navToggle() {
    var collapsed = false;
    try { collapsed = window.localStorage.getItem(NAV_KEY) === '1'; } catch (e) {}
    document.body.classList.toggle('ea-nav-collapsed', collapsed);
    var btn = document.querySelector('.ea-navtoggle');
    if (!btn) {
      btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'ea-navtoggle';
      var inner = document.querySelector('.md-header__inner');
      if (inner) inner.insertBefore(btn, inner.firstChild); else document.body.appendChild(btn);
      btn.addEventListener('click', function () {
        var now = !document.body.classList.contains('ea-nav-collapsed');
        document.body.classList.toggle('ea-nav-collapsed', now);
        try { window.localStorage.setItem(NAV_KEY, now ? '1' : '0'); } catch (e) {}
        label(btn, now);
      });
    }
    label(btn, collapsed);
  }
  function label(btn, collapsed) {
    btn.textContent = '☰';
    btn.title = collapsed ? 'Показати меню' : 'Сховати меню';
    btn.setAttribute('aria-label', btn.title);
    btn.setAttribute('aria-pressed', collapsed ? 'true' : 'false');
  }

  function init() {
    navToggle();
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
