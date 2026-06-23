# 阿里云 ECS 部署步骤

## 1. 准备服务器

建议系统：Ubuntu 22.04 或 24.04。

安装依赖：

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx git
```

## 2. 上传项目

目标目录：

```bash
sudo mkdir -p /var/www/blog
sudo chown -R "$USER":"$USER" /var/www/blog
```

把项目文件放到 `/var/www/blog`。

## 3. 安装 Python 依赖

```bash
cd /var/www/blog
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r backend/requirements.txt
```

## 4. 初始化数据库和管理员

```bash
cd /var/www/blog
. .venv/bin/activate
export BLOG_ADMIN_USERNAME="admin"
export BLOG_ADMIN_PASSWORD="替换成强密码"
python -m backend.app.seed
```

数据库会生成在：

```text
/var/www/blog/backend/data/blog.db
```

## 5. 配置 systemd

```bash
sudo cp deploy/blog.service /etc/systemd/system/blog.service
sudo systemctl daemon-reload
sudo systemctl enable --now blog
sudo systemctl status blog
```

查看日志：

```bash
journalctl -u blog -f
```

## 6. 配置 Nginx

先把 `deploy/nginx-blog.conf` 里的 `server_name example.com;` 改成你的域名或服务器公网 IP。

```bash
sudo cp deploy/nginx-blog.conf /etc/nginx/sites-available/blog
sudo ln -s /etc/nginx/sites-available/blog /etc/nginx/sites-enabled/blog
sudo nginx -t
sudo systemctl reload nginx
```

## 7. 阿里云安全组

放行：

```text
80
443
```

不要对公网开放 `8000`。

## 8. 验证

```text
http://你的域名或公网IP/
http://你的域名或公网IP/api/health
http://你的域名或公网IP/admin/
```

## 9. HTTPS

域名解析完成后，可以用 Certbot 或阿里云证书给 Nginx 配 HTTPS。
