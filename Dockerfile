# 🛑 KRİTİK DEĞİŞİKLİK: Hazır Selenium Base İmajına geçiyoruz.
# Bu imajın içinde Python, Java, Chrome, ChromeDriver hepsi kurulu ve hazırdır.
FROM selenium/standalone-chrome:126.0

# Render Build sürecinde Python ortamını yapılandırıyoruz:
USER root

# Çalışma dizinini ayarlıyoruz
# ... (Diğer satırlar aynı kalır) ...

# Çalışma dizinini ayarlıyoruz
WORKDIR /usr/src/app

# requirements.txt dosyasını kopyalayıp Python bağımlılıklarını kuruyoruz
COPY requirements.txt ./
# 🛑 KESİN ÇÖZÜM: 'pip' komutu yerine 'python3 -m pip' kullanıyoruz
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Bot kodunu kopyalıyoruz
COPY papel.py .
COPY *.zip .

# Ortam değişkenini ayarlıyoruz (PATH'i koruyoruz)
ENV PATH="/usr/bin/python3:$PATH"

# Botu çalıştırıyoruz (Bu da python3 olmalı)
CMD ["python3", "papel.py"]
