#!/usr/bin/env python3
"""
Build All RAG Systems
Script to build all RAG systems (goalkeeper and outfield).
"""

import os
import sys
from datetime import datetime

# Add src directory to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

# Change to project root directory
os.chdir(project_root)

def build_goalkeeper_rag():
    """Build goalkeeper RAG system."""
    print("Building Goalkeeper RAG...")

    try:
        from core.rag_system import GoalkeeperRAG
        rag = GoalkeeperRAG()
        rag.build_vector_store(force_rebuild=False)  # Use existing if available

        player_count = len(rag.data_processor.player_data)
        print(f"✓ Goalkeeper RAG: {player_count} players")
        return True, player_count

    except Exception as e:
        print(f"✗ Goalkeeper RAG failed: {e}")
        import traceback
        traceback.print_exc()
        return False, 0

def build_outfield_rag():
    """Build outfield RAG systems."""
    print("Building Outfield RAG systems...")

    results = {}

    # Define RAG systems to build
    systems = [
        ("All Outfield", "OutfieldRAG"),
        ("Forwards", "ForwardRAG"),
        ("Midfielders", "MidfielderRAG"),
        ("Defenders", "DefenderRAG")
    ]

    for name, class_name in systems:
        try:
            print(f"  Building {name}...")

            # Import from new structure
            from core.rag_system import OutfieldRAG, ForwardRAG, MidfielderRAG, DefenderRAG

            # Get the appropriate class
            class_map = {
                'OutfieldRAG': OutfieldRAG,
                'ForwardRAG': ForwardRAG,
                'MidfielderRAG': MidfielderRAG,
                'DefenderRAG': DefenderRAG
            }

            rag_class = class_map[class_name]
            rag = rag_class()
            rag.build_vector_store(force_rebuild=False)

            player_count = len(rag.data_processor.player_data)
            print(f"    ✓ {name}: {player_count} players")
            results[name] = player_count

        except Exception as e:
            print(f"    ✗ {name} failed: {e}")
            import traceback
            traceback.print_exc()
            results[name] = 0

    return results

def main():
    print("=" * 60)
    print("BUILDING ALL RAG SYSTEMS")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    print("This will build RAG systems for all player positions.")
    print("Note: First run may take 10-30 minutes to generate embeddings.")
    print()

    # Build goalkeeper RAG
    print("1. GOALKEEPER RAG SYSTEM")
    print("-" * 30)
    gk_success, gk_count = build_goalkeeper_rag()
    print()

    # Build outfield RAG systems
    print("2. OUTFIELD RAG SYSTEMS")
    print("-" * 30)
    outfield_results = build_outfield_rag()
    print()

    # Summary
    print("=" * 60)
    print("BUILD SUMMARY")
    print("=" * 60)

    print(f"Goalkeeper RAG: {'✓ Success' if gk_success else '✗ Failed'} ({gk_count} players)")

    total_outfield = 0
    for name, count in outfield_results.items():
        status = "✓ Success" if count >= 0 else "✗ Failed"
        print(f"{name} RAG: {status} ({count} players)")
        if name != "All Outfield":  # Don't double count
            total_outfield += count

    # Check vector store files
    print("\nVector Store Files:")
    vector_stores = [
        ("storage/vector_store", "Goalkeepers"),
        ("storage/vector_store_outfield", "All Outfield"),
        ("storage/vector_store_forwards", "Forwards"),
        ("storage/vector_store_midfielders", "Midfielders"),
        ("storage/vector_store_defenders", "Defenders")
    ]

    for vs_path, vs_name in vector_stores:
        exists = "✓" if os.path.exists(vs_path) else "✗"
        print(f"  {exists} {vs_path} ({vs_name})")

    # Final status
    total_systems = 1 + len(outfield_results)  # GK + outfield systems
    successful_systems = (1 if gk_success else 0) + sum(1 for count in outfield_results.values() if count >= 0)

    print(f"\nOverall: {successful_systems}/{total_systems} RAG systems built successfully")
    print(f"Total players: {gk_count + sum(outfield_results.values())}")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if successful_systems > 0:
        print("\n🎉 SUCCESS! RAG systems are ready.")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Select position type in the sidebar dropdown")
        print("3. Use AI Assistant, Player Search, or Player Comparison")

        if gk_count == 0 and sum(outfield_results.values()) == 0:
            print("\n⚠️  WARNING: No player data found!")
            print("   Make sure CSV files are in the data/stats/ directory")
    else:
        print("\n❌ FAILED! No RAG systems were built successfully.")
        print("\nTroubleshooting:")
        print("1. Check Ollama is running: ollama list")
        print("2. Verify deepseek-r1:8b model: ollama pull deepseek-r1:8b")
        print("3. Check data files in data/stats/ directory")
        print("4. Verify Python dependencies are installed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBuild interrupted by user.")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()

    input("\nPress Enter to exit...")
