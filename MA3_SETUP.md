# MA3 Plugin Setup Anleitung

## Installation des Plugins

### Schritt 1: Plugin in MA3 laden

1. **Öffne GrandMA3** (onPC oder Konsole)

2. **Navigiere zum Plugin-Ordner:**
   - Windows: `C:\ProgramData\MA Lighting Technologies\grandma3\gma3_library\datapools\plugins`
   - oder über MA3: `Menu → Backup → USB → Browse` zum Plugin-Ordner

3. **Kopiere `XboxControl.lua`** in den Plugin-Ordner

4. **In MA3:**
   - Drücke `Menu → Plugins`
   - Klicke `Import Plugin`
   - Wähle `XboxControl.lua`
   - Plugin erscheint in der Plugin-Liste

### Schritt 2: OSC Input konfigurieren

1. **Öffne OSC-Einstellungen:**
   ```
   Menu → In & Out → OSC
   ```

2. **Aktiviere OSC Input:**
   - Click auf `OSC Input` Tab
   - Aktiviere Port `8000` (oder deinen gewählten Port)
   - Input Slot = aktiv (grün)

3. **Test:** Starte das Python-Script - in der OSC-Log sollten Nachrichten erscheinen

### Schritt 3: Executors anlegen

Das Plugin benötigt **Page 1, Executor 201-203** (oder deine konfigurierten IDs):

1. **Gehe zu Page 1:**
   ```
   Page 1
   ```

2. **Erstelle leere Executors:**
   - Executor 201: Für Pan
   - Executor 202: Für Tilt  
   - Executor 203: Für Dimmer

   **So geht's:**
   ```
<   Store Executor 1.201
>   Store Executor 1.202
   Store Executor 1.203
   ```
   
   *(Alternativ: Leer lassen, OSC erstellt sie automatisch)*

### Schritt 4: Python-Script anpassen (optional)

Wenn du andere Page/Fader verwenden möchtest, ändere in `xbox_to_ma3.py`:

```python
# Zeile 37-39 ändern:
client.send_message("/Page1/Fader201", (pan_val + 1) * 50) 
client.send_message("/Page1/Fader202", (tilt_val + 1) * 50)
client.send_message("/Page1/Fader203", (trigger_val + 1) * 50)
```

UND in `XboxControl.lua`:

```lua
-- Zeile 30-32 ändern:
local CONFIG = {
    source_page = 1,      -- Deine Page
    fader_pan = 201,      -- Dein Pan-Fader
    fader_tilt = 202,     -- Dein Tilt-Fader
    fader_dimmer = 203,   -- Dein Dimmer-Fader
```

---

## Plugin verwenden

### Quick Start

1. **Starte Python-Script:**
   ```bash
   python xbox_to_ma3.py
   ```

2. **In MA3 - Plugin starten:**
   - Navigiere zu `Menu → Plugins`
   - Finde `XboxControl` in der Liste
   - Klicke `Start Plugin`
   
   **ODER lege es auf einen Executor:**
   ```
   Assign Plugin "XboxControl" at Executor 2.1
   ```
   Dann: Drücke den Executor-Button

3. **Wähle Fixtures aus:**
   ```
   Group 1
   ```
   
4. **Bewege den Controller** → Fixtures folgen!

### Workflow

```
1. Python Script starten
2. Controller verbinden (sichtbar im UI)
3. MA3 Plugin starten
4. Fixtures selektieren
5. Controller bewegen → Licht reagiert
6. Andere Gruppe wählen → Diese reagiert jetzt
```

---

## Konfiguration

### Modi umschalten

Das Plugin unterstützt zwei Modi:

#### **Relative Mode** (Standard - Ego-Shooter Style)
- Stick nach links → Licht dreht links
- Stick loslassen → Licht stoppt
- Wie ein Joystick in einem Spiel

#### **Absolute Mode**
- Stick-Position = Licht-Position
- Stick Mitte = Pan/Tilt Center
- Stick loslassen → Licht fährt zur Mitte

**Modus wechseln in MA3 Commandline:**
```
Lua "ToggleMode()"
```

### Geschwindigkeit anpassen

**Schneller/langsamer im Relativen Modus:**
```
Lua "SetSpeed(5.0)"    -- 5x schneller
Lua "SetSpeed(0.5)"    -- Halbe Geschwindigkeit
```

### Deadzone einstellen

**Verhindert Stick-Drift (wenn Controller minimal abrutscht):**
```
Lua "SetDeadzone(10)"   -- 10% Deadzone (größer)
Lua "SetDeadzone(2)"    -- 2% Deadzone (kleiner)
```

Standard: **5%**

---

## Plugin-Features

✅ **Relativer Modus:** Ego-Shooter Style Control
✅ **Absoluter Modus:** Direkte Position Mapping  
✅ **Deadzone Filter:** Prevents Stick Drift
✅ **Selection-Aware:** Arbeitet immer mit aktuell gewählten Fixtures
✅ **Live Speed Adjust:** Geschwindigkeit im laufenden Betrieb ändern
✅ **Dimmer Support:** Right Trigger steuert Dimmer
✅ **Easy Config:** Alles in der CONFIG-Tabelle anpassbar

---

## Konfiguration im Plugin anpassen

Öffne `XboxControl.lua` und ändere die CONFIG-Tabelle:

```lua
local CONFIG = {
    source_page = 1,           -- Page für OSC Input
    fader_pan = 201,           -- Fader ID für Pan
    fader_tilt = 202,          -- Fader ID für Tilt
    fader_dimmer = 203,        -- Fader ID für Dimmer
    
    deadzone = 5,              -- Deadzone in Prozent (0-100)
    default_mode = "relative", -- "relative" oder "absolute"
    speed_multiplier = 2.0,    -- Geschwindigkeit (höher = schneller)
    update_interval = 0.05,    -- Update-Rate in Sekunden (0.05 = 20Hz)
}
```

Nach Änderung: **Plugin neu starten** (Stop → Start)

---

## Troubleshooting

### "Plugin startet nicht"

**Check:**
- Ist das Python-Script am Laufen?
- Sendet es OSC? (Im Python UI sichtbar)
- Ist MA3 OSC Input aktiv? (`Menu → In & Out → OSC`)

### "Licht reagiert nicht auf Controller"

**Check:**
- Sind Fixtures selektiert? (`Selection` sollte nicht leer sein)
- Bewegt sich der Stick genug? (Deadzone = 5%)
- Im Python UI: Bewegen sich die OSC-Werte?
- In MA3: Bewegen sich die Fader 201-203?

**Debug:**
```
List Executor 1.201   # Zeigt Fader-Wert an
```

### "Licht bewegt sich nicht smooth"

**Lösung:**
```lua
-- In XboxControl.lua, Zeile 41 ändern:
update_interval = 0.03,  -- 33 Hz statt 20 Hz
```

Oder Geschwindigkeit reduzieren:
```
Lua "SetSpeed(1.0)"
```

### "Stick driftet (Licht bewegt sich von alleine)"

**Lösung:**
```
Lua "SetDeadzone(10)"  -- Größere Deadzone
```

---

## Advanced: Executor-Button für Mode-Switch

Du kannst den Mode-Switch auf einen Executor legen:

```
Store Macro 1 "ToggleMode"
Assign Macro 1 at Executor 3.1
Label Executor 3.1 "Relative/Absolute"
```

Jetzt: Button drücken = Modus wechseln! 🎮

---

## Nächste Schritte

- [ ] Speed Control mit rechtem Stick implementieren
- [ ] Farb-Steuerung mit D-Pad
- [ ] Preset-Recall mit Buttons
- [ ] Multi-Parameter Mapping (Gobo, Zoom, etc.)

Viel Erfolg mit dem Setup! 🎭💡
