import logging
import time
import random
import re
import zipfile 
import os 
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackContext,
)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, InvalidElementStateException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
# 👇👇👇 KRİTİK IMPORT: Service objesi için eklendi 👇👇👇
from selenium.webdriver.chrome.service import Service 

# ==============================================================================
# ⚠️ AYARLAR ⚠️
# ==============================================================================

# Lütfen TOKEN'ınızı buraya girin!
TELEGRAM_TOKEN = "8472595823:AAFO4B_OPb_twBR8zXu-dsjrs4hkt0ra4oE"
BASE_URL = "https://mywallet.papel.com.tr/register"

# YÖNETİCİ AYARI: Sadece bu ID'ye sahip kullanıcı özel komutları kullanabilir.
ADMIN_ID = 6672759317 

# 👇👇👇 PROXY AYARLARI BAŞLANGICI 👇👇👇

# Proxy Kimlik Bilgileri
PROXY_USERNAME = "u15ef7771569d05be-zone-custom-region-tr-session-9Ek2vWsaf-sessTime-100"
PROXY_PASSWORD = "CengizzAtay"

# Proxy Listesi (IP:PORT formatında) - HESAP AÇARKEN RASTGELE KULLANILACAK
PROXY_LIST = [
    "118.193.59.17:17553", "118.193.59.87:17948", "118.193.59.17:17551",
    "118.193.59.87:17941", "118.193.59.165:17663", "118.193.59.165:17670",
    "118.193.59.92:17565", "118.193.59.165:17672", "118.193.59.92:17556",
    "118.193.59.165:17665", "118.193.59.165:17667", "118.193.59.165:17657",
    "118.193.59.92:17560", "118.193.59.92:17558", "118.193.59.92:17563",
    "118.193.59.87:17958", "118.193.59.165:17660", "118.193.59.165:17662",
    "118.193.59.17:17548", "118.193.59.87:17956", "118.193.59.92:17574",
    "107.150.117.248:17805", "118.193.59.87:17949", "118.193.59.87:17951",
    "107.150.117.248:17803", "118.193.59.92:17571", "107.150.117.248:17804",
    "118.193.59.87:17959", "118.193.59.87:17947", "118.193.59.17:17549",
    "107.150.117.248:17797", "118.193.59.87:17957", "107.150.117.248:17808",
    "118.193.59.87:17945", "118.193.59.17:17546", "118.193.59.87:17950",
    "118.193.59.92:17561", "107.150.117.248:17793", "107.150.117.248:17795",
    "118.193.59.17:17538", "107.150.117.248:17801", "118.193.59.17:17556",
    "118.193.59.17:17539", "118.193.59.17:17540", "118.193.59.92:17566",
    "118.193.59.92:17562", "118.193.59.87:17942", "118.193.59.92:17572",
    "118.193.59.87:17943", "118.193.59.165:17664", "107.150.117.248:17807",
    "118.193.59.17:17550", "118.193.59.92:17564", "107.150.117.248:17790",
    "118.193.59.17:17547", "118.193.59.92:17557", "118.193.59.17:17543",
    "118.193.59.165:17668", "118.193.59.17:17545", "118.193.59.87:17946",
    "118.193.59.87:17940", "107.150.117.248:17791", "107.150.117.248:17800",
    "107.150.117.248:17798", "118.193.59.17:17557", "118.193.59.92:17567",
    "118.193.59.92:17573", "118.193.59.165:17671", "107.150.117.248:17794",
    "118.193.59.92:17568", "118.193.59.87:17954", "118.193.59.87:17953",
    "118.193.59.87:17955", "118.193.59.165:17673", "107.150.117.248:17789",
    "118.193.59.17:17541", "118.193.59.92:17559", "118.193.59.165:17658",
    "107.150.117.248:17792", "118.193.59.165:17659", "118.193.59.165:17669",
    "118.193.59.87:17952", "118.193.59.17:17544", "118.193.59.17:17554",
    "118.१९3.59.92:17570", "118.193.59.165:17661", "107.150.117.248:17796",
    "118.193.59.87:17944", "107.150.117.248:17799", "118.193.59.92:17569",
    "118.193.59.165:17655", "118.193.59.165:17654", "118.193.59.17:17555",
    "107.150.117.248:17802", "118.193.59.92:17575", "118.193.59.165:17666",
    "118.193.59.17:17552", "107.150.117.248:17806", "118.193.59.165:17656",
    "118.193.59.17:17542"
]

# 👆👆👆 PROXY AYARLARI SONU 👆👆👆

# Web sitesi elementlerinin (ID/XPath) tam ve güncel hali
WEB_ELEMENTS = {
    "PHONE_INPUT_XPATH": "//input[@class='react-international-phone-input']",
    "PHONE_NEXT_BTN_XPATH": "//button[contains(span/text(), 'Devam')]",
    "SMS_CODE_INPUT_CLASS": "input-otp",
    "SMS_CODE_PARENT_CLASS": "otp-inputs-wrapper",
    "SECURITY_IMAGE_CLASS": "security-image-wrapper",
    "SECURITY_NEXT_BTN_XPATH": "//button[contains(span/text(), 'Devam Et')]",
    "SECURITY_IMAGE_TITLE_CLASS": "security-image-title",
    "NAME_INPUT_ID": "name",
    "SURNAME_INPUT_ID": "surname",
    "INVITATION_CODE_ID": "code",
    "CHECKBOX_1_ID": "checkbox_group_1",
    "CHECKBOX_3_ID": "checkbox_group_3",
    "CHECKBOX_4_ID": "checkbox_group_4",
    "CHECKBOX_6_ID": "checkbox_group_6",
    "NAME_SURNAME_NEXT_BTN_XPATH": "//button[contains(span/text(), 'Devam')]",
    "MODAL_TITLE_XPATH": "//div[@class='modal__body__title']",
    "MODAL_CONTINUE_XPATH": "//div[@role='dialog']//button[contains(span/text(), 'Devam Et')]",
    "MODAL_ACCEPT_XPATH": "//div[@role='dialog']//button[contains(span/text(), 'Okudum ve Kabul Ediyorum')]",
    
    "EMAIL_INPUT_ID": "email",
    "EMAIL_NEXT_BTN_XPATH": "//button[contains(@class, 'email__button') and contains(span/text(), 'Devam')]",
    "EMAIL_CODE_INPUT_CLASS": "input-otp",
    "EMAIL_CODE_PARENT_CLASS": "otp-inputs-wrapper",
    "PASSWORD_INPUT_ID": "password",
    "REPEAT_PASSWORD_INPUT_ID": "repeatPassword",
    "CREATE_PASSWORD_BTN_XPATH": "//button[contains(span/text(), 'Şifre Oluştur')]",
}

# ==============================================================================
# Durumlar (SADECE ONAY KODLARI İÇİN KALDI)
# ==============================================================================
SMS_CODE, EMAIL_CODE, CREATE_PASSWORD = range(3)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==============================================================================
# Yetkilendirme ve Yardımcı Fonksiyonlar
# ==============================================================================

def is_authorized_group(chat_id, context: CallbackContext) -> bool:
    """Belirtilen chat_id'nin hesap açma hakkı olup olmadığını kontrol eder."""
    # Grup ID'leri negatif sayılardır.
    if chat_id > 0:
        return False # Özel sohbetleri (DM) yetkilendirme dışı bırak

    # Botun grup verilerini al
    group_data = context.application.bot_data.get(chat_id, {})
    remaining_rights = group_data.get('rights', 0)
    
    return remaining_rights > 0

async def unauthorized_message(update: Update):
    """Yetkisiz kullanıcılar veya gruplar için hata mesajı gönderir."""
    await update.message.reply_text(
        "Hakkınız yoktur. İletişim için @CengizzAtay.",
        reply_to_message_id=update.message.message_id 
    )

def create_proxy_extension(proxy_address):
    # ... (Aynı kalacak) ...
    # Kodu karmaşıklaştırmamak için bu kısmı yukarıdaki tam kodda olduğu gibi bırakıyorum.

    # 1. Manifest dosyası
    manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""
    # 2. Arkaplan betiği (Kimlik bilgilerini buraya gömüyoruz)
    background_js = """
var config = {
    mode: "fixed_servers",
    rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
    }
};

chrome.proxy.settings.set({config: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
    callbackFn,
    {urls: ["<all_urls>"]},
    ['blocking']
);
""" % (proxy_address.split(":")[0], proxy_address.split(":")[1], PROXY_USERNAME, PROXY_PASSWORD)
    
    # Her çalıştırma için benzersiz bir dosya adı oluştur
    plugin_file = f'proxy_auth_plugin_{int(time.time() * 1000)}.zip'
    
    with zipfile.ZipFile(plugin_file, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
        
    return plugin_file

def initialize_driver(user_id):
    """Her kullanıcı için ayrı bir Selenium Driver başlatır ve rastgele proxy ekler."""
    
    # 1. Rastgele Proxy Seçimi (Listedeki proxy'ler SILINMEYECEK)
    if not PROXY_LIST:
        logger.error("Proxy listesi boş. Proxy olmadan devam ediliyor.")
        random_proxy = None
    else:
        random_proxy = random.choice(PROXY_LIST)
        logger.info(f"Kullanıcı {user_id} için rastgele seçilen proxy: {random_proxy}")
        
    chrome_options = Options()
    
    # 🛑 RENDER İÇİN KRİTİK AYARLAR VE HEADLESS MOD 🛑
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-zygote") # Çekirdek hatası için ek önlem
    
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")

    proxy_plugin_path = None
    if random_proxy:
        try:
            # 2. Proxy Eklentisini Oluştur ve Ekle
            proxy_plugin_path = create_proxy_extension(random_proxy)
            chrome_options.add_extension(proxy_plugin_path)
            logger.info(f"Proxy eklentisi ({random_proxy}) driver'a eklendi.")
        except Exception as e:
            logger.error(f"Proxy eklentisi oluşturma hatası: {e}")
            random_proxy = None # Hata durumunda proxy kullanımdan kaldırılır
            
# initialize_driver fonksiyonunun içinde, try bloğu:
    try:
        # RENDER KRİTİK AYARI: RENDER'ın Chromium'u bulması için
        # executable_path parametresini kullanıyoruz. Render'da genellikle bu yoldadır.
        # 🛑 DÜZELTME: Service objesi oluşturuyoruz
        # Render'daki Chromium yolu /usr/bin/chromium-browser
        service = Service(executable_path='/usr/bin/chromium-browser')
        
        # 🛑 DÜZELTME: Service objesi ile çağırıyoruz
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get(BASE_URL)
        return driver
    # Varsa fazla boşlukları silip, try ile aynı hizada olduğundan emin olun:
    except Exception as e:
        # Bu satır (logger.error), except'in 4 boşluk içeride olmalı:
        logger.error(f"FATAL RENDER HATA: Selenium Driver başlatılamadı. Hata: {type(e).__name__} - {e}")
        return None
        
def close_driver(key, context: CallbackContext):
    """Driver'ı kapatır ve kayıtları temizler. Driver'ı saklamak için benzersiz KEY kullanır."""
    
    # Key, user_id veya user_id_chat_id olabilir.
    if key in context.application.bot_data and 'driver' in context.application.bot_data[key]:
        context.application.bot_data[key]['driver'].quit()
        
        del context.application.bot_data[key]['driver']
        # Tüm ConversationHandler bittiğinde driver_key'i de temizleyelim.
        if 'driver_key' in context.user_data:
            del context.user_data['driver_key']
        logger.info(f"Driver ({key}) kapatıldı.")


async def _custom_modal_action(driver, modal_continue_xpath, wait_time, log_msg):
    # ... (Aynı kalacak) ...
    try:
        btn = WebDriverWait(driver, 5).until( # Maksimum 5 saniye bekleme
            EC.element_to_be_clickable((By.XPATH, modal_continue_xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        driver.execute_script("arguments[0].click();", btn)
        logger.info(log_msg)
        time.sleep(wait_time) # İstenen bekleme süresi butona basıldıktan sonra uygulanır
    except TimeoutException:
        logger.warning(f"Zaman aşımı: {log_msg} butonu bulunamadı/tıklanamadı.")
        pass
    except Exception as e:
        logger.error(f"Özel Modal Aksiyon Hatası: {e}")
        raise e

# ==============================================================================
# YÖNETİCİ KOMUTLARI
# ==============================================================================

async def hakver(update: Update, context: CallbackContext) -> None:
    """Belirtilen gruba hesap açma hakkı ekler."""
    if update.effective_user.id != ADMIN_ID:
        await unauthorized_message(update)
        return
        
    chat_id = update.effective_chat.id
    
    try:
        if context.args and context.args[0].isdigit():
            count = int(context.args[0])
            
            # Gruplar için bot_data'da bir giriş oluştur
            if chat_id not in context.application.bot_data:
                context.application.bot_data[chat_id] = {'rights': 0, 'accounts_opened': 0}
            
            context.application.bot_data[chat_id]['rights'] += count
            
            await update.message.reply_text(
                f"✅ Bu gruba {count} adet hesap açma hakkı verildi.\n"
                f"Güncel hak sayısı: {context.application.bot_data[chat_id]['rights']}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("Hata: Lütfen hak sayısını belirtin. Örn: `/hakver 20`")

    except Exception as e:
        logger.error(f"Hak verme hatası: {e}")
        await update.message.reply_text("Hak verme sırasında bir hata oluştu.")


async def kaldir(update: Update, context: CallbackContext) -> None:
    """Belirtilen grubun hesap açma haklarını sıfırlar."""
    if update.effective_user.id != ADMIN_ID:
        await unauthorized_message(update)
        return
        
    chat_id = update.effective_chat.id
    
    if chat_id in context.application.bot_data:
        context.application.bot_data[chat_id]['rights'] = 0
        await update.message.reply_text("✅ Bu grubun tüm hesap açma hakları sıfırlandı.", parse_mode='Markdown')
    else:
        await update.message.reply_text("Bu grubun zaten tanımlı bir hakkı bulunmuyor.")


async def rapor(update: Update, context: CallbackContext) -> None:
    """O gün açılan hesap sayısını söylesin."""
    if update.effective_user.id != ADMIN_ID:
        await unauthorized_message(update)
        return

    chat_id = update.effective_chat.id
    
    # Tüm gruplardaki toplam açılan hesabı bul
    total_opened = 0
    report_details = []
    
    # Sadece negatif (grup) ID'leri kontrol et
    for cid, data in context.application.bot_data.items():
        if cid < 0:
            count = data.get('accounts_opened', 0)
            total_opened += count
            
            # Grubu bul ve ismini al
            try:
                 chat_info = await context.bot.get_chat(cid)
                 chat_name = chat_info.title
            except Exception:
                 chat_name = f"ID: {cid}"

            report_details.append(f"- {chat_name} : {count} hesap (Kalan Hak: {data.get('rights', 0)})")


    if total_opened == 0:
        message = "Bugün henüz hiçbir grupta hesap açılmamış."
    else:
        message = (
            f"BUGÜN AÇILAN HESAP RAPORU\n\n"
            f"Toplam Açılan Hesap: {total_opened}\n\n"
            f"Detaylar:\n" + "\n".join(report_details)
        )
        
    await update.message.reply_text(message, parse_mode='Markdown')

# ==============================================================================
# Telegram Conversation Handler Fonksiyonları
# ==============================================================================

async def start_hesapac_with_data(update: Update, context: CallbackContext) -> int:
    """/hesapac komutunu alır, yetkiyi ve argümanları kontrol eder, Selenium akışını başlatır."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # 1. Yetki Kontrolü
    if not is_authorized_group(chat_id, context):
        await unauthorized_message(update)
        return ConversationHandler.END

    # 2. Argümanları Ayrıştırma
    full_text = update.message.text.strip()
    args = full_text.split()
    
    if len(args) < 6:
        await update.message.reply_text(
            "Hata: Lütfen komutu doğru formatta kullanın.\n"
            "Örn: `/hesapac 5xx xxxxxxx mail@ornek.com Ali Yilmaz 123456`",
            reply_to_message_id=update.message.message_id
        )
        return ConversationHandler.END

    # Argümanların sırası: (telefon) (mail) (ad) (soyad) (şifre)
    phone_number_raw = args[1]
    email_address = args[2]
    name = args[3]
    surname = args[4]
    password = args[5]

    # Temizleme ve Doğrulama
    phone_number = phone_number_raw.replace(" ", "").replace("+90", "").lstrip("0")
    if not phone_number.isdigit() or len(phone_number) != 10:
        await update.message.reply_text("Hata: Telefon numarası formatı geçersiz (10 hane olmalı).")
        return ConversationHandler.END
        
    if "@" not in email_address or len(password) != 6 or not password.isdigit():
        await update.message.reply_text("Hata: E-posta veya Şifre formatı geçersiz (Şifre 6 haneli rakam olmalı).")
        return ConversationHandler.END

    # 3. Verileri Kaydet ve Oturumu Başlat
    context.user_data['phone'] = phone_number
    context.user_data['email'] = email_address
    context.user_data['name'] = name
    context.user_data['surname'] = surname
    context.user_data['password'] = password
    context.user_data['chat_id'] = chat_id # Komutun geldiği grup ID'sini kaydet
    
    # 🛑 EŞ ZAMANLI ÇALIŞMA İÇİN BENZERSİZ ANAHTAR OLUŞTURULDU
    driver_key = f"{user_id}_{chat_id}"
    context.user_data['driver_key'] = driver_key # Kapatma için anahtarı sakla
    
    close_driver(driver_key, context) # Yeni benzersiz anahtarla kapat

    driver = initialize_driver(user_id)
    if not driver:
        # initialize_driver'dan gelen hata loglandı, şimdi kullanıcıya hata mesajı gönder
        await update.message.reply_text("Hata: Web tarayıcı başlatılamadı. Lütfen logları kontrol edin.", reply_to_message_id=update.message.message_id)
        return ConversationHandler.END

    if driver_key not in context.application.bot_data:
        context.application.bot_data[driver_key] = {}
        
    # Driver'ı benzersiz anahtarla saklıyoruz
    context.application.bot_data[driver_key]['driver'] = driver
    
    try:
        # Selenium Adımları (Telefon Numarası Girişi)
        phone_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, WEB_ELEMENTS["PHONE_INPUT_XPATH"]))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", phone_input)
        
        phone_input.send_keys(phone_number)
        driver.find_element(By.XPATH, WEB_ELEMENTS["PHONE_NEXT_BTN_XPATH"]).click()
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, WEB_ELEMENTS["SMS_CODE_PARENT_CLASS"]))
        )
        
        # SMS kodu mesajını gruba gönder ve message_id'yi kaydet
        message = await context.bot.send_message(
             chat_id=chat_id,
             text=f"<b>{phone_number}</b> numarasına gönderilen 6 haneli SMS onay kodunu bu mesaja yanıt vererek girin.",
             parse_mode='HTML'
        )
        context.user_data['sms_message_id'] = message.message_id
        
        return SMS_CODE
        
    except Exception as e:
        logger.error(f"Telefon adımında hata ({user_id}): {e}")
        close_driver(driver_key, context) # Benzersiz anahtarla kapat
        await context.bot.send_message(
            chat_id=chat_id,
            text="Telefon gönderme hatası. Lütfen /hesapac komutunu tekrar dene.",
            reply_to_message_id=update.message.message_id
        )
        return ConversationHandler.END

async def get_sms_code(update: Update, context: CallbackContext) -> int:
    """SMS kodunu, botun mesajına yanıt olarak gelirse alır ve işler."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    driver_key = context.user_data.get('driver_key') # Benzersiz anahtarı al
    driver = context.application.bot_data.get(driver_key, {}).get('driver') # Benzersiz anahtarla eriş
    
    # 1. Kodun, beklenen mesaja yanıt olup olmadığını kontrol et
    if not update.message.reply_to_message or update.message.reply_to_message.message_id != context.user_data.get('sms_message_id'):
        return SMS_CODE # Yanıt değilse, beklemede kal
        
    sms_code = update.message.text.strip()

    if not driver:
        await context.bot.send_message(chat_id, "Oturum süresi doldu. Lütfen tekrar /hesapac yaz.")
        return ConversationHandler.END
        
    if len(sms_code) != 6 or not sms_code.isdigit():
        await context.bot.send_message(chat_id, "Hata: Lütfen sadece 6 haneli kodu girin.", reply_to_message_id=update.message.message_id)
        return SMS_CODE

    # ... (Geri kalan Selenium SMS Kodu adımları aynı kalacak) ...
    try:
        code_inputs = driver.find_elements(By.CLASS_NAME, WEB_ELEMENTS["SMS_CODE_INPUT_CLASS"])
        if len(code_inputs) < 6:
            raise Exception("Beklenen 6 adet SMS kodu input alanı bulunamadı.")
            
        for i, digit in enumerate(sms_code):
            code_inputs[i].send_keys(digit)
            time.sleep(0.1) 

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, WEB_ELEMENTS["SECURITY_IMAGE_TITLE_CLASS"]))
        )
        
        await context.bot.send_message(chat_id, "✅ SMS kodu doğru.", reply_to_message_id=update.message.message_id)
        
        return await select_security_image(update, context)
        
    except Exception as e:
        logger.error(f"SMS kodu adımında hata ({user_id}): {e}")
        close_driver(driver_key, context) # Benzersiz anahtarla kapat
        await context.bot.send_message(chat_id, "SMS kodu yanlış veya zaman aşımına uğradı. Lütfen /hesapac ile tekrar dene.", reply_to_message_id=update.message.message_id)
        return ConversationHandler.END

# select_security_image, fill_name_surname_and_continue fonksiyonları aynı kalacak
# (update.message.reply_text yerine context.bot.send_message(chat_id=chat_id, ...) kullanımlarını korudum)

async def select_security_image(update: Update, context: CallbackContext) -> int:
    """Rastgele bir güvenlik resmi seçer, devam eder ve Ad/Soyad adımına geçer (otomatik)."""
    user_id = update.effective_user.id
    chat_id = context.user_data.get('chat_id')
    
    driver_key = context.user_data.get('driver_key') # Benzersiz anahtarı al
    driver = context.application.bot_data.get(driver_key, {}).get('driver') # Benzersiz anahtarla eriş

    if not driver:
        return ConversationHandler.END

    try:
        # ... (Selenium adımları) ...
        image_wrappers = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, WEB_ELEMENTS["SECURITY_IMAGE_CLASS"]))
        )
        if not image_wrappers:
            raise Exception("Captcha bulunamadı.")
            
        driver.execute_script("arguments[0].scrollIntoView({block: 'start'});", image_wrappers[0])
        
        random_image = random.choice(image_wrappers)
        random_image.click() 
        
        time.sleep(2) 

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, WEB_ELEMENTS["SECURITY_NEXT_BTN_XPATH"]))
        ).click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, WEB_ELEMENTS["NAME_INPUT_ID"]))
        )
        
        return await fill_name_surname_and_continue(update, context)
        
    except Exception as e:
        logger.error(f"Güvenlik resmi adımında hata ({user_id}): {e}")
        close_driver(driver_key, context) # Benzersiz anahtarla kapat
        await context.bot.send_message(chat_id, "Captchayı geçemedim. Lütfen /hesapac ile tekrar dene.")
        return ConversationHandler.END


async def fill_name_surname_and_continue(update: Update, context: CallbackContext) -> int:
    """
    AD SOYAD GİRİŞİNİ VE ÖZEL CHECKBOX ZİNCİRİNİ YÖNETİR.
    """
    user_id = update.effective_user.id
    chat_id = context.user_data.get('chat_id')
    
    driver_key = context.user_data.get('driver_key') # Benzersiz anahtarı al
    driver = context.application.bot_data.get(driver_key, {}).get('driver') # Benzersiz anahtarla eriş
    
    name = context.user_data.get('name')
    surname = context.user_data.get('surname')

    if not driver or not name or not surname:
        await context.bot.send_message(chat_id, "Hata: Ad/Soyad bilgileri eksik veya oturum doldu. Lütfen tekrar /hesapac yaz.")
        return ConversationHandler.END

    try:
        # ... (ActionChains adımları) ...
        
        actions = ActionChains(driver)

        # 1. TAB ile Ad alanına gel (1. TAB)
        actions.send_keys(Keys.TAB).pause(0.5).perform()
        actions.send_keys(name).pause(0.5).perform()

        # 3. TAB ile Soyad alanına geç (2. TAB)
        actions.send_keys(Keys.TAB).pause(0.5).perform()
        actions.send_keys(surname).pause(0.5).perform()
        
        # Devam Butonu'na geç
        actions.send_keys(Keys.TAB).pause(0.5).perform() # Davet Kodu'na
        actions.send_keys(Keys.TAB).pause(0.5).perform() # Devam Butonu'na
        actions.send_keys(Keys.SPACE).pause(1).perform() # Tıkla (İlk Modal açılır)

        # Modal Zincirleri (1. Onay)
        await _custom_modal_action(driver, WEB_ELEMENTS["MODAL_CONTINUE_XPATH"], wait_time=5, log_msg="ÖZEL 1. MODAL: Devam Et butonu tıklandı (5 sn bekleme).")
        await _custom_modal_action(driver, WEB_ELEMENTS["MODAL_ACCEPT_XPATH"], wait_time=0.1, log_msg="ÖZEL 1. MODAL: Okudum ve Kabul Ediyorum butonu tıklandı.")

        await _custom_modal_action(driver, WEB_ELEMENTS["MODAL_CONTINUE_XPATH"], wait_time=3, log_msg="ÖZEL 2. MODAL: Devam Et butonu tıklandı (3 sn bekleme).")
        await _custom_modal_action(driver, WEB_ELEMENTS["MODAL_ACCEPT_XPATH"], wait_time=0.1, log_msg="ÖZEL 2. MODAL: Okudum ve Kabul Ediyorum butonu tıklandı.")

        await _custom_modal_action(driver, WEB_ELEMENTS["MODAL_CONTINUE_XPATH"], wait_time=3, log_msg="ÖZEL 3. MODAL: Devam Et butonu tıklandı (3 sn bekleme).")
        await _custom_modal_action(driver, WEB_ELEMENTS["MODAL_ACCEPT_XPATH"], wait_time=0.1, log_msg="ÖZEL 3. MODAL: Okudum ve Kabul Ediyorum butonu tıklandı.")

        # Checkbox 2 (Açık Rıza Metni)
        for i in range(7): actions.send_keys(Keys.TAB).pause(0.1).perform()
        actions.send_keys(Keys.SPACE).pause(1).perform()
        await _custom_modal_action(driver, WEB_ELEMENTS["MODAL_CONTINUE_XPATH"], wait_time=1, log_msg="ÖZEL 4. MODAL: Devam Et butonu tıklandı (1 sn bekleme).")
        await _custom_modal_action(driver, WEB_ELEMENTS["MODAL_ACCEPT_XPATH"], wait_time=0.1, log_msg="ÖZEL 4. MODAL: Okudum ve Kabul Ediyorum butonu tıklandı.")

        # Checkbox 3 (Ticari İleti Onayı)
        for i in range(8): actions.send_keys(Keys.TAB).pause(0.1).perform()
        actions.send_keys(Keys.SPACE).pause(1).perform()
        await _custom_modal_action(driver, WEB_ELEMENTS["MODAL_CONTINUE_XPATH"], wait_time=0.5, log_msg="ÖZEL 5. MODAL: Devam Et butonu tıklandı (0.5 sn bekleme).")
        await _custom_modal_action(driver, WEB_ELEMENTS["MODAL_ACCEPT_XPATH"], wait_time=0.1, log_msg="ÖZEL 5. MODAL: Okudum ve Kabul Ediyorum butonu tıklandı.")

        # Checkbox 4 (Papel Sohbet)
        for i in range(9): actions.send_keys(Keys.TAB).pause(0.1).perform()
        actions.send_keys(Keys.SPACE).pause(1).perform()
        await _custom_modal_action(driver, WEB_ELEMENTS["MODAL_CONTINUE_XPATH"], wait_time=1, log_msg="ÖZEL 6. MODAL: Devam Et butonu tıklandı (1 sn bekleme).")
        await _custom_modal_action(driver, WEB_ELEMENTS["MODAL_ACCEPT_XPATH"], wait_time=0.1, log_msg="ÖZEL 6. MODAL: Okudum ve Kabul Ediyorum butonu tıklandı.")

        # Checkbox 5 (Yeni Onay)
        for i in range(10): actions.send_keys(Keys.TAB).pause(0.1).perform()
        actions.send_keys(Keys.SPACE).pause(1).perform()
        await _custom_modal_action(driver, WEB_ELEMENTS["MODAL_CONTINUE_XPATH"], wait_time=1, log_msg="YENİ ONAY: 'Devam Et' butonu tıklandı (1 sn bekleme).")
        await _custom_modal_action(driver, WEB_ELEMENTS["MODAL_ACCEPT_XPATH"], wait_time=0.1, log_msg="YENİ ONAY: 'Okudum ve Kabul Ediyorum' butonu tıklandı.")

        # Final Devam tuşuna tıkla
        devam_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, WEB_ELEMENTS["NAME_SURNAME_NEXT_BTN_XPATH"]))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", devam_btn)
        devam_btn.click()
        time.sleep(2)
        
        # E-posta alanına odaklanmak için TAB
        actions.send_keys(Keys.TAB).pause(0.5).perform()
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, WEB_ELEMENTS["EMAIL_INPUT_ID"]))
        )

        return await fill_email_and_get_code(update, context)
        
    except Exception as e:
        logger.error(f"Ad/Soyad/Onay adımında hata ({user_id}): {e} (Tür: {type(e).__name__})")
        close_driver(driver_key, context) # Benzersiz anahtarla kapat
        await context.bot.send_message(chat_id, "Aktif proxy bulamadım. Lütfen /hesapac ile tekrar dene.")
        return ConversationHandler.END


async def fill_email_and_get_code(update: Update, context: CallbackContext) -> int:
    """Kullanıcıdan alınan E-posta'yı siteye girer ve Mail kodu ister."""
    user_id = update.effective_user.id
    chat_id = context.user_data.get('chat_id')
    
    driver_key = context.user_data.get('driver_key') # Benzersiz anahtarı al
    driver = context.application.bot_data.get(driver_key, {}).get('driver') # Benzersiz anahtarla eriş
    
    email_address = context.user_data.get('email')

    if not driver or not email_address:
        await context.bot.send_message(chat_id, "Hata: E-posta bilgileri eksik veya oturum doldu. Lütfen tekrar /hesapac yaz.")
        return ConversationHandler.END

    try:
        # E-posta alanına adresi gir
        actions = ActionChains(driver)
        actions.send_keys(email_address).pause(0.5).perform()

        # Devam tuşuna tıkla
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, WEB_ELEMENTS["EMAIL_NEXT_BTN_XPATH"]))
        ).click()

        # E-posta kodu alanını bekle
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, WEB_ELEMENTS["EMAIL_CODE_INPUT_CLASS"]))
        )

        # Mail kodu mesajını gruba gönder ve message_id'yi kaydet
        message = await context.bot.send_message(
             chat_id=chat_id,
             text=f"{email_address} adresine gelen 6 haneli onay kodunu bu mesaja yanıt vererek girin.",
        )
        context.user_data['email_message_id'] = message.message_id

        return EMAIL_CODE

    except Exception as e:
        logger.error(f"E-posta adımında hata ({user_id}): {e}")
        close_driver(driver_key, context) # Benzersiz anahtarla kapat
        await context.bot.send_message(chat_id, "E-posta gönderme hatası. Lütfen /hesapac ile tekrar dene.")
        return ConversationHandler.END

async def get_email_code(update: Update, context: CallbackContext) -> int:
    """E-posta onay kodunu, botun mesajına yanıt olarak gelirse alır ve işler."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    driver_key = context.user_data.get('driver_key') # Benzersiz anahtarı al
    driver = context.application.bot_data.get(driver_key, {}).get('driver') # Benzersiz anahtarla eriş
    
    # 1. Kodun, beklenen mesaja yanıt olup olmadığını kontrol et
    if not update.message.reply_to_message or update.message.reply_to_message.message_id != context.user_data.get('email_message_id'):
        return EMAIL_CODE # Yanıt değilse, beklemede kal

    email_code = update.message.text.strip()

    if not driver:
        await context.bot.send_message(chat_id, "Oturum süresi doldu. Lütfen tekrar /hesapac yaz.")
        return ConversationHandler.END

    if len(email_code) != 6 or not email_code.isdigit():
        await context.bot.send_message(chat_id, "Hata: Lütfen sadece 6 haneli kodu girin.", reply_to_message_id=update.message.message_id)
        return EMAIL_CODE

    # ... (Geri kalan Selenium E-posta Kodu adımları aynı kalacak) ...
    try:
        code_inputs = driver.find_elements(By.CLASS_NAME, WEB_ELEMENTS["EMAIL_CODE_INPUT_CLASS"])
        if len(code_inputs) < 6:
            raise Exception("Mail kodu 6 haneli olmalı.")

        for i, digit in enumerate(email_code):
            code_inputs[i].send_keys(digit)
            time.sleep(0.1)

        # Şifre Oluşturma sayfasını bekle
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, WEB_ELEMENTS["PASSWORD_INPUT_ID"]))
        )

        await context.bot.send_message(chat_id, "✅ E-posta kodu doğru.", reply_to_message_id=update.message.message_id)
        
        return await create_password(update, context)


    except Exception as e:
        logger.error(f"E-posta kodu adımında hata ({user_id}): {e}")
        close_driver(driver_key, context) # Benzersiz anahtarla kapat
        await context.bot.send_message(chat_id, "E-posta kodu hatası. Lütfen /hesapac ile tekrar dene.")
        return ConversationHandler.END


async def create_password(update: Update, context: CallbackContext) -> int:
    """Şifreyi girer, hesabı tamamlar, hakları düşürür ve raporu günceller."""
    user_id = update.effective_user.id
    chat_id = context.user_data.get('chat_id')
    
    driver_key = context.user_data.get('driver_key') # Benzersiz anahtarı al
    driver = context.application.bot_data.get(driver_key, {}).get('driver') # Benzersiz anahtarla eriş
    
    password = context.user_data.get('password')

    if not driver or not password:
        await context.bot.send_message(chat_id, "Oturum süresi doldu veya şifre bilgisi eksik. Lütfen tekrar /hesapac yaz.")
        return ConversationHandler.END

    try:
        # Selenium Adımları (Şifre Girişi)
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, WEB_ELEMENTS["PASSWORD_INPUT_ID"]))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", password_input)

        password_input.send_keys(password)
        driver.find_element(By.ID, WEB_ELEMENTS["REPEAT_PASSWORD_INPUT_ID"]).send_keys(password)

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, WEB_ELEMENTS["CREATE_PASSWORD_BTN_XPATH"]))
        ).click()

        time.sleep(10) 
        
        # HAK DÜŞÜRME VE RAPOR GÜNCELLEME İLK YAPILMALI
        kalan_hak = 0
        if chat_id in context.application.bot_data and context.application.bot_data[chat_id]['rights'] > 0:
            context.application.bot_data[chat_id]['rights'] -= 1
            context.application.bot_data[chat_id]['accounts_opened'] = context.application.bot_data[chat_id].get('accounts_opened', 0) + 1
            kalan_hak = context.application.bot_data[chat_id]['rights']

        final_message = (
            "HESAP BAŞARIYLA AÇILDI!\n"
            "Papel hesap açma işlemi tamamlanmıştır.\n\n"
            f"Telefon No :  `{context.user_data.get('phone', 'Bilinmiyor')}`\n"
            f"Ad Soyad :  `{context.user_data.get('name', 'Bilinmiyor')} {context.user_data.get('surname', 'Bilinmiyor')}`\n"
            f"Mail :  `{context.user_data.get('email', 'Bilinmiyor')}`\n"
            f"Hesap Şifre :  `{context.user_data.get('password', 'Bilinmiyor')}`\n\n"
            f"KALAN HAK :  `{kalan_hak}`"
        )
        await context.bot.send_message(chat_id, final_message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Şifre oluşturma adımında hata ({user_id}): {e}")
        await context.bot.send_message(chat_id, "Şifre oluşturma hatası. Lütfen /hesapac ile tekrar dene.")
    finally:
        close_driver(driver_key, context) # Benzersiz anahtarla kapat

    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    """Kullanıcı /cancel komutuyla işlemi sonlandırır."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    user_name = update.effective_user.first_name
    
    driver_key = context.user_data.get('driver_key') # Benzersiz anahtarı al
    close_driver(driver_key, context) # Yeni key ile kapatıyoruz
    
    context.user_data.clear()

    await context.bot.send_message(
        chat_id,
        f'{user_name}, işlem iptal edildi. Tekrar başlamak için /hesapac yazabilirsin.',
    )

    return ConversationHandler.END

# ==============================================================================
# Main
# ==============================================================================

def main() -> None:
    """Botu Application kullanarak başlatır."""

    # Her grup için başlangıç verilerini tutar (rights, accounts_opened)
    application = Application.builder().token(TELEGRAM_TOKEN).concurrent_updates(True).build()
    
    # Grup Komut Filtresi: Sadece grup sohbetlerinde ve / ile başlayan mesajları al
    # Yetkisiz kişilerin özelden yazmasını ve grupta / ile başlamayan mesajları engeller.
    group_command_filter = filters.ChatType.GROUPS & filters.COMMAND 

    # Yetkili (ADMIN) Komutları: Sadece Admin ID'ye sahip kullanıcılar için
    admin_filter = filters.User(ADMIN_ID)
    application.add_handler(CommandHandler('hakver', hakver, filters=admin_filter))
    application.add_handler(CommandHandler('kaldir', kaldir, filters=admin_filter))
    application.add_handler(CommandHandler('rapor', rapor, filters=admin_filter))


    # Konuşma İşleyicisi (Yetkili Grup Filtresi ile birleştirilecek)
    conv_handler = ConversationHandler(
        # YALNIZCA YETKİLİ GRUPLARDAKİ /hesapac KOMUTLARINI DİNLE
        entry_points=[CommandHandler('hesapac', start_hesapac_with_data, filters=group_command_filter)], 

        states={
            # SMS ve E-POSTA kodları için, YALNIZCA yanıt mesajlarını (reply) dinle.
            SMS_CODE: [MessageHandler(filters.TEXT & filters.REPLY, get_sms_code)], 
            EMAIL_CODE: [MessageHandler(filters.TEXT & filters.REPLY, get_email_code)], 
        },

        fallbacks=[CommandHandler('cancel', cancel)],
        # Tüm ConversationHandler'ın süresi dolduktan sonra temizlik yapılır.
    )

    application.add_handler(conv_handler)

    logger.info("Bot çalışıyor...")

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    # Bot_Data yapısını başlat: { chat_id: { 'rights': 0, 'accounts_opened': 0 } }
    # Bu veri, bot her yeniden başlatıldığında sıfırlanır, kalıcı depolama için farklı bir yöntem gerekir.

    main()

