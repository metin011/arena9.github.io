# 🚀 Deployment Talimatları

## Render.com'a Deploy Etme (ÜCRETSİZ)

### 1. GitHub'a Yükleyin

```bash
cd C:\Users\agaza\CascadeProjects\football-stats-app

# Git başlat
git init
git add .
git commit -m "Initial commit"

# GitHub'da yeni repo oluşturun (football-stats-app)
# Sonra:
git remote add origin https://github.com/KULLANICI_ADINIZ/football-stats-app.git
git branch -M main
git push -u origin main
```

### 2. Render.com'da Deploy

1. **Render.com'a gidin:** https://render.com
2. **Sign Up** yapın (GitHub ile giriş yapabilirsiniz)
3. **New +** butonuna tıklayın
4. **Web Service** seçin
5. GitHub repository'nizi bağlayın
6. Ayarlar:
   - **Name:** football-stats-app
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free

7. **Create Web Service** butonuna tıklayın

### 3. Siteniz Hazır! 🎉

Deploy tamamlandığında size bir URL verilecek:
```
https://football-stats-app.onrender.com
```

## ⚠️ Önemli Notlar

1. **İlk yükleme 2-3 dakika sürebilir**
2. **Ücretsiz planda site 15 dakika kullanılmazsa uyur** (ilk açılış 30 saniye sürer)
3. **Veritabanı her deploy'da sıfırlanır** - Production için PostgreSQL ekleyin

## 🔒 Güvenlik (Production İçin)

`app.py` dosyasında SECRET_KEY'i değiştirin:

```python
app.config['SECRET_KEY'] = 'BURAYA-GÜÇLÜ-BİR-ŞİFRE-YAZIN'
```

## 📊 Alternatif: PythonAnywhere

1. https://www.pythonanywhere.com adresine gidin
2. Ücretsiz hesap oluşturun
3. **Web** sekmesine gidin
4. **Add a new web app** tıklayın
5. **Flask** seçin
6. Dosyaları yükleyin

## 🆘 Sorun mu var?

- Render.com loglarını kontrol edin
- `gunicorn` kurulu olduğundan emin olun
- Port ayarlarını kontrol edin
