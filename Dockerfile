FROM python:3.10-slim

WORKDIR /app

# 安裝系統基本依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 複製並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案原始碼與資源
COPY . .

# 暴露 Streamlit 預設連接埠
EXPOSE 8501

# 設定環境變數
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true

# 啟動命令
CMD ["streamlit", "run", "app.py"]
