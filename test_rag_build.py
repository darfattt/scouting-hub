#!/usr/bin/env python3
"""
Test script to build RAG systems step by step.
This helps debug and monitor the RAG system building process.
"""

import os
import sys
from rag_system import GoalkeeperRAG, ForwardRAG, MidfielderRAG, DefenderRAG, OutfieldRAG

def test_goalkeeper_rag():
    """Test building goalkeeper RAG system."""
    print("=" * 60)
    print("TESTING GOALKEEPER RAG SYSTEM")
    print("=" * 60)
    
    try:
        # Initialize goalkeeper RAG
        print("1. Initializing GoalkeeperRAG...")
        gk_rag = GoalkeeperRAG()
        print("   ✓ GoalkeeperRAG initialized successfully")
        
        # Build vector store
        print("2. Building vector store...")
        gk_rag.build_vector_store(force_rebuild=False)  # Use existing if available
        print("   ✓ Vector store built successfully")
        
        # Test a simple query
        print("3. Testing query...")
        result = gk_rag.query("How many goalkeepers are in the dataset?")
        print(f"   Query result: {result['answer'][:100]}...")
        print("   ✓ Query test successful")
        
        # Get player count
        player_count = len(gk_rag.data_processor.player_data)
        print(f"4. Total goalkeepers processed: {player_count}")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error in goalkeeper RAG: {str(e)}")
        return False

def test_outfield_rag():
    """Test building outfield RAG system."""
    print("\n" + "=" * 60)
    print("TESTING OUTFIELD RAG SYSTEM")
    print("=" * 60)
    
    try:
        # Initialize outfield RAG
        print("1. Initializing OutfieldRAG...")
        outfield_rag = OutfieldRAG()
        print("   ✓ OutfieldRAG initialized successfully")
        
        # Build vector store
        print("2. Building vector store...")
        outfield_rag.build_vector_store(force_rebuild=False)
        print("   ✓ Vector store built successfully")
        
        # Get player count
        player_count = len(outfield_rag.data_processor.player_data)
        print(f"3. Total outfield players processed: {player_count}")
        
        if player_count > 0:
            # Test a simple query
            print("4. Testing query...")
            result = outfield_rag.query("How many outfield players are in the dataset?")
            print(f"   Query result: {result['answer'][:100]}...")
            print("   ✓ Query test successful")
        else:
            print("4. No outfield players found - this is expected if you only have goalkeeper data")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error in outfield RAG: {str(e)}")
        return False

def test_position_specific_rags():
    """Test building position-specific RAG systems."""
    print("\n" + "=" * 60)
    print("TESTING POSITION-SPECIFIC RAG SYSTEMS")
    print("=" * 60)
    
    positions = [
        ("Forward", ForwardRAG),
        ("Midfielder", MidfielderRAG),
        ("Defender", DefenderRAG)
    ]
    
    results = {}
    
    for position_name, rag_class in positions:
        try:
            print(f"\n{position_name}RAG:")
            print(f"1. Initializing {position_name}RAG...")
            rag = rag_class()
            print(f"   ✓ {position_name}RAG initialized successfully")
            
            print("2. Building vector store...")
            rag.build_vector_store(force_rebuild=False)
            print("   ✓ Vector store built successfully")
            
            player_count = len(rag.data_processor.player_data)
            print(f"3. Total {position_name.lower()}s processed: {player_count}")
            
            results[position_name] = player_count
            
        except Exception as e:
            print(f"   ✗ Error in {position_name} RAG: {str(e)}")
            results[position_name] = 0
    
    return results

def main():
    """Main test function."""
    print("RAG SYSTEM BUILD AND TEST")
    print("=" * 60)
    print("This script will build and test all RAG systems.")
    print("Note: First run may take several minutes to generate embeddings.")
    print("=" * 60)
    
    # Test goalkeeper RAG
    gk_success = test_goalkeeper_rag()
    
    # Test outfield RAG
    outfield_success = test_outfield_rag()
    
    # Test position-specific RAGs
    position_results = test_position_specific_rags()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Goalkeeper RAG: {'✓ Success' if gk_success else '✗ Failed'}")
    print(f"Outfield RAG: {'✓ Success' if outfield_success else '✗ Failed'}")
    
    for position, count in position_results.items():
        status = "✓ Success" if count >= 0 else "✗ Failed"
        print(f"{position} RAG: {status} ({count} players)")
    
    # Check vector store files
    print("\nVector Store Files:")
    vector_stores = [
        "vector_store",
        "vector_store_outfield", 
        "vector_store_forwards",
        "vector_store_midfielders",
        "vector_store_defenders"
    ]
    
    for vs in vector_stores:
        exists = "✓" if os.path.exists(vs) else "✗"
        print(f"  {exists} {vs}")
    
    print("\n" + "=" * 60)
    print("RAG SYSTEM BUILD COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
