# IDEA-0003: Continuous Duplex Pipeline (Synchron-Translation)

## 1. Das Problem
Das aktuelle System arbeitet im **Half-Duplex** Modus ("Walkie-Talkie"-Prinzip):
1.  User spricht.
2.  System erkennt Pause -> **Blockiert Input**.
3.  System übersetzt & spielt Audio ab.
4.  User darf erst wieder sprechen, wenn Audio fertig ist.

Für eine flüssige Rede oder Dolmetscher-Funktion ist das zu langsam und unnatürlich.

## 2. Die Lösung: Full-Duplex Pipeline
Das System soll **gleichzeitig** zuhören und sprechen können.

### 2.1 Voraussetzungen
*   **Akustische Trennung:** Zwingend erforderlich (Kopfhörer oder Richtmikrofon mit Echo Cancellation), damit das Mikrofon nicht die Ausgabe des Übersetzers wieder aufnimmt (Rückkopplungsschleife).

### 2.2 Architektur-Änderungen

#### Input-Seite (Das "Ohr")
*   Das Mikrofon bleibt **permanent offen**.
*   Der `VADProcessor` arbeitet kontinuierlich weiter, auch wenn gerade Audio abgespielt wird.
*   Sobald ein Satz (Satz A) fertig ist, wird er sofort an den `TranslatorEngine` übergeben.
*   Der User spricht währenddessen bereits Satz B.

#### Processing (Das "Gehirn")
*   Die Übersetzung muss asynchron erfolgen, ohne den WebSocket-Empfang zu blockieren.
*   Python's `asyncio` Event-Loop muss genutzt werden, um Empfangen (Listen) und Senden (Speak) zu entkoppeln.

#### Output-Seite (Der "Mund")
*   **Audio Queue (Warteschlange):**
    *   Wenn Satz A fertig übersetzt ist, wird er an den Browser gesendet.
    *   Wenn Satz B fertig übersetzt ist, während Satz A noch im Browser abgespielt wird, darf Satz B nicht "verschluckt" oder überlagert werden.
    *   Er wird in eine **Frontend-Queue** eingereiht.
*   Das Frontend spielt die Queue sequenziell ab (FIFO: First-In-First-Out).

### 2.3 Zeitlicher Ablauf (Beispiel)

| Zeit | User (Input) | System (Processing) | Lautsprecher (Output) |
| :--- | :--- | :--- | :--- |
| 00s | Spricht Satz 1 | ... | (stille) |
| 05s | Spricht Satz 2 | Erkennt Ende Satz 1 -> Übersetzt Satz 1 | (stille) |
| 07s | Spricht Satz 2 | Übersetzung Satz 1 fertig | **Spielt Satz 1** |
| 10s | Spricht Satz 3 | Erkennt Ende Satz 2 -> Übersetzt Satz 2 | **Spielt Satz 1** |
| 12s | Spricht Satz 3 | Übersetzung Satz 2 fertig -> In Queue | **Spielt Satz 1** (Ende) |
| 13s | Spricht Satz 3 | ... | **Spielt Satz 2** |

## 3. Technische Herausforderungen
1.  **Browser Audio Context:** Darf nicht blockieren.
2.  **WebSocket Concurrency:** Python FastAPI muss gleichzeitig `receive_bytes` (Input) und `send_bytes` (Output) handhaben. Eventuell Aufteilung in zwei separate WebSockets oder asynchrone Tasks.
3.  **Latenz:** Die Pipeline muss extrem effizient sein, damit der "Stau" in der Queue nicht immer größer wird.

## 4. Akzeptanzkriterien
*   [ ] User kann ohne Pause durchsprechen.
*   [ ] System gibt Übersetzungen nacheinander aus, ohne Sätze zu verschlucken.
*   [ ] Keine Audio-Überlappungen.
