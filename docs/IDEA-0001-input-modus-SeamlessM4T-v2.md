# Analysebericht: Eingabemodalitäten für SeamlessM4T v2

## 1. Grundlegende Architektur
Das Modell `seamless-m4t-v2-large` (Massively Multilingual & Multimodal Machine Translation) ist ein **multimodales** Modell. Das bedeutet, es ist architektonisch darauf ausgelegt, verschiedene Arten von Daten als Eingabe zu verarbeiten, nicht nur Sprache.

Die Architektur basiert auf dem **UnitY2**-Framework, welches zwei Encoder besitzt:
1.  **Speech Encoder:** Basiert auf `w2v-bert 2.0` (für Audio).
2.  **Text Encoder:** Basiert auf der `NLLB` (No Language Left Behind) Architektur (für Text).

Daraus ergeben sich zwei fundamentale Eingabekategorien: **Audio (Speech)** und **Text**.

---

## 2. Eingabeformat: Audio (Speech)
Dies ist der Modus, den Sie aktuell nutzen. Das Modell ist jedoch nicht auf den Mikrofon-Live-Stream beschränkt.

### Technische Anforderungen
Das Modell erwartet als Input mathematische Tensoren (Vektoren), die eine Audio-Wellenform repräsentieren.
*   **Sampling Rate:** Zwingend **16.000 Hz (16 kHz)**.
*   **Kanäle:** Mono (das Modell mischt Stereo-Signale intern meist auf Mono oder verarbeitet nur einen Kanal).

### Mögliche Datenquellen (Software-seitig)
Da das Modell rohe Wellenformen verarbeitet, ist es völlig agnostisch gegenüber der *Quelle* des Audios, solange die Software die Daten vor der Übergabe dekodiert.

*   **Audiodateien (Batch Processing):**
    *   **Formate:** WAV, MP3, FLAC, OGG, AAC, M4A.
    *   **Anwendung:** Sie könnten eine `.mp3` Datei hochladen. Das System decodiert diese mittels `ffmpeg` oder `librosa` in ein Numpy-Array (Float32, 16kHz) und übergibt sie dem Modell.
*   **System-Audio (Loopback):**
    *   Das Audiosignal anderer Anwendungen (z.B. Zoom, YouTube-Video, Podcast im Browser) kann abgegriffen ("Was-Sie-hören"-Aufnahme) und in den Translator gespeist werden.
*   **Audio-Streams (RTSP/HLS):**
    *   Live-Radio oder TV-Streams können in Chunks zerlegt und dem Modell häppchenweise gefüttert werden.

---

## 3. Eingabeformat: Text
Das ist die zweite, vollständig unterstützte Eingabemodalität. Das Modell kann geschriebenen Text als Input akzeptieren.

### Funktionalitäten mit Text-Input
*   **T2ST (Text-to-Speech Translation):**
    *   *Input:* Deutscher Text (getippt).
    *   *Output:* Englische Sprache (Audio).
*   **T2TT (Text-to-Text Translation):**
    *   *Input:* Deutscher Text.
    *   *Output:* Englischer Text.

---

## 4. Übersicht der unterstützten "Core Tasks"
Laut dem Meta AI Research Paper unterstützt das Modell offiziell folgende vier Input/Output-Kombinationen:

| Kürzel | Bezeichnung | Input | Output | Status im aktuellen Projekt |
| :--- | :--- | :--- | :--- | :--- |
| **S2ST** | Speech-to-Speech Translation | **Audio** | **Audio** | ✅ Implementiert |
| **S2TT** | Speech-to-Text Translation | **Audio** | Text | ❌ Nicht implementiert |
| **T2ST** | Text-to-Speech Translation | **Text** | **Audio** | ❌ Nicht implementiert |
| **T2TT** | Text-to-Text Translation | **Text** | Text | ❌ Nicht implementiert |

## 5. Grenzen (Was nicht funktioniert)
*   **Bilder/Video (Visuell):** Es ist kein Vision-Language-Modell. Video-Dateien müssen erst zu Audio konvertiert werden.
*   **Andere Sampling-Raten:** Audio, das nicht 16kHz hat, führt ohne Resampling zu Fehlern.
*   **Gemischte Sprachen im gleichen Satz (Code-Switching):** Das Modell erwartet eine definierte `src_lang` (Quellsprache).

## Fazit
Das genutzte Modell ist **bi-modal** auf der Eingabeseite. Neben dem aktuellen **Audio-Input** ist es auch vollständig fähig, **Text-Input** zu verarbeiten.
