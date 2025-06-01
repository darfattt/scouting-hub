#!/usr/bin/env python3
"""
Test script to verify that the model change from deepseek-r1:8b to phi3:mini is working correctly.
"""

import os
import sys
import subprocess

# Add src directory to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

# Change to project root directory
os.chdir(project_root)

def check_ollama_models():
    """Check if required models are available in Ollama."""
    print("🔍 CHECKING OLLAMA MODELS")
    print("-" * 50)
    
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Ollama is running")
            print("\nAvailable models:")
            print(result.stdout)
            
            # Check for required models
            has_phi3 = 'phi3:mini' in result.stdout
            has_nomic = 'nomic-embed-text' in result.stdout
            
            print(f"\nModel availability:")
            if has_phi3:
                print("✅ phi3:mini model available")
            else:
                print("❌ phi3:mini model not found")
                print("   Run: ollama pull phi3:mini")
            
            if has_nomic:
                print("✅ nomic-embed-text model available")
            else:
                print("❌ nomic-embed-text model not found")
                print("   Run: ollama pull nomic-embed-text")
            
            return has_phi3 and has_nomic
        else:
            print("❌ Ollama not responding")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False

def test_rag_initialization():
    """Test that RAG systems initialize with phi3:mini model."""
    print("\n🔍 TESTING RAG INITIALIZATION")
    print("-" * 50)
    
    try:
        # Test GoalkeeperRAG
        from core.rag_system import GoalkeeperRAG
        gk_rag = GoalkeeperRAG()
        
        if gk_rag.model_name == "phi3:mini":
            print("✅ GoalkeeperRAG uses phi3:mini")
        else:
            print(f"❌ GoalkeeperRAG uses {gk_rag.model_name} (expected phi3:mini)")
            return False
        
        # Test OutfieldRAG
        from core.rag_system import OutfieldRAG
        outfield_rag = OutfieldRAG()
        
        if outfield_rag.model_name == "phi3:mini":
            print("✅ OutfieldRAG uses phi3:mini")
        else:
            print(f"❌ OutfieldRAG uses {outfield_rag.model_name} (expected phi3:mini)")
            return False
        
        # Test ForwardRAG
        from core.rag_system import ForwardRAG
        forward_rag = ForwardRAG()
        
        if forward_rag.model_name == "phi3:mini":
            print("✅ ForwardRAG uses phi3:mini")
        else:
            print(f"❌ ForwardRAG uses {forward_rag.model_name} (expected phi3:mini)")
            return False
        
        # Test MidfielderRAG
        from core.rag_system import MidfielderRAG
        midfielder_rag = MidfielderRAG()
        
        if midfielder_rag.model_name == "phi3:mini":
            print("✅ MidfielderRAG uses phi3:mini")
        else:
            print(f"❌ MidfielderRAG uses {midfielder_rag.model_name} (expected phi3:mini)")
            return False
        
        # Test DefenderRAG
        from core.rag_system import DefenderRAG
        defender_rag = DefenderRAG()
        
        if defender_rag.model_name == "phi3:mini":
            print("✅ DefenderRAG uses phi3:mini")
        else:
            print(f"❌ DefenderRAG uses {defender_rag.model_name} (expected phi3:mini)")
            return False
        
        print("\n✅ All RAG systems correctly use phi3:mini model")
        return True
        
    except Exception as e:
        print(f"❌ Error testing RAG initialization: {e}")
        return False

def test_custom_model_override():
    """Test that custom model specification still works."""
    print("\n🔍 TESTING CUSTOM MODEL OVERRIDE")
    print("-" * 50)
    
    try:
        from core.rag_system import GoalkeeperRAG
        
        # Test custom model specification
        custom_rag = GoalkeeperRAG(model_name="custom-model:test")
        
        if custom_rag.model_name == "custom-model:test":
            print("✅ Custom model override works correctly")
            return True
        else:
            print(f"❌ Custom model override failed: got {custom_rag.model_name}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing custom model override: {e}")
        return False

def main():
    """Main test function."""
    print("=" * 80)
    print("PHI3:MINI MODEL CHANGE VERIFICATION")
    print("=" * 80)
    print("Testing the change from deepseek-r1:8b to phi3:mini")
    print()
    
    # Test 1: Check Ollama models
    models_available = check_ollama_models()
    
    # Test 2: Test RAG initialization
    rag_test_passed = test_rag_initialization()
    
    # Test 3: Test custom model override
    override_test_passed = test_custom_model_override()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    all_tests_passed = models_available and rag_test_passed and override_test_passed
    
    if models_available:
        print("✅ Ollama models: Available")
    else:
        print("❌ Ollama models: Missing")
        print("   Run: ollama pull phi3:mini")
        print("   Run: ollama pull nomic-embed-text")
    
    if rag_test_passed:
        print("✅ RAG initialization: Correct")
    else:
        print("❌ RAG initialization: Failed")
    
    if override_test_passed:
        print("✅ Custom model override: Working")
    else:
        print("❌ Custom model override: Failed")
    
    print()
    
    if all_tests_passed:
        print("🎉 SUCCESS! Model change to phi3:mini is working correctly.")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Test AI Assistant functionality")
        print("3. Verify responses are generated correctly")
    else:
        print("💥 FAILED! Some tests did not pass.")
        print("\nPlease fix the issues above before proceeding.")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
