FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    cron \
    chromium \
    chromium-driver \
    wget \
    curl \
    unzip \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libglib2.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxshmfence1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN mkdir -p /data /var/log

ENV DATA_DIR=/data
ENV TZ=Asia/Taipei

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "main.py"]
