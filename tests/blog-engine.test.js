const test = require("node:test");
const assert = require("node:assert/strict");

const {
  filterPosts,
  paginatePosts,
  findPostBySlug,
  nextTrackIndex,
  previousTrackIndex,
} = require("../blog-engine");

const posts = [
  { slug: "render-pipeline", category: "tech", title: "渲染管线笔记" },
  { slug: "quiet-week", category: "notes", title: "安静的一周" },
  { slug: "static-blog", category: "works", title: "静态博客实验" },
  { slug: "css-layout", category: "tech", title: "CSS 布局复盘" },
  { slug: "cache-design", category: "tech", title: "缓存设计清单" },
];

test("filterPosts returns all posts when category is all", () => {
  assert.deepEqual(filterPosts(posts, "all"), posts);
});

test("filterPosts returns only the requested category", () => {
  assert.deepEqual(
    filterPosts(posts, "tech").map((post) => post.slug),
    ["render-pipeline", "css-layout", "cache-design"],
  );
});

test("paginatePosts clamps invalid pages and reports page metadata", () => {
  assert.deepEqual(paginatePosts(posts, 9, 2), {
    items: [posts[4]],
    page: 3,
    pageSize: 2,
    totalPages: 3,
    totalItems: 5,
  });
});

test("findPostBySlug finds a matching article or returns null", () => {
  assert.equal(findPostBySlug(posts, "static-blog"), posts[2]);
  assert.equal(findPostBySlug(posts, "missing"), null);
});

test("track navigation wraps around the placeholder playlist", () => {
  const tracks = [{ title: "A" }, { title: "B" }, { title: "C" }];

  assert.equal(nextTrackIndex(2, tracks), 0);
  assert.equal(previousTrackIndex(0, tracks), 2);
});
