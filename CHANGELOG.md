# MA3 Controller Bridge - Changelog

## v2.0 - Major Enhancement Update

### 🎯 Neue Features

#### 1. **Deadzone-Filter** ✨
- **Problem gelöst:** Controller-Drift (Stick bewegt sich minimal wenn losgelassen)
- **Lösung:** Konfigurierbarer Deadzone-Bereich (Standard: 15%)
- **Visualisierung:** Grauer Kreis im UI zeigt Deadzone an
- **Effekt:** Werte innerhalb der Deadzone werden auf 0 gesetzt
- **Bonus:** Intelligente Skalierung außerhalb der Deadzone für vollen Bewegungsbereich

#### 2. **Smooth Value Interpolation** 🌊
- **Problem:** Ruckartige, nervöse Bewegungen
- **Lösung:** Lineare Interpolation zwischen Werten (Smoothing)
- **Konfigurierbar:** 0% (keine Glättung) bis 100% (maximale Glättung)
- **Standard:** 30% Smoothing
- **Visualisierung:** Raw-Werte (grau) vs. Smoothed-Werte (grün) im UI
- **Ergebnis:** Flüssige, professionelle Bewegungen

#### 3. **config.json - Easy Customization** ⚙️
Keine Code-Änderungen mehr nötig! Alle Einstellungen in `config.json`:

```json
{
  "osc": {
    "host": "127.0.0.1",
    "port": 8000,
    "target_page": 1,
    "fader_pan": 201,
    "fader_tilt": 202,
    "fader_dimmer": 203,
    "fader_fine_pan": 204,
    "fader_fine_tilt": 205
  },
  "controller": {
    "deadzone": 0.15,          // 15% Deadzone
    "sensitivity": 1.0,         // Normale Empfindlichkeit
    "fine_sensitivity": 0.3,    // Fein-Steuerung (30%)
    "update_rate": 50,          // 50 Hz
    "smoothing": 0.3            // 30% Glättung
  },
  "features": {
    "use_right_stick_fine_control": true,
    "show_debug_info": false,
    "auto_reconnect": true
  }
}
```

#### 4. **Rechter Stick = Fine Control** 🎯
- **Funktion:** Präzise Feinsteuerung mit reduzierter Empfindlichkeit
- **Mapping:**
  - Rechter Stick X → Fader 204 (Fine Pan)
  - Rechter Stick Y → Fader 205 (Fine Tilt)
- **Use-Case:** Exakte Positionierung für wichtige Momente
- **Optional:** Kann in config.json deaktiviert werden

#### 5. **Verbessertes UI** 📊

**Neue Anzeigen:**
- ✅ Raw vs. Smoothed Values (visueller Vergleich)
- ✅ Deadzone-Visualisierung (grauer Kreis)
- ✅ Zwei Stick-Indikatoren (Links + Rechts)
- ✅ Statistiken: Runtime, OSC Messages gesendet, FPS
- ✅ Config-Info unten angezeigt (Deadzone, Smoothing, Sensitivity)
- ✅ OSC Connection Status (grün = verbunden)

**Verbesserungen:**
- Größere Schrift für bessere Lesbarkeit
- Mehr Informationen ohne Clutter
- Version-Nummer im Titel (v2.0)

#### 6. **Bessere Konfiguration & Verwaltung** 🛠️

- **Auto-Load:** config.json wird automatisch geladen
- **Fallback:** Funktioniert auch ohne config.json (Default-Werte)
- **Merge-Logic:** Fehlende Keys werden mit Defaults ergänzt
- **Console Output:** Zeigt beim Start alle aktiven Settings

---

### 🔧 Technische Verbesserungen

#### Deadzone-Algorithmus
```python
def apply_deadzone(value, deadzone):
    if abs(value) < deadzone:
        return 0.0
    # Reskalieren auf vollen Bereich außerhalb Deadzone
    sign = 1 if value > 0 else -1
    scaled = (abs(value) - deadzone) / (1.0 - deadzone)
    return sign * scaled
```

#### Smoothing-Algorithmus
```python
def smooth_value(current, target, smoothing):
    # Linear Interpolation
    return current + (target - current) * (1.0 - smoothing)
```

#### OSC Message Paths
Die OSC-Pfade sind jetzt dynamisch aus der Config:
```python
f"/Page{target_page}/Fader{fader_id}"
```

---

### 📈 Performance

| Metrik | v1.0 | v2.0 | Verbesserung |
|--------|------|------|-------------|
| Update Rate | 50 Hz | Konfigurierbar (50 Hz default) | ✓ |
| Stick Drift | Vorhanden | Eliminiert (Deadzone) | ✅ |
| Ruckeln | Manchmal | Smooth (Interpolation) | ✅ |
| Konfiguration | Code-Edit | config.json | ✅ |
| Fine Control | Nein | Rechter Stick | ✅ |
| UI Feedback | Basic | Advanced mit Stats | ✅ |

---

### 🎮 Controller Mapping (Erweitert)

| Input | OSC Path | Default Fader | Funktion |
|-------|----------|---------------|----------|
| **Left Stick X** | `/Page1/Fader201` | 201 | Pan (grob) |
| **Left Stick Y** | `/Page1/Fader202` | 202 | Tilt (grob) |
| **Right Stick X** | `/Page1/Fader204` | 204 | Pan (fein) - *NEU* |
| **Right Stick Y** | `/Page1/Fader205` | 205 | Tilt (fein) - *NEU* |
| **Right Trigger** | `/Page1/Fader203` | 203 | Dimmer |
| **Button A/X** | `/Page1/Key201` | 201 Key | Flash |

---

### 🚀 Verwendung

#### Quick Start mit v2.0

1. **Erste Verwendung:**
   ```bash
   python xbox_to_ma3.py
   ```
   → Lädt Default-Config, funktioniert sofort!

2. **Customization:**
   - Editiere `config.json`
   - Starte Script neu
   - Neue Settings sind sofort aktiv!

3. **Testen:**
   - Bewege Sticks langsam → Sieh Deadzone-Effekt
   - Bewege Sticks schnell → Sieh Smoothing
   - Vergleiche grau (raw) vs. grün (smoothed)

#### Config-Beispiele

**Sehr präzise (kleine Deadzone, kein Smoothing):**
```json
{
  "controller": {
    "deadzone": 0.05,
    "smoothing": 0.0,
    "sensitivity": 1.0
  }
}
```

**Sehr smooth (große Deadzone, viel Smoothing):**
```json
{
  "controller": {
    "deadzone": 0.25,
    "smoothing": 0.6,
    "sensitivity": 0.8
  }
}
```

**Busking-Mode (schnell & reaktiv):**
```json
{
  "controller": {
    "deadzone": 0.10,
    "smoothing": 0.1,
    "sensitivity": 1.5,
    "update_rate": 60
  }
}
```

---

### 🐛 Bug Fixes

- ✅ Controller-Drift eliminiert (Deadzone)
- ✅ Nervöse Bewegungen behoben (Smoothing)
- ✅ Config hardcoded → jetzt flexibel
- ✅ UI zeigt mehr relevante Infos
- ✅ Better organized code structure

---

### 📦 Migration von v1.0 zu v2.0

**Breaking Changes:** Keine! v2.0 ist 100% rückwärtskompatibel.

**Wenn du `config.json` NICHT erstellst:**
- Funktioniert wie v1.0 (mit Defaults)

**Wenn du `config.json` erstellst:**
- Alle Features von v2.0 verfügbar
- Keine Code-Änderungen nötig

**Empfohlen:**
1. Kopiere `config.json` (Vorlage liegt bei)
2. Passe nach Bedarf an
3. Genieße die neuen Features!

---

### 🎯 Was als Nächstes?

Mögliche v2.1 Features:
- [ ] Preset-System (Controller-Profile speichern/laden)
- [ ] UI-Themes (Dark/Light/Custom)
- [ ] Controller-Vibration als Feedback
- [ ] OSC Bi-Directional (Feedback von MA3)
- [ ] Multi-Controller Support
- [ ] Web-UI für Remote-Config

---

### ✅ Zusammenfassung

**v2.0 macht aus einem guten Tool ein PROFESSIONELLES Tool:**

1. ✨ **Deadzone** → Kein Drift mehr
2. 🌊 **Smoothing** → Flüssige Bewegungen
3. ⚙️ **config.json** → Easy Customization
4. 🎯 **Fine Control** → Präzise Steuerung
5. 📊 **Better UI** → Mehr Feedback

**Upgrade empfohlen für alle User!** 🚀

---

*MA3 Controller Bridge v2.0 - Professional Grade Controller Interface*
