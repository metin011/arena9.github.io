# 🧪 İZLƏYİCİ TEST SSENARİSİ

## 🎯 Necə Test Edək:

### Test 1: Düymələr Görünür?

**İzləyici olaraq:**

1. Ana səhifə → "İzləyici Olaraq Davam Et"
2. Dashboard açılır
3. **Oyunçular** səhifəsinə get

**YOXLA:**
- ➕ düyməsi görünür? → ❌ OLMAMALIDIR
- Əgər görünürsə: PROBLEM var!

4. **İstənilən oyunçuya klik**
5. Profil açılır

**YOXLA:**
- ✏️ (redaktə) düyməsi görünür? → ❌ OLMAMALIDIR
- 🗑️ (silmə) düyməsi görünür? → ❌ OLMAMALIDIR
- Əgər görünürsə: PROBLEM var!

---

### Test 2: URL Hack Cəhdi

**İzləyici olaraq girdikdən sonra:**

1. Brauzer address bar-a yazın:
   ```
   /admin/player/add
   ```

2. **NƏ OLMALIDIR:**
   - Dashboard-a redirect ✅
   - Flash mesajı: "⛔ Bu əməliyyat üçün admin icazəniz yoxdur!" ✅

3. Əgər form açılırsa: ❌ PROBLEM!

---

### Test 3: Developer Console Cəhdi

**İzləyici olaraq:**

1. F12 basın (Developer Tools)
2. Console-da yazın:
   ```javascript
   fetch('/admin/player/add', {method: 'POST'})
   ```

3. **NƏ OLMALIDIR:**
   - 403 Forbidden və ya redirect ✅

---

## 🔍 NECƏ YOXLAYAQ "is_admin"?

**Console-da:**

1. F12 → Console
2. Yazın:
   ```javascript
   document.cookie
   ```

3. Baxın session-da nə var

---

## 📊 NƏTİCƏLƏR:

### ✅ DÜZGÜN:

```
İzləyici:
- ➕ düymələri YOX
- ✏️ 🗑️ düymələri YOX  
- /admin/player/add → redirect
- Flash: "icazəniz yoxdur"
```

### ❌ PROBLEM:

```
İzləyici:
- ➕ düymələri VAR ← PROBLEM!
- ✏️ 🗑️ düymələri VAR ← PROBLEM!
- /admin/player/add → form açılır ← PROBLEM!
```

---

## 💡 ƏGƏR PROBLEM VARSA:

### 1. Session yoxlanışı:

app.py dashboard route:
```python
if 'user_id' not in session:
    session['is_admin'] = False  ← Bu işləyir?
```

### 2. Template yoxlanışı:

players_new.html:
```html
{% if is_admin %}
  <a href="/admin/player/add">➕</a>
{% endif %}
```

### 3. Backend yoxlanışı:

app.py:
```python
@app.route('/admin/player/add')
def admin_add_player():
    if not session.get('is_admin'):  ← Bu işləyir?
        return redirect('dashboard')
```

---

## 🎯 SİZİN TEST NƏTİCƏLƏRİ:

**Hansı problem var?**

A) ➕ düyməsi görünür (izləyicidə)
B) ✏️ 🗑️ düymələri görünür (profildə)
C) URL-ə birbaşa gedəndə form açılır
D) POST request işləyir

**Dəqiq deyin, mən həll edim!** 😊
