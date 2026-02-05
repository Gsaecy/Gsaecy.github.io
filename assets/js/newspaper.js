/* Newspaper-like UI enhancements for hugo-theme-stack.
   - Adds click-to-open transition on list cards
   - Adds enter animation on article pages
   - Appends a consistent promo slogan at bottom of each article
*/

(function () {
  const PROMO_TEXT = '关注「AI智汇观察」，了解更多行业最新资讯';

  function onReady(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn, { once: true });
    } else {
      fn();
    }
  }

  function isArticlePage() {
    return document.body && document.body.classList.contains('article-page');
  }

  function isListPage() {
    return document.querySelector('.article-list--compact, .article-list--tile, .article-list') != null;
  }

  function addEnterAnimation() {
    document.documentElement.classList.add('np-enter');
    // Let CSS transitions run.
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        document.documentElement.classList.add('np-enter-active');
      });
    });
    setTimeout(() => {
      document.documentElement.classList.remove('np-enter');
      document.documentElement.classList.remove('np-enter-active');
    }, 700);
  }

  function addPromoSlogan() {
    const content = document.querySelector('.article-content');
    if (!content) return;

    // Avoid duplicates (e.g., PJAX / theme scripts)
    if (content.querySelector('[data-np-promo="1"]')) return;

    const wrap = document.createElement('div');
    wrap.setAttribute('data-np-promo', '1');
    wrap.className = 'np-promo';
    wrap.innerHTML = `
      <div class="np-promo__rule"></div>
      <p class="np-promo__text">${PROMO_TEXT}</p>
    `;
    content.appendChild(wrap);
  }

  function wireCardOpenTransition() {
    const cards = document.querySelectorAll(
      'section.article-list--compact article > a, section.article-list--tile article > a'
    );
    if (!cards.length) return;

    cards.forEach((a) => {
      a.addEventListener('click', (e) => {
        // allow cmd/ctrl click, new tab, etc.
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
        if (e.defaultPrevented) return;

        const href = a.getAttribute('href');
        if (!href || href.startsWith('#')) return;

        e.preventDefault();

        const article = a.closest('article');
        if (article) article.classList.add('np-opening');
        document.documentElement.classList.add('np-navigate');

        setTimeout(() => {
          window.location.href = href;
        }, 220);
      });
    });
  }

  onReady(() => {
    if (isListPage()) {
      wireCardOpenTransition();
    }
    if (isArticlePage()) {
      addEnterAnimation();
      addPromoSlogan();
    }
  });
})();
