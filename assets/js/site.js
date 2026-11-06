/* Hidalgo Eye Care & Optical: small page behaviors. The site works without this file,
   apart from the mobile menu, the open/closed badge and the carousel arrows. */
(function () {
  'use strict';

  /* Language. Regular pages exist in each language (/page/ and /es/page/) and the button is a
     plain link between them. Only 404.html holds both languages and switches in place. */
  var htmlEl = document.documentElement;
  function setAttrs(lang) {
    /* [Spanish source, attribute it fills, where the English original is kept] */
    [['data-aria-es', 'aria-label', 'ariaEn'], ['data-alt-es', 'alt', 'altEn'], ['data-title-es', 'title', 'titleEn']].forEach(function (x) {
      document.querySelectorAll('[' + x[0] + ']').forEach(function (el) {
        if (el === htmlEl) return;
        if (el.dataset[x[2]] === undefined) el.dataset[x[2]] = el.getAttribute(x[1]) || '';
        el.setAttribute(x[1], lang === 'es' ? el.getAttribute(x[0]) : el.dataset[x[2]]);
      });
    });
  }
  function setLang(lang) {
    htmlEl.setAttribute('data-lang', lang);
    htmlEl.lang = lang;
    document.title = htmlEl.getAttribute(lang === 'es' ? 'data-title-es' : 'data-title-en');
    setAttrs(lang);
    window.dispatchEvent(new Event('resize')); /* carousels recount their pages */
  }
  var langBtn = document.getElementById('langBtn');
  if (htmlEl.hasAttribute('data-both')) {
    setAttrs(htmlEl.getAttribute('data-lang') || 'en');
    if (langBtn) {
      langBtn.addEventListener('click', function (e) {
        e.preventDefault();
        var next = htmlEl.getAttribute('data-lang') === 'es' ? 'en' : 'es';
        try { localStorage.setItem('lang', next); } catch (err) { /* still switches for this page */ }
        setLang(next);
      });
    }
  }

  var yr = document.getElementById('yr');
  if (yr) yr.textContent = new Date().getFullYear();

  /* Mobile menu */
  var mb = document.getElementById('menuBtn');
  var nav = document.getElementById('nav');
  if (mb && nav) {
    var setMenu = function (open) {
      nav.classList.toggle('open', open);
      mb.setAttribute('aria-expanded', String(open));
    };
    mb.addEventListener('click', function () { setMenu(!nav.classList.contains('open')); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('open')) { setMenu(false); mb.focus(); }
    });
  }

  /* Open / closed badge, Tampa time, closed on the 11 federal holidays */
  var status = document.getElementById('status');
  if (status) {
    try {
      var parts = new Intl.DateTimeFormat('en-US', {
        timeZone: 'America/New_York', year: 'numeric', month: 'numeric', day: 'numeric',
        hour: 'numeric', minute: 'numeric', hour12: false
      }).formatToParts(new Date());
      var g = function (t) { return +parts.find(function (p) { return p.type === t; }).value; };
      var y = g('year'), m = g('month'), d = g('day'), h = g('hour') % 24, min = g('minute');
      var dow = new Date(y, m - 1, d).getDay();
      var nth = function (mo, wd, n) { var f = new Date(y, mo - 1, 1).getDay(); return 1 + ((wd - f + 7) % 7) + (n - 1) * 7; };
      var last = function (mo, wd) { var ld = new Date(y, mo, 0); return ld.getDate() - ((ld.getDay() - wd + 7) % 7); };
      /* Weekend holidays are observed on the nearest weekday */
      var obs = function (mo, dd) {
        var w = new Date(y, mo - 1, dd).getDay();
        var t = new Date(y, mo - 1, dd + (w === 6 ? -1 : w === 0 ? 1 : 0));
        return [t.getMonth() + 1, t.getDate()];
      };
      var hol = [obs(1, 1), [1, nth(1, 1, 3)], [2, nth(2, 1, 3)], [5, last(5, 1)], obs(6, 19), obs(7, 4),
        [9, nth(9, 1, 1)], [10, nth(10, 1, 2)], obs(11, 11), [11, nth(11, 4, 4)], obs(12, 25)];
      /* New Year's Day on a Saturday is observed on Dec 31 of the year before */
      if (new Date(y + 1, 0, 1).getDay() === 6) hol.push([12, 31]);
      var isHol = hol.some(function (x) { return x[0] === m && x[1] === d; });
      var mins = h * 60 + min;
      var open = !isHol && dow >= 1 && dow <= 5 && mins >= 540 && mins < 1020;
      /* Each page only has its own language's badge text */
      var put = function (id, value) { var el = document.getElementById(id); if (el) el.textContent = value; };
      if (open) {
        status.classList.add('open');
        put('stateEn', 'Open now'); put('subEn', 'Until 5 PM');
        put('stateEs', 'Abierto ahora'); put('subEs', 'Hasta las 5 PM');
      } else {
        put('stateEn', isHol ? 'Closed today for the holiday' : 'Closed now'); put('subEn', 'Mon–Fri 9–5');
        put('stateEs', isHol ? 'Cerrado hoy por día feriado' : 'Cerrado ahora'); put('subEs', 'Lun–Vie 9–5');
      }
    } catch (err) { /* the static hours stay visible */ }
  }

  /* Review carousels (the reviews themselves are plain HTML) */
  var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('[data-carousel]').forEach(function (root) {
    var track = root.querySelector('.rv-track');
    var dots = root.querySelector('.rv-dots');
    var prev = root.querySelector('[data-dir="-1"]');
    var next = root.querySelector('[data-dir="1"]');
    var count = track.children.length;
    var perView = function () {
      return Math.max(1, Math.round(track.clientWidth / track.firstElementChild.getBoundingClientRect().width));
    };
    /* Distance from one page of cards to the next, gap included */
    var pageStep = function () {
      return (track.children[1].offsetLeft - track.children[0].offsetLeft) * perView();
    };
    function draw() {
      if (!track.clientWidth) return;
      var n = Math.ceil(count / perView());
      var p = Math.min(Math.round(track.scrollLeft / pageStep()), n - 1);
      if (n > 10) {
        /* One review per screen on phones: 20 dots would not fit, so show "3 / 20" */
        dots.className = 'rv-dots rv-count';
        dots.textContent = (p + 1) + ' / ' + n;
      } else {
        dots.className = 'rv-dots';
        if (dots.children.length !== n) dots.innerHTML = new Array(n + 1).join('<i></i>');
        Array.prototype.forEach.call(dots.children, function (dot, i) { dot.classList.toggle('on', i === p); });
      }
      prev.disabled = track.scrollLeft < 5;
      next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 5;
    }
    function move(dir) {
      track.scrollBy({ left: dir * pageStep(), behavior: reduced ? 'auto' : 'smooth' });
    }
    prev.addEventListener('click', function () { move(-1); });
    next.addEventListener('click', function () { move(1); });
    track.addEventListener('scroll', function () { requestAnimationFrame(draw); }, { passive: true });
    window.addEventListener('resize', draw);
    track.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); move(1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); move(-1); }
    });
    draw();
  });
  /* Count call, online booking and directions clicks in Umami (no cookies, no personal data) */
  document.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('a[href]') : null;
    if (!a || !window.umami) return;
    var h = a.getAttribute('href'), name = null;
    if (h.indexOf('tel:') === 0) name = 'Call';
    else if (h.indexOf('book2.getweave.com') !== -1) name = 'Request appointment';
    else if (/maps\.apple\.com|google\.com\/maps\/dir/.test(h)) name = 'Directions';
    if (!name) return;
    var spot = a.closest('.mobile-bar') ? 'phone bar' : a.closest('header') ? 'header' : a.closest('footer') ? 'footer' : 'page';
    window.umami.track(name, { page: location.pathname, spot: spot, lang: document.documentElement.getAttribute('data-lang') || 'en' });
  });
})();
