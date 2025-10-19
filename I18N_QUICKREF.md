# i18n Quick Reference Card

## 🚀 Quick Start

### Switch Language (Users)
1. Click language dropdown in header (🌐)
2. Select: 🇮🇷 فارسی or 🇬🇧 English
3. Language saves automatically

### URLs
- Persian: `http://localhost:8000/`
- English: `http://localhost:8000/en/`
- API: `http://localhost:8000/api/` (no prefix)

---

## 🛠️ Developer Commands

### Compile Translations (Required after changes)
```bash
python manage.py compilemessages
```

### Extract New Translatable Strings
```bash
python manage.py makemessages -l fa -l en --ignore=.venv
```

### Compile Specific Language
```bash
python manage.py compilemessages -l fa
```

---

## 📝 Code Patterns

### In Python Files (models.py, views.py, forms.py)

```python
from django.utils.translation import gettext_lazy as _

# Models
class MyModel(models.Model):
    name = models.CharField(verbose_name=_("Name"))
    
    class Meta:
        verbose_name = _("Item")
        verbose_name_plural = _("Items")

# Views
message = _("Success!")

# Forms
class MyForm(forms.Form):
    field = forms.CharField(label=_("Field Name"))
```

### In Templates

```django
{% load i18n %}

<!-- Simple translation -->
<h1>{% trans "Welcome" %}</h1>

<!-- With variables -->
{% blocktrans with name=user.name %}
    Hello, {{ name }}!
{% endblocktrans %}

<!-- Get current language -->
<html lang="{{ LANGUAGE_CODE }}">
```

### RTL/LTR Conditional Classes

```django
<!-- Direction -->
<html dir="{% if LANGUAGE_CODE == 'fa' %}rtl{% else %}ltr{% endif %}">

<!-- Spacing -->
<div class="{% if LANGUAGE_CODE == 'fa' %}me-2{% else %}ms-2{% endif %}">

<!-- Alignment -->
<div class="{% if LANGUAGE_CODE == 'fa' %}text-end{% else %}text-start{% endif %}">
```

---

## 📂 File Locations

```
locale/
├── fa/LC_MESSAGES/
│   ├── django.po  ← Edit this (Persian)
│   └── django.mo  ← Auto-generated
└── en/LC_MESSAGES/
    ├── django.po  ← Edit this (English)
    └── django.mo  ← Auto-generated
```

---

## 🔄 Translation Workflow

1. **Mark strings for translation** in code
   ```python
   _("New text")
   ```

2. **Extract strings**
   ```bash
   python manage.py makemessages -l fa -l en
   ```

3. **Edit `.po` files**
   ```po
   msgid "New text"
   msgstr "متن جدید"  # Add Persian translation
   ```

4. **Compile**
   ```bash
   python manage.py compilemessages
   ```

5. **Restart server**
   ```bash
   python manage.py runserver
   ```

---

## 🎨 UI Components

### Language Switcher (Already in base.html)
```django
<form action="{% url 'core:set_language' %}" method="post">
    {% csrf_token %}
    <input name="next" type="hidden" value="{{ request.get_full_path }}">
    <input type="hidden" name="language" value="fa">
    <button type="submit">🇮🇷 فارسی</button>
</form>
```

### Bootstrap CSS Selection
```django
{% if LANGUAGE_CODE == 'fa' %}
    <link href="bootstrap.rtl.min.css">
{% else %}
    <link href="bootstrap.min.css">
{% endif %}
```

---

## ⚡ Common Translations

### Models
```python
verbose_name=_("Name")
verbose_name=_("Title")
verbose_name=_("Description")
verbose_name=_("Created At")
```

### Forms & Validation
```python
_("This field is required.")
_("Invalid value.")
_("Successfully saved.")
_("An error occurred.")
```

### UI Elements
```django
{% trans "Home" %}
{% trans "Search" %}
{% trans "Login" %}
{% trans "Logout" %}
{% trans "Save" %}
{% trans "Cancel" %}
{% trans "Delete" %}
{% trans "Edit" %}
```

---

## 🐛 Quick Troubleshooting

### Translations not showing?
```bash
python manage.py compilemessages
# Restart server
```

### `gettext` not found?
```bash
# Ubuntu/Debian
sudo apt-get install gettext

# macOS
brew install gettext
```

### Language not switching?
- Clear browser cookies
- Check URL: `/en/` for English
- Verify middleware order in settings.py

### Missing translations?
1. Check `locale/fa/LC_MESSAGES/django.po`
2. Look for empty `msgstr ""`
3. Add translation
4. Run `compilemessages`

---

## 📋 Settings Checklist

In `settings.py`:
```python
LANGUAGE_CODE = "fa"
LANGUAGES = [("fa", "فارسی"), ("en", "English")]
USE_I18N = True
LOCALE_PATHS = [BASE_DIR / "locale"]

MIDDLEWARE = [
    # ...
    "django.middleware.locale.LocaleMiddleware",  # After SessionMiddleware
    # ...
]
```

---

## 🎯 Best Practices

✅ **DO:**
- Use `gettext_lazy` in models
- Keep strings simple and complete
- Test both languages
- Compile after changes

❌ **DON'T:**
- Concatenate translated strings
- Use `gettext` in models (use `gettext_lazy`)
- Forget to compile messages
- Hardcode text in templates

---

## 📊 Current Status

| Component | Coverage |
|-----------|----------|
| Models | ✅ 100% |
| Views | ✅ 100% |
| Templates | ✅ 100% |
| Serializers | ✅ 100% |
| Admin | ✅ 100% |

**Total Strings:** 441 per language  
**Languages:** Persian (fa) + English (en)

---

## 🔗 Full Documentation

See `I18N_GUIDE.md` for complete details.

---

## 💡 Quick Examples

### Model Field
```python
name = models.CharField(max_length=100, verbose_name=_("Name"))
```

### View Message
```python
messages.success(request, _("Saved successfully!"))
```

### Template Text
```django
<button>{% trans "Save" %}</button>
```

### Validation Error
```python
raise ValidationError(_("This field cannot be empty."))
```

### Form Label
```python
name = forms.CharField(label=_("Your Name"))
```

---

**Quick Help:** If stuck, see `I18N_GUIDE.md` for detailed instructions!