# DIREKTES OSC SETUP - OHNE EXECUTORS!

## Problem
Die bisherige Methode mit Executors ist zu kompliziert - MA3 erstellt sie nicht automatisch.

## ✅ EINFACHE LÖSUNG

Das Python Script kann **DIREKT** Attribute via OSC setzen - ohne Executors!

## Setup in MA3 (NUR 2 SCHRITTE!)

### 1. OSC Input aktivieren
```
Menu → In & Out → OSC
Tab "OSC Input"
Port 8000 → Enabled ✓
```

### 2. Fixtures selektieren
```
Fixture 1 Thru 10
(oder welche Fixtures du steuern willst)
```

**DAS IST ALLES!** ✨

## OSC-Pfade die funktionieren

MA3 versteht diese OSC-Befehle DIREKT:

```
/Programmer/Pan <value>          # Setzt Pan direkt
/Programmer/Tilt <value>         # Setzt Tilt direkt
/Programmer/Dimmer <value>       # Setzt Dimmer direkt
```

ODER mit Fixture-ID:

```
/Fixture/1/Pan <value>           # Nur Fixture 1
/Fixture/2/Tilt <value>          # Nur Fixture 2
```

## Python Script anpassen

Statt:
```python
# ALT - braucht Executors
/Page1/Fader201 → 50.0
```

Neu:
```python
# NEU - funktioniert DIREKT!
/Programmer/Pan → -25.5
/Programmer/Tilt → +15.3
```

## Vorteile

✅ Keine Executors nötig
✅ Keine manuelle Einrichtung
✅ Funktioniert sofort
✅ Direkter Zugriff auf Programmer
✅ Weniger Komplexität

## Was ich jetzt mache

Ich passe das Python Script an:
- Sendet direkt `/Programmer/Pan` etc.
- Funktioniert SOFORT nach MA3 Start
- Keine weiteren Schritte nötig!

Soll ich das umsetzen?
