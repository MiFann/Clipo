# Q Blog

一个极简个人博客，已规划并接入 FastAPI + SQLite 动态后端。

## 功能

- 前台文章列表、分类筛选、搜索、文章详情。
- 匿名评论和留言，默认进入后台审核。
- 后台登录、文章管理、评论审核、留言审核、基础统计。
- 保留原有黑白极简视觉风格和音乐播放器。

## 本地查看静态兜底

直接打开 `index.html` 可以查看前台静态兜底内容。

## 本地启动动态版本

```powershell
python -m pip install -r backend\requirements.txt
python -m backend.app.seed
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

访问：

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/admin/
http://127.0.0.1:8000/api/health
```

默认管理员：

```text
admin / admin123456
```

生产环境部署前请修改管理员密码。

## 测试

```powershell
python -m pytest tests\backend
node --test tests\blog-engine.test.js
```

## ECS 部署

部署说明见：

```text
deploy/ecs-deploy.md
```
