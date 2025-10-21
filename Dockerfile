# 🛑 KRİTİK DEĞİŞİKLİK: Hazır Selenium Base İmajına geçiyoruz.
FROM selenium/standalone-chrome:126.0

USER root

# Çalışma dizinini ayarlıyoruz
WORKDIR /usr/src/app

# requirements.txt dosyasını kopyalayıp Python bağımlılıklarını kuruyoruz
COPY requirements.txt ./

# 🛑 KRİTİK ÇÖZÜM: pip'i manuel olarak kuruyoruz.
# Temel curl aracını kuruyoruz
RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*
    
# get-pip.py script'i ile pip'i kuruyoruz
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3

# Botun kütüphanelerini yüklüyoruz (Artık pip kuruldu!)
RUN pip install --no-cache-dir -r requirements.txt

# Bot kodunu kopyalıyoruz
COPY papel.py .
COPY *.zip .

# Ortam değişkenini ayarlıyoruz (PATH'i koruyoruz)
ENV PATH="/usr/bin/python3:$PATH"

# Botu çalıştırıyoruz
CMD ["python3", "papel.py"]
