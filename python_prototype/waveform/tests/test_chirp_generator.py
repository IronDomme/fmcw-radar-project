import numpy as np
import pytest
from python_prototype.waveform.chirp_generator import ChirpGenerator  


def test_chirp_duration():
    """Test: Chirp hat richtige Länge"""
    gen = ChirpGenerator(f_start=24e9, bandwidth=200e6,
                        chirp_duration=100e-6, sample_rate=500e6)
    time, signal, phase = gen.generate_chirp()
      
     # Prüfung 1: Letzter Zeitpunkt ≈ chirp_duration
    expected_duration = gen.chirp_duration
    actual_duration = time[-1]
    
    assert np.isclose(actual_duration, expected_duration), \
        f"Expected duration {expected_duration}, but got {actual_duration}"

    # Prüfung 2: Anzahl Samples korrekt
    expected_signal_length=gen.sample_rate * gen.chirp_duration
    actual_signal_length=len(signal) 
    assert expected_signal_length == actual_signal_length, \
        f"Expected length {expected_signal_length}, but got actual length of {actual_signal_length}"
    
    

def test_frequency_sweep():
    """Test: Frequenz steigt linear von f_start bis f_stop"""
    gen = ChirpGenerator(f_start=24e9, bandwidth=200e6,
                        chirp_duration=100e-6, sample_rate=500e6)
    
    time, signal, phase = gen.generate_chirp()
    
    # TODO: Berechne instantane Frequenz mit np.diff(phase)
    # TODO: Prüfe, dass freq[0] ≈ f_start und freq[-1] ≈ f_stop
    
    # Nummerische Bestimmung der Instantan Frequenz = (1/2π) * d(phase)/dt
   
    ft=np.diff(phase)/(2*np.pi*np.diff(time))

    assert np.isclose(ft[0], gen.f_start, rtol=1e10), \
        f"instantanoues frequency at time index zero {ft[0]} differs from f_start{gen.f_start}"
    
    f_stop=gen.f_start+gen.bandwidth
    assert np.isclose(ft[-1], f_stop, rtol=1e10), \
        f"instantanoues frequency at last time index zero {ft[-1]} differs from f_stop{f_stop}"
    
   

def test_signal_amplitude():
    """Test: Signal ist normalisiert (-1 bis +1)"""
    # TODO: Prüfe np.max(signal) ≈ 1 und np.min(signal) ≈ -1
    gen = ChirpGenerator(f_start=24e9, bandwidth=200e6,
                        chirp_duration=100e-6, sample_rate=500e6)
    time, signal, phase = gen.generate_chirp()

     # Maximalwert ≈ 1
    assert np.isclose(np.max(signal), 1.0, atol=0.01), \
        f"Max amplitude {np.max(signal)} should be close to 1.0"
    
    # Minimalwert ≈ -1
    assert np.isclose(np.min(signal), -1.0, atol=0.01), \
        f"Min amplitude {np.min(signal)} should be close to -1.0"
    
    # Keine Werte außerhalb [-1, 1]
    assert np.all(np.abs(signal) <= 1.0), \
        "Signal contains values outside [-1, 1]"

    



