#!/bin/sh

# Fonksiyon: Veritabanı hazır olana kadar bekler
wait_for_db() {
  until PGPASSWORD=postgres psql -h db -U postgres -d workchecker  -c '\q'; do
    echo "Bekleniyor - Veritabanı hazır olana kadar..."
    sleep 1
  done
  echo "Veritabanı hazır - Migrate işlemi başlıyor."
}

# Veritabanı hazır olana kadar bekleyin
wait_for_db

# Django migrate komutunu çalıştırın
echo "Migrate işlemi başlıyor..."
python manage.py migrate --no-input

echo "Feed datasi isleniyor..."
python manage.py insert_feed_data

# Django collectstatic komutunu çalıştırın (isteğe bağlı)
echo "Static dosyalar toplanıyor..."
python manage.py collectstatic --noinput

# Gunicorn ile Django uygulamasını başlatın
echo "Gunicorn ile Django uygulaması başlatılıyor..."
gunicorn WorkChecker.wsgi:application --bind 0.0.0.0:8000