/* =========================================================
   MOHAMMED HUSSEIN — portfolio behaviour
   ========================================================= */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- theme (set early in <head> to avoid flash) ---------- */
  var toggle = document.querySelector('.theme-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      document.documentElement.dataset.theme = next;
      try { localStorage.setItem('mh-theme', next); } catch (e) {}
      toggle.setAttribute('aria-label', next === 'dark' ? 'تفعيل الوضع النهاري' : 'تفعيل الوضع الليلي');
    });
  }

  /* ---------- mobile nav ---------- */
  var navToggle = document.querySelector('.nav-toggle');
  var navLinks = document.querySelector('nav.links');
  if (navToggle && navLinks) {
    var setNav = function (open) {
      navLinks.classList.toggle('open', open);
      navToggle.setAttribute('aria-expanded', String(open));
      document.body.style.overflow = open ? 'hidden' : '';
    };
    navToggle.addEventListener('click', function () {
      setNav(navToggle.getAttribute('aria-expanded') !== 'true');
    });
    navLinks.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () { setNav(false); });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && navLinks.classList.contains('open')) { setNav(false); navToggle.focus(); }
    });
  }

  /* ---------- active nav link ---------- */
  var current = document.body.dataset.page;
  document.querySelectorAll('nav.links a').forEach(function (a) {
    if (a.dataset.page === current) { a.classList.add('active'); a.setAttribute('aria-current', 'page'); }
  });

  /* ---------- sticky header shadow + scroll progress ---------- */
  var header = document.querySelector('header.site');
  var bar = document.querySelector('.progress');
  var ticking = false;
  function onScroll() {
    if (header) header.classList.toggle('stuck', window.scrollY > 8);
    if (bar) {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + '%';
    }
    ticking = false;
  }
  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(onScroll); }
  }, { passive: true });
  onScroll();

  /* ---------- reveal on scroll ---------- */
  var revealEls = document.querySelectorAll('.reveal, .stagger');
  if ('IntersectionObserver' in window && !reduced) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { entry.target.classList.add('in'); io.unobserve(entry.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('in'); });
  }

  /* ---------- animated counters ---------- */
  var counters = document.querySelectorAll('[data-count]');
  if (counters.length) {
    var run = function (el) {
      var target = parseFloat(el.dataset.count);
      var suffix = el.dataset.suffix || '';
      if (reduced) { el.textContent = target + suffix; return; }
      var start = performance.now(), dur = 1400;
      var tick = function (now) {
        var p = Math.min((now - start) / dur, 1);
        var eased = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(target * eased) + suffix;
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };
    if ('IntersectionObserver' in window) {
      var cio = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) { run(e.target); cio.unobserve(e.target); } });
      }, { threshold: 0.5 });
      counters.forEach(function (el) { cio.observe(el); });
    } else counters.forEach(run);
  }

  /* ---------- hero typing ---------- */
  var typeEl = document.querySelector('[data-typing]');
  if (typeEl) {
    var lines = JSON.parse(typeEl.dataset.typing);
    if (reduced) {
      typeEl.textContent = lines[lines.length - 1];
    } else {
      var li = 0, ci = 0, deleting = false;
      var cursor = document.createElement('span');
      cursor.className = 'type-cursor';
      cursor.textContent = '█';
      cursor.setAttribute('aria-hidden', 'true');
      var out = document.createElement('span');
      typeEl.textContent = '';
      typeEl.append(out, cursor);
      (function tick() {
        var full = lines[li];
        if (!deleting) {
          ci++;
          out.textContent = full.slice(0, ci);
          if (ci === full.length) {
            deleting = li < lines.length - 1;
            setTimeout(tick, deleting ? 1500 : 100000);
            return;
          }
        } else {
          ci--;
          out.textContent = full.slice(0, ci);
          if (ci === 0) { deleting = false; li++; }
        }
        setTimeout(tick, deleting ? 20 : 45);
      })();
    }
  }

  /* ---------- portfolio filters ---------- */
  var filters = document.querySelectorAll('.filter');
  if (filters.length) {
    var items = document.querySelectorAll('[data-cat]');
    var empty = document.querySelector('#no-results');
    filters.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var cat = btn.dataset.filter;
        filters.forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); });
        var shown = 0;
        items.forEach(function (it) {
          var match = cat === 'all' || it.dataset.cat.split(' ').indexOf(cat) > -1;
          it.classList.toggle('hide', !match);
          if (match) shown++;
        });
        if (empty) empty.hidden = shown !== 0;
      });
    });
  }

  /* ---------- contact form ---------- */
  var form = document.querySelector('#contact-form');
  if (form) {
    var status = form.querySelector('.form-status');
    var setErr = function (input, on) { input.closest('.field').classList.toggle('invalid', on); };

    form.querySelectorAll('input,textarea').forEach(function (i) {
      i.addEventListener('input', function () { setErr(i, false); });
    });

    var buildText = function (d) {
      return 'مرحبًا محمد، اسمي ' + d.name + '.\n' +
        'وسيلة تواصل بديلة: ' + d.contact + '\n' +
        (d.budget ? 'الميزانية التقريبية: ' + d.budget + '\n' : '') + '\n' + d.message;
    };

    var readForm = function () {
      return {
        name: form.name.value.trim(),
        contact: form.contact.value.trim(),
        budget: form.budget ? form.budget.value : '',
        message: form.message.value.trim()
      };
    };

    var validate = function () {
      var ok = true;
      ['name', 'contact', 'message'].forEach(function (k) {
        var el = form[k];
        var bad = el.value.trim().length < (k === 'message' ? 10 : 2);
        setErr(el, bad);
        if (bad && ok) { el.focus(); ok = false; }
      });
      return ok;
    };

    // WhatsApp path
    var waBtn = form.querySelector('[data-send="whatsapp"]');
    if (waBtn) {
      waBtn.addEventListener('click', function () {
        if (!validate()) return;
        window.open('https://wa.me/201000220606?text=' + encodeURIComponent(buildText(readForm())), '_blank', 'noopener');
        if (status) { status.className = 'form-status ok'; status.textContent = 'فتحنا لك واتساب برسالة جاهزة — ابعتها وهرد عليك في أقرب وقت.'; }
      });
    }

    // Email path (Web3Forms — replace the access key with your own)
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!validate()) return;
      var key = form.dataset.accessKey;
      var submitBtn = form.querySelector('[type="submit"]');

      if (!key || key.indexOf('YOUR-') === 0) {
        // Not configured yet → fall back to the user's mail client, nothing is lost.
        var d = readForm();
        window.location.href = 'mailto:egyup@outlook.com?subject=' +
          encodeURIComponent('مشروع جديد من ' + d.name) + '&body=' + encodeURIComponent(buildText(d));
        if (status) { status.className = 'form-status ok'; status.textContent = 'فتحنا لك برنامج الإيميل برسالة جاهزة. لو مفتحش، ابعت على egyup@outlook.com مباشرة.'; }
        return;
      }

      var oldLabel = submitBtn.textContent;
      submitBtn.disabled = true; submitBtn.textContent = 'جاري الإرسال…';
      var d2 = readForm();
      fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          access_key: key, subject: 'مشروع جديد من ' + d2.name,
          from_name: d2.name, name: d2.name, contact: d2.contact,
          budget: d2.budget, message: d2.message
        })
      }).then(function (r) { return r.json(); }).then(function (j) {
        if (j.success) {
          form.reset();
          status.className = 'form-status ok';
          status.textContent = 'وصلتني رسالتك ✔ هرد عليك خلال يوم عمل واحد.';
        } else throw new Error('failed');
      }).catch(function () {
        status.className = 'form-status bad';
        status.textContent = 'حصلت مشكلة في الإرسال. جرّب زرار الواتساب تحت، أو ابعت على egyup@outlook.com.';
      }).finally(function () {
        submitBtn.disabled = false; submitBtn.textContent = oldLabel;
      });
    });
  }

  /* ---------- current year ---------- */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
