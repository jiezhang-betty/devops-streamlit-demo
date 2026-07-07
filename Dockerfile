FROM python:3.11-slim

WORKDIR /app

# 可选：安装额外系统依赖（如果需要，但 slim 已自带 gcc 等）
# RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev && rm -rf /var/lib/apt/lists/*

# 安装 bash 和 kubectl
# kubectl 的版本建议与你的 K3s 集群版本匹配，这里以安装最新稳定版为例
RUN apt-get update && apt-get install -y --no-install-recommends bash curl gnupg \
    && curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["streamlit", "run", "app.py", "--server.port=8000", "--server.address=0.0.0.0"]