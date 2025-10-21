# 🛑 KRİTİK DEĞİŞİKLİK: Hazır Selenium Base İmajına geçiyoruz.
# Bu imajın içinde Python, Java, Chrome, ChromeDriver hepsi kurulu ve hazırdır.
FROM selenium/standalone-chrome:126.0

# Render Build sürecinde Python ortamını yapılandırıyoruz:
USER root

# Çalışma dizinini ayarlıyoruz
WORKDIR /usr/src/app

# requirements.txt dosyasını kopyalayıp Python bağımlılıklarını kuruyoruz
COPY requirements.txt ./
# Python kütüphanelerini kuruyoruz (Bu imajda zaten Python 3.11+ var)
RUN pip install --no-cache-dir -r requirements.txt

# Bot kodunu kopyalıyoruz
COPY papel.py .
# Proxy zip dosyalarını kopyalıyoruz
COPY *.zip .

# Ortam değişkenini ayarlıyoruz (Bu imaj, botu başlatmak için varsayılan olarak Python'ı kullanır)
ENV PATH="/usr/bin/python3:$PATH"

# Botu çalıştırıyoruz
CMD ["python3", "papel.py"]
