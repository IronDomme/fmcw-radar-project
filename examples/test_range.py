import numpy as np
import matplotlib.pyplot as plt
from python_prototype.waveform.chirp_generator import ChirpGenerator
from python_prototype.signal_processing.range_fft import RangeProcessor

print("="*70)
print("FMCW RANGE PROCESSING TEST")
print("="*70)

# 1. PARAMETER DEFINIEREN (Hardware: Eval-DEMORAD)
f_start = 24.00e9
bandwidth = 250e6
chirp_duration = 256e-6
sample_rate = 1e6

# 2. CHIRP GENERATOR ERSTELLEN
gen = ChirpGenerator(
    f_start=f_start,
    bandwidth=bandwidth,
    chirp_duration=chirp_duration,
    sample_rate=sample_rate
)

# 3. RANGE PROCESSOR ERSTELLEN (bekommt Generator übergeben!)
proc = RangeProcessor(gen)

# 4. TARGET SIMULIEREN
target_range = 50.0  # 50 Meter
time, tx_signal, rx_signal = proc.simulate_target(range_m=target_range, rcs=0.01)

#5 SIGNAL MISCHEN
beat_signal = proc.mix_signals(tx_signal, rx_signal)

#6 RANGE FFT
frequ_bins, range_bins, range_profile_db = proc.range_fft(beat_signal=beat_signal,  window='hann')

#7 PEAK DETECTION
peak_idxs = proc.detect_peaks(range_profile_db, threshold_db=-170)
detected_beat_freqs = frequ_bins[peak_idxs]
detected_ranges = range_bins[peak_idxs]
magnitudes = range_profile_db[peak_idxs]

#8 Validation
expected_beat_freq = 2*bandwidth*target_range/(chirp_duration*proc.c)


# ===== AUSGABE =====
print(f"\n{'='*60}")
print("VALIDATION RESULTS")
print(f"{'='*60}")
print(f"Target Range:            {target_range:.2f} m")
print(f"Expected Beat Frequency: {expected_beat_freq/1e3:.1f} kHz")

if len(peak_idxs) > 0:
    print(f"\n✅ DETECTED {len(peak_idxs)} TARGET(S):")
    for i, (freq, rng, mag) in enumerate(zip(detected_beat_freqs, detected_ranges, magnitudes)):
        print(f"\n  Target #{i+1}:")
        print(f"    Beat Frequency: {freq/1e3:.1f} kHz")
        print(f"    Range:          {rng:.2f} m")
        print(f"    Magnitude:      {mag:.1f} dB")
        
        # Fehler berechnen
        freq_error = abs(freq - expected_beat_freq)
        range_error = abs(rng - target_range)
        
        print(f"    Freq Error:     {freq_error/1e3:.2f} kHz")
        print(f"    Range Error:    {range_error:.2f} m")
        
        if range_error < 1.0:
            print(f"    ✅ VALIDATED (error < 1m)")
        else:
            print(f"    ⚠️  WARNING (error > 1m)")
else:
    print("❌ NO TARGETS DETECTED!")

print(f"{'='*60}\n")


