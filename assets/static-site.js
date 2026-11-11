/* Small, dependency-free enhancements for the preserved static site. */
(() => {
  'use strict';
  const drawer = document.querySelector('[data-ux="NavigationDrawer"]');
  const toggle = document.querySelector('[data-aid="HAMBURGER_MENU_LINK"]');
  const close = document.querySelector('[data-ux="CloseIcon"]');
  function setDrawer(open) {
    if (!drawer) return;
    drawer.style.setProperty('transform', open ? 'translateX(0)' : 'translateX(-110%)', 'important');
    drawer.style.setProperty('left', '0', 'important');
    drawer.style.setProperty('visibility', open ? 'visible' : 'hidden', 'important');
    drawer.setAttribute('aria-hidden', String(!open));
    drawer.inert = !open;
    toggle?.setAttribute('aria-expanded', String(open));
    if (open) { (close || drawer.querySelector('a'))?.focus(); }
    else if (drawer.contains(document.activeElement)) toggle?.focus();
  }
  if (drawer && toggle) toggle.setAttribute('aria-controls', drawer.id);
  setDrawer(false);
  window.matchMedia('(min-width:1200px)').addEventListener('change', e => { if (e.matches) setDrawer(false); });
  document.addEventListener('click', event => {
    const opener = event.target.closest('[data-aid="HAMBURGER_MENU_LINK"]');
    const closer = event.target.closest('[data-ux="CloseIcon"]');
    if (opener || closer) { event.preventDefault(); setDrawer(Boolean(opener)); return; }
    document.querySelectorAll('.more-disclosure[open]').forEach(menu => {
      if (!menu.contains(event.target)) menu.open = false;
    });
  });
  document.querySelectorAll('.more-disclosure').forEach(menu => {
    menu.addEventListener('keydown', event => {
      if (event.key === 'Escape') { menu.open = false; menu.querySelector('summary').focus(); event.stopPropagation(); }
      if (event.key === 'ArrowDown' && event.target.tagName === 'SUMMARY') {
        event.preventDefault(); menu.open = true; menu.querySelector('a')?.focus();
      }
    });
    menu.addEventListener('focusout', event => { if (!menu.contains(event.relatedTarget)) menu.open = false; });
  });
  document.querySelectorAll('.blog-listing').forEach(listing => {
    const filters = listing.querySelector('.blog-filters');
    if (!filters) return;
    filters.hidden = false;
    filters.addEventListener('click', event => {
      const button = event.target.closest('[data-blog-category]');
      if (!button) return;
      filters.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
      listing.querySelectorAll('.blog-card').forEach(card => {
        card.hidden = button.dataset.blogCategory !== 'All' && !JSON.parse(card.dataset.categories).includes(button.dataset.blogCategory);
      });
    });
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') setDrawer(false);
    if (['Enter', ' '].includes(event.key) && event.target.matches('[role="button"]:not(button)')) { event.preventDefault(); event.target.click(); }
    if (event.key === 'Tab' && drawer && !drawer.inert) {
      const items = [...drawer.querySelectorAll('a[href],button,[tabindex="0"]')].filter(el => el.getClientRects().length);
      if (event.shiftKey && document.activeElement === items[0]) { event.preventDefault(); items.at(-1)?.focus(); }
      else if (!event.shiftKey && document.activeElement === items.at(-1)) { event.preventDefault(); items[0]?.focus(); }
    }
  });
  document.querySelectorAll('.accordion-question').forEach(button => {
    const panel = document.getElementById(button.getAttribute('aria-controls'));
    if (!panel) return;
    button.setAttribute('aria-expanded', 'false'); panel.hidden = true;
    button.addEventListener('click', () => { panel.hidden = !panel.hidden; button.setAttribute('aria-expanded', String(!panel.hidden)); });
  });
  document.querySelectorAll('.static-gallery').forEach(gallery => {
    const slides = [...gallery.querySelectorAll('.static-slide')];
    const controls = gallery.querySelector('.gallery-controls');
    let current = 0;
    function show(index) {
      current = (index + slides.length) % slides.length;
      slides.forEach((slide, i) => { slide.hidden = i !== current; });
      gallery.querySelector('.gallery-position').textContent = `${current + 1} / ${slides.length}`;
    }
    if (!slides.length) return;
    gallery.classList.add('enhanced'); controls.hidden = false; show(0);
    gallery.querySelectorAll('[data-gallery-step]').forEach(button => button.addEventListener('click', () => show(current + Number(button.dataset.galleryStep))));
    gallery.addEventListener('keydown', event => {
      if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') { event.preventDefault(); show(current + (event.key === 'ArrowRight' ? 1 : -1)); }
    });
  });
  document.querySelectorAll('form[action="https://www.paypal.com/cgi-bin/webscr"]').forEach(form => {
    ['return', 'cancel_return'].forEach(name => { const input = form.querySelector(`input[name="${name}"]`); if (input) input.value = location.href; });
  });
})();
