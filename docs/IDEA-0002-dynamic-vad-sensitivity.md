# IDEA-0002: Dynamic VAD Sensitivity (Speed Adjustment)

## 1. Das Problem
Aktuell ist der Parameter `min_silence_duration_ms` (minimale Pausenlänge, bevor ein Satz als beendet gilt) fest in der `config.yaml` auf 500ms eingestellt.
*   **Schnelle Sprecher** fühlen sich ausgebremst, da das System zu lange wartet, bis es "begreift", dass der Satz zu Ende ist.
*   **Langsame Sprecher** (oder beim Diktieren) werden unterbrochen, wenn sie kurz nachdenken, weil das System die Denkpause fälschlicherweise als Satzende interpretiert.

## 2. Die Lösung
Der Nutzer soll diesen Wert zur Laufzeit (während der Aufnahme) über einen Schieberegler (Slider) im Frontend anpassen können.

### 2.1 Frontend (UI)
*   Hinzufügen eines Sliders `range` input.
*   Wertebereich: `200ms` (sehr schnell/aggressiv) bis `2000ms` (sehr geduldig).
*   Standardwert: `500ms`.

### 2.2 Kommunikation (WebSocket)
Bisher überträgt der WebSocket rein binäre Audiodaten (Float32 Arrays). Um Steuerbefehle zu senden, muss das Protokoll erweitert werden.
*   **Option A (Hybrid):** Unterscheidung zwischen Text-Frames (JSON Config) und Binary-Frames (Audio).
    *   `{"type": "config", "vad_silence_ms": 800}`
*   **Option B (Query Params):** Nur beim Verbindungsaufbau (einfacher, aber erfordert Reconnect bei Änderung).
    *   *Entscheidung:* Option A ist für "Live-Adjustment" notwendig.

### 2.3 Backend (Logik)
*   Der `VADProcessor` erhält eine Methode `set_min_silence(ms)`.
*   Der WebSocket-Loop in `main.py` prüft den Nachrichtentyp:
    *   `bytes` -> Audioverarbeitung (wie bisher).
    *   `str/json` -> Konfigurationsupdate -> Ruft `vad.set_min_silence()` auf.

## 3. Akzeptanzkriterien
*   [ ] Slider im UI vorhanden.
*   [ ] Änderungen am Slider werden sofort (ohne Neustart der Aufnahme) an das Backend gesendet.
*   [ ] Backend passt das VAD-Verhalten sofort an.
