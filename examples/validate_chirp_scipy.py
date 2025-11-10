import numpy as np 
import matplotlib.pyplot as plt
from python_prototype.waveform.chirp_generator import ChirpGenerator  
from scipy.signal import chirp as scipyChirp

# Eval-DEMORAD Parameter (Analog Devices)
f_start = 24.00e9        # 24.00 GHz
bandwidth = 250e6        # 250 MHz (24.00 - 24.25 GHz) 
f_stop = f_start + bandwidth
chirp_duration = 256e-6  # 256 µs
sample_rate = 1e6        # 1 MHz 
samples_per_chirp = 256  # 256 samples chirp_duration*sample_rate

'init generated chirp'
gen = ChirpGenerator(f_start, bandwidth,
                        chirp_duration, sample_rate)

time, my_signal, my_phase = gen.generate_chirp()

scipy_signal = scipyChirp(time, f0=f_start, t1=chirp_duration, f1=f_stop,  method='linear')

difference = my_signal - scipy_signal
max_error = np.max(abs(difference))
rms_error = np.sqrt(np.mean(difference**2))
correlation = np.corrcoef(my_signal, scipy_signal)


print("="*70)
print(f"\n Valdation Results:  ")
print(f"    Max absolute error:   {max_error: .2e}")
print(f"    RMS Error:   {rms_error: .2e}")
print(f"    Correlation:   {correlation}")

if max_error < 1e-10:
    print("  ✅ PERFECT MATCH! Implementation identical to scipy!")
elif max_error < 1e-6:
    print("  ✅ EXCELLENT! Only tiny numerical differences.")
else:
    print("  ⚠️  WARNING: Significant differences detected!")

print("="*70)

# Plotting
fig = plt.figure(figsize=(14, 10))
gs = fig.add_gridspec(4, 2, hspace=0.3, wspace=0.3)

# 1. Beide Signale übereinander (alle Samples!)
ax1 = fig.add_subplot(gs[0, :])
ax1.plot(time * 1e6, my_signal, label='Your Implementation', 
         linewidth=1.5, alpha=0.8)
ax1.plot(time * 1e6, scipy_signal, '--', label='Scipy Reference', 
         linewidth=1, alpha=0.8)
ax1.set_xlabel('Time [µs]')
ax1.set_ylabel('Amplitude')
ax1.set_title('Complete Chirp Signal (256 samples @ 1 MHz)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# 2. Zoom auf erste 50 Samples
ax2 = fig.add_subplot(gs[1, 0])
ax2.plot(time[:50] * 1e6, my_signal[:50], 'o-', 
         label='Your Chirp', markersize=3, linewidth=1)
ax2.plot(time[:50] * 1e6, scipy_signal[:50], 'x--', 
         label='Scipy Chirp', markersize=4, linewidth=1)
ax2.set_xlabel('Time [µs]')
ax2.set_ylabel('Amplitude')
ax2.set_title('Zoom: First 50 Samples')
ax2.legend()
ax2.grid(True, alpha=0.3)

# 3. Differenz
ax3 = fig.add_subplot(gs[1, 1])
ax3.plot(time * 1e6, difference, linewidth=0.8, color='red')
ax3.set_xlabel('Time [µs]')
ax3.set_ylabel('Difference')
ax3.set_title(f'Difference Signal (Max: {max_error:.2e})')
ax3.grid(True, alpha=0.3)
ax3.axhline(y=0, color='black', linestyle='--', linewidth=0.5)

# 4. Instantane Frequenz
ax4 = fig.add_subplot(gs[2, :])
inst_freq = gen.get_instantaneous_frequency(time)
ax4.plot(time * 1e6, inst_freq / 1e9, linewidth=1.5)
ax4.set_xlabel('Time [µs]')
ax4.set_ylabel('Frequency [GHz]')
ax4.set_title('Instantaneous Frequency (Linear Sweep)')
ax4.grid(True, alpha=0.3)
ax4.set_ylim([23.95, 24.3])

# 5. Spektrum Vergleich
ax5 = fig.add_subplot(gs[3, 0])
fft_mine = np.abs(np.fft.fft(my_signal))
fft_scipy = np.abs(np.fft.fft(scipy_signal))
freqs = np.fft.fftfreq(len(time), d=1/sample_rate)

# Nur positive Frequenzen
pos_mask = freqs >= 0
ax5.plot(freqs[pos_mask] / 1e3, 20*np.log10(fft_mine[pos_mask] + 1e-10), 
         label='Your Chirp', alpha=0.8, linewidth=1.5)
ax5.plot(freqs[pos_mask] / 1e3, 20*np.log10(fft_scipy[pos_mask] + 1e-10), 
         '--', label='Scipy Chirp', alpha=0.8, linewidth=1)
ax5.set_xlabel('Frequency [kHz]')
ax5.set_ylabel('Magnitude [dB]')
ax5.set_title('Frequency Spectrum')
ax5.set_xlim([0, 500])  # Bis Nyquist (500 kHz)
ax5.legend()
ax5.grid(True, alpha=0.3)

# 6. Spektrogramm
ax6 = fig.add_subplot(gs[3, 1])
ax6.specgram(my_signal, Fs=sample_rate, NFFT=64, 
             noverlap=32, cmap='viridis')
ax6.set_xlabel('Time [µs]')
ax6.set_ylabel('Frequency [Hz]')
ax6.set_title('Spectrogram (Chirp Sweep)')

plt.suptitle('Eval-DEMORAD Hardware Chirp Validation', 
             fontsize=14, fontweight='bold')
plt.savefig('chirp_validation_hardware.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n📊 Validation plot saved as 'chirp_validation_hardware.png'")
print("✅ Chirp validation complete!\n")