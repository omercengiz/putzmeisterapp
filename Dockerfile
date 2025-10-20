# Dockerfile

# Python imajını kullan
FROM python:3.11-slim

# pandas + psycopg2 için gerekli
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizini oluştur
WORKDIR /app

# Bağımlılıkları kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projeyi kopyala
COPY . .

# Port belirt
EXPOSE 8000

# Uygulamayı başlat
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
