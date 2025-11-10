print("Starting import test...")

try:
    from python_prototype.waveform.chirp_generator import ChirpGenerator
    print("✅ SUCCESS! Import worked!")
    print(f"ChirpGenerator class: {ChirpGenerator}")
except ModuleNotFoundError as e:
    print(f"❌ FAILED! Error: {e}")
    
    import sys
    print("\nPython path:")
    for path in sys.path:
        print(f"  - {path}")