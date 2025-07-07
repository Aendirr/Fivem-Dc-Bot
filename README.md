# Discord Ticket & Mülakat Botu - Modüler Yapı

Bu bot, Discord sunucuları için gelişmiş bir ticket sistemi, mülakat (başvuru) sistemi ve moderasyon araçları sağlar. Modüler yapıda tasarlanmıştır ve kolayca genişletilebilir.

## Özellikler

### 🎫 Ticket Sistemi
- Modal tabanlı ticket oluşturma
- Ceza menüsü ile rol yönetimi
- Ticket transkripti kaydetme
- Otomatik kanal yönetimi

### 📝 Mülakat (Başvuru) Sistemi
- Slash komutuyla mülakat başlatma (`/mülakat`)
- 20 adet Hard RP sorusu, 4 sayfa halinde modal ile cevaplanır
- Cevaplar embed olarak okunabilir şekilde log kanalına gönderilir
- Cevaplar JSON olarak arşivlenir (sadece dosyada, kanala gönderilmez)
- Mülakat tamamlanınca kullanıcıya "onay bekleme" rolü verilir, eski rolü alınır
- Sadece belirli role sahip kullanıcılar mülakat başlatabilir

### ✅ Mülakat Onay Komutu
- `/mülakatonay <kullanıcı_id>` komutu ile adminler kullanıcıya IC-ISIM rolü verir, bekleme rolünü alır
- İşlem sonucu hem terminale hem de log kanalına yazılır
- Yetkisiz kullanım, kullanıcı bulunamama ve rol işlemleri de loglanır

### 🛡️ Moderasyon Komutları
- Kullanıcı kayıt sistemi
- Rol yönetimi (kayıtal, bayan, erkek, isim)
- Mesaj temizleme (clear)
- Kanal silme (kanalsil)
- Avatar görüntüleme

### 🌐 Sunucu Yönetimi
- Sunucu durumu bildirimleri (aktif, restart, bakım)
- IP adresi paylaşımı
- Ses kanalı yönetimi

### 👥 Üye Yönetimi
- Otomatik rol verme
- Giriş/çıkış logları
- Kayıt sistemi

## Kurulum

1. **Gereksinimleri yükleyin:**
```bash
pip install -r requirements.txt
```

2. **Config dosyasını düzenleyin:**
`config.json` dosyasındaki ayarları kendi sunucunuza göre güncelleyin.

3. **Botu çalıştırın:**
```bash
python bot.py
```

## Klasör Yapısı

```
titcket-bot/
├── bot.py                 # Ana bot dosyası
├── config.json           # Konfigürasyon dosyası
├── requirements.txt      # Gerekli kütüphaneler
├── README.md            # Bu dosya
├── cogs/                # Komut modülleri
│   ├── __init__.py
│   ├── ticket_system.py    # Ticket sistemi komutları
│   ├── server_commands.py  # Sunucu komutları
│   ├── moderation_commands.py # Moderasyon komutları
│   └── mulakat_system.py   # Mülakat sistemi ve onay komutu
├── events/              # Event modülleri
│   ├── __init__.py
│   ├── ready.py            # Bot hazır olduğunda
│   └── member_events.py    # Üye eventleri
├── utils/               # Yardımcı fonksiyonlar
│   ├── __init__.py
│   └── helpers.py          # Genel yardımcı fonksiyonlar
└── data/                # Ticket verileri
    └── *.json
└── responses/           # Mülakat cevapları (JSON arşiv)
    └── *_mulakat_final.json
```

## Komutlar

### Ticket Komutları
- `/ticket` - Ticket sistemi embed'ini oluşturur
- `/dataticket <user_id>` - Kullanıcının ticket transkriptini getirir

### Mülakat Komutları
- `/mülakat` - Mülakat (başvuru) sistemini başlatır (sadece belirli role sahip kullanıcılar)
- `/mülakatonay <kullanıcı_id>` - Kullanıcıya IC-ISIM rolü verir, bekleme rolünü alır (sadece adminler)

### Sunucu Komutları
- `/aktif` - Sunucu aktif durumunu bildirir
- `/restart` - Sunucu restart durumunu bildirir
- `/bakim` - Sunucu bakım durumunu bildirir
- `/ip` - Sunucu IP adresini gösterir

### Moderasyon Komutları
- `/kayital <user>` - Kullanıcıyı kayıt eder
- `/bayan <user>` - Kullanıcıya bayan rolü verir
- `/erkek <user>` - Kullanıcıya erkek rolü verir
- `/isim <user> <new_name>` - Kullanıcının ismini değiştirir
- `/avatar <user>` - Kullanıcının avatarını gösterir
- `/clear <amount>` - Belirtilen sayıda mesaj siler
- `/kanalsil <channel_name>` - Belirtilen isimdeki kanalı siler
- `/join` - Ses kanalına katılır
- `/leave` - Ses kanalından ayrılır

## Config Ayarları

`config.json` dosyasında aşağıdaki ayarları yapılandırabilirsiniz:

- **Token**: Discord bot token'ı
- **Prefix**: Komut öneki
- **Rol ID'leri**: Admin, moderator, ticket kullanıcı rolleri, IC-ISIM rolü, mülakat bekleme rolü
- **Kanal ID'leri**: Log, giriş, çıkış, kayıt, mülakat log kanalı
- **Embed ayarları**: Renk, başlık, açıklama
- **Ceza rolleri**: Uyarı, CK point, blacklist rolleri
- **Sunucu bilgileri**: IP, Discord URL, resimler
- **Mülakat soruları**: `mulakat_questions` listesi (20 adet)
- **Mülakat log kanalı**: `mulakat_channel_id` (cevapların embed olarak gönderileceği kanal)
- **Mülakat bekleme rolü**: `mulakat_role_to_add` (mülakat bitince verilecek rol)
- **IC-ISIM rolü**: `/mülakatonay` ile verilecek rol (sabit: 1330578864396828682)

## Loglama

- `/mülakatonay` komutu ile yapılan tüm işlemler hem terminale hem de `1391725335263051806` ID'li log kanalına yazılır.
- Başarı, hata, yetkisiz kullanım ve kullanıcı bulunamama durumları loglanır.

## Geliştirme

### Yeni Komut Ekleme
1. `cogs/` klasöründe yeni bir dosya oluşturun
2. `commands.Cog` sınıfından türetin
3. `setup()` fonksiyonu ekleyin
4. Bot otomatik olarak yükleyecektir

### Yeni Event Ekleme
1. `events/` klasöründe yeni bir dosya oluşturun
2. `commands.Cog` sınıfından türetin
3. `@commands.Cog.listener()` decorator'ı kullanın
4. `setup()` fonksiyonu ekleyin

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## Destek

Herhangi bir sorun yaşarsanız, lütfen issue açın veya iletişime geçin. 