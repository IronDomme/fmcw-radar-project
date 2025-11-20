# FMCW Radar Signal Processing

A comprehensive FMCW (Frequency-Modulated Continuous Wave) radar signal processing framework with Python prototyping and C++ embedded implementation for real-time applications.

## Overview

This project implements a complete FMCW radar signal processing pipeline, from chirp generation to target detection, tracking, and classification. It includes both a Python prototype for algorithm development and validation, and a C++ implementation optimized for embedded systems (Raspberry Pi).

## Features

- **Waveform Generation**: Configurable FMCW chirp signal generation
- **Range Processing**: FFT-based range estimation
- **Doppler Processing**: Velocity estimation through Doppler FFT
- **CFAR Detection**: Constant False Alarm Rate target detection
- **Tracking**: Kalman filter-based multi-target tracking
- **Classification**: Micro-Doppler signature analysis and ML-based classification
- **Hardware Integration**: Real-time processing with Hardware

## Project Structure

```
fmcw-radar-project/
├── README.md                          # Project overview
├── requirements.txt                   # Python dependencies
├── docs/                              # Documentation
│   ├── theory/                        # Theoretical foundations
│   └── notebooks/                     # Jupyter notebooks
├── python_prototype/                  # Python implementation
│   ├── waveform/                      # Chirp generation
│   ├── signal_processing/             # Range/Doppler FFT
│   ├── detection/                     # CFAR detection
│   ├── tracking/                      # Kalman filtering
│   ├── classification/                # ML classification
│   ├── visualization/                 # Plotting utilities
│   └── utils/                         # Helper functions
├── cpp_embedded/                      # C++ implementation for Raspberry Pi
│   ├── src/                           # Source files
│   ├── include/                       # Header files
│   └── tests/                         # Unit tests
├── hardware_integration/              # HackRF One integration
│   ├── capture.py                     # Data acquisition
│   ├── realtime_processing.py         # Real-time pipeline
│   └── config/                        # Configuration files
├── data/                              # Test data
│   ├── simulated/                     # Simulated scenarios
│   └── recorded/                      # Real hardware recordings
└── examples/                          # Demo scripts
    ├── simple_range_demo.py
    ├── doppler_demo.py
    └── full_pipeline_demo.py
```
### System Limitations

**Single-Channel Mixing (No IQ-Sampling):**
- This implementation uses real-valued mixing for simplicity
- Consequence: Cannot determine target direction (approaching vs. receding)
- Doppler frequency magnitude is measured, but sign is ambiguous
- Real-world systems use I/Q sampling for full directional information

**Why this choice:**
- Focus on core DSP concepts (Range-FFT, Doppler-FFT, 2D processing)
- Reduced simulation complexity for educational purposes
- I/Q extension possible as future enhancement

**Doppler Information Source:**
Despite no IQ-sampling, Doppler is detected through:
- Phase progression between consecutive chirps
- Complex FFT outputs preserve phase information
- Doppler-FFT on complex range-data reveals velocity


## Installation

### Python Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/fmcw-radar-project.git
cd fmcw-radar-project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### C++ Build (Raspberry Pi)

```bash
cd cpp_embedded
mkdir build && cd build
cmake ..
make
```

## Quick Start

### Basic Range Detection

```python
from python_prototype.waveform.chirp_generator import ChirpGenerator
from python_prototype.signal_processing.range_fft import RangeFFT

# Generate chirp
chirp_gen = ChirpGenerator(f_start=24e9, bandwidth=200e6, T_chirp=100e-6, fs=10e6)
chirp = chirp_gen.generate_chirp()

# Process range
range_proc = RangeFFT(chirp_gen.params)
range_profile = range_proc.process(chirp)
```

### Run Examples

```bash
# Simple range estimation
python examples/simple_range_demo.py

# Doppler processing
python examples/doppler_demo.py

# Full processing pipeline
python examples/full_pipeline_demo.py
```


## Development Roadmap

- [x] Module 1: Chirp generation and validation
- [x] Module 2: Range FFT processing
- [ ] Module 3: Doppler FFT processing
- [ ] Module 4: CFAR detection
- [ ] Module 5: Kalman filter tracking
- [ ] Module 6: Micro-Doppler classification
- [ ] Hardware integration and real-time processing

## Documentation

Detailed documentation is available in the `docs/` directory:

- [FMCW Basics](docs/theory/01_Chirp%20Basics.md)
- [Range Processing](docs/theory/02_RangeFFT.md)
- Interactive Jupyter notebooks in `docs/notebooks/`

## Testing

```bash
# Run all tests
pytest

# Run specific module tests
pytest python_prototype/waveform/tests/

# With coverage
pytest --cov=python_prototype
```

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on FMCW radar theory and modern signal processing techniques
- Developed for educational and research purposes

## Contact

For questions and support, please open an issue on GitHub.
