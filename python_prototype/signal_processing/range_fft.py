# python_prototype/signal_processing/range_fft.py

import numpy as np 
from typing import Tuple
from python_prototype.waveform.chirp_generator import ChirpGenerator  
from scipy.signal import windows
from scipy.signal import find_peaks
import warnings

class RangeProcessor:
    """
    Verarbeitet FMCW Chirps zu Range-Profiles.
    """
    def __init__(self, chirp_generator: ChirpGenerator):
        """
        Speichert ChirpGenerator-Instanz.
        Extrahiert Parameter für spätere Berechnungen.
        
        WICHTIG: Generiert NOCH KEINEN Chirp!
        Chirps werden erst bei Bedarf erzeugt.
        """
        # Speichere die Referenz auf den übergebenen Generator
        self.chirp_gen = chirp_generator 
        
        # Extrahiere Parameter für spätere Verwendung
        self.f_start = chirp_generator.f_start
        self.bandwidth = chirp_generator.bandwidth
        self.chirp_duration = chirp_generator.chirp_duration
        self.sample_rate = chirp_generator.sample_rate
        self.chirp_rate = chirp_generator.chirp_rate
        self.n_samples = chirp_generator.n_samples
        
        # Konstanten
        self.c = 3e8  # Lichtgeschwindigkeit [m/s]


        
    def simulate_target(self, range_m: float, rcs: float = 1.0, 
                   velocity_mps: float = 0.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Simuliert Echo von einem Target.
        
        Args:
            range_m: Entfernung in Metern
            rcs: Radar Cross Section (Reflektivität)
            velocity_mps: Geschwindigkeit (ignoriert in Modul 2)
            
        Returns:
        time: Zeit-Array
        tx_signal: TX-Chirp-Signal
        rx_signal: RX-Echo-Signal (verzögert und gedämpft)
        
        
        """
        # Generiere TX-Chirp
        time, tx_signal, phase_tx = self.chirp_gen.generate_chirp()
        
        # TX-Amplitude (bei cos-Signal ist Amplitude = 1.0)
        A_tx = 1.0  # Vereinfacht, da tx_signal bereits normalisiert

         # ===== FIX: Handle range_m = 0 =====
        if range_m <= 0:
            warnings.warn(f"Invalid range {range_m}m, using 0.1m instead", 
                     RuntimeWarning)
            range_m = 0.1
        
        # Berechne Laufzeit (Round-Trip Time)
        tau = 2 * range_m / self.c
        
        # Berechne verzögerte Phase: phase_rx(t) = phase_tx(t - tau)
        # Methode: Nutze die originale Phase-Formel mit (t - tau)
        time_delayed = time - tau
        
        # Phase des verzögerten Signals
        phase_rx = 2 * np.pi * (
            self.f_start * time_delayed + 
            0.5 * self.chirp_rate * time_delayed**2
        )
        
        # RX-Amplitude (vereinfachte Radar-Gleichung)
        # Realistische Version: A_rx = A_tx * sqrt(RCS) / (range_m^2)
       # A_rx = A_tx * np.sqrt(rcs) / (range_m**2)
       # Exact version:
        wavelength = self.c / self.f_start
        A_rx = A_tx * np.sqrt(rcs) * wavelength**2 / ((4*np.pi)**1.5 * range_m**2)
        
        # Generiere RX-Signal
        rx_signal = A_rx * np.cos(phase_rx)
        
        return time, tx_signal, rx_signal

    def mix_signals(self, tx, rx) -> Tuple[np.ndarray]:
        """
        Mischt TX und RX → Beat-Signal. Mixing / Heterodyning 
        """
        return tx * rx

    def apply_window(self, beatsignal, window_type='hann') -> Tuple[np.ndarray] :
        """
        Wendet Fenster-Funktion an. 
        """
        # Erstelle ein Fenster mit der gleichen Länge wie das Signal und
        # multipliziere das Signal damit; gebe das geglättete Signal zurück.
        win = windows.get_window(window_type, len(beatsignal))
        return beatsignal * win

    def range_fft(self, beat_signal, window='hann') -> Tuple[np.ndarray, np.ndarray] :
        """
        Führt Range-FFT durch.
        
        Returns:
            range_bins, range_profile_db
        """
        signalfft=self.apply_window(beat_signal, 'hann')
        fourier =np.fft.fft(signalfft)
        magnitude_pos = np.abs(fourier[:self.n_samples//2])
        range_profile_db = 20*np.log10(magnitude_pos+ 1e-10)  # +epsilon gegen log(0))

        # freq bins
        freq = np.fft.fftfreq(len(beat_signal), d=1/self.sample_rate)
        freq_pos=freq[:self.n_samples//2]

        #transform frequencies into range
        range_bins = self.freq_to_range(freq_pos)
        
        return freq_pos, range_bins, range_profile_db 

    def freq_to_range(self, freq_hz: np.ndarray) -> np.ndarray:
        """
        Konvertiert Beat-Frequenz zu Range.
        
        Formula: R = (f_beat × c × T) / (2 × B)
        """
        return freq_hz * self.c * self.chirp_duration / (2 * self.bandwidth)
        
    def detect_peaks(self, range_profile: np.ndarray,
                 snr_db: float = 20,
                 max_peaks: int = 10) -> np.ndarray:
        """
        Robuste Peak Detection mit mehreren Fallback-Strategien.
        
        Args:
            range_profile: Range-Profile [dB]
            snr_db: Minimum Signal-to-Noise Ratio [dB]
            max_peaks: Maximum Anzahl zu detektierender Peaks
            
        Returns:
            peak_indices: Array von Peak-Indizes (sortiert nach Stärke)
        """
        from scipy.signal import find_peaks
        
        # Schätze Noise Floor (robuste Methode)
        sorted_profile = np.sort(range_profile)
        noise_floor = np.median(sorted_profile[:len(sorted_profile)//4])
        
        # Adaptive Threshold
        threshold = noise_floor + snr_db
        
        # DEBUG
        print(f"\n[Peak Detection]")
        print(f"  Profile range: [{np.min(range_profile):.1f}, {np.max(range_profile):.1f}] dB")
        print(f"  Noise floor:   {noise_floor:.1f} dB")
        print(f"  Threshold:     {threshold:.1f} dB")
        print(f"  Above thresh:  {np.sum(range_profile > threshold)} bins")
        
        # Strategie 1: Mit moderaten Constraints
        peaks, properties = find_peaks(
            range_profile,
            height=threshold,
            prominence=5,          # Reduziert von 10 → 5 dB
            distance=5,            # Reduziert von 10 → 5 bins (~3m)
            width=(1, None)       # Reduziert von 2 → 1 bin
        )
        
        print(f"  Strategy 1 (prominence=5): {len(peaks)} peaks")
        
        # Strategie 2: Falls wenig gefunden, lockere weiter
        if len(peaks) < 2:
            peaks, _ = find_peaks(
                range_profile,
                height=threshold,
                distance=3  # Nur min. Abstand
            )
            print(f"  Strategy 2 (distance=3):   {len(peaks)} peaks")
        
        # Strategie 3: Falls immer noch wenig, nur Height
        if len(peaks) < 1:
            peaks, _ = find_peaks(
                range_profile,
                height=threshold
            )
            print(f"  Strategy 3 (height only):  {len(peaks)} peaks")
        
        # Strategie 4: Notfall - nimm stärkste Peaks über Threshold
        if len(peaks) < 1:
            above_threshold = np.where(range_profile > threshold)[0]
            if len(above_threshold) > 0:
                # Sortiere nach Stärke
                sorted_idx = np.argsort(range_profile[above_threshold])[::-1]
                peaks = above_threshold[sorted_idx[:max_peaks]]
                print(f"  Strategy 4 (manual):       {len(peaks)} peaks")
        
        # Sortiere nach Stärke und limitiere
        if len(peaks) > 0:
            peak_magnitudes = range_profile[peaks]
            sorted_idx = np.argsort(peak_magnitudes)[::-1]
            peaks = peaks[sorted_idx]
            
            if len(peaks) > max_peaks:
                peaks = peaks[:max_peaks]
            
            print(f"  Final peaks:   {len(peaks)}")
        else:
            print(f"  ❌ No peaks found!")
        
        return peaks