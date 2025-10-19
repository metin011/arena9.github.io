# ⚡ TƏZ BAŞLAMA - 5 DƏQİQƏDƏ DEPLOY! 🚀

## 🎯 Layihəni 24/7 Pulsuz Sayta Çevirmək

### ADDIM 1: GitHub-a Göndər ✅

**Əgər yeni dəyişiklik etmisinizsə:**

```bash
git add .
git commit -m "Deploy edilə bilər"
git push
```

✅ **Artıq GitHub-da kodunuz hazırdır!**
Repository: https://github.com/metin011/arena9.github.io

---

### ADDIM 2: Render.com-a Get 🌐

1. **Sayta get:** https://render.com
2. **"Get Started"** düyməsinə klik
3. **"Sign Up with GitHub"** seçin
4. GitHub ilə daxil olun

---

### ADDIM 3: Web Service Yarat 🔧

1. Dashboard-da **"New +"** düyməsinə klik
2. **"Web Service"** seçin
3. **"arena9.github.io"** repository-ni seçin
4. **"Connect"** düyməsinə klik

---

### ADDIM 4: Parametrləri Doldur 📝

Bu parametrləri daxil edin:

| Parametr | Dəyər |
|----------|-------|
| **Name** | `football-stats-arena9` |
| **Region** | `Frankfurt (EU Central)` |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Instance Type** | `Free` |

---

### ADDIM 5: Deploy Et! 🚀

**"Create Web Service"** düyməsinə klik edin və gözləyin (2-5 dəqiqə).

Yaşıl **"Live"** yazısı görünəndə **HAZIRDIR!** ✅

---

## 🎉 Saytınız Hazırdır!

Sizə belə bir URL veriləcək:

```
https://football-stats-arena9.onrender.com
```

### İlk Giriş:
- **İstifadəçi:** `admin`
- **Şifrə:** `admin123`

---

## 🔄 Yeniləmək üçün:

```bash
git add .
git commit -m "Yeniləmə"
git push
```

Render.com **avtomatik** yeniləyəcək! ⚡

---

## 📚 Ətraflı Təlimat

Daha çox məlumat üçün: **[DEPLOY_AZƏRBAYCAN.md](DEPLOY_AZƏRBAYCAN.md)**

---

## 🆘 Problem?

1. Render Dashboard → **Logs** yoxla
2. **Manual Deploy** düyməsinə klik
3. Əgər lazımsa, **Restart** et

---

## 🌟 Növbəti Addımlar

✅ **PostgreSQL əlavə et** (məlumat qorunması)
✅ **Admin şifrəsini dəyiş** (təhlükəsizlik)
✅ **UptimeRobot qur** (sayt həmişə sürətli olsun)

Ətraflı: [DEPLOY_AZƏRBAYCAN.md](DEPLOY_AZƏRBAYCAN.md)

---

**İNDİ BAŞLA! 🚀**
https://render.com
