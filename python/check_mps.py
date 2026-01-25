#!/usr/bin/env python3
"""
Quick diagnostic script to check MPS (Metal Performance Shaders) availability on Apple Silicon.
"""
import sys

print("=" * 60)
print("MPS Availability Diagnostic")
print("=" * 60)

# Check Python version
print(f"\nPython version: {sys.version}")

# Check PyTorch
try:
    import torch
    print(f"\nPyTorch version: {torch.__version__}")
    print(f"PyTorch file location: {torch.__file__}")

    # Check MPS availability
    print("\n--- MPS Backend Check ---")
    print(f"MPS built: {torch.backends.mps.is_built()}")
    print(f"MPS available: {torch.backends.mps.is_available()}")

    # Check device
    if torch.backends.mps.is_available():
        print("\n✅ MPS is available and ready to use!")
        try:
            # Try to create a tensor on MPS
            device = torch.device("mps")
            test_tensor = torch.ones(1, device=device)
            print(f"✅ Successfully created tensor on MPS device")
        except Exception as e:
            print(f"❌ Error creating tensor on MPS: {e}")
    else:
        print("\n❌ MPS is NOT available")
        if not torch.backends.mps.is_built():
            print("   Reason: MPS backend not built into PyTorch")
            print("   Solution: Reinstall PyTorch with MPS support")
        else:
            print("   Reason: Unknown - MPS should work on M1 Pro")

    # Check other backends
    print("\n--- Other Backends ---")
    print(f"CUDA available: {torch.cuda.is_available()}")

except ImportError as e:
    print(f"\n❌ PyTorch not installed: {e}")
    print("   Install with: pip install torch")

# Check sentence-transformers
try:
    import sentence_transformers
    print(f"\nsentence-transformers version: {sentence_transformers.__version__}")
except ImportError:
    print("\n❌ sentence-transformers not installed")

print("\n" + "=" * 60)
print("Recommended Actions:")
print("=" * 60)

try:
    import torch
    if not torch.backends.mps.is_available():
        if not torch.backends.mps.is_built():
            print("\n1. Reinstall PyTorch with MPS support:")
            print("   pip uninstall torch")
            print("   pip install torch torchvision torchaudio")
        else:
            print("\n1. Update PyTorch to latest version:")
            print("   pip install --upgrade torch")
    else:
        print("\n✅ Everything looks good! MPS should work.")
except:
    print("\n1. Install PyTorch:")
    print("   pip install torch torchvision torchaudio")

print("\n" + "=" * 60)
