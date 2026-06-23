(function () {
  const tokenKey = "q_blog_admin_token";
  let token = window.localStorage.getItem(tokenKey) || "";

  const loginPanel = document.querySelector("#login-panel");
  const workspace = document.querySelector("#workspace");
  const loginForm = document.querySelector("#login-form");
  const loginMessage = document.querySelector("#login-message");
  const postForm = document.querySelector("#post-form");

  function headers() {
    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    };
  }

  async function api(path, options = {}) {
    const response = await fetch(path, {
      ...options,
      headers: {
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(options.headers || {}),
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return response.status === 204 ? null : response.json();
  }

  function setAuthed(authed) {
    loginPanel.classList.toggle("is-hidden", authed);
    workspace.classList.toggle("is-hidden", !authed);
  }

  function postPayload() {
    const data = new FormData(postForm);
    return {
      title: data.get("title"),
      slug: data.get("slug"),
      excerpt: data.get("excerpt"),
      body: data.get("body"),
      category: data.get("category"),
      status: data.get("status"),
      published_at: data.get("status") === "published" ? new Date().toISOString().slice(0, 10) : null,
    };
  }

  function fillPostForm(post) {
    postForm.elements.id.value = post.id;
    postForm.elements.title.value = post.title;
    postForm.elements.slug.value = post.slug;
    postForm.elements.category.value = post.category;
    postForm.elements.status.value = post.status;
    postForm.elements.excerpt.value = post.excerpt || "";
    postForm.elements.body.value = post.body || "";
  }

  async function loadPosts() {
    const data = await api("/api/admin/posts");
    document.querySelector("#posts-list").innerHTML = data.items
      .map(
        (post) => `
          <article class="admin-item">
            <header>
              <div>
                <h2>${post.title}</h2>
                <p>${post.category} / ${post.status} / ${post.slug}</p>
              </div>
              <div class="item-actions">
                <button type="button" data-edit-post="${post.id}">编辑</button>
                <button type="button" data-delete-post="${post.id}">删除</button>
              </div>
            </header>
          </article>
        `,
      )
      .join("");
    window.__adminPosts = data.items;
  }

  async function loadModeration(type) {
    const data = await api(`/api/admin/${type}`);
    const target = document.querySelector(`#${type}-list`);
    target.innerHTML = data.items
      .map(
        (item) => `
          <article class="admin-item">
            <header>
              <div>
                <h2>${item.nickname}</h2>
                <p>${item.content}</p>
                <p>${item.status}${item.post_title ? ` / ${item.post_title}` : ""}</p>
              </div>
              <div class="item-actions">
                <button type="button" data-moderate="${type}:${item.id}:approved">通过</button>
                <button type="button" data-moderate="${type}:${item.id}:hidden">隐藏</button>
                <button type="button" data-delete="${type}:${item.id}">删除</button>
              </div>
            </header>
          </article>
        `,
      )
      .join("");
  }

  async function loadStats() {
    const data = await api("/api/admin/stats");
    const labels = {
      total_visits: "访问",
      post_count: "文章",
      comment_count: "评论",
      message_count: "留言",
    };
    document.querySelector("#stats-list").innerHTML = Object.entries(labels)
      .map(([key, label]) => `<div class="stat-item"><span>${label}</span><strong>${data[key]}</strong></div>`)
      .join("");
  }

  async function refresh(view = "posts") {
    if (view === "posts") await loadPosts();
    if (view === "comments") await loadModeration("comments");
    if (view === "messages") await loadModeration("messages");
    if (view === "stats") await loadStats();
  }

  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = new FormData(loginForm);

    try {
      const result = await api("/api/admin/login", {
        method: "POST",
        body: JSON.stringify({ username: data.get("username"), password: data.get("password") }),
      });
      token = result.token;
      window.localStorage.setItem(tokenKey, token);
      setAuthed(true);
      await refresh("posts");
    } catch (error) {
      loginMessage.textContent = "登录失败";
    }
  });

  postForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const id = postForm.elements.id.value;
    await api(id ? `/api/admin/posts/${id}` : "/api/admin/posts", {
      method: id ? "PUT" : "POST",
      headers: headers(),
      body: JSON.stringify(postPayload()),
    });
    postForm.reset();
    postForm.elements.id.value = "";
    await loadPosts();
  });

  document.querySelector("#reset-post-form").addEventListener("click", () => {
    postForm.reset();
    postForm.elements.id.value = "";
  });

  document.querySelector("#logout-button").addEventListener("click", () => {
    token = "";
    window.localStorage.removeItem(tokenKey);
    setAuthed(false);
  });

  document.querySelector(".tabs").addEventListener("click", async (event) => {
    const tab = event.target.closest("[data-view]");
    if (!tab) return;

    document.querySelectorAll(".tab").forEach((item) => item.classList.toggle("is-active", item === tab));
    document.querySelectorAll(".view").forEach((view) => {
      view.classList.toggle("is-hidden", view.id !== `view-${tab.dataset.view}`);
    });
    await refresh(tab.dataset.view);
  });

  workspace.addEventListener("click", async (event) => {
    const editButton = event.target.closest("[data-edit-post]");
    const deletePostButton = event.target.closest("[data-delete-post]");
    const moderateButton = event.target.closest("[data-moderate]");
    const deleteButton = event.target.closest("[data-delete]");

    if (editButton) {
      const post = (window.__adminPosts || []).find((item) => item.id === Number(editButton.dataset.editPost));
      if (post) fillPostForm(post);
    }

    if (deletePostButton) {
      await api(`/api/admin/posts/${deletePostButton.dataset.deletePost}`, { method: "DELETE" });
      await loadPosts();
    }

    if (moderateButton) {
      const [type, id, status] = moderateButton.dataset.moderate.split(":");
      await api(`/api/admin/${type}/${id}`, { method: "PUT", body: JSON.stringify({ status }) });
      await loadModeration(type);
    }

    if (deleteButton) {
      const [type, id] = deleteButton.dataset.delete.split(":");
      await api(`/api/admin/${type}/${id}`, { method: "DELETE" });
      await loadModeration(type);
    }
  });

  async function boot() {
    if (!token) {
      setAuthed(false);
      return;
    }

    try {
      await api("/api/admin/me");
      setAuthed(true);
      await refresh("posts");
    } catch (error) {
      window.localStorage.removeItem(tokenKey);
      token = "";
      setAuthed(false);
    }
  }

  boot();
})();
