# Dockerfile

# Python imajını kullan
FROM python:3.11-slim

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
