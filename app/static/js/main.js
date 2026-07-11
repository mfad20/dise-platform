/**
 * DISE — JavaScript principal
 * Adapté du design system "La Relève" — SANS Three.js ni particules.
 * Loader léger · Navbar scroll/burger · AOS · Compteurs · Carousel hero ·
 * Back-to-top · Focus visible
 */

const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

/* 1. LOADER — une fois par session, sans particules */
(function initLoader() {
  const loader = $('#loader');
  if (!loader) return;

  if (sessionStorage.getItem('loaderSeen')) {
    loader.style.display = 'none';
    document.body.classList.remove('loading');
    return;
  }

  const bar = $('.loader-bar');
  const percent = $('.loader-percent');
  let prog = 0;

  function step() {
    const remaining = 100 - prog;
    prog += Math.max(1.2, remaining * 0.08);
    if (prog >= 100) prog = 100;
    if (bar) bar.style.width = prog + '%';
    if (percent) percent.textContent = Math.floor(prog) + '%';
    if (prog < 100) {
      requestAnimationFrame(step);
    } else {
      setTimeout(dismiss, 250);
    }
  }

  function dismiss() {
    sessionStorage.setItem('loaderSeen', '1');
    loader.classList.add('fade-out');
    setTimeout(() => {
      loader.style.display = 'none';
      document.body.classList.remove('loading');
    }, 600);
  }

  setTimeout(() => requestAnimationFrame(step), 150);
})();


/* 2. NAVBAR — scroll, burger mobile */
(function initNavbar() {
  const navbar = $('.navbar');
  if (!navbar) return;

  let lastY = 0;
  function handleScroll() {
    const y = window.scrollY;
    navbar.classList.toggle('scrolled', y > 60);
    if (y > 200) {
      navbar.classList.toggle('navbar-hidden', y > lastY + 5);
      navbar.classList.toggle('navbar-visible', y < lastY - 5);
    } else {
      navbar.classList.remove('navbar-hidden', 'navbar-visible');
    }
    lastY = y;
  }
  window.addEventListener('scroll', handleScroll, { passive: true });

  const burger = $('#navBurger, .nav-burger');
  const mobileMenu = $('#navMobile, .nav-mobile');
  if (burger && mobileMenu) {
    burger.addEventListener('click', () => {
      const isOpen = mobileMenu.classList.toggle('open');
      burger.classList.toggle('open', isOpen);
      burger.setAttribute('aria-expanded', isOpen);
      document.body.classList.toggle('menu-open', isOpen);
    });
    $$('a', mobileMenu).forEach((a) => {
      a.addEventListener('click', () => {
        mobileMenu.classList.remove('open');
        burger.classList.remove('open');
        document.body.classList.remove('menu-open');
      });
    });
    document.addEventListener('click', (e) => {
      if (!navbar.contains(e.target) && mobileMenu.classList.contains('open')) {
        mobileMenu.classList.remove('open');
        burger.classList.remove('open');
        document.body.classList.remove('menu-open');
      }
    });
  }

  /* Sous-menus déroulants ("La DISE", "La communauté") */
  const dropdowns = $$('.nav-item-dropdown');
  function closeDropdowns(except) {
    dropdowns.forEach((d) => {
      if (d === except) return;
      d.classList.remove('open');
      const toggle = $('.nav-dropdown-toggle', d);
      if (toggle) toggle.setAttribute('aria-expanded', 'false');
    });
  }
  dropdowns.forEach((dropdown) => {
    const toggle = $('.nav-dropdown-toggle', dropdown);
    if (!toggle) return;
    toggle.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = dropdown.classList.toggle('open');
      toggle.setAttribute('aria-expanded', isOpen);
      closeDropdowns(dropdown);
    });
  });
  document.addEventListener('click', () => closeDropdowns());
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeDropdowns();
  });
})();


/* 3. AOS — Animate on Scroll (si chargé via CDN) */
(function initAOS() {
  if (typeof AOS === 'undefined') return;
  AOS.init({ duration: 700, easing: 'ease-out-cubic', once: true, offset: 60 });
})();


/* 4. COMPTEURS ANIMÉS (chiffres clés) */
(function initCounters() {
  const counters = $$('[data-count]');
  if (!counters.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      observer.unobserve(entry.target);
      const el = entry.target;
      const target = parseFloat(el.dataset.count);
      const suffix = el.dataset.suffix || '';
      const duration = 1500;
      const start = performance.now();

      function tick(now) {
        const progress = Math.min((now - start) / duration, 1);
        const ease = 1 - Math.pow(1 - progress, 3);
        const value = target * ease;
        el.textContent = (Number.isInteger(target) ? Math.round(value) : value.toFixed(1)) + suffix;
        if (progress < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    });
  }, { threshold: 0.4 });

  counters.forEach((el) => observer.observe(el));
})();


/* 5. CARROUSEL PHOTO — photos ENSEA, points, flèches, légende, autoplay.
   Réutilisé sur l'accueil (#heroCarousel) et en bannière des pages
   intérieures (#pageHeaderCarousel) : on initialise toutes les instances
   présentes sur la page. */
$$('.hero-carousel').forEach(function initHeroCarousel(root) {
  const slides = $$('.hero-carousel-slide', root);
  const dots = $$('.hero-carousel-dot', root);
  const prevBtn = $('.hero-carousel-arrow.prev', root);
  const nextBtn = $('.hero-carousel-arrow.next', root);
  if (!slides.length) return;

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const delay = parseInt(root.dataset.autoplay, 10) || 5500;
  let current = Math.max(0, slides.findIndex((s) => s.classList.contains('active')));
  let timer = null;

  function goTo(index) {
    const next = (index + slides.length) % slides.length;
    if (next === current) return;
    slides[current].classList.remove('active');
    dots[current] && dots[current].classList.remove('active');
    dots[current] && dots[current].setAttribute('aria-selected', 'false');
    current = next;
    slides[current].classList.add('active');
    dots[current] && dots[current].classList.add('active');
    dots[current] && dots[current].setAttribute('aria-selected', 'true');
  }

  function start() {
    if (reduceMotion) return;
    stop();
    timer = setInterval(() => goTo(current + 1), delay);
  }
  function stop() {
    if (timer) clearInterval(timer);
    timer = null;
  }
  function restart() { stop(); start(); }

  if (prevBtn) prevBtn.addEventListener('click', () => { goTo(current - 1); restart(); });
  if (nextBtn) nextBtn.addEventListener('click', () => { goTo(current + 1); restart(); });
  dots.forEach((dot, i) => dot.addEventListener('click', () => { goTo(i); restart(); }));

  root.addEventListener('mouseenter', stop);
  root.addEventListener('mouseleave', start);
  root.addEventListener('focusin', stop);
  root.addEventListener('focusout', start);

  let touchStartX = null;
  root.addEventListener('touchstart', (e) => { touchStartX = e.touches[0].clientX; }, { passive: true });
  root.addEventListener('touchend', (e) => {
    if (touchStartX === null) return;
    const delta = e.changedTouches[0].clientX - touchStartX;
    if (Math.abs(delta) > 40) goTo(current + (delta < 0 ? 1 : -1));
    touchStartX = null;
    restart();
  }, { passive: true });

  start();
});


/* 6. COPIER UN NUMÉRO DE PAIEMENT */
$$('[data-copy]').forEach((btn) => {
  btn.addEventListener('click', () => {
    const value = btn.getAttribute('data-copy');
    navigator.clipboard.writeText(value).then(() => {
      const original = btn.textContent;
      btn.textContent = 'Copié !';
      setTimeout(() => { btn.textContent = original; }, 1500);
    });
  });
});


/* 7. CONFIRMATION AVANT ACTIONS SENSIBLES */
$$('[data-confirm]').forEach((form) => {
  form.addEventListener('submit', (e) => {
    if (!window.confirm(form.getAttribute('data-confirm'))) e.preventDefault();
  });
});


/* 8. FERMETURE AUTO DES MESSAGES FLASH */
$$('.flash').forEach((flash) => {
  setTimeout(() => {
    flash.style.transition = 'opacity .4s ease';
    flash.style.opacity = '0';
    setTimeout(() => flash.remove(), 400);
  }, 6000);
});


/* 9. SMOOTH SCROLL (ancres) */
$$('a[href^="#"]').forEach((a) => {
  a.addEventListener('click', (e) => {
    const id = a.getAttribute('href').slice(1);
    const el = document.getElementById(id);
    if (!el) return;
    e.preventDefault();
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
});


/* 10. BACK TO TOP */
(function initBackToTop() {
  if ($('#back-to-top')) return;
  const btn = document.createElement('button');
  btn.id = 'back-to-top';
  btn.className = 'back-to-top-btn';
  btn.title = 'Retour en haut';
  btn.innerHTML = '↑';
  btn.setAttribute('aria-label', 'Retour en haut de page');
  document.body.appendChild(btn);
  btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  window.addEventListener('scroll', () => {
    btn.classList.toggle('visible', window.scrollY > 400);
  }, { passive: true });
})();


/* 11. ACCESSIBILITÉ — focus clavier */
document.addEventListener('keydown', () => document.body.classList.add('keyboard-nav'));
document.addEventListener('mousedown', () => document.body.classList.remove('keyboard-nav'));
