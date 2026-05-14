// Ameya Wiki — main JS
// Wikipedia-style SPA that renders markdown pages from the wiki/ directory

const REPO = 'ameyaagrawal99/ameya-wiki';
const BRANCH = 'main';
const BASE_RAW = `https://raw.githubusercontent.com/${REPO}/${BRANCH}`;

// Page registry: slug → { title, category, file }
const PAGES = [
  { slug: 'overview',                    title: 'Overview',                     cat: 'Overview',          file: 'wiki/overview.md' },
  { slug: 'identity-ameya-agrawal',      title: 'Profile & Bio',                cat: 'Identity',          file: 'wiki/pages/identity-ameya-agrawal.md' },
  { slug: 'achievements-awards',         title: 'Achievements & Awards',        cat: 'Identity',          file: 'wiki/pages/achievements-awards.md' },
  { slug: 'blog-mind-machine-meaning',   title: 'Blog — Mind, Machine & Meaning', cat: 'Writing',        file: 'wiki/pages/blog-mind-machine-meaning.md' },
  { slug: 'a-leap-within',              title: 'A Leap Within (Book)',          cat: 'Writing',           file: 'wiki/pages/a-leap-within.md' },
  { slug: 'medium-writing',             title: 'Medium Articles',               cat: 'Writing',           file: 'wiki/pages/medium-writing.md' },
  { slug: 'media-coverage-interviews',  title: 'Media & Interviews',            cat: 'Writing',           file: 'wiki/pages/media-coverage-interviews.md' },
  { slug: 'professional-experience',    title: 'Professional Experience',       cat: 'Work',              file: 'wiki/pages/professional-experience.md' },
  { slug: 'mgss-mahatma-gandhi-seva-sangh', title: 'MGSS',                     cat: 'Work',              file: 'wiki/pages/mgss-mahatma-gandhi-seva-sangh.md' },
  { slug: 'skillslate-foundation',      title: 'SkillSlate Foundation',         cat: 'Work',              file: 'wiki/pages/skillslate-foundation.md' },
  { slug: 'github-projects',            title: 'GitHub Projects',               cat: 'Work',              file: 'wiki/pages/github-projects.md' },
  { slug: 'certifications-skills',      title: 'Certifications & Skills',       cat: 'Work',              file: 'wiki/pages/certifications-skills.md' },
  { slug: 'ideas-recurring-themes',     title: 'Recurring Themes',              cat: 'Ideas',             file: 'wiki/pages/ideas-recurring-themes.md' },
  { slug: 'social-presence',           title: 'All Platforms',                  cat: 'Social',            file: 'wiki/pages/social-presence.md' },
  { slug: 'linkedin-profile',          title: 'LinkedIn',                       cat: 'Social',            file: 'wiki/pages/linkedin-profile.md' },
];

const pageMap = Object.fromEntries(PAGES.map(p => [p.slug, p]));
let pageCache = {};
let allContent = []; // for search

// Resolve [[wikilink]] to href
function resolveWikiLinks(md) {
  return md.replace(/\[\[([^\]]+)\]\]/g, (_, slug) => {
    const page = pageMap[slug];
    const label = page ? page.title : slug;
    return `[${label}](?page=${slug})`;
  });
}

// Render markdown with wikilinks resolved
function renderMarkdown(md) {
  const resolved = resolveWikiLinks(md);
  marked.setOptions({ breaks: false, gfm: true });
  return marked.parse(resolved);
}

// Get current page slug from URL
function getCurrentSlug() {
  const params = new URLSearchParams(window.location.search);
  return params.get('page') || 'overview';
}

// Fetch a markdown file (with cache)
async function fetchPage(slug) {
  if (pageCache[slug]) return pageCache[slug];
  const page = pageMap[slug];
  if (!page) return null;

  try {
    const url = `${BASE_RAW}/${page.file}`;
    const res = await fetch(url);
    if (!res.ok) {
      // fallback: try fetching locally (when running on GH Pages)
      const localRes = await fetch(page.file);
      if (!localRes.ok) return null;
      const text = await localRes.text();
      pageCache[slug] = text;
      return text;
    }
    const text = await res.text();
    pageCache[slug] = text;
    return text;
  } catch {
    try {
      const localRes = await fetch(page.file);
      if (!localRes.ok) return null;
      const text = await localRes.text();
      pageCache[slug] = text;
      return text;
    } catch {
      return null;
    }
  }
}

// Strip frontmatter from markdown
function stripFrontmatter(md) {
  return md.replace(/^---[\s\S]*?---\n/, '');
}

// Load and render a page
async function loadPage(slug) {
  const article = document.getElementById('article');
  const editLink = document.getElementById('edit-link');
  const breadcrumb = document.getElementById('breadcrumb');

  article.className = 'loading';
  article.innerHTML = '';

  // Update active nav
  document.querySelectorAll('.nav-link').forEach(a => {
    a.classList.toggle('active', a.dataset.page === slug);
  });

  const page = pageMap[slug];
  if (!page) {
    article.className = '';
    article.innerHTML = '<p>Page not found.</p>';
    return;
  }

  // Breadcrumb
  breadcrumb.textContent = `${page.cat} › ${page.title}`;

  // Edit link
  editLink.href = `https://github.com/${REPO}/edit/${BRANCH}/${page.file}`;

  // Fetch content
  const md = await fetchPage(slug);
  article.className = '';

  if (!md) {
    article.innerHTML = '<p>Could not load this page. It may not be synced yet.</p>';
    return;
  }

  const clean = stripFrontmatter(md);
  article.innerHTML = renderMarkdown(clean);

  // Make internal links work as SPA navigation
  article.querySelectorAll('a[href]').forEach(a => {
    const href = a.getAttribute('href');
    if (href && href.startsWith('?page=')) {
      a.addEventListener('click', e => {
        e.preventDefault();
        const params = new URLSearchParams(href.slice(1));
        const target = params.get('page');
        navigateTo(target);
      });
    }
  });

  // Update last modified
  const lastMod = document.getElementById('last-modified');
  lastMod.textContent = `Last updated: 2026-05-14`;

  // Update page title
  document.title = `${page.title} — Ameya Agrawal Wiki`;

  // Scroll to top
  document.getElementById('content').scrollTo(0, 0);
  window.scrollTo(0, 0);
}

function navigateTo(slug) {
  const url = new URL(window.location);
  url.searchParams.set('page', slug);
  window.history.pushState({ slug }, '', url);
  loadPage(slug);
}

// === SEARCH ===
async function buildSearchIndex() {
  for (const page of PAGES) {
    const md = await fetchPage(page.slug);
    if (md) {
      allContent.push({
        slug: page.slug,
        title: page.title,
        text: stripFrontmatter(md).toLowerCase(),
        snippet: stripFrontmatter(md).slice(0, 200),
      });
    }
  }
}

function doSearch(query) {
  const q = query.toLowerCase().trim();
  if (!q) return [];
  return allContent
    .filter(p => p.title.toLowerCase().includes(q) || p.text.includes(q))
    .slice(0, 6)
    .map(p => ({
      slug: p.slug,
      title: p.title,
      snippet: (() => {
        const idx = p.text.indexOf(q);
        const start = Math.max(0, idx - 40);
        const raw = p.snippet || p.text.slice(start, start + 120);
        return raw.replace(/[#*`\[\]]/g, '').trim();
      })(),
    }));
}

// === INIT ===
document.addEventListener('DOMContentLoaded', () => {
  // Initial page load
  loadPage(getCurrentSlug());

  // Browser back/forward
  window.addEventListener('popstate', e => {
    loadPage(e.state?.slug || getCurrentSlug());
  });

  // Nav link clicks
  document.querySelectorAll('.nav-link').forEach(a => {
    a.addEventListener('click', e => {
      e.preventDefault();
      navigateTo(a.dataset.page);
    });
  });

  // Search
  const searchInput = document.getElementById('search');
  const searchResults = document.getElementById('search-results');

  buildSearchIndex(); // preload in background

  searchInput.addEventListener('input', () => {
    const q = searchInput.value;
    if (q.length < 2) {
      searchResults.classList.remove('active');
      return;
    }
    const results = doSearch(q);
    if (!results.length) {
      searchResults.classList.remove('active');
      return;
    }
    searchResults.innerHTML = results.map(r => `
      <div class="search-result" data-slug="${r.slug}">
        <div class="search-result-title">${r.title}</div>
        <div class="search-result-snippet">${r.snippet}…</div>
      </div>
    `).join('');
    searchResults.classList.add('active');
  });

  searchResults.addEventListener('click', e => {
    const item = e.target.closest('.search-result');
    if (item) {
      navigateTo(item.dataset.slug);
      searchInput.value = '';
      searchResults.classList.remove('active');
    }
  });

  document.addEventListener('click', e => {
    if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
      searchResults.classList.remove('active');
    }
  });

  // Last updated in sidebar
  document.getElementById('last-updated').textContent = 'Updated: 2026-05-14';
});
