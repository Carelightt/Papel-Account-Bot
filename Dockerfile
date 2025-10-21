# Temel Python imajını kullanıyoruz
FROM python:3.11-slim

# KRİTİK DNS ÇÖZÜMÜ: apt update başarısız olursa, DNS'i Google'a ayarlıyoruz.
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf

# Gerekli sistem paketlerini (Chromium dahil) kuruyoruz.
# update ve install komutları tek bir katmanda zincirlenmeli.
RUN apt-get update && apt-get install -y --no-install-recommends \
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
COPY *.zip .

# Start Command'ımız
CMD ["python", "papel.py"]
