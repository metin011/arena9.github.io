# 🚀 GitHub'a Yükleme ve Render.com'a Deploy Rehberi

Bu rehber, Football Stats App'inizi GitHub'a yükleyip Render.com'da 7/24 yayınlamanız için adım adım talimatlar içerir.

---

## 📋 ADIM 1: GitHub'a Yükleme

### 1.1 GitHub Hesabı Oluşturun (Eğer yoksa)
- https://github.com adresine gidin
- **Sign up** butonuna tıklayın
- Email, kullanıcı adı ve şifre belirleyin
- Email doğrulamasını yapın

### 1.2 Yeni Repository Oluşturun
1. GitHub'da oturum açın
2. Sağ üstteki **+** işaretine tıklayın
3. **New repository** seçin
4. Ayarlar:
   - **Repository name**: `football-stats-app`
   - **Description**: "Futbol istatistikleri yönetim sistemi"
   - **Public** seçin (ücretsiz hosting için gerekli)
   - ❌ **Initialize this repository** seçeneklerini BOŞTA BIRAKIN
5. **Create repository** butonuna tıklayın

### 1.3 Repository URL'ini Kopyalayın
Repository oluştuktan sonra göreceğiniz URL'i kopyalayın:
```
https://github.com/KULLANICI_ADINIZ/football-stats-app.git
```

### 1.4 PowerShell'de Komutları Çalıştırın

**ADIM 1:** Proje klasörüne gidin
```powershell
cd C:\Users\agaza\CascadeProjects\football-stats-app
```

**ADIM 2:** Tüm dosyaları ekleyin
```powershell
git add .
```

**ADIM 3:** İlk commit'i yapın
```powershell
git commit -m "Initial commit - Football Stats App"
```

**ADIM 4:** Ana branch'i main yapın
```powershell
git branch -M main
```

**ADIM 5:** GitHub repository'sini bağlayın
⚠️ **ÖNEMLİ**: `KULLANICI_ADINIZ` yerine kendi GitHub kullanıcı adınızı yazın!
```powershell
git remote add origin https://github.com/KULLANICI_ADINIZ/football-stats-app.git
```

**ADIM 6:** Kodu GitHub'a gönderin
```powershell
git push -u origin main
```

İlk push'ta GitHub kullanıcı adı ve şifrenizi soracak. Girin ve devam edin.

---

## 🌐 ADIM 2: Render.com'a Deploy (ÜCRETSİZ)

### 2.1 Render.com Hesabı Oluşturun
1. https://render.com adresine gidin
2. **Get Started** butonuna tıklayın
3. **Sign Up with GitHub** seçin
4. GitHub hesabınızla giriş yapın
5. Render'a GitHub erişimi verin

### 2.2 Web Service Oluşturun
1. Dashboard'da **New +** butonuna tıklayın
2. **Web Service** seçin
3. **Connect a repository** bölümünde:
   - `football-stats-app` repository'sini bulun
   - **Connect** butonuna tıklayın

### 2.3 Ayarları Yapın
Açılan sayfada şu ayarları yapın:

**Name (İsim):**
```
football-stats-app
```

**Region (Bölge):**
```
Frankfurt (EU Central) veya en yakın bölge
```

**Branch:**
```
main
```

**Root Directory:**
```
(Boş bırakın)
```

**Runtime:**
```
Python 3
```

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
gunicorn app:app
```

**Instance Type:**
```
Free
```

### 2.4 Environment Variables (Ortam Değişkenleri)
**Advanced** butonuna tıklayın ve şu değişkenleri ekleyin:

**SECRET_KEY:**
```
your-super-secret-key-change-this-in-production-12345
```

**DATABASE_URL:**
```
(Boş bırakın - SQLite kullanılacak)
```

### 2.5 Deploy Edin
- **Create Web Service** butonuna tıklayın
- Deploy işlemi başlayacak (2-5 dakika sürer)
- Yeşil "Live" yazısını görene kadar bekleyin

---

## ✅ ADIM 3: Siteniz Yayında! 🎉

Deploy tamamlandığında siteniz şu formatta bir adreste yayında olacak:
```
https://football-stats-app-XXXX.onrender.com
```

### İlk Giriş Bilgileri:
- **Kullanıcı Adı**: `admin`
- **Şifre**: `admin123`

---

## 🔄 Güncelleme Yapmak

Kodunuzda değişiklik yaptığınızda:

```powershell
cd C:\Users\agaza\CascadeProjects\football-stats-app

# Değişiklikleri ekle
git add .

# Commit yap
git commit -m "Değişiklik açıklaması"

# GitHub'a gönder
git push
```

Render.com otomatik olarak yeni versiyonu deploy edecektir!

---

## ⚠️ Önemli Notlar

### Ücretsiz Plan Limitleri:
- ✅ **7/24 erişilebilir** (ama 15 dakika kullanılmazsa uyur)
- ✅ İlk açılış 30-50 saniye sürebilir
- ✅ Aylık 750 saat ücretsiz (yeterli)
- ✅ Otomatik HTTPS/SSL

### Veritabanı:
- SQLite kullanılıyor
- Her deploy'da veritabanı sıfırlanır
- Kalıcı veri için PostgreSQL ekleyin (ücretsiz 1GB)

### Güvenlik:
- Production'da `SECRET_KEY` değiştirin
- Admin şifresini değiştirin
- HTTPS otomatik aktif

---

## 🆘 Sorun Giderme

### Problem: "git: command not found"
**Çözüm:** Git'i yükleyin: https://git-scm.com/download/win

### Problem: "Permission denied"
**Çözüm:** GitHub Personal Access Token oluşturun:
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token
3. `repo` yetkisini seçin
4. Token'ı şifre yerine kullanın

### Problem: "Build failed"
**Çözüm:** 
- `requirements.txt` dosyasını kontrol edin
- Render loglarını inceleyin

### Problem: Site açılmıyor
**Çözüm:**
- Render Dashboard'da "Logs" sekmesini kontrol edin
- "Restart" butonuna tıklayın

---

## 🎯 Alternatif: PythonAnywhere

Render.com yerine PythonAnywhere da kullanabilirsiniz:

1. https://www.pythonanywhere.com adresine gidin
2. Ücretsiz hesap oluşturun
3. **Files** → Dosyaları yükleyin
4. **Web** → **Add new web app** → **Flask**
5. `app.py` dosyasını seçin

---

## 📱 Mobil Erişim

Site mobil uyumlu! Telefonunuzdan da erişebilirsiniz:
```
https://football-stats-app-XXXX.onrender.com
```

---

## 🎊 Tebrikler!

Siteniz artık internette 7/24 yayında! 🚀

**Paylaşabileceğiniz link:**
```
https://football-stats-app-XXXX.onrender.com
```

Herkes bu linke tıklayarak sitenizi görebilir!
