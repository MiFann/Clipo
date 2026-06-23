const CATEGORY_LABELS = {
  all: "全部",
  notes: "随笔",
  tech: "技术",
  works: "作品",
};

const posts = [
  {
    slug: "render-pipeline-notes",
    category: "tech",
    date: "2026.06.18",
    title: "从一次页面卡顿看渲染管线",
    excerpt: "拆解样式计算、布局、绘制与合成之间的边界，记录一次性能定位过程。",
    readTime: "7 min",
    body: [
      "一次交互卡顿通常不是单点问题，而是样式失效范围、布局读写顺序和主线程任务排队共同作用的结果。",
      "我习惯先用 Performance 面板定位长任务，再回到代码里确认是否存在连续的 layout read/write。能不触发布局的状态，尽量交给 transform 和 opacity。",
      "这篇占位文章后续可以替换成真实的性能分析：保留问题背景、采样证据、修复方案和结果对比四段结构即可。",
    ],
  },
  {
    slug: "static-site-routing",
    category: "tech",
    date: "2026.06.15",
    title: "静态站里的 Hash 路由设计",
    excerpt: "不用框架也能把列表、详情、分页和回退体验组织清楚。",
    readTime: "5 min",
    body: [
      "静态博客最轻的跳转方案是 hash。它不需要服务端重写，也不会破坏文件直开体验。",
      "列表状态适合放在运行时，文章详情适合放在 hash 中。这样复制链接时能直达文章，同时保留分页和筛选的即时响应。",
      "如果未来迁移到 Astro、Next 或 Nuxt，这套数据结构依然能直接复用。",
    ],
  },
  {
    slug: "cache-invalidation",
    category: "tech",
    date: "2026.06.10",
    title: "缓存失效不是删除缓存那么简单",
    excerpt: "缓存策略真正难的部分，是命名、过期边界和写入路径的一致性。",
    readTime: "8 min",
    body: [
      "缓存命中率很容易被指标包装得很好看，但错误的数据会把所有收益清零。",
      "一个可控的缓存设计至少要回答三件事：谁写入、谁失效、什么时候允许读旧值。",
      "工程里最稳的方案往往不是最聪明的方案，而是最容易被后来者验证的方案。",
    ],
  },
  {
    slug: "type-boundary",
    category: "tech",
    date: "2026.06.02",
    title: "类型边界应该靠近不可信输入",
    excerpt: "把校验推到系统边界，内部代码会轻很多。",
    readTime: "6 min",
    body: [
      "类型系统能表达约束，但它不能替你检查接口、表单、配置文件和本地存储。",
      "我更喜欢在边界处把 unknown 收窄成业务类型，然后让内部函数只接受已经可信的数据。",
      "这能减少到处散落的防御式判断，也让测试集中在输入转换层。",
    ],
  },
  {
    slug: "quiet-interface",
    category: "notes",
    date: "2026.05.29",
    title: "安静的界面更耐看",
    excerpt: "少一点说明文字，多一点明确的结构，使用者会更快进入内容。",
    readTime: "4 min",
    body: [
      "我喜欢克制的界面，因为它不会一直争夺注意力。",
      "留白、秩序和稳定的交互，比堆叠装饰更能形成记忆点。",
      "个人博客尤其适合这种方式：内容是主体，视觉只负责建立气质。",
    ],
  },
  {
    slug: "blog-system-work",
    category: "works",
    date: "2026.05.22",
    title: "个人博客系统原型",
    excerpt: "一个无框架的静态博客实验，包含索引、详情、分页和音乐播放器。",
    readTime: "3 min",
    body: [
      "这个作品原型优先验证信息架构，而不是追求复杂技术栈。",
      "它把博客最常用的动作压缩到单页内：筛选、翻页、阅读和听音乐。",
      "后续可以逐步接入 Markdown 构建、RSS、搜索和主题切换。",
    ],
  },
  {
    slug: "component-checklist",
    category: "tech",
    date: "2026.05.18",
    title: "组件评审时我会看什么",
    excerpt: "状态边界、键盘可达性、空状态和响应式约束，是最容易被低估的部分。",
    readTime: "6 min",
    body: [
      "一个组件是否可靠，不能只看默认状态是否好看。",
      "我会先检查它在极长文本、空数据、加载中、错误和窄屏下是否仍然稳定。",
      "视觉细节要服务于重复使用，而不是只服务于截图。",
    ],
  },
];

const tracks = [
  {
    title: "Placeholder 01",
    artist: "Q Blog",
    duration: 186,
    src: "",
  },
  {
    title: "Midnight Compile",
    artist: "Q Blog",
    duration: 214,
    src: "",
  },
  {
    title: "Static Memory",
    artist: "Q Blog",
    duration: 162,
    src: "",
  },
];

function filterPosts(sourcePosts, category) {
  if (!category || category === "all") {
    return sourcePosts;
  }

  return sourcePosts.filter((post) => post.category === category);
}

function paginatePosts(sourcePosts, page, pageSize) {
  const totalItems = sourcePosts.length;
  const safePageSize = Math.max(1, Number(pageSize) || 1);
  const totalPages = Math.max(1, Math.ceil(totalItems / safePageSize));
  const requestedPage = Number(page) || 1;
  const safePage = Math.min(Math.max(1, requestedPage), totalPages);
  const start = (safePage - 1) * safePageSize;

  return {
    items: sourcePosts.slice(start, start + safePageSize),
    page: safePage,
    pageSize: safePageSize,
    totalPages,
    totalItems,
  };
}

function findPostBySlug(sourcePosts, slug) {
  return sourcePosts.find((post) => post.slug === slug) || null;
}

function nextTrackIndex(currentIndex, sourceTracks) {
  if (!sourceTracks.length) {
    return 0;
  }

  return (currentIndex + 1) % sourceTracks.length;
}

function previousTrackIndex(currentIndex, sourceTracks) {
  if (!sourceTracks.length) {
    return 0;
  }

  return (currentIndex - 1 + sourceTracks.length) % sourceTracks.length;
}

const api = {
  CATEGORY_LABELS,
  posts,
  tracks,
  filterPosts,
  paginatePosts,
  findPostBySlug,
  nextTrackIndex,
  previousTrackIndex,
};

if (typeof module !== "undefined") {
  module.exports = api;
}

if (typeof window !== "undefined") {
  window.BlogEngine = api;
}
