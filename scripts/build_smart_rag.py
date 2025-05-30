#!/usr/bin/env python3
"""
Smart RAG Builder
Automatically detects available data and builds appropriate RAG systems.
"""

import os
import pandas as pd
import glob
from datetime import datetime

def analyze_data_files():
    """Analyze CSV files to determine what types of players are available."""
    print("Analyzing data files...")

    data_dir = "data/stats"
    if not os.path.exists(data_dir):
        print(f"✗ Data directory not found: {data_dir}")
        return {}

    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    if not csv_files:
        print(f"✗ No CSV files found in {data_dir}")
        return {}

    print(f"Found {len(csv_files)} CSV files")

    player_types = {
        'goalkeepers': 0,
        'forwards': 0,
        'midfielders': 0,
        'defenders': 0,
        'unknown': 0
    }

    for file in csv_files:
        try:
            df = pd.read_csv(file)

            # Check if this is goalkeeper data (has goalkeeper-specific columns)
            gk_columns = ['Saves', 'Conceded goals', 'Shots against']
            if all(col in df.columns for col in gk_columns):
                player_types['goalkeepers'] += 1
                continue

            # Check if this is outfield data (has Position column)
            if 'Position' in df.columns:
                positions = df['Position'].fillna('')

                # Check for Wyscout position codes
                forward_codes = ['CF', 'RWF', 'LWF', 'LAMF', 'RAMF', 'AMF', 'SS', 'LW', 'RW']
                midfielder_codes = ['CM', 'CDM', 'CAM', 'LCM', 'RCM', 'LDMF', 'RDMF', 'DMF', 'LCMF', 'RCMF', 'CMF', 'LCMF3', 'RCMF3']
                defender_codes = ['CB', 'LB', 'RB', 'LCB', 'RCB', 'LWB', 'RWB', 'LB5', 'RB5', 'CB5']

                has_forwards = any(any(code in pos for code in forward_codes) for pos in positions)
                has_midfielders = any(any(code in pos for code in midfielder_codes) for pos in positions)
                has_defenders = any(any(code in pos for code in defender_codes) for pos in positions)

                if has_forwards:
                    player_types['forwards'] += 1
                elif has_midfielders:
                    player_types['midfielders'] += 1
                elif has_defenders:
                    player_types['defenders'] += 1
                else:
                    player_types['unknown'] += 1
            else:
                player_types['unknown'] += 1

        except Exception as e:
            print(f"Warning: Could not analyze {file}: {e}")
            player_types['unknown'] += 1

    return player_types

def build_goalkeeper_rag():
    """Build goalkeeper RAG system."""
    print("Building Goalkeeper RAG...")

    try:
        from rag_system import GoalkeeperRAG
        rag = GoalkeeperRAG()
        rag.build_vector_store(force_rebuild=False)

        player_count = len(rag.data_processor.player_data)
        if player_count > 0:
            print(f"✓ Goalkeeper RAG: {player_count} players")
            return True, player_count
        else:
            print("✗ Goalkeeper RAG: No data found")
            return False, 0

    except Exception as e:
        print(f"✗ Goalkeeper RAG failed: {e}")
        return False, 0

def build_outfield_rag_systems(available_types):
    """Build outfield RAG systems based on available data."""
    results = {}

    # Only build systems for which we have data
    systems_to_build = []

    if available_types.get('forwards', 0) > 0:
        systems_to_build.append(("Forwards", "ForwardRAG"))

    if available_types.get('midfielders', 0) > 0:
        systems_to_build.append(("Midfielders", "MidfielderRAG"))

    if available_types.get('defenders', 0) > 0:
        systems_to_build.append(("Defenders", "DefenderRAG"))

    # Always try to build general outfield RAG if any outfield data exists
    total_outfield = sum(available_types.get(pos, 0) for pos in ['forwards', 'midfielders', 'defenders'])
    if total_outfield > 0:
        systems_to_build.append(("All Outfield", "OutfieldRAG"))

    if not systems_to_build:
        print("No outfield player data detected - skipping outfield RAG systems")
        return {}

    print(f"Building {len(systems_to_build)} outfield RAG systems...")

    for name, class_name in systems_to_build:
        try:
            print(f"  Building {name}...")

            # Dynamic import
            from rag_system import OutfieldRAG, ForwardRAG, MidfielderRAG, DefenderRAG
            rag_class = globals().get(class_name) or getattr(__import__('rag_system'), class_name)

            rag = rag_class()
            rag.build_vector_store(force_rebuild=False)

            player_count = len(rag.data_processor.player_data)
            print(f"    ✓ {name}: {player_count} players")
            results[name] = player_count

        except Exception as e:
            print(f"    ✗ {name} failed: {e}")
            results[name] = 0

    return results

def main():
    print("=" * 60)
    print("SMART RAG SYSTEM BUILDER")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    print("This script analyzes your data and builds only the appropriate RAG systems.")
    print()

    # Analyze data files
    print("1. DATA ANALYSIS")
    print("-" * 30)
    available_types = analyze_data_files()

    if not available_types:
        print("❌ No data files found. Please add CSV files to data/stats/ directory.")
        return False

    print("\nData summary:")
    for player_type, count in available_types.items():
        if count > 0:
            print(f"  ✓ {player_type.title()}: {count} files")

    total_files = sum(available_types.values())
    print(f"\nTotal: {total_files} data files")

    if total_files == 0:
        print("❌ No valid data files found.")
        return False

    # Build RAG systems
    print(f"\n2. BUILDING RAG SYSTEMS")
    print("-" * 30)

    results = {}

    # Build goalkeeper RAG if data available
    if available_types.get('goalkeepers', 0) > 0:
        gk_success, gk_count = build_goalkeeper_rag()
        results['Goalkeepers'] = gk_count if gk_success else 0
    else:
        print("No goalkeeper data found - skipping goalkeeper RAG")
        results['Goalkeepers'] = 0

    # Build outfield RAG systems if data available
    outfield_results = build_outfield_rag_systems(available_types)
    results.update(outfield_results)

    # Summary
    print(f"\n3. BUILD SUMMARY")
    print("-" * 30)

    successful_systems = 0
    total_players = 0

    for system_name, player_count in results.items():
        status = "✓ Success" if player_count > 0 else "✗ No data"
        print(f"{system_name}: {status} ({player_count} players)")

        if player_count > 0:
            successful_systems += 1
            total_players += player_count

    # Check vector store files
    print(f"\nVector Store Files:")
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

    if successful_systems > 0:
        print(f"\n🎉 SUCCESS! Built {successful_systems} RAG systems for {total_players} players.")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Select appropriate position type in the sidebar")
        print("3. Use AI Assistant, Player Search, or Player Comparison")

        if results.get('Goalkeepers', 0) == 0:
            print("\n⚠️  Note: No goalkeeper RAG system was built.")
            print("   Add goalkeeper CSV files if you want goalkeeper analysis.")

        if sum(outfield_results.values()) == 0:
            print("\n⚠️  Note: No outfield RAG systems were built.")
            print("   Add outfield player CSV files if you want outfield analysis.")
    else:
        print("\n❌ FAILED! No RAG systems were built successfully.")
        print("\nPossible issues:")
        print("1. CSV files don't contain expected columns")
        print("2. Ollama models not available")
        print("3. Data format issues")

    return successful_systems > 0

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\nPlease check your data files and try again.")
    except KeyboardInterrupt:
        print("\n\nBuild interrupted by user.")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()

    input("\nPress Enter to exit...")
