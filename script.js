(function () {
  const {
    CATEGORY_LABELS,
    posts: fallbackPosts,
    tracks,
    filterPosts,
    paginatePosts,
    findPostBySlug,
    nextTrackIndex,
    previousTrackIndex,
  } = window.BlogEngine;

  const state = {
    posts: fallbackPosts,
    category: "all",
    query: "",
    page: 1,
    pageSize: 4,
    currentTrack: 0,
    playing: false,
    progress: 0,
    timer: null,
    apiReady: true,
    activeSlug: null,
  };

  const listEl = document.querySelector("#post-list");
  const filterButtons = Array.from(document.querySelectorAll(".filter-button"));
  const pageNumbersEl = document.querySelector("#page-numbers");
  const prevPageEl = document.querySelector("#prev-page");
  const nextPageEl = document.querySelector("#next-page");
  const articleEl = document.querySelector("#article");
  const searchFormEl = document.querySelector("#search-form");
  const searchInputEl = document.querySelector("#search-input");
  const messagesListEl = document.querySelector("#messages-list");
  const messageFormEl = document.querySelector("#message-form");
  const messageStatusEl = document.querySelector("#message-status");
  const trackTitleEl = document.querySelector("#track-title");
  const trackArtistEl = document.querySelector("#track-artist");
  const togglePlayEl = document.querySelector("#toggle-play");
  const progressEl = document.querySelector("#track-progress");
  const currentTimeEl = document.querySelector("#current-time");
  const durationEl = document.querySelector("#duration");
  const volumeEl = document.querySelector("#volume-control");
  const heroCardEl = document.querySelector(".hero-card");

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  async function apiFetch(path, options = {}) {
    const response = await fetch(path, {
      ...options,
      headers: {
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...(options.headers || {}),
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return response.json();
  }

  function fillPatternRows() {
    document.querySelectorAll(".pattern-row").forEach((row) => {
      row.innerHTML = "";

      for (let index = 0; index < 24; index += 1) {
        const item = document.createElement("span");
        item.textContent = "Q";
        row.appendChild(item);
      }
    });
  }

  function setHeroSpot(event) {
    const rect = heroCardEl.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 100;
    const y = ((event.clientY - rect.top) / rect.height) * 100;

    heroCardEl.style.setProperty("--spot-x", `${x}%`);
    heroCardEl.style.setProperty("--spot-y", `${y}%`);
  }

  function formatTime(seconds) {
    const safeSeconds = Math.max(0, Math.floor(seconds));
    const minutes = Math.floor(safeSeconds / 60);
    const rest = String(safeSeconds % 60).padStart(2, "0");
    return `${minutes}:${rest}`;
  }

  function normalizePost(post) {
    const date = post.date || post.published_at || post.created_at || "";
    return {
      ...post,
      date: date ? String(date).slice(0, 10).replaceAll("-", ".") : "",
      readTime: post.readTime || "Read",
      body: Array.isArray(post.body) ? post.body : String(post.body || "").split(/\n{2,}/),
    };
  }

  async function loadPosts() {
    const params = new URLSearchParams({ page_size: "100" });
    if (state.category !== "all") params.set("category", state.category);
    if (state.query) params.set("query", state.query);

    try {
      const data = await apiFetch(`/api/posts?${params.toString()}`);
      state.posts = data.items.map(normalizePost);
      state.apiReady = true;
    } catch (error) {
      state.posts = filterPosts(fallbackPosts, state.category).filter((post) => {
        if (!state.query) return true;
        const target = `${post.title} ${post.excerpt} ${post.body.join(" ")}`.toLowerCase();
        return target.includes(state.query.toLowerCase());
      });
      state.apiReady = false;
    }
  }

  function renderPosts() {
    const page = paginatePosts(state.posts, state.page, state.pageSize);
    state.page = page.page;

    if (!page.items.length) {
      listEl.innerHTML = `
        <li class="empty-row">
          <p>${state.apiReady ? "没有找到文章。" : "暂时无法连接后端，正在显示本地兜底内容。"}</p>
        </li>
      `;
      renderPagination(page);
      renderActiveFilter();
      return;
    }

    listEl.innerHTML = page.items
      .map((post, index) => {
        const number = String((page.page - 1) * page.pageSize + index + 1).padStart(2, "0");
        const label = CATEGORY_LABELS[post.category] || post.category;

        return `
          <li class="post-item">
            <a class="post-link" href="#post/${escapeHtml(post.slug)}" data-slug="${escapeHtml(post.slug)}">
              <span class="post-number">${number}</span>
              <span class="post-main">
                <span class="post-meta">${escapeHtml(label)} / ${escapeHtml(post.date)} / ${escapeHtml(post.readTime)}</span>
                <strong>${escapeHtml(post.title)}</strong>
                <span>${escapeHtml(post.excerpt)}</span>
              </span>
            </a>
          </li>
        `;
      })
      .join("");

    renderPagination(page);
    renderActiveFilter();
  }

  function renderPagination(page) {
    prevPageEl.disabled = page.page <= 1;
    nextPageEl.disabled = page.page >= page.totalPages;

    pageNumbersEl.innerHTML = Array.from({ length: page.totalPages }, (_, index) => {
      const pageNumber = index + 1;
      const activeClass = pageNumber === page.page ? " is-active" : "";
      return `<button class="page-number${activeClass}" type="button" data-page="${pageNumber}">${pageNumber}</button>`;
    }).join("");
  }

  function renderActiveFilter() {
    filterButtons.forEach((button) => {
      button.classList.toggle("is-active", button.dataset.category === state.category);
    });
  }

  async function loadComments(slug) {
    if (!state.apiReady) return { items: [] };
    return apiFetch(`/api/posts/${encodeURIComponent(slug)}/comments`);
  }

  async function renderArticle(slug) {
    let post = findPostBySlug(state.posts, slug) || findPostBySlug(fallbackPosts, slug);

    if (state.apiReady) {
      try {
        post = normalizePost(await apiFetch(`/api/posts/${encodeURIComponent(slug)}`));
        apiFetch("/api/stats/visit", {
          method: "POST",
          body: JSON.stringify({ path: window.location.hash || "/", slug }),
        }).catch(() => {});
      } catch (error) {
        post = findPostBySlug(fallbackPosts, slug);
      }
    }

    if (!post) {
      return;
    }

    state.activeSlug = slug;
    const comments = await loadComments(slug).catch(() => ({ items: [] }));

    articleEl.innerHTML = `
      <article class="article-detail">
        <p class="eyebrow">${escapeHtml(CATEGORY_LABELS[post.category] || post.category)} / ${escapeHtml(post.date)}</p>
        <h2 id="article-title">${escapeHtml(post.title)}</h2>
        <p class="article-excerpt">${escapeHtml(post.excerpt)}</p>
        ${post.body.map((paragraph) => `<p>${escapeHtml(paragraph)}</p>`).join("")}
        <section class="interaction-block" aria-labelledby="comments-title">
          <h3 id="comments-title">评论</h3>
          <div class="comment-list">
            ${
              comments.items.length
                ? comments.items
                    .map((comment) => `<p><strong>${escapeHtml(comment.nickname)}</strong> / ${escapeHtml(comment.content)}</p>`)
                    .join("")
                : "<p>暂无公开评论。</p>"
            }
          </div>
          <form id="comment-form" class="inline-form">
            <input name="nickname" placeholder="昵称" required maxlength="40" />
            <textarea name="content" placeholder="评论会在审核后显示" required maxlength="1000"></textarea>
            <button type="submit">提交评论</button>
            <p id="comment-status" class="form-status" aria-live="polite"></p>
          </form>
        </section>
        <a class="article-back" href="#index">Back to Index</a>
      </article>
    `;
  }

  async function refreshPosts() {
    await loadPosts();
    renderPosts();
  }

  async function readHash() {
    const hash = window.location.hash.replace(/^#/, "");

    if (hash.startsWith("post/")) {
      await renderArticle(hash.replace("post/", ""));
      document.querySelector("#article").scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }

    if (["notes", "tech", "works"].includes(hash)) {
      state.category = hash;
      state.page = 1;
      await refreshPosts();
      document.querySelector("#index").scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  async function setCategory(category) {
    state.category = category;
    state.page = 1;
    await refreshPosts();
  }

  async function loadMessages() {
    if (!messagesListEl) return;

    try {
      const data = await apiFetch("/api/messages");
      messagesListEl.innerHTML = data.items.length
        ? data.items.map((item) => `<p><strong>${escapeHtml(item.nickname)}</strong> / ${escapeHtml(item.content)}</p>`).join("")
        : "<p>暂无公开留言。</p>";
    } catch (error) {
      messagesListEl.innerHTML = "<p>留言暂时无法加载。</p>";
    }
  }

  function renderPlayer() {
    const track = tracks[state.currentTrack];
    const currentSeconds = Math.round((state.progress / 100) * track.duration);

    trackTitleEl.textContent = track.title;
    trackArtistEl.textContent = track.artist;
    togglePlayEl.textContent = state.playing ? "Pause" : "Play";
    progressEl.value = String(state.progress);
    currentTimeEl.textContent = formatTime(currentSeconds);
    durationEl.textContent = formatTime(track.duration);
  }

  function stopTimer() {
    if (state.timer) {
      window.clearInterval(state.timer);
      state.timer = null;
    }
  }

  function startTimer() {
    stopTimer();
    state.timer = window.setInterval(() => {
      state.progress += 1;

      if (state.progress >= 100) {
        state.currentTrack = nextTrackIndex(state.currentTrack, tracks);
        state.progress = 0;
      }

      renderPlayer();
    }, 1000);
  }

  function setPlaying(playing) {
    state.playing = playing;

    if (state.playing) {
      startTimer();
    } else {
      stopTimer();
    }

    renderPlayer();
  }

  filterButtons.forEach((button) => {
    button.addEventListener("click", async () => {
      await setCategory(button.dataset.category);
      window.location.hash = button.dataset.category === "all" ? "index" : button.dataset.category;
      document.querySelector("#index").scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  searchFormEl.addEventListener("submit", async (event) => {
    event.preventDefault();
    state.query = searchInputEl.value.trim();
    state.page = 1;
    await refreshPosts();
  });

  pageNumbersEl.addEventListener("click", (event) => {
    const button = event.target.closest("[data-page]");
    if (!button) {
      return;
    }

    state.page = Number(button.dataset.page);
    renderPosts();
  });

  prevPageEl.addEventListener("click", () => {
    state.page -= 1;
    renderPosts();
  });

  nextPageEl.addEventListener("click", () => {
    state.page += 1;
    renderPosts();
  });

  document.querySelectorAll("[data-nav-category]").forEach((link) => {
    link.addEventListener("click", () => {
      setCategory(link.dataset.navCategory);
    });
  });

  articleEl.addEventListener("submit", async (event) => {
    if (!event.target.matches("#comment-form")) return;
    event.preventDefault();

    const status = document.querySelector("#comment-status");
    const data = new FormData(event.target);

    try {
      await apiFetch(`/api/posts/${encodeURIComponent(state.activeSlug)}/comments`, {
        method: "POST",
        body: JSON.stringify({ nickname: data.get("nickname"), content: data.get("content") }),
      });
      event.target.reset();
      status.textContent = "已提交，审核后显示。";
    } catch (error) {
      status.textContent = "提交失败，请稍后再试。";
    }
  });

  messageFormEl.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = new FormData(messageFormEl);

    try {
      await apiFetch("/api/messages", {
        method: "POST",
        body: JSON.stringify({ nickname: data.get("nickname"), content: data.get("content") }),
      });
      messageFormEl.reset();
      messageStatusEl.textContent = "已提交，审核后显示。";
    } catch (error) {
      messageStatusEl.textContent = "提交失败，请稍后再试。";
    }
  });

  document.querySelector("#previous-track").addEventListener("click", () => {
    state.currentTrack = previousTrackIndex(state.currentTrack, tracks);
    state.progress = 0;
    renderPlayer();
  });

  document.querySelector("#next-track").addEventListener("click", () => {
    state.currentTrack = nextTrackIndex(state.currentTrack, tracks);
    state.progress = 0;
    renderPlayer();
  });

  togglePlayEl.addEventListener("click", () => {
    setPlaying(!state.playing);
  });

  progressEl.addEventListener("input", () => {
    state.progress = Number(progressEl.value);
    renderPlayer();
  });

  volumeEl.addEventListener("input", () => {
    volumeEl.style.setProperty("--volume", `${volumeEl.value}%`);
  });

  window.addEventListener("hashchange", readHash);

  if (heroCardEl) {
    heroCardEl.addEventListener("mousemove", setHeroSpot);
    heroCardEl.addEventListener("mouseleave", () => {
      heroCardEl.style.setProperty("--spot-x", "50%");
      heroCardEl.style.setProperty("--spot-y", "84%");
    });
  }

  async function boot() {
    fillPatternRows();
    await refreshPosts();
    await loadMessages();
    renderPlayer();
    await readHash();
    apiFetch("/api/stats/visit", {
      method: "POST",
      body: JSON.stringify({ path: window.location.pathname || "/" }),
    }).catch(() => {});
  }

  boot();
})();
