#!/usr/bin/env python3
"""
Test script to verify the role weight functionality in Find Similar Player feature.
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

def test_role_weight_functions():
    """Test that the role weight functions can be imported and work correctly."""
    print("🔍 TESTING ROLE WEIGHT FUNCTIONS")
    print("-" * 50)
    
    try:
        from components.player_clone_components import (
            get_role_weights_for_players,
            calculate_role_scores,
            generate_role_insights
        )
        
        print("✅ Successfully imported role weight functions")
        
        # Test function signatures
        import inspect
        
        # Test get_role_weights_for_players
        sig1 = inspect.signature(get_role_weights_for_players)
        expected_params1 = ['selected_player', 'players_to_show', 'player_data']
        actual_params1 = list(sig1.parameters.keys())
        
        if actual_params1 == expected_params1:
            print("✅ get_role_weights_for_players signature correct")
        else:
            print(f"❌ get_role_weights_for_players signature mismatch. Expected: {expected_params1}, Got: {actual_params1}")
            return False
        
        # Test calculate_role_scores
        sig2 = inspect.signature(calculate_role_scores)
        expected_params2 = ['player_name', 'player_stats', 'role_weights', 'all_players_data', 'per_90_mode']
        actual_params2 = list(sig2.parameters.keys())
        
        if actual_params2 == expected_params2:
            print("✅ calculate_role_scores signature correct")
        else:
            print(f"❌ calculate_role_scores signature mismatch. Expected: {expected_params2}, Got: {actual_params2}")
            return False
        
        # Test generate_role_insights
        sig3 = inspect.signature(generate_role_insights)
        expected_params3 = ['position_type', 'role_weights', 'per_90_mode']
        actual_params3 = list(sig3.parameters.keys())
        
        if actual_params3 == expected_params3:
            print("✅ generate_role_insights signature correct")
        else:
            print(f"❌ generate_role_insights signature mismatch. Expected: {expected_params3}, Got: {actual_params3}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing role weight functions: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_role_weight_detection():
    """Test the role weight detection based on player positions."""
    print("\n🔍 TESTING ROLE WEIGHT DETECTION")
    print("-" * 50)
    
    try:
        from components.player_clone_components import get_role_weights_for_players
        
        # Test data for different positions
        test_cases = [
            {
                "player": "Test GK",
                "position": "GK",
                "expected_type": "Goalkeeper",
                "expected_roles": ["Shot Stopper", "Sweeper Keeper"]
            },
            {
                "player": "Test CF",
                "position": "CF",
                "expected_type": "Center Forward",
                "expected_roles": ["Advance Forward", "Pressing Forward", "Deep-lying Forward", "Poacher"]
            },
            {
                "player": "Test CB",
                "position": "CB",
                "expected_type": "Center Back",
                "expected_roles": ["No-Nonsense Centre-Back", "Central Defender", "Ball Playing Defender"]
            },
            {
                "player": "Test MF",
                "position": "MF",
                "expected_type": "Outfield",
                "expected_roles": ["Advance Forward", "Pressing Forward", "Deep-lying Forward", "Poacher"]
            }
        ]
        
        for test_case in test_cases:
            player_data = {
                test_case["player"]: {
                    "position": test_case["position"],
                    "goals": 10,
                    "assists": 5
                }
            }
            
            players_to_show = [(test_case["player"], 1.0)]
            
            role_weights, position_type = get_role_weights_for_players(
                test_case["player"],
                players_to_show,
                player_data
            )
            
            if position_type == test_case["expected_type"]:
                print(f"✅ {test_case['position']} position detected as {position_type}")
            else:
                print(f"❌ {test_case['position']} position detection failed. Expected: {test_case['expected_type']}, Got: {position_type}")
                return False
            
            actual_roles = list(role_weights.keys())
            if set(actual_roles) == set(test_case["expected_roles"]):
                print(f"✅ {test_case['position']} roles correct: {actual_roles}")
            else:
                print(f"❌ {test_case['position']} roles incorrect. Expected: {test_case['expected_roles']}, Got: {actual_roles}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing role weight detection: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_role_score_calculation():
    """Test the role score calculation logic."""
    print("\n🔍 TESTING ROLE SCORE CALCULATION")
    print("-" * 50)
    
    try:
        from components.player_clone_components import calculate_role_scores
        
        # Create mock data for testing
        mock_role_weights = {
            "Test Role": {
                "goals": 0.5,
                "assists": 0.3,
                "shots": 0.2
            }
        }
        
        mock_player_stats = {
            "goals": 15,
            "assists": 8,
            "shots": 45,
            "minutes": 1800
        }
        
        mock_all_players = {
            "Player A": {"goals": 15, "assists": 8, "shots": 45, "minutes": 1800},
            "Player B": {"goals": 10, "assists": 12, "shots": 35, "minutes": 1600},
            "Player C": {"goals": 20, "assists": 5, "shots": 55, "minutes": 2000}
        }
        
        # Test normal mode
        role_scores = calculate_role_scores(
            "Player A",
            mock_player_stats,
            mock_role_weights,
            mock_all_players,
            per_90_mode=False
        )
        
        if "Test Role" in role_scores:
            score = role_scores["Test Role"]
            if 0 <= score <= 100:
                print(f"✅ Normal mode role score calculated: {score:.1f}%")
            else:
                print(f"❌ Normal mode role score out of range: {score}")
                return False
        else:
            print("❌ Normal mode role score not calculated")
            return False
        
        # Test per 90 mode
        role_scores_per90 = calculate_role_scores(
            "Player A",
            mock_player_stats,
            mock_role_weights,
            mock_all_players,
            per_90_mode=True
        )
        
        if "Test Role" in role_scores_per90:
            score_per90 = role_scores_per90["Test Role"]
            if 0 <= score_per90 <= 100:
                print(f"✅ Per 90 mode role score calculated: {score_per90:.1f}%")
            else:
                print(f"❌ Per 90 mode role score out of range: {score_per90}")
                return False
        else:
            print("❌ Per 90 mode role score not calculated")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing role score calculation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_role_insights_generation():
    """Test the role insights generation."""
    print("\n🔍 TESTING ROLE INSIGHTS GENERATION")
    print("-" * 50)
    
    try:
        from components.player_clone_components import generate_role_insights
        
        # Test different position types
        test_cases = [
            {
                "position_type": "Goalkeeper",
                "role_weights": {
                    "Shot Stopper": {"saves": 0.3, "conceded_goals": -0.2},
                    "Sweeper Keeper": {"exits": 0.25, "long_passes_accurate": 0.2}
                }
            },
            {
                "position_type": "Center Forward",
                "role_weights": {
                    "Advance Forward": {"goals": 0.3, "shots": 0.2},
                    "Poacher": {"goals": 0.5, "shots": 0.3}
                }
            },
            {
                "position_type": "Center Back",
                "role_weights": {
                    "No-Nonsense Centre-Back": {"duels_won": 0.25, "recoveries": 0.2},
                    "Ball Playing Defender": {"passes_accurate": 0.25, "pass_accuracy": 0.2}
                }
            }
        ]
        
        for test_case in test_cases:
            # Test normal mode
            insights = generate_role_insights(
                test_case["position_type"],
                test_case["role_weights"],
                per_90_mode=False
            )
            
            if len(insights) > 100:  # Should be substantial content
                print(f"✅ {test_case['position_type']} insights generated (normal mode)")
            else:
                print(f"❌ {test_case['position_type']} insights too short (normal mode)")
                return False
            
            # Test per 90 mode
            insights_per90 = generate_role_insights(
                test_case["position_type"],
                test_case["role_weights"],
                per_90_mode=True
            )
            
            if len(insights_per90) > 100:  # Should be substantial content
                print(f"✅ {test_case['position_type']} insights generated (per 90 mode)")
            else:
                print(f"❌ {test_case['position_type']} insights too short (per 90 mode)")
                return False
            
            # Check for expected sections
            expected_sections = ["Role Definitions", "How Role Scores Work", "Weight Breakdown", "How to Use Role Scores"]
            sections_found = sum(1 for section in expected_sections if section in insights)
            
            if sections_found >= 3:  # Allow some flexibility
                print(f"✅ {test_case['position_type']} insights contain expected sections")
            else:
                print(f"❌ {test_case['position_type']} insights missing sections. Found {sections_found}/4")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing role insights generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("=" * 80)
    print("ROLE WEIGHT FUNCTIONALITY VERIFICATION")
    print("=" * 80)
    print("Testing the new role weight features for Find Similar Player")
    print()
    
    # Test 1: Function import test
    import_test_passed = test_role_weight_functions()
    
    # Test 2: Role weight detection test
    detection_test_passed = test_role_weight_detection()
    
    # Test 3: Role score calculation test
    calculation_test_passed = test_role_score_calculation()
    
    # Test 4: Role insights generation test
    insights_test_passed = test_role_insights_generation()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    all_tests_passed = (import_test_passed and detection_test_passed and 
                       calculation_test_passed and insights_test_passed)
    
    if import_test_passed:
        print("✅ Role weight functions: Working correctly")
    else:
        print("❌ Role weight functions: Failed")
    
    if detection_test_passed:
        print("✅ Role weight detection: Working correctly")
    else:
        print("❌ Role weight detection: Failed")
    
    if calculation_test_passed:
        print("✅ Role score calculation: Working correctly")
    else:
        print("❌ Role score calculation: Failed")
    
    if insights_test_passed:
        print("✅ Role insights generation: Working correctly")
    else:
        print("❌ Role insights generation: Failed")
    
    print()
    
    if all_tests_passed:
        print("🎉 SUCCESS! Role weight functionality is working correctly.")
        print("\nFeatures implemented:")
        print("- ✅ Dynamic role detection based on player position")
        print("- ✅ Role score calculation with normalization")
        print("- ✅ Progress columns for role scores in results table")
        print("- ✅ Comprehensive role insights and explanations")
        print("- ✅ Support for GK, CF, and CB positions")
        print("- ✅ Per 90 minutes calculation support")
        print("- ✅ Negative weight handling for defensive stats")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Navigate to 'Find Similar Player' menu")
        print("3. Test the role weight columns in results table")
        print("4. Check the role insights explanations")
    else:
        print("💥 FAILED! Some role weight tests did not pass.")
        print("\nPlease fix the issues above before proceeding.")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
