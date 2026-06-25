# 1. 选择基础镜像（Python 3.11 轻量版，体积小、拉取快）
FROM python:3.11-slim

# 2. 设置容器内工作目录（避免文件混乱）
WORKDIR /app

# 3. 先拷贝依赖清单，利用Docker缓存机制，修改代码不会重复安装依赖
COPY requirements.txt .

# 4. 安装依赖，关闭pip缓存以减小镜像体积
RUN pip install --no-cache-dir -r requirements.txt

# 5. 拷贝项目全部代码到容器内
COPY . .

# 6. 声明服务端口（和后续K8s Service配置统一）
EXPOSE 8501

# 7. 容器启动命令，运行Streamlit应用
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]