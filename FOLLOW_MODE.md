# Direct Fixture Assignment (Follow Mode) - Anleitung

## Was ist Follow Mode?

Mit **Follow Mode** kannst du einen spezifischen Moving Head direkt dem Controller zuweisen, unabhängig von der Selection. Perfect für:
- Follow-Spot Effekte
- Einzelne Fixture-Kontrolle während andere arbeiten
- Präzise Steuerung ohne Selection zu ändern
- Live-Performance mit einem "Hero Fixture"

## 🎯 Schnellstart

### Fixture dem Controller zuweisen

1. **Finde die Fixture ID** in MA3:
   ```
   List Fixture  # Zeigt alle Fixtures mit IDs
   ```
   Beispiel: Fixture 101 = "Spot 1"

2. **Weise es zu:**
   ```lua
   Lua "AssignFixture(101)"
   ```

3. **Bewege den Controller** → Nur Fixture 101 bewegt sich!

### Follow Mode beenden

```lua
Lua "ClearFixture()"
```
→ Zurück zum normalen Selection Mode

---

## 📋 Commands

### AssignFixture(fixtureId)
Weist ein Fixture dem Controller zu.

**Beispiele:**
```lua
Lua "AssignFixture(101)"  -- Fixture 101
Lua "AssignFixture(25)"   -- Fixture 25
```

**Was passiert:**
- Plugin wechselt in Follow Mode
- Nur dieses Fixture wird gesteuert
- Selection wird ignoriert
- Console zeigt Bestätigung

**Output:**
```
✓ FOLLOW MODE aktiv: Fixture 101 (Spot 1)
  Nur dieses Fixture wird gesteuert!
  Zum Beenden: Lua "ClearFixture()"
```

### ClearFixture()
Beendet Follow Mode.

```lua
Lua "ClearFixture()"
```

**Was passiert:**
- Follow Mode wird beendet
- Plugin kehrt zu Selection Mode zurück
- Jetzt werden wieder alle selektierten Fixtures gesteuert

---

## 🎭 Workflows

### Workflow 1: Follow-Spot

```
Szenario: Ein Spot soll Performer folgen, Rest macht eigenes Ding

1. Alle Fixtures für Szene programmiert & laufen
2. Lua "AssignFixture(42)"  # Spot 42 zuweisen
3. Controller bewegen → Spot 42 folgt
4. Andere Fixtures laufen weiter (unabhängig)
5. Lua "ClearFixture()" wenn fertig
```

### Workflow 2: Einzelne Fixture programmieren

```
Szenario: Präzise Position für ein Fixture finden

1. Lua "AssignFixture(15)"
2. Controller: Grobe Position (linker Stick)
3. Controller: Feine Anpassung (rechter Stick)
4. Position gefunden → Store
5. ClearFixture() → Nächstes Fixture
```

### Workflow 3: Live Performance Switch

```
Szenario: Zwischen verschiedenen Hero Fixtures wechseln

Song Part 1:
- Lua "AssignFixture(10)"  # Front Spot
- Controller steuert nur Spot 10

Chorus:
- Lua "AssignFixture(25)"  # Side Spot
- Controller steuert jetzt Spot 25

Outro:
- Lua "ClearFixture()"
- Group "All Spots"
- Controller steuert alle zusammen
```

---

## 🔍 Status prüfen

```lua
Lua "ShowStatus()"
```

**Selection Mode:**
```
═══════════════════════════════════════════
  XBOX CONTROLLER STATUS
═══════════════════════════════════════════
Modus:       RELATIVE
Mode:        SELECTION
Selection:   8 Fixtures
═══════════════════════════════════════════
```

**Follow Mode:**
```
═══════════════════════════════════════════
  XBOX CONTROLLER STATUS
═══════════════════════════════════════════
Modus:       RELATIVE
Mode:        FOLLOW (Fixture 101)
Target:      Spot 1
═══════════════════════════════════════════
```

---

## ⚙️ Modi-Kombination

Follow Mode funktioniert mit ALLEN anderen Features:

### Relative + Follow
```lua
Lua "AssignFixture(50)"
# Relative Mode (default)
→ Stick bewegen = Fixture bewegt sich kontinuierlich
```

### Absolute + Follow
```lua
Lua "AssignFixture(50)"
Lua "ToggleMode()"  # Zu Absolute
→ Stick Position = Fixture Position (direkt)
```

### Fine Control + Follow
```
Lua "AssignFixture(50)"
→ Linker Stick = Grob
→ Rechter Stick = Fein
Beide steuern Fixture 50
```

### Speed Adjust + Follow
```lua
Lua "AssignFixture(50)"
Lua "SetSpeed(5.0)"  # Schneller
→ Fixture 50 bewegt sich mit 5x Speed
```

---

## 🛠️ Advanced Use-Cases

### Macro für schnellen Zugriff

Erstelle Macros für oft verwendete Fixtures:

```
Macro 1:
  Lua "AssignFixture(10)"
  Label "Follow Front Spot"

Macro 2:
  Lua "AssignFixture(25)"
  Label "Follow Side Spot"

Macro 3:
  Lua "ClearFixture()"
  Label "Exit Follow Mode"
```

Lege auf Executors → Ein Klick zum Wechseln!

### Multi-Fixture Follow (Trick)

Zwar kannst du nur 1 Fixture direkt zuweisen, aber:

```
1. Erstelle Gruppe mitgewünschten Fixtures:
   Group "FollowGroup" Fixture 10 + 11 + 12

2. Nutze Selection Mode:
   Group "FollowGroup"
   # Alle 3 Fixtures zusammen steuern

3. Für echtes Single-Fixture:
   Lua "AssignFixture(10)"  # Nur Fixture 10
```

---

## 📊 Performance

Follow Mode ist **genauso performant** wie Selection Mode:
- Gleiche Update-Rate (20 Hz)
- Gleiche Velocity Smoothing
- Gleiche Deadzone
- Keine zusätzliche Latenz

**Unterschied:**
- Selection Mode: `Attribute 'Pan' At +2.5` (auf Selection)
- Follow Mode: `Fixture 101 Attribute 'Pan' At +2.5` (direkt)

---

## ⚠️ Fehlerbehandlung

### Fixture nicht gefunden
```lua
Lua "AssignFixture(999)"
→ ⚠ Fixture 999 nicht gefunden!
```

### Fixture wird gelöscht während Follow Mode
```
→ ⚠ Assigned Fixture 101 nicht mehr verfügbar!
→ Follow Mode automatisch beendet
→ Zurück zu Selection Mode
```

### Ungültige ID
```lua
Lua "AssignFixture(abc)"
→ ⚠ Ungültige Fixture ID!
```

---

## 🎯 Best Practices

1. **Fixture ID merken:** Notiere oft verwendete IDs
2. **Macros nutzen:** Schneller Zugriff auf Follow Mode
3. **Status checken:** Bei Problemen `ShowStatus()` verwenden
4. **ClearFixture() nicht vergessen:** Sonst steuert Selection nicht mehr!
5. **Kombiniere mit Speed:** Langsam für Follow-Spot, schnell für Programming

---

## 📝 Zusammenfassung

**Follow Mode erlaubt:**
✅ Einzelnes Fixture direkt steuern
✅ Unabhängig von Selection
✅ Kombination mit allen Features (Relative, Absolute, Fine Control)
✅ Perfect für Follow-Spots & focused control

**Commands:**
- `AssignFixture(id)` → Fixture zuweisen
- `ClearFixture()` → Follow Mode beenden
- `ShowStatus()` → Aktuellen Status sehen

**Use-Cases:**
- Follow-Spot Effects
- Präzises Einzelfixture Programming
- Live Performance mit Hero Fixture
- Isolierte Kontrolle während Show läuft

---

*MA3 Controller Bridge v2.1 - Now with Direct Fixture Assignment!* 🎯💡
