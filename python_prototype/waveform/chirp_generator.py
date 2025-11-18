import numpy as np
from typing import Tuple

class ChirpGenerator:
    """
    FMCW Chirp Signal Generator
    
    Erzeugt linear frequency-modulated continuous wave signals.
    """
    #constructor 
    """
        Initialisiert das Objekt.
        Speichert Parameter als Eigenschaften (self.xxx)
        self.xxx Gilt für die GESAMTE Klasse, in ALLEN Methoden!
        """
    def __init__(self, f_start: float, bandwidth: float, 
                 chirp_duration: float, sample_rate: float):
    
        self.f_start=f_start 
        self.bandwidth=bandwidth
        self.chirp_duration=chirp_duration
        self.sample_rate=sample_rate

        self.f_stop=f_start+bandwidth
        self.chirp_rate=bandwidth/chirp_duration
        self.n_samples = int(sample_rate * chirp_duration)


        speedOfLight=3e8 #m/s
       
        'maxrange is limited by samplerate. Nyquist theorem'
        if sample_rate < bandwidth/2:
            fbeat_max=sample_rate/2
            self.max_range = fbeat_max*speedOfLight*chirp_duration/(2*bandwidth)
        else:
            self.max_range = speedOfLight*chirp_duration/2
            fbeat_max=bandwidth
        self.range_resolution=speedOfLight/(2*bandwidth)
        self.max_velocity=(speedOfLight/f_start) / (4*chirp_duration)

        # ===== KONSOLEN-AUSGABE =====
        print("\n" + "="*60)
        print("FMCW RADAR CHIRP GENERATOR INITIALIZED")
        print("="*60)
        print(f"Frequency Range:    {f_start/1e9:.2f} - {self.f_stop/1e9:.2f} GHz")
        print(f"Bandwidth:          {bandwidth/1e6:.1f} MHz")
        print(f"Chirp Duration:     {chirp_duration*1e6:.1f} µs")
        print(f"Sample Rate:        {sample_rate/1e6:.1f} MHz")
        print(f"Samples per Chirp:  {self.n_samples:,}")
        print("-"*60)
        print("RADAR PERFORMANCE:")
        print(f"Range Resolution:   {self.range_resolution:.2f} m")
        print(f"Max Range:          {self.max_range:.2f} m")
        print(f"Max Velocity:       {self.max_velocity:.2f} m/s ({self.max_velocity*3.6:.1f} km/h)")
        print("="*60 + "\n")
        
    
    def generate_chirp(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
     
        #1. time vector
        t=np.linspace(0, self.chirp_duration, self.n_samples)  

        #2. instantaneous frequency#
        f_t=self.get_instantaneous_frequency(t)

        #3 phase calculation
        phi_t = 2*np.pi*(self.f_start * t + 0.5 * self.chirp_rate * t**2) 

        #4 signal generation
        s_t= np.cos(phi_t) 

        return t, s_t, phi_t


    def get_instantaneous_frequency(self, time: np.ndarray) -> np.ndarray:
        """
        Berechnet die Augenblicks-Frequenz f(t).
        
        f(t) = f_start + chirp_rate * t
        
        Hinweis: Das ist eine lineare Rampe! y=mx+t
        """
        self.f_t = self.f_start + self.chirp_rate * time

        return self.f_t