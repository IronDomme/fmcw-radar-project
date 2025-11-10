2.1 Das FMCW-Prinzip (Refresh)
Das Setup:
RADAR
├─ TX-Antenne: Sendet Chirp aus
│   └─ f(t) = 24.0 → 24.25 GHz über 256 µs
│
├─ TARGET: Drohne bei 50m
│   └─ Reflektiert Signal zurück
│
└─ RX-Antenne: Empfängt Echo
    └─ f(t-τ) = Verzögert um Laufzeit τ
Die Laufzeit:
τ = 2R / c

Warum 2R? 
→ Signal muss hin UND zurück! (Two-way propagation)

Beispiel bei R = 50m:
τ = (2 × 50) / 3e8 = 333 ns

2.2 Der Mix-Down Prozess (Das Herzstück!)
Was passiert im Radar:
TX-Signal (jetzt):           f_tx(t) = 24.0 GHz + slope×t
RX-Signal (Echo, verzögert): f_rx(t) = 24.0 GHz + slope×(t-τ)
                                      └─ τ Verzögerung!

Mixer (Multiplikation):  TX × RX
                         ↓
Beat-Signal:  f_beat = f_tx(t) - f_rx(t)
                     = slope × τ
                     = KONSTANT! (über die Zeit)
Das ist der Trick: Die Frequenzdifferenz ist konstant und proportional zur Laufzeit!

2.3 Die Beat-Frequenz (Mathematik)
Herleitung:
1. TX-Signal Frequenz:
   f_tx(t) = f_start + (B/T) × t
   
2. RX-Signal Frequenz (verzögert um τ):
   f_rx(t) = f_start + (B/T) × (t - τ)
   
3. Beat-Frequenz (Differenz):
   f_beat = f_tx(t) - f_rx(t)
          = f_start + (B/T)×t - [f_start + (B/T)×(t-τ)]
          = (B/T) × τ
          = (B/T) × (2R/c)
          = (2BR)/(cT)
Umgestellt nach Range:
R = (f_beat × c × T) / (2 × B)
Das ist DIE Kernformel! 🎯

2.4 Audio-Analogie: Die Schwebung
Stell dir vor:
Du hast zwei Stimmgabeln:

Stimmgabel A: 440 Hz (A4)
Stimmgabel B: 445 Hz (leicht verstimmt)

Wenn beide gleichzeitig schwingen, hörst du eine Schwebung (Beat) von:
f_beat = 445 - 440 = 5 Hz
→ Du hörst 5× pro Sekunde ein "WUB-WUB-WUB"
Im Radar:

TX-Chirp: "Stimmgabel A" (steigt von 24.0 → 24.25 GHz)
RX-Echo: "Stimmgabel B" (gleicher Sweep, aber verzögert)
Beat: Die Differenz = konstante Frequenz!

Audio-DSP Analogie:
python# Das kennst du vielleicht:
signal_A = np.sin(2*np.pi*440*t)
signal_B = np.sin(2*np.pi*445*t)
beat = signal_A * signal_B  # Ring-Modulation!
# → Erzeugt 5 Hz Schwebung + hohe Frequenz (885 Hz)
```

Im Radar filtern wir die hohe Frequenz weg (Tiefpass) und behalten nur den Beat!

---

## 🔬 3. DER SIGNAL-PROCESSING ABLAUF

**Step-by-Step was im Radar passiert:**
```
STEP 1: CHIRP GENERIEREN
├─ ChirpGenerator erstellt TX-Signal
└─ Output: time[], tx_signal[]

STEP 2: TARGET SIMULIEREN
├─ Berechne Laufzeit τ = 2R/c
├─ Kopiere TX-Signal → RX-Signal
├─ Verzögere RX um τ (Zeit-Shift)
├─ Dämpfe RX (Range⁴ Law)
├─ Addiere Doppler-Shift (falls Target bewegt)
└─ Output: time[], rx_signal[]

STEP 3: MISCHEN
├─ Multipliziere: beat = tx × rx
├─ Tiefpass-Filter (optional, für Hardware)
└─ Output: beat_signal[]

STEP 4: FENSTERUNG
├─ Wähle Fenster (Hann, Hamming, etc.)
├─ Multipliziere: windowed = beat × window
└─ Reduziert Spektral-Leckage

STEP 5: RANGE-FFT
├─ FFT des Beat-Signals
├─ Berechne Magnitude: |FFT|
├─ Konvertiere zu dB: 20×log10(|FFT|)
└─ Output: Range-Profile (Amplitude über Range)

STEP 6: FREQUENZ → RANGE KONVERSION
├─ FFT-Bins sind Frequenzen
├─ Jede Frequenz entspricht einer Range
├─ R = (f_beat × c × T) / (2 × B)
└─ Output: range_bins[], range_profile[]

STEP 7: PEAK DETECTION
├─ Finde Maxima im Range-Profile
├─ Schwellwert-Entscheidung (später: CFAR)
└─ Output: Detektierte Target-Ranges

📐 4. MATHEMATISCHE FORMELN (Komplett)
4.1 TX-Signal (aus Modul 1)
pythonf(t) = f_start + chirp_rate × t

phase(t) = 2π × ∫f(t)dt 
         = 2π × (f_start×t + 0.5×chirp_rate×t²)

signal_tx(t) = A_tx × cos(phase(t))

4.2 RX-Signal (Echo mit Verzögerung)
python# Laufzeit
τ = 2R / c

# Verzögertes Signal (Zeit-Shift)
signal_rx(t) = A_rx × cos(phase(t - τ))

# Amplitude-Dämpfung (Radar-Gleichung, vereinfacht)
A_rx = A_tx × sqrt(RCS) / (R²)

# Mit Doppler-Shift (falls Target bewegt):
signal_rx(t) = A_rx × cos(phase(t - τ) + 2π×f_doppler×t)

wobei:
f_doppler = 2 × v × f_carrier / c
Wichtig: In Modul 2 ignorieren wir erstmal Doppler (v=0), kommt in Modul 3!

4.3 Beat-Signal (Mischen)
python# Multiplikation (Mixer)
beat(t) = signal_tx(t) × signal_rx(t)

# Trigonometrische Identität:
cos(A) × cos(B) = 0.5 × [cos(A-B) + cos(A+B)]

# Ergibt:
beat(t) = 0.5 × A_tx × A_rx × [
    cos(Δphase)           ← Niederfrequenz (Beat!)
  + cos(phase_sum)        ← Hochfrequenz (2×f_carrier)
]

# Nach Tiefpass bleibt nur:
beat(t) ≈ 0.5 × A_tx × A_rx × cos(2π × f_beat × t)

# Mit:
f_beat = (2 × B × R) / (c × T)

4.4 Range-FFT
python# FFT des Beat-Signals
spectrum = FFT(beat_signal × window)

# Magnitude (Absolutwert)
magnitude = |spectrum|

# In dB
magnitude_dB = 20 × log10(magnitude + ε)  # ε gegen log(0)

# Frequenz-Bins
freq_bins = [0, Δf, 2Δf, ..., fs/2]
wobei Δf = fs / N_samples

# Range-Bins (Konversion)
range_bins[i] = (freq_bins[i] × c × T) / (2 × B)

4.5 Wichtige Größen
GrößeFormelMit Hardware-ParameternBeat-Frequenzf_beat = (2BR)/(cT)Bei R=50m: 325.5 kHzRange ResolutionΔr = c/(2B)0.6 mMax Unambiguous RangeR_max = (fs/2 × c × T)/(2B)76.8 mFrequency ResolutionΔf = fs/N3.9 kHzRange per FFT-BinΔR = (Δf × c × T)/(2B)0.6 m