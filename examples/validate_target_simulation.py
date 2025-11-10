import numpy as np
import matplotlib.pyplot as plt
from python_prototype.waveform.chirp_generator import ChirpGenerator
from python_prototype.signal_processing.range_fft import RangeProcessor

# Setup
gen = ChirpGenerator(f_start=24e9, bandwidth=250e6, 
                     chirp_duration=256e-6, sample_rate=1e6)
proc = RangeProcessor(gen)

# Simuliere Target bei 50m
target_range = 50.0
time, tx, rx = proc.simulate_target(range_m=target_range, rcs=1.0)

# Berechne erwartete Beat-Frequenz
expected_beat_freq = (2 * proc.bandwidth * target_range) / (proc.c * proc.chirp_duration)
print(f"Target Range: {target_range} m")
print(f"Expected Beat Frequency: {expected_beat_freq/1e3:.1f} kHz")

# Mische Signale
beat = tx * rx

# FFT des Beat-Signals
spectrum = np.fft.fft(beat)
freqs = np.fft.fftfreq(len(beat), d=1/proc.sample_rate)

# Nur positive Frequenzen
pos_mask = freqs > 0
freqs_pos = freqs[pos_mask]
spectrum_pos = np.abs(spectrum[pos_mask])

# Finde Peak
peak_idx = np.argmax(spectrum_pos)
detected_beat_freq = freqs_pos[peak_idx]

print(f"Detected Beat Frequency: {detected_beat_freq/1e3:.1f} kHz")
print(f"Error: {abs(detected_beat_freq - expected_beat_freq)/1e3:.2f} kHz")

# Berechne Range aus Beat-Frequenz
detected_range = (detected_beat_freq * proc.c * proc.chirp_duration) / (2 * proc.bandwidth)
print(f"Detected Range: {detected_range:.2f} m")
print(f"Range Error: {abs(detected_range - target_range):.2f} m")

# Plot
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# 1. TX und RX Signale (erste 100 Samples)
axes[0].plot(time[:100]*1e6, tx[:100], label='TX', alpha=0.7)
axes[0].plot(time[:100]*1e6, rx[:100], label='RX (delayed)', alpha=0.7)
axes[0].set_xlabel('Time [µs]')
axes[0].set_ylabel('Amplitude')
axes[0].set_title('TX and RX Signals (first 100 samples)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# 2. Beat-Signal (erste 100 Samples)
axes[1].plot(time[:100]*1e6, beat[:100], color='red', linewidth=1)
axes[1].set_xlabel('Time [µs]')
axes[1].set_ylabel('Amplitude')
axes[1].set_title(f'Beat Signal (f_beat ≈ {detected_beat_freq/1e3:.1f} kHz)')
axes[1].grid(True, alpha=0.3)

# 3. FFT des Beat-Signals
axes[2].plot(freqs_pos/1e3, 20*np.log10(spectrum_pos + 1e-10))
axes[2].axvline(expected_beat_freq/1e3, color='green', linestyle='--', 
                label=f'Expected: {expected_beat_freq/1e3:.1f} kHz')
axes[2].axvline(detected_beat_freq/1e3, color='red', linestyle='--',
                label=f'Detected: {detected_beat_freq/1e3:.1f} kHz')
axes[2].set_xlabel('Frequency [kHz]')
axes[2].set_ylabel('Magnitude [dB]')
axes[2].set_title('Beat Signal Spectrum')
axes[2].set_xlim([0, 500])  # Bis Nyquist
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('target_simulation_validation.png', dpi=150)
plt.show()

if abs(detected_range - target_range) < 1.0:
    print("\n✅ VALIDATION PASSED! Range detection accurate within 1m.")
else:
    print(f"\n⚠️ WARNING: Range error {abs(detected_range - target_range):.2f}m exceeds tolerance!")