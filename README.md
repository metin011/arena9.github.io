# ⚽ Futbol İstatistikleri Web Uygulaması

Modern ve güvenli bir futbol istatistik yönetim sistemi. Admin paneli ile maç ve oyuncu yönetimi, normal kullanıcılar için görüntüleme modu.

🌐 **LIVE DEMO:** Deploy sonrası buraya link eklenecek

## 🎯 Özellikler

### 👤 Kullanıcı Rolleri
- **Admin Kullanıcılar**: Tüm verileri ekleyebilir, düzenleyebilir ve silebilir
- **Normal Kullanıcılar**: Sadece verileri görüntüleyebilir

### ⚽ Maç Yönetimi
- Maç ekleme, düzenleme ve silme (Admin)
- Maç durumu: Planlandı, Canlı, Bitti
- Skor takibi
- Stadyum bilgisi
- Tarih ve saat bilgisi

### 👥 Oyuncu Yönetimi
- Oyuncu profili ekleme, düzenleme ve silme (Admin)
- İstatistikler: Gol, Asist, Oynanan Maç
- Pozisyon ve takım bilgisi

### 🔐 Güvenlik
- Şifreli kullanıcı sistemi (bcrypt)
- Session-based authentication
- Admin/User rol kontrolü
- CSRF koruması

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- pip

### Adımlar

1. **Bağımlılıkları yükleyin:**
```bash
cd C:\Users\agaza\CascadeProjects\football-stats-app
pip install -r requirements.txt
```

2. **Uygulamayı başlatın:**
```bash
python app.py
```

3. **Tarayıcınızda açın:**
```
http://localhost:5000
```

## 👨‍💼 Varsayılan Admin Hesabı

İlk çalıştırmada otomatik olarak bir admin hesabı oluşturulur:

- **Kullanıcı Adı:** `admin`
- **Şifre:** `admin123`

⚠️ **Önemli:** Güvenlik için admin şifresini ilk girişten sonra değiştirin!

## 📖 Kullanım

### Normal Kullanıcı
1. "Kayıt Ol" butonuna tıklayın
2. Kullanıcı adı ve şifre belirleyin
3. Giriş yapın
4. Maçları ve oyuncuları görüntüleyin

### Admin Kullanıcı
1. Admin hesabı ile giriş yapın
2. "Admin Panel" butonuna tıklayın
3. Maçlar, Oyuncular ve Kullanıcılar sekmelerinden yönetim yapın

#### Maç Ekleme
- Ev sahibi ve deplasman takımlarını girin
- Skorları belirleyin
- Tarih ve saat seçin
- Stadyum bilgisi ekleyin (opsiyonel)
- Maç durumunu seçin

#### Oyuncu Ekleme
- Oyuncu adını girin
- Pozisyon ve takım bilgisi ekleyin
- İstatistikleri girin (gol, asist, maç sayısı)

## 🗂️ Proje Yapısı

```
football-stats-app/
├── app.py                 # Ana uygulama dosyası
├── requirements.txt       # Python bağımlılıkları
├── README.md             # Dokümantasyon
├── football_stats.db     # SQLite veritabanı (otomatik oluşturulur)
└── templates/            # HTML şablonları
    ├── base.html         # Ana şablon
    ├── index.html        # Ana sayfa
    ├── login.html        # Giriş sayfası
    ├── register.html     # Kayıt sayfası
    ├── matches.html      # Maçlar sayfası
    ├── players.html      # Oyuncular sayfası
    └── admin.html        # Admin panel
```

## 🛠️ Teknolojiler

- **Backend:** Flask (Python)
- **Database:** SQLite + SQLAlchemy ORM
- **Authentication:** Werkzeug Security
- **Frontend:** HTML5, CSS3, JavaScript
- **Design:** Modern gradient UI, responsive tasarım

## 📱 Responsive Tasarım

Uygulama mobil, tablet ve masaüstü cihazlarda sorunsuz çalışır.

## 🔒 Güvenlik Notları

1. Production ortamında `SECRET_KEY`'i değiştirin
2. Admin şifresini güçlü bir şifre ile değiştirin
3. HTTPS kullanın
4. Düzenli yedekleme yapın

## 📝 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

## 🤝 Katkıda Bulunma

Önerileriniz ve katkılarınız için teşekkürler!

---

**Geliştirici:** Cascade AI
**Versiyon:** 1.0.0
**Tarih:** 2024
