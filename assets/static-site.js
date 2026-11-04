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
  setDrawer(false);
  document.addEventListener('click', event => {
    const opener = event.target.closest('[data-aid="HAMBURGER_MENU_LINK"]');
    const closer = event.target.closest('[data-ux="CloseIcon"]');
    if (opener || closer) { event.preventDefault(); setDrawer(Boolean(opener)); return; }
    const dropdown = event.target.closest('[data-ux="NavLinkDropdown"]');
    if (dropdown) {
      event.preventDefault();
      const menu = dropdown.parentElement.parentElement.querySelector('[data-ux="Dropdown"]');
      const open = dropdown.getAttribute('aria-expanded') !== 'true';
      if (menu) menu.style.setProperty('display', open ? 'block' : 'none', 'important');
      dropdown.setAttribute('aria-expanded', String(open));
    } else {
      document.querySelectorAll('[data-ux="NavLinkDropdown"][aria-expanded="true"]').forEach(link => {
        link.setAttribute('aria-expanded', 'false');
        link.parentElement.parentElement.querySelector('[data-ux="Dropdown"]')?.style.setProperty('display', 'none', 'important');
      });
    }
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
