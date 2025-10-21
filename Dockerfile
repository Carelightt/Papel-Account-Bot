# Temel Python imajını kullanıyoruz
FROM python:3.11-slim

# Gerekli sistem paketlerini (Chromium dahil) kuruyoruz.
# DİKKAT: apt-get update komutu tamamen kaldırıldı.
RUN apt-get install -y --no-install-recommends \
    chromium-browser \
    libnss3 \
    libgconf-2-4 \
    libasound2 \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizinini ayarlıyoruz
WORKDIR /usr/src/app

# requirements.txt dosyasını kopyalayıp Python bağımlılıklarını kuruyoruz
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Bot kodunu kopyalıyoruz
COPY papel.py .
COPY *.zip . # Proxy zip dosyalarını da kopyala

# Start Command'ımız
CMD ["python", "papel.py"]
