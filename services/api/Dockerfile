FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=Asia/Shanghai

WORKDIR /app

COPY pyproject.toml alembic.ini ./

RUN pip install --upgrade pip \
    && pip install -i https://pypi.tuna.tsinghua.edu.cn/simple .

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]
