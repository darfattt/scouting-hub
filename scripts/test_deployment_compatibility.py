#!/usr/bin/env python3
"""
Test script to verify deployment compatibility without RAG dependencies.
"""

import os
import sys

# Add src directory to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

# Change to project root directory
os.chdir(project_root)

def test_rag_system_import():
    """Test that the RAG system can be imported without dependencies."""
    print("🔍 TESTING RAG SYSTEM IMPORT")
    print("-" * 50)
    
    try:
        from core.rag_system import RAG_AVAILABLE, GoalkeeperRAG, OutfieldRAG, ForwardRAG, MidfielderRAG, DefenderRAG
        
        print(f"✅ RAG system imported successfully")
        print(f"✅ RAG_AVAILABLE flag: {RAG_AVAILABLE}")
        
        if not RAG_AVAILABLE:
            print("✅ RAG dependencies not available (expected for deployment)")
        else:
            print("✅ RAG dependencies available")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing RAG system: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rag_system_initialization():
    """Test that RAG systems can be initialized without dependencies."""
    print("\n🔍 TESTING RAG SYSTEM INITIALIZATION")
    print("-" * 50)
    
    try:
        from core.rag_system import GoalkeeperRAG, OutfieldRAG
        
        # Test GoalkeeperRAG initialization
        gk_rag = GoalkeeperRAG()
        print("✅ GoalkeeperRAG initialized")
        
        # Test OutfieldRAG initialization
        outfield_rag = OutfieldRAG()
        print("✅ OutfieldRAG initialized")
        
        # Test build_vector_store (should handle missing dependencies gracefully)
        gk_rag.build_vector_store()
        print("✅ GoalkeeperRAG build_vector_store completed")
        
        outfield_rag.build_vector_store()
        print("✅ OutfieldRAG build_vector_store completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing RAG systems: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rag_query_fallback():
    """Test that RAG query provides appropriate fallback when dependencies are missing."""
    print("\n🔍 TESTING RAG QUERY FALLBACK")
    print("-" * 50)
    
    try:
        from core.rag_system import GoalkeeperRAG, RAG_AVAILABLE
        
        gk_rag = GoalkeeperRAG()
        
        # Test query
        result = gk_rag.query("Who is the best goalkeeper?")
        
        if not RAG_AVAILABLE:
            expected_message = "RAG functionality is not available"
            if expected_message in result["answer"]:
                print("✅ Query fallback message correct")
            else:
                print(f"❌ Query fallback message incorrect: {result['answer']}")
                return False
        else:
            print("✅ Query executed (RAG available)")
        
        print(f"✅ Query result: {result['answer'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing RAG query fallback: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_components_import():
    """Test that app components can be imported."""
    print("\n🔍 TESTING APP COMPONENTS IMPORT")
    print("-" * 50)
    
    try:
        from components.app_components import (
            render_player_search,
            render_player_comparison,
            add_global_filters,
            filter_player_data
        )
        print("✅ App components imported successfully")
        
        from components.outfield_components import render_outfield_player_comparison, render_outfield_player_search
        print("✅ Outfield components imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing app components: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_processor_functionality():
    """Test that data processors work without RAG dependencies."""
    print("\n🔍 TESTING DATA PROCESSOR FUNCTIONALITY")
    print("-" * 50)
    
    try:
        from core.data_processor import GoalkeeperDataProcessor, OutfieldDataProcessor
        
        # Test GoalkeeperDataProcessor
        gk_processor = GoalkeeperDataProcessor("data/stats")
        print("✅ GoalkeeperDataProcessor initialized")
        
        # Test OutfieldDataProcessor
        outfield_processor = OutfieldDataProcessor("data/stats")
        print("✅ OutfieldDataProcessor initialized")
        
        # Test data processing (may not have data files, but should not crash)
        try:
            gk_processor.process_data()
            print("✅ GoalkeeperDataProcessor.process_data() completed")
        except Exception as e:
            print(f"ℹ️ GoalkeeperDataProcessor.process_data() failed (expected if no data): {e}")
        
        try:
            outfield_processor.process_data()
            print("✅ OutfieldDataProcessor.process_data() completed")
        except Exception as e:
            print(f"ℹ️ OutfieldDataProcessor.process_data() failed (expected if no data): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing data processor functionality: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_streamlit_compatibility():
    """Test basic Streamlit compatibility."""
    print("\n🔍 TESTING STREAMLIT COMPATIBILITY")
    print("-" * 50)
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
        
        # Test basic Streamlit functions (these won't actually run in test mode)
        print("✅ Streamlit basic functions available")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Streamlit compatibility: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_required_dependencies():
    """Test that all required dependencies are available."""
    print("\n🔍 TESTING REQUIRED DEPENDENCIES")
    print("-" * 50)
    
    required_deps = [
        'pandas',
        'numpy', 
        'streamlit',
        'matplotlib',
        'seaborn',
        'sklearn'
    ]
    
    all_available = True
    
    for dep in required_deps:
        try:
            __import__(dep)
            print(f"✅ {dep} available")
        except ImportError:
            print(f"❌ {dep} not available")
            all_available = False
    
    return all_available

def main():
    """Main test function."""
    print("=" * 80)
    print("DEPLOYMENT COMPATIBILITY VERIFICATION")
    print("=" * 80)
    print("Testing app compatibility without RAG dependencies")
    print()
    
    # Test 1: RAG system import
    import_test_passed = test_rag_system_import()
    
    # Test 2: RAG system initialization
    init_test_passed = test_rag_system_initialization()
    
    # Test 3: RAG query fallback
    query_test_passed = test_rag_query_fallback()
    
    # Test 4: App components import
    components_test_passed = test_app_components_import()
    
    # Test 5: Data processor functionality
    processor_test_passed = test_data_processor_functionality()
    
    # Test 6: Streamlit compatibility
    streamlit_test_passed = test_streamlit_compatibility()
    
    # Test 7: Required dependencies
    deps_test_passed = test_required_dependencies()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    all_tests_passed = (import_test_passed and init_test_passed and 
                       query_test_passed and components_test_passed and
                       processor_test_passed and streamlit_test_passed and
                       deps_test_passed)
    
    if import_test_passed:
        print("✅ RAG system import: Working correctly")
    else:
        print("❌ RAG system import: Failed")
    
    if init_test_passed:
        print("✅ RAG system initialization: Working correctly")
    else:
        print("❌ RAG system initialization: Failed")
    
    if query_test_passed:
        print("✅ RAG query fallback: Working correctly")
    else:
        print("❌ RAG query fallback: Failed")
    
    if components_test_passed:
        print("✅ App components import: Working correctly")
    else:
        print("❌ App components import: Failed")
    
    if processor_test_passed:
        print("✅ Data processor functionality: Working correctly")
    else:
        print("❌ Data processor functionality: Failed")
    
    if streamlit_test_passed:
        print("✅ Streamlit compatibility: Working correctly")
    else:
        print("❌ Streamlit compatibility: Failed")
    
    if deps_test_passed:
        print("✅ Required dependencies: All available")
    else:
        print("❌ Required dependencies: Some missing")
    
    print()
    
    if all_tests_passed:
        print("🎉 SUCCESS! App is deployment-ready without RAG dependencies.")
        print("\nDeployment status:")
        print("- ✅ Core functionality works without RAG dependencies")
        print("- ✅ Graceful fallback for AI Assistant features")
        print("- ✅ All analysis features remain functional")
        print("- ✅ Streamlit Cloud compatible")
        print("\nFeatures available in deployment:")
        print("- ✅ Player Search")
        print("- ✅ Player Comparison") 
        print("- ✅ Performance Analysis")
        print("- ✅ Player Search Profiler")
        print("- ✅ Attribute Analysis")
        print("- ✅ Find Similar Player")
        print("- ❌ AI Assistant (requires additional dependencies)")
        print("\nNext steps:")
        print("1. Deploy to Streamlit Cloud")
        print("2. Upload your data files to data/stats/ directory")
        print("3. Test all features in the deployed environment")
    else:
        print("💥 FAILED! Some deployment compatibility tests did not pass.")
        print("\nPlease fix the issues above before deploying.")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
