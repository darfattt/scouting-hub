#!/usr/bin/env python3
"""
Test Fixed RAG System
Test the fixed RAG system to ensure it handles missing outfield data properly.
"""

import os
from datetime import datetime

def test_goalkeeper_rag():
    """Test goalkeeper RAG system."""
    print("Testing GoalkeeperRAG...")
    
    try:
        from rag_system import GoalkeeperRAG
        
        rag = GoalkeeperRAG()
        rag.build_vector_store(force_rebuild=False)
        
        player_count = len(rag.data_processor.player_data)
        print(f"✓ GoalkeeperRAG: {player_count} players loaded")
        
        if player_count > 0:
            # Test query
            result = rag.query("How many goalkeepers are in the dataset?")
            print(f"✓ Query test: {result['answer'][:100]}...")
        
        return True, player_count
        
    except Exception as e:
        print(f"✗ GoalkeeperRAG failed: {e}")
        return False, 0

def test_outfield_rag():
    """Test outfield RAG systems (should handle missing data gracefully)."""
    print("\nTesting OutfieldRAG systems...")
    
    systems = [
        ("OutfieldRAG", "OutfieldRAG"),
        ("ForwardRAG", "ForwardRAG"),
        ("MidfielderRAG", "MidfielderRAG"),
        ("DefenderRAG", "DefenderRAG")
    ]
    
    results = {}
    
    for name, class_name in systems:
        print(f"\nTesting {name}...")
        
        try:
            # Dynamic import
            from rag_system import OutfieldRAG, ForwardRAG, MidfielderRAG, DefenderRAG
            rag_class = globals().get(class_name) or getattr(__import__('rag_system'), class_name)
            
            rag = rag_class()
            rag.build_vector_store(force_rebuild=False)
            
            player_count = len(rag.data_processor.player_data)
            print(f"✓ {name}: {player_count} players loaded")
            
            # Test query
            result = rag.query("How many players are available?")
            print(f"✓ Query response: {result['answer'][:100]}...")
            
            results[name] = player_count
            
        except Exception as e:
            print(f"✗ {name} error: {e}")
            results[name] = -1  # Error indicator
    
    return results

def test_app_initialization():
    """Test if the app can initialize without errors."""
    print("\nTesting app initialization...")
    
    try:
        # Import the app components
        from rag_system import GoalkeeperRAG, OutfieldRAG, ForwardRAG, MidfielderRAG, DefenderRAG
        
        print("✓ All RAG classes imported successfully")
        
        # Test initialization without building vector stores
        systems = {}
        
        # Test goalkeeper
        try:
            systems['Goalkeepers'] = GoalkeeperRAG()
            print("✓ GoalkeeperRAG initialized")
        except Exception as e:
            print(f"✗ GoalkeeperRAG init failed: {e}")
            systems['Goalkeepers'] = None
        
        # Test outfield systems
        outfield_systems = [
            ('All Outfield', OutfieldRAG),
            ('Forwards', ForwardRAG),
            ('Midfielders', MidfielderRAG),
            ('Defenders', DefenderRAG)
        ]
        
        for name, rag_class in outfield_systems:
            try:
                systems[name] = rag_class()
                print(f"✓ {name} initialized")
            except Exception as e:
                print(f"✗ {name} init failed: {e}")
                systems[name] = None
        
        available_systems = [name for name, system in systems.items() if system is not None]
        print(f"✓ Available systems: {available_systems}")
        
        return len(available_systems) > 0
        
    except Exception as e:
        print(f"✗ App initialization failed: {e}")
        return False

def main():
    print("=" * 60)
    print("TESTING FIXED RAG SYSTEM")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("This test verifies that the RAG system handles missing outfield data properly.")
    print()
    
    # Test 1: Goalkeeper RAG
    print("1. GOALKEEPER RAG TEST")
    print("-" * 30)
    gk_success, gk_count = test_goalkeeper_rag()
    
    # Test 2: Outfield RAG systems
    print("\n2. OUTFIELD RAG TESTS")
    print("-" * 30)
    outfield_results = test_outfield_rag()
    
    # Test 3: App initialization
    print("\n3. APP INITIALIZATION TEST")
    print("-" * 30)
    app_success = test_app_initialization()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    print(f"Goalkeeper RAG: {'✓ Success' if gk_success else '✗ Failed'} ({gk_count} players)")
    
    for system, count in outfield_results.items():
        if count == -1:
            status = "✗ Error"
        elif count == 0:
            status = "✓ No data (expected)"
        else:
            status = f"✓ Success ({count} players)"
        print(f"{system}: {status}")
    
    print(f"App initialization: {'✓ Success' if app_success else '✗ Failed'}")
    
    # Check vector stores
    print("\nVector Store Files:")
    vector_stores = [
        ("vector_store", "Goalkeepers"),
        ("vector_store_outfield", "All Outfield"),
        ("vector_store_forwards", "Forwards"),
        ("vector_store_midfielders", "Midfielders"),
        ("vector_store_defenders", "Defenders")
    ]
    
    for vs_path, vs_name in vector_stores:
        exists = "✓" if os.path.exists(vs_path) else "✗"
        print(f"  {exists} {vs_path} ({vs_name})")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if gk_success and app_success:
        print("\n🎉 SUCCESS! The RAG system is working correctly.")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Select 'Goalkeepers' in the position dropdown")
        print("3. Use all features normally")
        
        if all(count <= 0 for count in outfield_results.values() if count != -1):
            print("\n📝 Note: No outfield data found (this is normal).")
            print("   Add outfield player CSV files to enable those features.")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("\nPlease check the error messages above.")
        
        if not gk_success:
            print("- Goalkeeper RAG failed - check your data files and Ollama setup")
        if not app_success:
            print("- App initialization failed - check imports and dependencies")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to exit...")
