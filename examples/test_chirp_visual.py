import numpy as np
import matplotlib.pyplot as plt
from python_prototype.waveform.chirp_generator import ChirpGenerator

# Erzeuge Chirp
gen = ChirpGenerator(f_start=24e9, bandwidth=200e6,
                     chirp_duration=100e-6, sample_rate=500e6)
# ↑ Ruft __init__() auf, speichert Parameter in self.xxx. gen ist objekt/instanz

time, signal, phase = gen.generate_chirp()
# Nutze Methoden des Objekts

# Plot 1: Erste 1000 Samples (Zeitbereich)
plt.figure(figsize=(12, 8))

plt.subplot(3, 1, 1)
plt.plot(time[:1000] * 1e6, signal[:1000])  # µs
plt.xlabel('Time [µs]')
plt.ylabel('Amplitude')
plt.title('Chirp Signal (first 1000 samples)')
plt.grid(True)

# Plot 2: Instantane Frequenz
plt.subplot(3, 1, 2)
inst_freq = gen.get_instantaneous_frequency(time)
plt.plot(time * 1e6, inst_freq / 1e9)  # GHz
plt.xlabel('Time [µs]')
plt.ylabel('Frequency [GHz]')
plt.title('Instantaneous Frequency (should be linear!)')
plt.grid(True)

# Plot 3: Spektrogramm (wie STFT!)
plt.subplot(3, 1, 3)
plt.specgram(signal, Fs=500e6, NFFT=1024, noverlap=512)
plt.xlabel('Time [µs]')
plt.ylabel('Frequency [MHz]')
plt.title('Spectrogram')
plt.colorbar(label='Power [dB]')

plt.tight_layout()
plt.savefig('chirp_visualization.png', dpi=150)
plt.show()

print("✅ Chirp visualization saved!")
print(f"📊 Chirp Rate: {gen.chirp_rate/1e12:.2f} THz/s")
print(f"📏 Range Resolution: {3e8/(2*gen.bandwidth):.2f} m")
print(f"📐 Max Range: {3e8*gen.chirp_duration/2/1e3:.2f} km")