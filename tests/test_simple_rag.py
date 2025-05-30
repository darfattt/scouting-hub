#!/usr/bin/env python3
"""
Simple RAG test - just build goalkeeper RAG system.
Updated for new project structure.
"""

import os
import sys
import pytest

# Add src directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.mark.rag
@pytest.mark.integration
def test_goalkeeper_rag_system():
    """
    Test the goalkeeper RAG system initialization and basic functionality.
    """
    print("Simple RAG Test - Goalkeeper Only")
    print("=" * 50)

    try:
        # Import the RAG system from new structure
        print("1. Importing RAG system...")
        from core.rag_system import GoalkeeperRAG
        print("   ✓ Import successful")

        # Initialize
        print("2. Initializing GoalkeeperRAG...")
        rag = GoalkeeperRAG()
        print("   ✓ Initialization successful")

        # Check if vector store exists in storage directory
        vector_store_path = os.path.join("storage", "vector_store")
        if os.path.exists(vector_store_path):
            print("3. Vector store already exists, loading...")
            rag.build_vector_store(force_rebuild=False)
        else:
            print("3. Building new vector store...")
            rag.build_vector_store(force_rebuild=True)

        print("   ✓ Vector store ready")

        # Check data
        player_count = len(rag.data_processor.player_data)
        print(f"4. Players loaded: {player_count}")

        assert player_count > 0, "No players loaded"

        if player_count > 0:
            # List some players
            players = list(rag.data_processor.player_data.keys())[:5]
            print("   Sample players:")
            for player in players:
                print(f"     - {player}")

        print("\n✓ Goalkeeper RAG system is ready!")
        return True

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        pytest.fail(f"RAG system test failed: {str(e)}")


@pytest.mark.rag
@pytest.mark.unit
def test_goalkeeper_data_processing():
    """
    Test goalkeeper data processing functionality.
    """
    try:
        from core.data_processor import GoalkeeperDataProcessor

        # Initialize data processor
        processor = GoalkeeperDataProcessor()

        # Load and process data
        processor.load_data()
        processor.process_data()

        # Verify data was loaded
        assert len(processor.player_data) > 0, "No player data processed"

        # Check that each player has required fields
        for player_name, player_data in processor.player_data.items():
            assert 'name' in player_data, f"Player {player_name} missing name field"
            assert 'team' in player_data, f"Player {player_name} missing team field"
            assert 'minutes' in player_data, f"Player {player_name} missing minutes field"
            assert 'saves' in player_data, f"Player {player_name} missing saves field"

        print(f"✓ Data processing test passed for {len(processor.player_data)} players")

    except Exception as e:
        pytest.fail(f"Data processing test failed: {str(e)}")


@pytest.mark.rag
@pytest.mark.unit
def test_goalkeeper_text_representation():
    """
    Test goalkeeper text representation generation.
    """
    try:
        from core.data_processor import GoalkeeperDataProcessor

        processor = GoalkeeperDataProcessor()
        processor.process_data()

        if processor.player_data:
            # Get first player
            player_name = list(processor.player_data.keys())[0]
            text_repr = processor.get_player_text_representation(player_name)

            assert text_repr, f"No text representation generated for {player_name}"
            assert player_name in text_repr, f"Player name not in text representation"
            assert "Statistics Summary" in text_repr, "Statistics summary not in text representation"

            print(f"✓ Text representation test passed for {player_name}")

    except Exception as e:
        pytest.fail(f"Text representation test failed: {str(e)}")


def main():
    """
    Main function for standalone execution.
    """
    print("Running Simple RAG Tests")
    print("=" * 50)

    try:
        # Run the main test
        test_goalkeeper_rag_system()

        # Run additional tests
        test_goalkeeper_data_processing()
        test_goalkeeper_text_representation()

        print("\n✓ All tests passed!")
        print("You can now run: streamlit run app.py")
        return True

    except Exception as e:
        print(f"\n✗ Tests failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        print("\nPlease check the error messages above.")
        sys.exit(1)
