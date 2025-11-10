TX (jetzt):  ~~~~~~~~~~~▲▲▲▲▲▲ (hohe Frequenz)
RX (Echo):   ~~~~~~▲▲▲▲▲       (niedrigere Frequenz, zeitverzögert)
              ↓
Beat:        ∿∿∿∿∿∿∿∿∿∿∿∿    (langsame Schwebung)
```

**Die Beat-Frequenz sagt dir die Entfernung!** Je weiter weg das Objekt, desto länger die Verzögerung, desto größer der Frequenzunterschied, desto höher die Beat-Frequenz.

---

## Die Mathematik dahinter

### 1. Der Chirp (TX-Signal)

Ein **Chirp** ist ein Signal, dessen Frequenz linear steigt:
```
f(t) = f_start + (Bandwidth / T_chirp) * t. 
```

- **f_start**: Anfangsfrequenz (z.B. 24 GHz)
- **Bandwidth (B)**: Wie weit die Frequenz schwingt (z.B. 200 MHz)
- **T_chirp**: Wie lange der Sweep dauert (z.B. 100 µs)
-f(t) = instantaneous frequenz  (Augenblicksfrequenz)

**Audio-Analogie:** Das ist wie ein **Synthesizer-Sweep** von 440 Hz (A4) bis 880 Hz (A5) über 1 Sekunde.

Die **Steigung** nennt man **Chirp Rate**:
```
Slope = B / T_chirp = 200 MHz / 100 µs = 2 × 10^15 Hz/s
```

Das Signal selbst ist:
```
s(t) = A A · cos(2π · phi)
     = A · cos(2π · ∫f(t) dt)
     = A · cos(2π · (f_start·t + 0.5·Slope·t²))
```

**Warum t²?** Weil die Frequenz **integriert** wird zur Phase! (Frequenz = Ableitung der Phase)

---

### 2. Das Echo (RX-Signal)

Das Echo ist derselbe Chirp, nur **zeitverzögert** um τ (tau):
```
τ = 2R / c     (Laufzeit hin und zurück)
```

- **R**: Range (Entfernung zum Objekt)
- **c**: Lichtgeschwindigkeit (3 × 10⁸ m/s)

Das RX-Signal ist also:
```
r(t) = A · cos(2π · (f_start·(t-τ) + 0.5·Slope·(t-τ)²))
```

---

### 3. Das Mischen (Beat-Signal)

Im Radar multiplizierst du TX und RX (wie ein **Mixer** in Audio!):
```
Beat = TX × RX
```

Nach etwas Trigonometrie (Produktformel für Cosinus) bekommst du eine **Differenzfrequenz**:
```
f_beat = Slope · τ = (B/T) · (2R/c)
```

Umgestellt nach Range:
```
R = (f_beat · c · T) / (2 · B)