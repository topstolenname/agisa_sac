#!/usr/bin/env python3
"""Simple test to verify Poetry environment is working."""

import sys
import subprocess

def test_basic_imports():
    """Test that basic Python packages are available."""
    try:
        import numpy
        print("✅ numpy available")
    except ImportError:
        print("❌ numpy not available")
        return False
    
    try:
        import scipy
        print("✅ scipy available")
    except ImportError:
        print("❌ scipy not available")
        return False
    
    try:
        import networkx
        print("✅ networkx available")
    except ImportError:
        print("❌ networkx not available")
        return False
    
    return True

def test_poetry_environment():
    """Test that we're in a Poetry environment."""
    try:
        result = subprocess.run(['poetry', '--version'], 
                              capture_output=True, text=True, cwd='/home/tristanj/agisa_sac')
        if result.returncode == 0:
            print(f"✅ Poetry available: {result.stdout.strip()}")
            return True
        else:
            print("❌ Poetry not available")
            return False
    except Exception as e:
        print(f"❌ Error checking Poetry: {e}")
        return False

def main():
    print("🧪 Testing Poetry setup for AGI-SAC...")
    print("=" * 50)
    
    # Test Poetry environment
    poetry_ok = test_poetry_environment()
    
    # Test basic imports
    imports_ok = test_basic_imports()
    
    print("\n" + "=" * 50)
    if poetry_ok and imports_ok:
        print("🎉 Poetry setup appears to be working!")
        print("\nNext steps:")
        print("1. Install the package: poetry install")
        print("2. Test the CLI: poetry run agisa-sac --help")
        print("3. Run a simulation: poetry run agisa-sac run --preset quick_test")
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())