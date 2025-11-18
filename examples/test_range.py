import numpy as np
import matplotlib.pyplot as plt
from python_prototype.waveform.chirp_generator import ChirpGenerator
from python_prototype.signal_processing.range_fft import RangeProcessor


# Setup
gen = ChirpGenerator(f_start=24e9, bandwidth=250e6, 
                     chirp_duration=256e-6, sample_rate=10e6)
proc = RangeProcessor(gen)

# ===== MULTI-TARGET CONFIGURATION =====
multiple_targets = True

if multiple_targets:
    # Target-Definition (Liste von Dictionaries - selbst-dokumentierend!)
    targets = [
        {'range_m': 10, 'rcs': 0.01, 'name': 'Drone (close)'},
        {'range_m': 120, 'rcs': 100, 'name': 'Commercial Airliner(Far)'},
        {'range_m': 70, 'rcs': 0.01, 'name': 'Drone (close)'},
       # {'range_m': 20, 'rcs': 0.001, 'name': 'Bird (close)'},
        {'range_m': 20, 'rcs': 0.005, 'name': 'F35 (close)'}
    ]
    
    print(f"\n{'='*60}")
    print(f"MULTI-TARGET SIMULATION ({len(targets)} targets)")
    print(f"{'='*60}")
    
    # Sammle RX-Signale
    rx_signals = []
    
    for i, target in enumerate(targets, start=1):
        print(f"[{i}/{len(targets)}] Simulating {target['name']}: "
              f"Range={target['range_m']}m, RCS={target['rcs']}m²")
        
        target_range = target['range_m']
        target_rcs =target['rcs']  
        time, tx_signal, rx_signal = proc.simulate_target(
            range_m=target_range,
            rcs=target_rcs
        )
        
        rx_signals.append(rx_signal)
    
    # Superposition: Alle Echos addieren
    rx_total = np.sum(rx_signals, axis=0)
    
    print(f"\n✅ Superposition complete: {len(rx_signals)} signals combined")
    
else:
    # Single Target
    target_range = 50.0
    time, tx_signal, rx_total = proc.simulate_target(
        range_m=target_range,
        rcs=0.01
    )



# Mischen
beat_signal = proc.mix_signals(tx_signal, rx_total)

# Range-FFT
freq_bins, range_bins, range_profile_db = proc.range_fft(
    beat_signal, 
    window='hann'
)

# Peak Detection
peak_idxs = proc.detect_peaks(range_profile_db, snr_db=20, max_peaks=10)

# Validierung
if multiple_targets:
    expected_ranges = [t['range_m'] for t in targets]
else:
    expected_ranges = [target_range]

detected_ranges = range_bins[peak_idxs]

print(f"\n{'='*60}")
print("DETECTION RESULTS")
print(f"{'='*60}")
print(f"Expected Ranges: {expected_ranges}")
print(f"Detected Ranges: {[f'{r:.1f}' for r in detected_ranges]}")

# Matching (welcher Peak gehört zu welchem Target?)
for exp in expected_ranges:
    # Finde nächsten detektierten Peak
    if len(detected_ranges) > 0:
        distances = np.abs(detected_ranges - exp)
        closest_idx = np.argmin(distances)
        closest_range = detected_ranges[closest_idx]
        error = abs(closest_range - exp)
        
        print(f"\nTarget @ {exp}m:")
        print(f"  Detected: {closest_range:.1f}m")
        print(f"  Error:    {error:.2f}m")
        
        if error < 1.0:
            print(f"  ✅ MATCH")
        else:
            print(f"  ⚠️  ERROR > 1m")

# Visualisierung
fig, axes = plt.subplots(4, 1, figsize=(14, 12))

# 1. Einzelne RX-Signale + Total
if multiple_targets:
    for i, (rx, target) in enumerate(zip(rx_signals, targets)):
        axes[0].plot(time[:50]*1e6, rx[:50], 
                    label=f"RX{i+1}: {target['name']}", alpha=0.6)
    axes[0].plot(time[:50]*1e6, rx_total[:50], 'k-', linewidth=2,
                label='Total (Superposition)', alpha=0.8)
else:
    axes[0].plot(time[:50]*1e6, rx_total[:50], label='RX Signal')

axes[0].set_xlabel('Time [µs]')
axes[0].set_ylabel('Amplitude')
axes[0].set_title('RX Signals')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# tx signal
axes[1].plot(time[:50]*1e6, tx_signal[:50], label='TX Signal')
axes[1].set_xlabel('Time [µs]')
axes[1].set_ylabel('Amplitude')
axes[1].set_title('TX Signal')
axes[1].legend()
axes[1].grid(True, alpha=0.3)
# 3. Beat-Signal
axes[2].plot(time[:100]*1e6, beat_signal[:100], color='red', linewidth=1)
axes[2].set_xlabel('Time [µs]')
axes[2].set_ylabel('Amplitude')
axes[2].set_title('Beat Signal')
axes[2].grid(True, alpha=0.3)

# 4. Range-Profile
axes[3].plot(range_bins, range_profile_db, linewidth=1)

# Erwartete Positionen
for exp in expected_ranges:
    axes[3].axvline(exp, color='green', linestyle='--', alpha=0.5)

# Detektierte Peaks
if len(peak_idxs) > 0:
    axes[3].plot(detected_ranges, range_profile_db[peak_idxs],
                'ro', markersize=10, label='Detected')

axes[3].set_xlabel('Range [m]')
axes[3].set_ylabel('Magnitude [dB]')
axes[3].set_title('Range Profile')
axes[3].set_xlim([0, 120])
axes[3].legend()
axes[3].grid(True, alpha=0.3)

plt.tight_layout()
# plt.savefig('multi_target_test.png', dpi=150)
plt.show()

# print(f"\n📊 Plot saved as 'multi_target_test.png'")

