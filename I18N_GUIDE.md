# Internationalization (i18n) Guide for Ganjoor Django

## 📋 Overview

This project now supports full internationalization (i18n) with Persian (فارسی) and English languages. This guide explains how the i18n system works and how to use it.

## 🌍 Supported Languages

- **Persian (فارسی)** - `fa` - Default language, RTL
- **English** - `en` - LTR

## 🚀 Features

- ✅ Language switcher in the header
- ✅ URL-based language selection
- ✅ Cookie-based language persistence
- ✅ RTL/LTR automatic switching
- ✅ Translated models, views, templates
- ✅ Bilingual error messages
- ✅ Admin panel translation support
- ✅ API response translations

## 📁 Project Structure

```
ganjoor-django/
├── locale/                    # Translation files directory
│   ├── fa/                   # Persian translations
│   │   └── LC_MESSAGES/
│   │       ├── django.po     # Translation source (editable)
│   │       └── django.mo     # Compiled translations (auto-generated)
│   └── en/                   # English translations
│       └── LC_MESSAGES/
│           ├── django.po
│           └── django.mo
├── core/
│   ├── models.py            # Uses gettext_lazy for field labels
│   ├── views.py             # Uses gettext for dynamic messages
│   ├── serializers.py       # Translatable validation messages
│   └── templates/
│       └── core/
│           └── base.html    # Uses {% trans %} and {% load i18n %}
└── ganjoor/
    ├── settings.py          # i18n configuration
    └── urls.py              # i18n URL patterns
```

## ⚙️ Configuration (settings.py)

```python
# Default language
LANGUAGE_CODE = "fa"  # Persian

# Available languages
LANGUAGES = [
    ("fa", "فارسی"),
    ("en", "English"),
]

# Enable i18n
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Translation files location
LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# Language cookie settings
LANGUAGE_COOKIE_NAME = "ganjoor_language"
LANGUAGE_COOKIE_AGE = 365 * 24 * 60 * 60  # 1 year

# Middleware (order matters!)
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # ← i18n middleware
    "django.middleware.common.CommonMiddleware",
    # ... rest of middleware
]
```

## 🔧 How It Works

### 1. URL Patterns

The project uses `i18n_patterns()` to add language prefixes to URLs:

```python
# ganjoor/urls.py
from django.conf.urls.i18n import i18n_patterns

# URLs without language prefix (API, static assets)
urlpatterns = [
    path("api/", include("core.api_urls")),
]

# URLs with language prefix (/fa/ or /en/)
urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("core.urls", namespace="core")),
    prefix_default_language=False,  # Don't prefix default language
)
```

**Result:**
- `/` → Home page (default Persian)
- `/en/` → Home page (English)
- `/api/poets/` → API (no language prefix)

### 2. Language Switching

Users can switch languages using the dropdown in the header:

```django
<!-- templates/core/base.html -->
<form action="{% url 'core:set_language' %}" method="post">
    {% csrf_token %}
    <input name="next" type="hidden" value="{{ request.get_full_path }}">
    <input type="hidden" name="language" value="fa">
    <button type="submit">🇮🇷 فارسی</button>
</form>
```

The language preference is stored in a cookie and persists across sessions.

### 3. Models Translation

Use `gettext_lazy` for model field labels:

```python
from django.utils.translation import gettext_lazy as _

class GanjoorPoet(models.Model):
    name = models.CharField(
        max_length=255, 
        verbose_name=_("Name")  # ← Translatable
    )
    
    class Meta:
        verbose_name = _("Poet")
        verbose_name_plural = _("Poets")
```

### 4. Views Translation

Use `gettext` or `gettext_lazy` for messages:

```python
from django.utils.translation import gettext_lazy as _

def my_view(request):
    message = _("Please provide a search query.")
    return Response({"message": str(message)})
```

### 5. Templates Translation

Use `{% load i18n %}` and translation tags:

```django
{% load i18n %}

<h1>{% trans "Welcome to Ganjoor" %}</h1>

<!-- With variables -->
<p>{% blocktrans count counter=list|length %}
    There is {{ counter }} poem.
{% plural %}
    There are {{ counter }} poems.
{% endblocktrans %}</p>

<!-- Get current language -->
<html lang="{{ LANGUAGE_CODE }}">
```

### 6. RTL/LTR Support

Templates automatically switch direction:

```django
<html dir="{% if LANGUAGE_CODE == 'fa' %}rtl{% else %}ltr{% endif %}">
```

CSS classes adjust based on language:

```django
<div class="{% if LANGUAGE_CODE == 'fa' %}me-2{% else %}ms-2{% endif %}">
```

## 📝 Translation Workflow

### Step 1: Mark Strings for Translation

**In Python files (models, views, forms):**
```python
from django.utils.translation import gettext_lazy as _

# Use gettext_lazy (_) for strings
title = _("Poem Title")
message = _("Your poem has been saved.")
```

**In templates:**
```django
{% load i18n %}
{% trans "Search" %}
```

### Step 2: Extract Messages

Generate/update `.po` files:

```bash
# Extract all translatable strings
python manage.py makemessages -l fa -l en --ignore=.venv

# For specific language
python manage.py makemessages -l fa

# For JavaScript files too
python manage.py makemessages -d djangojs -l fa
```

**Note:** Requires `gettext` to be installed:
```bash
# Ubuntu/Debian
sudo apt-get install gettext

# macOS
brew install gettext

# Windows
# Download from: https://mlocati.github.io/articles/gettext-iconv-windows.html
```

### Step 3: Translate Strings

Edit `.po` files in `locale/*/LC_MESSAGES/django.po`:

```po
# locale/fa/LC_MESSAGES/django.po
msgid "Search"
msgstr "جستجو"

msgid "Poet name cannot be empty."
msgstr "نام شاعر نمی‌تواند خالی باشد."
```

### Step 4: Compile Messages

Convert `.po` files to binary `.mo` files:

```bash
python manage.py compilemessages

# For specific language
python manage.py compilemessages -l fa
```

### Step 5: Restart Server

```bash
python manage.py runserver
```

## 🎨 Frontend Components

### Language Switcher

Already implemented in `base.html`:

```django
<!-- Language dropdown in header -->
<div class="dropdown">
    <button class="btn dropdown-toggle">
        {% if LANGUAGE_CODE == 'fa' %}
            🇮🇷 فارسی
        {% else %}
            🇬🇧 English
        {% endif %}
    </button>
    <ul class="dropdown-menu">
        <!-- Forms to switch language -->
    </ul>
</div>
```

### Bootstrap RTL/LTR

```django
<!-- Load correct Bootstrap CSS -->
{% if LANGUAGE_CODE == 'fa' %}
    <link href=".../bootstrap.rtl.min.css" rel="stylesheet">
{% else %}
    <link href=".../bootstrap.min.css" rel="stylesheet">
{% endif %}
```

### Font Selection

```css
body {
    font-family: {% if LANGUAGE_CODE == 'fa' %}'Vazirmatn', {% endif %}sans-serif;
}
```

## 🔌 API Translation

API responses are translated based on the `Accept-Language` header or user settings:

```bash
# Request in Persian
curl -H "Accept-Language: fa" http://localhost:8000/api/poets/

# Request in English
curl -H "Accept-Language: en" http://localhost:8000/api/poets/
```

Error messages are automatically translated:

```json
{
  "error": "validation_error",
  "message": "نام شاعر نمی‌تواند خالی باشد."
}
```

## 🛠️ Common Tasks

### Add a New Translatable String

1. In Python:
```python
from django.utils.translation import gettext_lazy as _
message = _("New message here")
```

2. In template:
```django
{% trans "New message here" %}
```

3. Extract and translate:
```bash
python manage.py makemessages -l fa -l en
# Edit locale/fa/LC_MESSAGES/django.po
python manage.py compilemessages
```

### Test Translations

```bash
# Switch language via URL
http://localhost:8000/fa/
http://localhost:8000/en/

# Or use language switcher in header
```

### Add a New Language

1. Add to `settings.py`:
```python
LANGUAGES = [
    ("fa", "فارسی"),
    ("en", "English"),
    ("ar", "العربية"),  # Add Arabic
]
```

2. Create translation files:
```bash
python manage.py makemessages -l ar
```

3. Translate in `locale/ar/LC_MESSAGES/django.po`

4. Compile:
```bash
python manage.py compilemessages -l ar
```

## 📖 Translation File Format

```po
# locale/fa/LC_MESSAGES/django.po

# Header
msgid ""
msgstr ""
"Language: fa\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"

# Simple translation
msgid "Home"
msgstr "خانه"

# With context
msgctxt "navigation menu"
msgid "Home"
msgstr "صفحه اصلی"

# Plural forms
msgid "%(count)d poem"
msgid_plural "%(count)d poems"
msgstr[0] "%(count)d شعر"
msgstr[1] "%(count)d شعر"

# With variables
msgid "Hello, %(name)s!"
msgstr "سلام، %(name)s!"

# Multi-line
msgid ""
"This is a long text "
"that spans multiple lines."
msgstr ""
"این یک متن بلند است "
"که در چند خط قرار دارد."
```

## 🎯 Best Practices

### 1. Always Use Lazy Translation in Models

```python
# ✅ Correct
from django.utils.translation import gettext_lazy as _
verbose_name = _("Poet")

# ❌ Wrong
from django.utils.translation import gettext as _
verbose_name = _("Poet")  # Evaluated immediately!
```

### 2. Use Context When Needed

```python
from django.utils.translation import pgettext_lazy

# Different translations for same word
header = pgettext_lazy("website header", "Home")
button = pgettext_lazy("navigation button", "Home")
```

### 3. Keep Strings Simple

```python
# ✅ Good
_("Search for poems")

# ❌ Bad (hard to translate)
_("Search for poems by " + poet + " in " + category)

# ✅ Better
_("Search for poems by %(poet)s in %(category)s") % {
    'poet': poet, 'category': category
}
```

### 4. Don't Concatenate Translations

```python
# ❌ Wrong
message = _("Welcome") + " " + _("to Ganjoor")

# ✅ Correct
message = _("Welcome to Ganjoor")
```

### 5. Test Both Languages

Always test your changes in both Persian and English to ensure:
- Text displays correctly
- Layout doesn't break
- RTL/LTR switching works
- No untranslated strings appear

## 🐛 Troubleshooting

### Translations Not Showing

1. **Compiled messages?**
   ```bash
   python manage.py compilemessages
   ```

2. **Server restarted?**
   ```bash
   python manage.py runserver
   ```

3. **Correct language code?**
   - Use `fa` not `fa-ir`
   - Use `en` not `en-us`

4. **Middleware order correct?**
   - `LocaleMiddleware` should be after `SessionMiddleware`

### Language Not Changing

1. **Clear cookies:**
   ```javascript
   // In browser console
   document.cookie = "ganjoor_language=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
   ```

2. **Check URL pattern:**
   - Ensure `i18n_patterns()` is used
   - Check `prefix_default_language` setting

### Missing Translations

1. **Extract messages:**
   ```bash
   python manage.py makemessages -l fa --all
   ```

2. **Check .po file:**
   - Look for `msgstr ""`
   - Add translation

3. **Compile:**
   ```bash
   python manage.py compilemessages
   ```

### RTL Layout Issues

1. **Use Bootstrap RTL:**
   ```django
   {% if LANGUAGE_CODE == 'fa' %}
       <link href="bootstrap.rtl.min.css">
   {% endif %}
   ```

2. **Use conditional spacing:**
   ```django
   class="{% if LANGUAGE_CODE == 'fa' %}me-2{% else %}ms-2{% endif %}"
   ```

3. **Text alignment:**
   ```django
   class="{% if LANGUAGE_CODE == 'fa' %}text-end{% else %}text-start{% endif %}"
   ```

## 📊 Translation Status

### Current Coverage

| Component | Persian | English | Notes |
|-----------|---------|---------|-------|
| Models | ✅ 100% | ✅ 100% | All fields labeled |
| Admin | ✅ 100% | ✅ 100% | Django default + custom |
| Templates | ✅ 100% | ✅ 100% | Base template complete |
| Views | ✅ 100% | ✅ 100% | All messages translated |
| Serializers | ✅ 100% | ✅ 100% | All validations translated |
| API Errors | ✅ 100% | ✅ 100% | Custom exception handler |

### Translation Files

- **Persian:** `locale/fa/LC_MESSAGES/django.po` - 441 strings
- **English:** `locale/en/LC_MESSAGES/django.po` - 441 strings

## 🔗 Useful Links

- [Django i18n Documentation](https://docs.djangoproject.com/en/5.2/topics/i18n/)
- [Translation String Extraction](https://docs.djangoproject.com/en/5.2/topics/i18n/translation/#message-files)
- [Locale Middleware](https://docs.djangoproject.com/en/5.2/topics/i18n/translation/#how-django-discovers-language-preference)
- [gettext Manual](https://www.gnu.org/software/gettext/manual/)

## 🎓 Examples

### Example 1: Translatable Form

```python
from django import forms
from django.utils.translation import gettext_lazy as _

class SearchForm(forms.Form):
    query = forms.CharField(
        label=_("Search Query"),
        help_text=_("Enter poem title or poet name")
    )
    poet = forms.ChoiceField(
        label=_("Poet"),
        required=False
    )
```

### Example 2: Translatable Messages

```python
from django.contrib import messages
from django.utils.translation import gettext as _

def my_view(request):
    messages.success(request, _("Poem saved successfully!"))
    messages.error(request, _("Failed to save poem."))
```

### Example 3: Template with Plurals

```django
{% load i18n %}

{% blocktrans count counter=poems.count %}
    Found {{ counter }} poem
{% plural %}
    Found {{ counter }} poems
{% endblocktrans %}
```

### Example 4: JavaScript Translations

```django
{% load i18n %}

<script>
const translations = {
    loading: "{% trans 'Loading...' %}",
    error: "{% trans 'An error occurred' %}",
    success: "{% trans 'Success!' %}"
};
</script>
```

## ✅ Checklist for New Features

When adding new features, ensure:

- [ ] All user-facing strings use `_()` or `{% trans %}`
- [ ] Model fields have `verbose_name`
- [ ] Forms have translated labels and help text
- [ ] Error messages are translatable
- [ ] Templates load `{% load i18n %}`
- [ ] Run `makemessages` to extract strings
- [ ] Add translations to both `.po` files
- [ ] Run `compilemessages`
- [ ] Test in both languages
- [ ] Check RTL/LTR layout

---

**Version:** 1.0  
**Last Updated:** 2025  
**Status:** ✅ Fully Implemented