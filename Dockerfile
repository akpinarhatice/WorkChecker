# Python 3.9-slim imajını kullan
FROM python:3.9-slim

# Gerekli sistem bağımlılıklarını yükle
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizinini oluştur
WORKDIR /app

# Gereksinimleri kopyala ve kur
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . /app/

# Port 8000'i aç
EXPOSE 8000

# Django server'ı çalıştır
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
