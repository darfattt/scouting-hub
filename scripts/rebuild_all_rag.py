#!/usr/bin/env python3
"""
Rebuild All RAG Systems
Force rebuild all RAG systems with the correct Wyscout position filters.
"""

import os
import sys
import shutil
from datetime import datetime

# Add src directory to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

def clean_vector_stores():
    """Remove existing vector stores to force rebuild."""
    print("Cleaning existing vector stores...")

    # Change to project root directory
    os.chdir(project_root)

    vector_stores = [
        "storage/vector_store",
        "storage/vector_store_outfield",
        "storage/vector_store_forwards",
        "storage/vector_store_midfielders",
        "storage/vector_store_defenders"
    ]

    for vs in vector_stores:
        if os.path.exists(vs):
            try:
                shutil.rmtree(vs)
                print(f"  ✓ Removed {vs}")
            except Exception as e:
                print(f"  ✗ Failed to remove {vs}: {e}")
        else:
            print(f"  - {vs} (not found)")

def build_goalkeeper_rag():
    """Build goalkeeper RAG system."""
    print("\nBuilding Goalkeeper RAG...")

    try:
        from core.rag_system import GoalkeeperRAG
        rag = GoalkeeperRAG()
        rag.build_vector_store(force_rebuild=True)

        player_count = len(rag.data_processor.player_data)
        print(f"✓ Goalkeeper RAG: {player_count} players")
        return True, player_count

    except Exception as e:
        print(f"✗ Goalkeeper RAG failed: {e}")
        import traceback
        traceback.print_exc()
        return False, 0

def build_outfield_rag_systems():
    """Build outfield RAG systems with correct position filters."""
    print("\nBuilding Outfield RAG systems...")

    systems = [
        ("All Outfield", "OutfieldRAG"),
        ("Forwards", "ForwardRAG"),
        ("Midfielders", "MidfielderRAG"),
        ("Defenders", "DefenderRAG")
    ]

    results = {}

    for name, class_name in systems:
        print(f"\n  Building {name}...")

        try:
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
            rag.build_vector_store(force_rebuild=True)

            player_count = len(rag.data_processor.player_data)
            print(f"    ✓ {name}: {player_count} players")
            results[name] = player_count

            # Show sample players if any found
            if player_count > 0:
                players = list(rag.data_processor.player_data.keys())[:3]
                print(f"    Sample players: {', '.join(players)}")

        except Exception as e:
            print(f"    ✗ {name} failed: {e}")
            import traceback
            traceback.print_exc()
            results[name] = 0

    return results

def main():
    print("=" * 60)
    print("REBUILD ALL RAG SYSTEMS")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    print("This script will force rebuild all RAG systems with correct Wyscout position filters.")
    print("Expected position codes:")
    print("- Forwards: CF, RWF, LWF, LAMF, RAMF, AMF, SS, LW, RW")
    print("- Midfielders: CM, CDM, CAM, LCM, RCM, LDMF, RDMF, DMF, LCMF, RCMF, CMF, LCMF3, RCMF3")
    print("- Defenders: CB, LB, RB, LCB, RCB, LWB, RWB, LB5, RB5, CB5")
    print()

    # Clean existing vector stores
    clean_vector_stores()

    # Build goalkeeper RAG
    print("\n" + "="*30)
    print("GOALKEEPER RAG")
    print("="*30)
    gk_success, gk_count = build_goalkeeper_rag()

    # Build outfield RAG systems
    print("\n" + "="*30)
    print("OUTFIELD RAG SYSTEMS")
    print("="*30)
    outfield_results = build_outfield_rag_systems()

    # Summary
    print("\n" + "=" * 60)
    print("REBUILD SUMMARY")
    print("=" * 60)

    print(f"Goalkeeper RAG: {'✓ Success' if gk_success else '✗ Failed'} ({gk_count} players)")

    total_outfield = 0
    for name, count in outfield_results.items():
        status = "✓ Success" if count > 0 else "✗ No data" if count == 0 else "✗ Failed"
        print(f"{name}: {status} ({count} players)")
        if count > 0:
            total_outfield += count

    # Check vector store files
    print(f"\nVector Store Files:")
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

    total_players = gk_count + total_outfield
    successful_systems = (1 if gk_success else 0) + sum(1 for count in outfield_results.values() if count > 0)

    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total players processed: {total_players}")
    print(f"Successful RAG systems: {successful_systems}")

    if successful_systems > 0:
        print("\n🎉 SUCCESS! RAG systems rebuilt successfully.")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Select position type in the sidebar")
        print("3. Use AI Assistant, Player Search, or Player Comparison")

        if gk_count > 0:
            print(f"\n✅ Goalkeeper analysis available ({gk_count} players)")

        outfield_available = [name for name, count in outfield_results.items() if count > 0]
        if outfield_available:
            print(f"✅ Outfield analysis available: {', '.join(outfield_available)}")

    else:
        print("\n❌ REBUILD FAILED!")
        print("\nPossible issues:")
        print("1. Ollama models not available (phi3:mini, nomic-embed-text)")
        print("2. Data format issues")
        print("3. Position codes don't match expected patterns")

    return successful_systems > 0

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\nPlease check the error messages above.")
    except KeyboardInterrupt:
        print("\n\nRebuild interrupted by user.")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()

    input("\nPress Enter to exit...")
