FROM python:3.11-slim

# 建立工作目錄
WORKDIR /app

# 複製依賴檔並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案程式碼（只要 .py、設定等，.venv 不會被用）
COPY . .

# 使用 uvicorn 啟動 FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000","--reload"]
