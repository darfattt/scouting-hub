#!/usr/bin/env python3
"""
Check Setup Script
Verifies that everything is ready for building RAG systems.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_packages():
    """Check if required Python packages are installed."""
    print("Checking Python packages...")

    required_packages = [
        'streamlit',
        'pandas',
        'numpy',
        'langchain',
        'langchain-community',
        'faiss-cpu',
        'plotly'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (missing)")
            missing_packages.append(package)

    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False

    return True

def check_ollama():
    """Check if Ollama is running and has the required model."""
    print("\nChecking Ollama...")

    try:
        # Check if ollama command exists
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("  ✓ Ollama is running")

            # Check for required models
            has_deepseek = 'deepseek-r1:8b' in result.stdout
            has_nomic = 'nomic-embed-text' in result.stdout

            if has_deepseek:
                print("  ✓ deepseek-r1:8b model available")
            else:
                print("  ✗ deepseek-r1:8b model not found")
                print("    Run: ollama pull deepseek-r1:8b")

            if has_nomic:
                print("  ✓ nomic-embed-text model available")
            else:
                print("  ✗ nomic-embed-text model not found")
                print("    Run: ollama pull nomic-embed-text")

            return has_deepseek and has_nomic
        else:
            print("  ✗ Ollama not responding")
            return False

    except subprocess.TimeoutExpired:
        print("  ✗ Ollama command timed out")
        return False
    except FileNotFoundError:
        print("  ✗ Ollama not installed or not in PATH")
        return False
    except Exception as e:
        print(f"  ✗ Error checking Ollama: {e}")
        return False

def check_data_files():
    """Check if data files exist."""
    print("\nChecking data files...")

    data_dir = Path("data/stats")

    if not data_dir.exists():
        print(f"  ✗ Data directory not found: {data_dir}")
        print("    Create the directory and add CSV files")
        return False

    csv_files = list(data_dir.glob("*.csv"))

    if not csv_files:
        print(f"  ✗ No CSV files found in {data_dir}")
        print("    Add player statistics CSV files to this directory")
        return False

    print(f"  ✓ Found {len(csv_files)} CSV files")

    # Show sample files
    for i, file in enumerate(csv_files[:5]):
        print(f"    - {file.name}")

    if len(csv_files) > 5:
        print(f"    ... and {len(csv_files) - 5} more")

    return True

def check_project_files():
    """Check if required project files exist."""
    print("\nChecking project files...")

    required_files = [
        'rag_system.py',
        'data_processor.py',
        'app_components.py',
        'app.py'
    ]

    missing_files = []

    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (missing)")
            missing_files.append(file)

    if missing_files:
        print(f"\nMissing files: {', '.join(missing_files)}")
        return False

    return True

def check_vector_stores():
    """Check if vector stores already exist."""
    print("\nChecking existing vector stores...")

    vector_stores = [
        ('vector_store', 'Goalkeepers'),
        ('vector_store_outfield', 'All Outfield'),
        ('vector_store_forwards', 'Forwards'),
        ('vector_store_midfielders', 'Midfielders'),
        ('vector_store_defenders', 'Defenders')
    ]

    existing_stores = []

    for store_path, store_name in vector_stores:
        if os.path.exists(store_path):
            print(f"  ✓ {store_path} ({store_name})")
            existing_stores.append(store_name)
        else:
            print(f"  ✗ {store_path} ({store_name}) - needs to be built")

    if existing_stores:
        print(f"\nExisting vector stores: {', '.join(existing_stores)}")
        print("These can be reused to speed up the build process.")

    return len(existing_stores) > 0

def main():
    print("=" * 60)
    print("SETUP VERIFICATION")
    print("=" * 60)
    print("Checking if everything is ready for building RAG systems...\n")

    checks = [
        ("Python packages", check_python_packages),
        ("Ollama service", check_ollama),
        ("Data files", check_data_files),
        ("Project files", check_project_files)
    ]

    results = {}

    for check_name, check_func in checks:
        results[check_name] = check_func()

    # Check vector stores (informational)
    has_existing_stores = check_vector_stores()

    # Summary
    print("\n" + "=" * 60)
    print("SETUP SUMMARY")
    print("=" * 60)

    all_good = True
    for check_name, result in results.items():
        status = "✓ Ready" if result else "✗ Needs attention"
        print(f"{check_name}: {status}")
        if not result:
            all_good = False

    if has_existing_stores:
        print("Vector stores: ✓ Some already exist")
    else:
        print("Vector stores: ⚠ Need to be built")

    print("\n" + "=" * 60)

    if all_good:
        print("🎉 SETUP COMPLETE!")
        print("\nYou're ready to build RAG systems.")
        print("\nNext steps:")
        print("1. Run: python build_goalkeeper_rag.py")
        print("2. Or run: python build_all_rag.py")
        print("3. Then run: streamlit run app.py")
    else:
        print("❌ SETUP INCOMPLETE!")
        print("\nPlease fix the issues marked with ✗ above.")
        print("\nCommon solutions:")
        print("- Install missing packages: pip install <package_name>")
        print("- Start Ollama: ollama serve")
        print("- Pull model: ollama pull deepseek-r1:8b")
        print("- Add CSV files to data/stats/ directory")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError during setup check: {e}")
        import traceback
        traceback.print_exc()

    input("\nPress Enter to exit...")
