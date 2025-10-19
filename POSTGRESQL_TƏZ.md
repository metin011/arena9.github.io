# ⚡ PostgreSQL - 3 Dəqiqədə! 🐘

## 🎯 Render.com-da PostgreSQL Əlavə Et

### ADDIM 1️⃣: Database Yarat

1. https://dashboard.render.com ← **Bura get**

2. **"New +"** düyməsinə klik

3. **"PostgreSQL"** seç

4. **Bu parametrləri yaz:**
   ```
   Name: football-stats-db
   Region: Frankfurt (EU Central)
   Plan: Free
   ```

5. **"Create Database"** - 2 dəqiqə gözlə

---

### ADDIM 2️⃣: URL Kopyala

Database hazır olduqdan sonra:

1. **"Info"** sekmesini aç

2. **"Internal Database URL"** kopyala ✅
   ```
   postgresql://user:pass@host/db
   ```
   (Uzun link olacaq - hamısını kopyala!)

---

### ADDIM 3️⃣: Web Service-ə Bağla

1. **Dashboard-da Web Service-ini aç** (football-stats-arena9)

2. **"Environment"** sekməsinə get

3. **"Add Environment Variable"** klik

4. **Daxil et:**
   ```
   Key: DATABASE_URL
   Value: (kopyaladığın URL)
   ```

5. **"Save Changes"** - Avtomatik restart olacaq!

---

## ✅ HAZIR! 🎉

**Sayta get və test et:**
- Oyunçu əlavə et
- Maç əlavə et  
- Saytı bağla-aç

**Məlumatlar qalırsa = UĞURLU!** ✅

---

## 📸 Vizual Təlimat

### 1. Dashboard:
```
[New +] ← Bura klik
  ↓
[PostgreSQL] ← Seç
```

### 2. Parametrlər:
```
Name: football-stats-db       ← Yaz
Region: Frankfurt             ← Seç
Plan: Free                    ← Seç
[Create Database]             ← Klik
```

### 3. URL Kopyala:
```
Info sekməsi
  ↓
Internal Database URL         ← Bu lazımdır!
[Copy] düyməsi                ← Klik
```

### 4. Environment Variable:
```
Web Service
  ↓
Environment
  ↓
[Add Environment Variable]
  ↓
Key: DATABASE_URL
Value: postgresql://...      ← Yapışdır
[Save Changes]
```

---

## ⚠️ Əsas Nöqtələr

✅ **Internal** Database URL (External deyil!)
✅ **Region eyni** olmalıdır (Frankfurt)
✅ **Save Changes** etməyi unutma!
✅ **2-3 dəqiqə** restart gözlə

---

## 🆘 Problem varsa?

**Logs yoxla:**
```
Web Service → Logs → "Database connected" axtarış et
```

**Restart et:**
```
Manual Deploy düyməsinə klik
```

---

## 📚 Ətraflı Təlimat

Daha çox məlumat: **[POSTGRESQL_QURAŞDIRMA.md](POSTGRESQL_QURAŞDIRMA.md)**

---

**3 dəqiqədə hazır! 🚀**
