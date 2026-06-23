# Q Blog Backend

## 本地启动

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
python -m backend.app.seed
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

健康检查：

```text
http://127.0.0.1:8000/api/health
```

后台地址：

```text
http://127.0.0.1:8000/admin
```

默认管理员：

```text
admin / admin123456
```

生产环境应通过环境变量设置管理员信息：

```powershell
$env:BLOG_ADMIN_USERNAME="admin"
$env:BLOG_ADMIN_PASSWORD="替换成强密码"
python -m backend.app.seed
```

## 数据库

默认数据库路径：

```text
backend/data/blog.db
```

可以通过 `BLOG_DB_PATH` 覆盖。

## 测试

```powershell
python -m pytest tests\backend
```
