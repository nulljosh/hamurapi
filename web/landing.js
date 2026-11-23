// Landing behaviour: fade-up on scroll. Nothing here is needed to read the page.
(function () {
  document.documentElement.classList.add('js');
  var items = Array.prototype.slice.call(document.querySelectorAll('.reveal'));
  function show(e) { e.classList.add('in'); }
  function run() {
    if (matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) return items.forEach(show);
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { show(e.target); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    items.forEach(function (e) { io.observe(e); });
  }
  if (document.readyState !== 'loading') run(); else document.addEventListener('DOMContentLoaded', run);
})();
