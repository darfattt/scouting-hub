#!/usr/bin/env python3
"""
Setup Ollama Models
Script to download required models for the RAG system.
"""

import os
import subprocess
import sys
from datetime import datetime

# Add src directory to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

# Change to project root directory
os.chdir(project_root)

def run_command(command, description):
    """Run a command and return success status."""
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            print("✓ Success")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print("✗ Failed")
            if result.stderr.strip():
                print(f"Error: {result.stderr.strip()}")
            return False

    except subprocess.TimeoutExpired:
        print("✗ Command timed out (5 minutes)")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def check_ollama():
    """Check if Ollama is available."""
    print("Checking Ollama availability...")

    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✓ Ollama is available: {result.stdout.strip()}")
            return True
        else:
            print("✗ Ollama command failed")
            return False
    except FileNotFoundError:
        print("✗ Ollama not found in PATH")
        print("Please install Ollama from: https://ollama.ai/")
        return False
    except Exception as e:
        print(f"✗ Error checking Ollama: {e}")
        return False

def pull_models():
    """Pull required models."""
    models = [
        ("phi3:mini", "Phi-3 Mini - Main reasoning model"),
        ("nomic-embed-text", "Nomic Embed Text - Embedding model")
    ]

    results = {}

    for model, description in models:
        print(f"\n{'='*60}")
        print(f"PULLING MODEL: {model}")
        print(f"Description: {description}")
        print(f"{'='*60}")

        success = run_command(['ollama', 'pull', model], f"Downloading {model}")
        results[model] = success

        if success:
            print(f"✓ {model} downloaded successfully")
        else:
            print(f"✗ Failed to download {model}")

    return results

def verify_models():
    """Verify that models are available."""
    print(f"\n{'='*60}")
    print("VERIFYING MODELS")
    print(f"{'='*60}")

    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("Available models:")
            print(result.stdout)

            # Check for required models
            required_models = ['phi3:mini', 'nomic-embed-text']
            available_models = result.stdout

            verification_results = {}
            for model in required_models:
                if model in available_models:
                    print(f"✓ {model} is available")
                    verification_results[model] = True
                else:
                    print(f"✗ {model} is not available")
                    verification_results[model] = False

            return verification_results
        else:
            print("✗ Failed to list models")
            return {}

    except Exception as e:
        print(f"✗ Error verifying models: {e}")
        return {}

def main():
    print("=" * 60)
    print("OLLAMA MODELS SETUP")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    print("This script will download the required models for the RAG system:")
    print("1. phi3:mini - Main reasoning model (~2.3GB)")
    print("2. nomic-embed-text - Embedding model (~274MB)")
    print()
    print("Note: This may take 10-30 minutes depending on your internet speed.")
    print()

    # Check Ollama
    if not check_ollama():
        print("\n❌ Ollama is not available. Please install it first.")
        return False

    # Ask for confirmation
    response = input("Continue with model download? (y/N): ").lower()
    if not response.startswith('y'):
        print("Setup cancelled.")
        return False

    # Pull models
    print(f"\n{'='*60}")
    print("DOWNLOADING MODELS")
    print(f"{'='*60}")

    pull_results = pull_models()

    # Verify models
    verification_results = verify_models()

    # Summary
    print(f"\n{'='*60}")
    print("SETUP SUMMARY")
    print(f"{'='*60}")

    all_success = True

    for model in ['phi3:mini', 'nomic-embed-text']:
        pull_status = "✓" if pull_results.get(model, False) else "✗"
        verify_status = "✓" if verification_results.get(model, False) else "✗"

        print(f"{model}:")
        print(f"  Download: {pull_status}")
        print(f"  Available: {verify_status}")

        if not (pull_results.get(model, False) and verification_results.get(model, False)):
            all_success = False

    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if all_success:
        print("\n🎉 SUCCESS! All models are ready.")
        print("\nNext steps:")
        print("1. Run: python check_setup.py")
        print("2. Run: python build_goalkeeper_rag.py")
        print("3. Run: streamlit run app.py")
    else:
        print("\n❌ SETUP INCOMPLETE!")
        print("\nSome models failed to download. Please:")
        print("1. Check your internet connection")
        print("2. Ensure Ollama is running properly")
        print("3. Try running the failed commands manually:")

        for model in ['phi3:mini', 'nomic-embed-text']:
            if not pull_results.get(model, False):
                print(f"   ollama pull {model}")

    return all_success

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    input("\nPress Enter to exit...")
