#!/usr/bin/env python3
"""
Test script to verify Unicode encoding fix
Tests that Unicode characters (✓, ✗, ℹ, ⚠) display correctly on Windows
"""

import sys
import os

def test_unicode_characters():
    """Test various Unicode characters used in the project"""
    
    print("Testing Unicode character display...")
    print("=" * 50)
    
    # Test characters commonly used in the project
    test_chars = {
        "Check mark": "✓",
        "Cross mark": "✗", 
        "Info symbol": "ℹ",
        "Warning symbol": "⚠",
        "Arrow right": "→",
        "Arrow left": "←",
        "Arrow up": "↑",
        "Arrow down": "↓",
        "Bullet": "•",
        "Degree": "°",
        "Plus/minus": "±",
        "Infinity": "∞",
        "Sum": "∑",
        "Square root": "√",
        "Pi": "π",
    }
    
    print("Unicode Character Test:")
    print("-" * 30)
    
    for name, char in test_chars.items():
        try:
            print(f"{name:15}: {char}")
        except UnicodeEncodeError as e:
            print(f"{name:15}: ERROR - {e}")
            return False
    
    print("-" * 30)
    print("All Unicode characters displayed successfully! ✓")
    
    # Test encoding info
    print("\nEncoding Information:")
    print("-" * 30)
    print(f"Default encoding: {sys.getdefaultencoding()}")
    print(f"File system encoding: {sys.getfilesystemencoding()}")
    print(f"stdout encoding: {sys.stdout.encoding}")
    print(f"stderr encoding: {sys.stderr.encoding}")
    print(f"PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', 'Not set')}")
    print(f"PYTHONUTF8: {os.environ.get('PYTHONUTF8', 'Not set')}")
    
    return True

def test_string_operations():
    """Test string operations with Unicode characters"""
    
    print("\nString Operations Test:")
    print("-" * 30)
    
    test_strings = [
        "Status: ✓ Complete",
        "Error: ✗ Failed", 
        "Info: ℹ Processing",
        "Warning: ⚠ Attention",
        "Math: ∑(i=1→n) i = n(n+1)/2",
        "Temperature: 23°C ± 2°C",
    ]
    
    for s in test_strings:
        try:
            print(f"✓ {s}")
            # Test length calculation
            length = len(s)
            print(f"  Length: {length} characters")
        except UnicodeEncodeError as e:
            print(f"✗ Error with '{s}': {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("Unicode Encoding Test Script")
    print("=" * 50)
    
    success = True
    success &= test_unicode_characters()
    success &= test_string_operations()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Unicode encoding is working correctly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Unicode encoding needs attention.")
        sys.exit(1)