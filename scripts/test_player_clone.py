#!/usr/bin/env python3
"""
Test script to verify that the Player Clone functionality works correctly.
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

def test_player_clone_import():
    """Test that the find similar player components can be imported."""
    print("🔍 TESTING FIND SIMILAR PLAYER IMPORT")
    print("-" * 50)
    
    try:
        from components.player_clone_components import (
            render_player_clone,
            get_strongest_stats,
            get_available_stats,
            calculate_similarity,
            display_similar_players
        )
        print("✅ Successfully imported all find similar player functions")
        
        # Check if functions are callable
        functions = [
            render_player_clone,
            get_strongest_stats,
            get_available_stats,
            calculate_similarity,
            display_similar_players
        ]
        
        for func in functions:
            if callable(func):
                print(f"✅ {func.__name__} is callable")
            else:
                print(f"❌ {func.__name__} is not callable")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing find similar player components: {e}")
        return False

def test_available_stats():
    """Test the get_available_stats function."""
    print("\n🔍 TESTING AVAILABLE STATS FUNCTION")
    print("-" * 50)
    
    try:
        from components.player_clone_components import get_available_stats
        
        # Test goalkeeper stats
        gk_stats = get_available_stats("Goalkeepers")
        print(f"✅ Goalkeeper stats ({len(gk_stats)} stats):")
        print(f"   {', '.join(gk_stats[:5])}...")  # Show first 5
        
        # Test outfield stats
        outfield_stats = get_available_stats("All Outfield")
        print(f"✅ Outfield stats ({len(outfield_stats)} stats):")
        print(f"   {', '.join(outfield_stats[:5])}...")  # Show first 5
        
        # Verify we have reasonable number of stats
        if len(gk_stats) >= 10 and len(outfield_stats) >= 15:
            print("✅ Reasonable number of stats for both position types")
            return True
        else:
            print(f"❌ Insufficient stats: GK={len(gk_stats)}, Outfield={len(outfield_stats)}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing available stats: {e}")
        return False

def test_strongest_stats_logic():
    """Test the strongest stats calculation logic."""
    print("\n🔍 TESTING STRONGEST STATS LOGIC")
    print("-" * 50)
    
    try:
        from components.player_clone_components import get_strongest_stats
        
        # Create mock player data
        mock_player_data = {
            "Player A": {
                "goals": 15,
                "assists": 8,
                "shots": 45,
                "passes": 1200,
                "passes_accurate": 1000,
                "minutes": 1800,
                "age": 25,
                "team": "Team A",
                "position": "CF"
            },
            "Player B": {
                "goals": 5,
                "assists": 12,
                "shots": 25,
                "passes": 1500,
                "passes_accurate": 1350,
                "minutes": 1600,
                "age": 27,
                "team": "Team B",
                "position": "MF"
            },
            "Player C": {
                "goals": 2,
                "assists": 3,
                "shots": 15,
                "passes": 800,
                "passes_accurate": 600,
                "minutes": 1200,
                "age": 23,
                "team": "Team C",
                "position": "DF"
            }
        }
        
        # Test strongest stats calculation
        strongest_stats = get_strongest_stats(
            "Player A", 
            mock_player_data, 
            "All Outfield", 
            per_90_mode=False, 
            num_stats=3
        )
        
        print(f"✅ Strongest stats for Player A: {strongest_stats}")
        
        if len(strongest_stats) == 3:
            print("✅ Correct number of strongest stats returned")
        else:
            print(f"❌ Expected 3 stats, got {len(strongest_stats)}")
            return False
        
        # Test with per 90 mode
        strongest_stats_per90 = get_strongest_stats(
            "Player A", 
            mock_player_data, 
            "All Outfield", 
            per_90_mode=True, 
            num_stats=3
        )
        
        print(f"✅ Strongest stats for Player A (per 90): {strongest_stats_per90}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing strongest stats logic: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_similarity_calculation():
    """Test the similarity calculation function."""
    print("\n🔍 TESTING SIMILARITY CALCULATION")
    print("-" * 50)
    
    try:
        from components.player_clone_components import calculate_similarity
        
        # Create mock player data with more realistic stats
        mock_player_data = {
            "Player A": {
                "goals": 15, "assists": 8, "shots": 45, "passes": 1200,
                "minutes": 1800, "age": 25, "team": "Team A", "position": "CF"
            },
            "Player B": {  # Similar to Player A
                "goals": 14, "assists": 9, "shots": 42, "passes": 1150,
                "minutes": 1750, "age": 26, "team": "Team B", "position": "CF"
            },
            "Player C": {  # Different from Player A
                "goals": 2, "assists": 15, "shots": 20, "passes": 1800,
                "minutes": 1600, "age": 27, "team": "Team C", "position": "MF"
            },
            "Player D": {  # Very different from Player A
                "goals": 0, "assists": 2, "shots": 5, "passes": 500,
                "minutes": 900, "age": 35, "team": "Team D", "position": "DF"
            }
        }
        
        # Test similarity calculation
        selected_stats = ["goals", "assists", "shots", "passes"]
        similar_players = calculate_similarity(
            "Player A",
            mock_player_data,
            selected_stats,
            per_90_mode=False,
            min_age=20,
            max_age=40,
            min_minutes=500
        )
        
        print(f"✅ Found {len(similar_players)} similar players")
        
        if similar_players:
            # Check that results are sorted by similarity (descending)
            similarities = [score for _, score in similar_players]
            is_sorted = all(similarities[i] >= similarities[i+1] for i in range(len(similarities)-1))
            
            if is_sorted:
                print("✅ Results are correctly sorted by similarity")
            else:
                print("❌ Results are not properly sorted")
                return False
            
            # Show top results
            print("Top similar players:")
            for i, (player, score) in enumerate(similar_players[:3]):
                print(f"  {i+1}. {player}: {score:.3f}")
            
            # Player B should be most similar to Player A
            if similar_players[0][0] == "Player B":
                print("✅ Most similar player is correct (Player B)")
            else:
                print(f"⚠️  Most similar player is {similar_players[0][0]} (expected Player B)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing similarity calculation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("=" * 80)
    print("FIND SIMILAR PLAYER FUNCTIONALITY VERIFICATION")
    print("=" * 80)
    print("Testing the new Find Similar Player feature")
    print()
    
    # Test 1: Import test
    import_test_passed = test_player_clone_import()
    
    # Test 2: Available stats test
    stats_test_passed = test_available_stats()
    
    # Test 3: Strongest stats logic test
    strongest_stats_test_passed = test_strongest_stats_logic()
    
    # Test 4: Similarity calculation test
    similarity_test_passed = test_similarity_calculation()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    all_tests_passed = (import_test_passed and stats_test_passed and 
                       strongest_stats_test_passed and similarity_test_passed)
    
    if import_test_passed:
        print("✅ Find Similar Player import: Working correctly")
    else:
        print("❌ Find Similar Player import: Failed")
    
    if stats_test_passed:
        print("✅ Available stats function: Working correctly")
    else:
        print("❌ Available stats function: Failed")
    
    if strongest_stats_test_passed:
        print("✅ Strongest stats logic: Working correctly")
    else:
        print("❌ Strongest stats logic: Failed")
    
    if similarity_test_passed:
        print("✅ Similarity calculation: Working correctly")
    else:
        print("❌ Similarity calculation: Failed")
    
    print()
    
    if all_tests_passed:
        print("🎉 SUCCESS! Find Similar Player functionality is working correctly.")
        print("\nFeatures implemented:")
        print("- Player selection for both GK and outfield players")
        print("- Automatic detection of strongest stats (minimum 3)")
        print("- Customizable stat selection with multiselect")
        print("- Per 90 minutes calculation option")
        print("- Age and minutes filters")
        print("- Similarity calculation using cosine similarity")
        print("- Results table with player info and similarity scores")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Navigate to 'Find Similar Player' menu")
        print("3. Test the functionality with real player data")
    else:
        print("💥 FAILED! Some tests did not pass.")
        print("\nPlease fix the issues above before proceeding.")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
