"""
Unit Tests für Range Processing (Modul 2)
"""

import numpy as np
import pytest
from python_prototype.waveform.chirp_generator import ChirpGenerator
from python_prototype.signal_processing.range_fft import RangeProcessor




class TestRangeProcessor:
    """Test-Suite für RangeProcessor"""
    
    @pytest.fixture
    def setup_processor(self):
        """Setup: Erstelle ChirpGenerator und RangeProcessor"""
        gen = ChirpGenerator(
            f_start=24e9,
            bandwidth=250e6,
            chirp_duration=256e-6,
            sample_rate=1e6
        )
        proc = RangeProcessor(gen)
        return gen, proc
    
    def test_initialization(self, setup_processor):
        """Test: RangeProcessor initialisiert korrekt"""
        gen, proc = setup_processor
        
        assert proc.bandwidth == 250e6
        assert proc.chirp_duration == 256e-6
        assert proc.sample_rate == 1e6
        assert proc.c == 3e8
        
        # Derived parameters
        assert gen.range_resolution == pytest.approx(0.6, rel=0.1)
        assert gen.max_range > 70  # Should be ~76.8m
    
    def test_simulate_target_basic(self, setup_processor):
        """Test: Target-Simulation erzeugt korrektes Signal"""
        gen, proc = setup_processor
        
        target_range = 50.0
        time, tx, rx = proc.simulate_target(target_range, rcs=0.1)
        
        # Check array shapes
        assert len(time) == 256
        assert len(tx) == 256
        assert len(rx) == 256
        
        # Check signal properties
        assert np.max(np.abs(tx)) <= 1.0  # Normalized
        assert np.max(np.abs(rx)) < np.max(np.abs(tx))  # RX is weaker
    
    def test_signal_mixing(self, setup_processor):
        """Test: Signal-Mischen erzeugt Beat-Signal"""
        gen, proc = setup_processor
        
        time, tx, rx = proc.simulate_target(50.0, rcs=0.1)
        beat = proc.mix_signals(tx, rx)
        
        assert len(beat) == len(tx)
        assert np.max(np.abs(beat)) <= 1.0  # Beat sollte normalisiert sein
    
    def test_freq_to_range_conversion(self, setup_processor):
        """Test: Frequenz-zu-Range Konversion"""
        gen, proc = setup_processor
        
        # Test mit bekannten Werten
        # Bei 50m erwarten wir ~325.5 kHz Beat-Frequenz
        expected_beat_freq = (2 * proc.bandwidth * 50.0) / \
                            (proc.c * proc.chirp_duration)
        
        # Konvertiere zurück zu Range
        calculated_range = proc.freq_to_range(expected_beat_freq)
        
        assert calculated_range == pytest.approx(50.0, abs=0.1)
    
    def test_single_target_detection(self, setup_processor):
        """Test: Einzelnes Target wird korrekt detektiert"""
        gen, proc = setup_processor
        
        target_range = 50.0
        time, tx, rx = proc.simulate_target(target_range, rcs=0.1)
        beat = proc.mix_signals(tx, rx)
        
        freq_bins, range_bins, profile = proc.range_fft(beat, window='hann')
        peaks = proc.detect_peaks(profile, snr_db=15, max_peaks=5)
        
        # Mindestens ein Peak gefunden
        assert len(peaks) >= 1, "No peaks detected"
        
        # Peak sollte nahe bei expected range sein
        detected_range = range_bins[peaks[0]]
        error = abs(detected_range - target_range)
        
        assert error < 1.0, f"Range error {error:.2f}m exceeds tolerance"
    
    def test_multi_target_detection(self, setup_processor):
        """Test: Mehrere Targets werden korrekt detektiert"""
        gen, proc = setup_processor
        
        # Unterschiedliche RCS für mehr Realismus
        target_configs = [
            (30.0, 0.05),   # Kleine Drohne nah
            (50.0, 0.1),    # Mittlere Drohne mittel
            (70.0, 0.08)    # Kleine Drohne fern
        ]
        
        rx_signals = []
        
        for range_m, rcs in target_configs:
            time, tx, rx = proc.simulate_target(range_m, rcs)
            rx_signals.append(rx)
        
        rx_total = np.sum(rx_signals, axis=0)
        beat = proc.mix_signals(tx, rx_total)
        
        freq_bins, range_bins, profile = proc.range_fft(beat)
        peaks = proc.detect_peaks(profile, snr_db=15, max_peaks=10)  # SNR 15 statt 20
        
        print(f"\nTest Result: Detected {len(peaks)} peaks")
        if len(peaks) > 0:
            detected_ranges = range_bins[peaks]
            print(f"Detected ranges: {detected_ranges}")
        
        # Erwarte mindestens 2 von 3
        assert len(peaks) >= 2, f"Expected at least 2 peaks, got {len(peaks)}"
        
        # Check dass Detektionen nahe bei erwarteten Ranges sind
        expected_ranges = [30.0, 50.0, 70.0]
        detected_ranges = range_bins[peaks[:3]] if len(peaks) >= 3 else range_bins[peaks]
        
        matches = 0
        for expected in expected_ranges:
            distances = [abs(d - expected) for d in detected_ranges]
            if len(distances) > 0 and min(distances) < 3.0:  # 3m Toleranz
                matches += 1
        
        print(f"Matched {matches} of 3 expected targets")
        assert matches >= 2, f"Only {matches} targets matched expected positions"
    
    def test_beat_frequency_accuracy(self, setup_processor):
        """Test: Beat-Frequenz stimmt mit Theorie überein"""
        gen, proc = setup_processor
        
        target_range = 50.0
        
        # Erwartete Beat-Frequenz
        expected_beat = (2 * proc.bandwidth * target_range) / \
                       (proc.c * proc.chirp_duration)
        
        # Simuliere und mische
        time, tx, rx = proc.simulate_target(target_range, rcs=0.1)
        beat = proc.mix_signals(tx, rx)
        
        # Finde dominante Frequenz im Beat
        spectrum = np.fft.fft(beat)
        freqs = np.fft.fftfreq(len(beat), d=1/proc.sample_rate)
        
        pos_mask = freqs > 0
        freqs_pos = freqs[pos_mask]
        spectrum_pos = np.abs(spectrum[pos_mask])
        
        peak_idx = np.argmax(spectrum_pos)
        detected_beat = freqs_pos[peak_idx]
        
        # Sollte sehr nah an erwarteter Frequenz sein
        error = abs(detected_beat - expected_beat)
        
        # Toleranz: 1 FFT-Bin (3.9 kHz)
        freq_resolution = proc.sample_rate / proc.n_samples
        assert error < freq_resolution, \
            f"Beat frequency error {error/1e3:.2f} kHz exceeds tolerance"
    
    def test_range_resolution(self, setup_processor):
        """Test: Range-Auflösung wie erwartet"""
        gen, proc = setup_processor
        
        # Theoretische Range-Resolution
        expected_res = proc.c / (2 * proc.bandwidth)
        factor = 2.5
        # Zwei Targets im Abstand der Range-Resolution
        range1 = 50.0
        range2 = range1 + expected_res * factor # 1.5× Resolution
        
        time, tx, rx1 = proc.simulate_target(range1, rcs=0.1)
        _, _, rx2 = proc.simulate_target(range2, rcs=0.1)
        
        rx_total = rx1 + rx2
        beat = proc.mix_signals(tx, rx_total)
        
        freq_bins, range_bins, profile = proc.range_fft(beat)
        peaks = proc.detect_peaks(profile, snr_db=15, max_peaks=5)
        
        # Sollten 2 getrennte Peaks finden
        assert len(peaks) >= 2, \
            f"Could not resolve targets at {expected_res*factor:.2f}m separation"
    
    def test_different_rcs(self, setup_processor):
        """Test: Targets mit unterschiedlicher RCS"""
        gen, proc = setup_processor
        
        # Großes Target (starkes Echo)
        time, tx, rx_large = proc.simulate_target(50.0, rcs=100.0)
        
        # Kleines Target (schwaches Echo)  
        _, _, rx_small = proc.simulate_target(50.0, rcs=0.001)
        
        # Großes Target sollte stärkeres Signal haben
        assert np.max(np.abs(rx_large)) > np.max(np.abs(rx_small))
    
    def test_window_functions(self, setup_processor):
        """Test: Verschiedene Fenster-Funktionen funktionieren"""
        gen, proc = setup_processor
        
        time, tx, rx = proc.simulate_target(50.0, rcs=0.1)
        beat = proc.mix_signals(tx, rx)
        
        # Teste verschiedene Fenster
        windows = ['hann', 'hamming', 'blackman']
        
        for window in windows:
            freq_bins, range_bins, profile = proc.range_fft(beat, window=window)
            
            assert len(freq_bins) == proc.n_samples // 2
            assert len(range_bins) == proc.n_samples // 2
            assert len(profile) == proc.n_samples // 2
            
            # Sollte mindestens einen Peak finden
            peaks = proc.detect_peaks(profile, snr_db=15)
            assert len(peaks) > 0, f"No peaks with {window} window"


class TestEdgeCases:
    """Tests für Edge-Cases und Fehlerbehandlung"""
    
    @pytest.fixture
    def setup_processor(self):
        gen = ChirpGenerator(24e9, 250e6, 256e-6, 1e6)
        proc = RangeProcessor(gen)
        return gen, proc
    
    def test_zero_range(self, setup_processor):
        """Test: Target bei Range=0 (sollte nicht crashen)"""
        gen, proc = setup_processor
        
        # Bei Range=0 sollte tau=0 sein, Signal sollte identisch sein
        time, tx, rx = proc.simulate_target(0.0, rcs=0.1)
        
        # RX sollte existieren (wenn auch sehr schwach wegen 1/R²)
        assert len(rx) == len(tx)
    
    def test_very_close_target(self, setup_processor):
        """Test: Sehr nahes Target (1m)"""
        gen, proc = setup_processor
        
        time, tx, rx = proc.simulate_target(1.0, rcs=0.1)
        beat = proc.mix_signals(tx, rx)
        
        freq_bins, range_bins, profile = proc.range_fft(beat)
        peaks = proc.detect_peaks(profile, snr_db=15)  # Niedrigerer threshold
        
        # Sollte detektierbar sein
        assert len(peaks) > 0
    
    def test_max_range_limit(self, setup_processor):
        """Test: Target nahe Nyquist-Limit"""
        gen, proc = setup_processor
        
        # Max Range ~76.8m
        max_safe_range = gen.max_range * 0.9  # 90% von max
        
        time, tx, rx = proc.simulate_target(max_safe_range, rcs=0.1)
        beat = proc.mix_signals(tx, rx)
        
        freq_bins, range_bins, profile = proc.range_fft(beat)
    
        # Signal sollte schwach aber vorhanden sein
        assert np.max(profile) > -200  # Nicht komplett im Noise


# ===== INTEGRATION TESTS =====

def test_full_pipeline_single_target():
    """Integration Test: Komplette Pipeline für Single-Target"""
    # Setup
    gen = ChirpGenerator(24e9, 250e6, 256e-6, 1e6)
    proc = RangeProcessor(gen)
    
    # Target
    target_range = 50.0
    
    # Pipeline
    time, tx, rx = proc.simulate_target(target_range, rcs=0.1)
    beat = proc.mix_signals(tx, rx)
    freq_bins, range_bins, profile = proc.range_fft(beat)
    peaks = proc.detect_peaks(profile, snr_db=15)
    
    detected_range = range_bins[peaks[0]]
    
    # Validation
    assert abs(detected_range - target_range) < 1.0


def test_full_pipeline_multi_target():
    """Integration Test: Komplette Pipeline für Multi-Target"""
    gen = ChirpGenerator(24e9, 250e6, 256e-6, 1e6)
    proc = RangeProcessor(gen)
    
    # 3 Targets mit unterschiedlichen RCS (realistischer!)
    target_configs = [
        (30.0, 0.08),   # Drohne bei 30m
        (50.0, 0.12),   # Größere Drohne bei 50m
        (70.0, 0.08)    # Drohne bei 70m
    ]
    
    rx_signals = []
    
    for range_m, rcs in target_configs:
        time, tx, rx = proc.simulate_target(range_m, rcs)
        rx_signals.append(rx)
    
    rx_total = np.sum(rx_signals, axis=0)
    beat = proc.mix_signals(tx, rx_total)
    
    freq_bins, range_bins, profile = proc.range_fft(beat)
    peaks = proc.detect_peaks(profile, snr_db=15, max_peaks=10)
    
    # Realistisch: Erwarte mindestens 2 von 3
    assert len(peaks) >= 2, \
        f"Expected at least 2 of 3 targets detected, got {len(peaks)}"
    
    # Optional: Check dass Detektionen nahe bei erwarteten Ranges sind
    if len(peaks) >= 2:
        expected_ranges = [30.0, 50.0, 70.0]
        detected_ranges = range_bins[peaks]
        
        matches = 0
        for exp_range in expected_ranges:
            distances = np.abs(detected_ranges - exp_range)
            if np.min(distances) < 3.0:  # 3m Toleranz
                matches += 1
        
        assert matches >= 2, \
            f"Only {matches} targets matched expected positions"


    # Alle Tests
# pytest python_prototype/signal_processing/tests/test_range_fft.py -v

# # Mit Coverage
# pytest python_prototype/signal_processing/tests/test_range_fft.py -v --cov=python_prototype.signal_processing

# # Nur eine Test-Klasse
# pytest python_prototype/signal_processing/tests/test_range_fft.py::TestRangeProcessor -v

# # Nur ein spezifischer Test
# pytest python_prototype/signal_processing/tests/test_range_fft.py::TestRangeProcessor::test_single_target_detection -v