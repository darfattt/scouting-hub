import os
import pandas as pd
import numpy as np
import glob
from typing import List, Dict, Any

class GoalkeeperDataProcessor:
    """
    Class to process goalkeeper data from CSV files and prepare it for the RAG system.
    """

    def __init__(self, data_dir: str = "data/stats"):
        """
        Initialize the data processor.

        Args:
            data_dir: Directory containing the goalkeeper statistics CSV files
        """
        self.data_dir = data_dir
        self.league_stats_dir = os.path.join(os.path.dirname(data_dir), 'stats_league')
        self.all_data = None
        self.league_data = None
        self.player_data = {}

    def load_data(self) -> pd.DataFrame:
        """
        Load all goalkeeper data from CSV files in the data directory.

        Returns:
            DataFrame containing all goalkeeper data
        """
        # Get all CSV files in the data directory
        csv_files = glob.glob(os.path.join(self.data_dir, "*.csv"))

        all_data = []

        for file in csv_files:
            # Extract player name from filename
            filename = os.path.basename(file)
            # Format: "Team - Player Name (Stats).csv"
            parts = filename.split(" - ")
            if len(parts) < 2:
                continue

            team = parts[0]
            player_name = parts[1].split(" (Stats)")[0]

            # Read the CSV file
            try:
                df = pd.read_csv(file)
                # Add team and player name columns
                df['Team'] = team
                df['Player'] = player_name
                all_data.append(df)
            except Exception as e:
                print(f"Error loading {file}: {e}")

        if all_data:
            self.all_data = pd.concat(all_data, ignore_index=True)
            return self.all_data
        else:
            print("No data loaded.")
            return pd.DataFrame()

    def load_league_data(self) -> pd.DataFrame:
        """
        Load league statistics data from CSV files in the stats_league directory.
        This contains additional goalkeeper metrics like xG against, prevented goals, etc.

        Returns:
            DataFrame containing all league statistics data
        """
        if not os.path.exists(self.league_stats_dir):
            print(f"League stats directory not found: {self.league_stats_dir}")
            return pd.DataFrame()

        all_league_data = []

        # Load all CSV files from the league stats directory
        for filename in os.listdir(self.league_stats_dir):
            if filename.endswith('.csv'):
                file_path = os.path.join(self.league_stats_dir, filename)
                try:
                    df = pd.read_csv(file_path)
                    if not df.empty:
                        all_league_data.append(df)
                        print(f"Loaded league data from {filename}: {len(df)} records")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")

        if all_league_data:
            self.league_data = pd.concat(all_league_data, ignore_index=True)
            print(f"Total league records loaded: {len(self.league_data)}")
        else:
            self.league_data = pd.DataFrame()
            print("No league data loaded")

        return self.league_data

    def _get_league_stats_for_player(self, player_name: str, team_name: str) -> Dict:
        """
        Get league statistics for a specific player.

        Args:
            player_name: Name of the player
            team_name: Team name for additional matching

        Returns:
            Dictionary containing league statistics or empty dict if not found
        """
        if self.league_data is None or self.league_data.empty:
            return {}

        # Try to find the player in league data
        # First try exact name match
        player_match = self.league_data[self.league_data['Player'] == player_name]

        # If no exact match, try partial name matching
        if player_match.empty:
            # Try matching by last name or first name
            name_parts = player_name.split()
            if len(name_parts) > 1:
                for part in name_parts:
                    if len(part) > 2:  # Only consider meaningful name parts
                        player_match = self.league_data[self.league_data['Player'].str.contains(part, case=False, na=False)]
                        if not player_match.empty:
                            break

        # If still no match, try team-based filtering
        if player_match.empty and team_name != "Unknown":
            team_players = self.league_data[self.league_data['Team'].str.contains(team_name, case=False, na=False)]
            if not team_players.empty:
                # Try name matching within the team
                for _, row in team_players.iterrows():
                    league_player_name = row['Player']
                    # Check if names have common parts
                    if any(part in league_player_name for part in player_name.split() if len(part) > 2):
                        player_match = team_players[team_players['Player'] == league_player_name]
                        break

        if not player_match.empty:
            # Return the first match as a dictionary
            return player_match.iloc[0].to_dict()

        return {}

    def process_data(self) -> Dict[str, Any]:
        """
        Process the loaded data to create comprehensive goalkeeper profiles with all statistics.
        Combines match-by-match data with league statistics for complete profiles.

        Returns:
            Dictionary mapping player names to their comprehensive statistics
        """
        if self.all_data is None:
            self.load_data()

        if self.all_data.empty:
            return {}

        # Load league data for additional statistics
        if self.league_data is None:
            self.load_league_data()

        # Group by player
        player_groups = self.all_data.groupby('Player')

        for player_name, player_df in player_groups:
            # Calculate aggregate statistics with safe column access
            total_matches = len(player_df)

            # Helper function to safely sum columns
            def safe_sum(column_name):
                return player_df[column_name].sum() if column_name in player_df.columns else 0

            # Basic match info
            total_minutes = safe_sum('Minutes played')

            # Core goalkeeping stats
            total_conceded = safe_sum('Conceded goals')
            total_xcg = safe_sum('xCG')
            total_shots_against = safe_sum('Shots against')
            total_saves = safe_sum('Saves')
            total_saves_with_reflexes = safe_sum('Saves with reflexes')

            # Distribution stats
            total_exits = safe_sum('Exits')
            total_long_passes = safe_sum('Long passes')
            total_long_passes_accurate = safe_sum('Long passes accurate')
            total_short_passes = safe_sum('Short passes')
            total_short_passes_accurate = safe_sum('Short passes accurate')

            # Goal kick stats
            total_goal_kicks = safe_sum('Goal kicks')
            total_short_goal_kicks = safe_sum('Short goal kicks')
            total_long_goal_kicks = safe_sum('Long goal kicks')

            # Calculate accuracy percentages (only for available combinations)
            long_pass_accuracy = (total_long_passes_accurate / total_long_passes * 100) if total_long_passes > 0 else 0
            short_pass_accuracy = (total_short_passes_accurate / total_short_passes * 100) if total_short_passes > 0 else 0

            # Calculate core derived metrics
            save_percentage = (total_saves / total_shots_against * 100) if total_shots_against > 0 else 0
            goals_conceded_per_90 = (total_conceded / total_minutes * 90) if total_minutes > 0 else 0
            xcg_per_90 = (total_xcg / total_minutes * 90) if total_minutes > 0 else 0

            # Calculate performance vs expected
            xcg_difference = total_conceded - total_xcg if total_xcg > 0 else 0

            # Calculate per 90 minutes statistics
            def per_90(value):
                return (value / total_minutes * 90) if total_minutes > 0 else 0

            # Per 90 stats
            shots_against_per_90 = per_90(total_shots_against)
            saves_per_90 = per_90(total_saves)
            saves_with_reflexes_per_90 = per_90(total_saves_with_reflexes)
            exits_per_90 = per_90(total_exits)
            long_passes_per_90 = per_90(total_long_passes)
            long_passes_accurate_per_90 = per_90(total_long_passes_accurate)
            short_passes_per_90 = per_90(total_short_passes)
            short_passes_accurate_per_90 = per_90(total_short_passes_accurate)
            goal_kicks_per_90 = per_90(total_goal_kicks)
            short_goal_kicks_per_90 = per_90(total_short_goal_kicks)
            long_goal_kicks_per_90 = per_90(total_long_goal_kicks)

            # Get the most recent team and position
            most_recent_match = player_df.sort_values('Date', ascending=False).iloc[0]
            current_team = most_recent_match['Team']
            position = most_recent_match.get('Position', 'GK')

            # Try to get additional league statistics for this player
            league_stats = self._get_league_stats_for_player(player_name, current_team)

            # Create comprehensive goalkeeper profile
            self.player_data[player_name] = {
                # Basic info
                'name': player_name,
                'team': current_team,
                'position': position,
                'matches': total_matches,
                'minutes': total_minutes,

                # Core goalkeeping stats
                'conceded_goals': total_conceded,
                'xcg': total_xcg,
                'shots_against': total_shots_against,
                'saves': total_saves,
                'saves_with_reflexes': total_saves_with_reflexes,

                # Distribution stats
                'exits': total_exits,
                'long_passes': total_long_passes,
                'long_passes_accurate': total_long_passes_accurate,
                'short_passes': total_short_passes,
                'short_passes_accurate': total_short_passes_accurate,

                # Goal kick stats
                'goal_kicks': total_goal_kicks,
                'short_goal_kicks': total_short_goal_kicks,
                'long_goal_kicks': total_long_goal_kicks,

                # Accuracy percentages
                'long_pass_accuracy': long_pass_accuracy,
                'short_pass_accuracy': short_pass_accuracy,

                # Core derived metrics
                'save_percentage': save_percentage,
                'goals_conceded_per_90': goals_conceded_per_90,
                'xcg_per_90': xcg_per_90,
                'xcg_difference': xcg_difference,

                # Per 90 minutes stats
                'shots_against_per_90': shots_against_per_90,
                'saves_per_90': saves_per_90,
                'saves_with_reflexes_per_90': saves_with_reflexes_per_90,
                'exits_per_90': exits_per_90,
                'long_passes_per_90': long_passes_per_90,
                'long_passes_accurate_per_90': long_passes_accurate_per_90,
                'short_passes_per_90': short_passes_per_90,
                'short_passes_accurate_per_90': short_passes_accurate_per_90,
                'goal_kicks_per_90': goal_kicks_per_90,
                'short_goal_kicks_per_90': short_goal_kicks_per_90,
                'long_goal_kicks_per_90': long_goal_kicks_per_90,

                # Match data for detailed analysis
                'match_data': player_df.to_dict('records')
            }

            # Add league statistics if available (non-existing stats from league data)
            if league_stats:
                # Add new statistics from league data that don't exist in match data
                self.player_data[player_name].update({
                    # League-specific stats (non-existing in match data)
                    'xg_against': league_stats.get('xG against', 0),
                    'xg_against_per_90': league_stats.get('xG against per 90', 0),
                    'prevented_goals': league_stats.get('Prevented goals', 0),
                    'prevented_goals_per_90': league_stats.get('Prevented goals per 90', 0),
                    'clean_sheets': league_stats.get('Clean sheets', 0),
                    'save_rate_percent': league_stats.get('Save rate, %', 0),
                    'aerial_duels_per_90': league_stats.get('Aerial duels per 90', 0),

                    # Additional league info
                    'age': league_stats.get('Age', 0),
                    'league_matches': league_stats.get('Matches played', 0),
                    'league_minutes': league_stats.get('Minutes played', 0),

                    # Override some stats with league data if available (more accurate)
                    'goals_conceded_per_90_league': league_stats.get('Conceded goals per 90', goals_conceded_per_90),
                    'exits_per_90_league': league_stats.get('Exits per 90', exits_per_90),
                    'shots_against_per_90_league': league_stats.get('Shots against per 90', shots_against_per_90),
                })

                # Calculate additional derived metrics from league data
                clean_sheet_percentage = (league_stats.get('Clean sheets', 0) / max(league_stats.get('Matches played', 1), 1) * 100)
                self.player_data[player_name]['clean_sheet_percentage'] = clean_sheet_percentage

        return self.player_data

    def get_player_text_representation(self, player_name: str) -> str:
        """
        Create a text representation of a player's data for embedding.

        Args:
            player_name: Name of the player

        Returns:
            Text representation of the player's data
        """
        if not self.player_data:
            self.process_data()

        if player_name not in self.player_data:
            return ""

        player = self.player_data[player_name]

        # Create a detailed text representation
        text = f"Player: {player['name']}\n"
        text += f"Team: {player['team']}\n"
        text += f"Statistics Summary:\n"
        text += f"- Matches played: {player['matches']}\n"
        text += f"- Minutes played: {player['minutes']}\n"
        text += f"- Goals conceded: {player['conceded_goals']}\n"
        text += f"- Saves: {player['saves']}\n"
        text += f"- Shots against: {player['shots_against']}\n"
        text += f"- Save percentage: {player['save_percentage']:.2f}%\n"
        text += f"- Goals conceded per 90 minutes: {player['goals_conceded_per_90']:.2f}\n\n"

        # Add match-by-match data (limit to last 10 matches for brevity)
        text += "Recent Matches:\n"
        for match in player['match_data'][-10:]:
            text += f"- {match['Match']} ({match['Date']}): {match['Minutes played']} minutes, {match['Conceded goals']} goals conceded, {match['Saves']} saves\n"

        return text

    def get_all_player_texts(self) -> List[Dict[str, str]]:
        """
        Get text representations for all players.

        Returns:
            List of dictionaries with player names and their text representations
        """
        if not self.player_data:
            self.process_data()

        texts = []
        for player_name in self.player_data:
            text = self.get_player_text_representation(player_name)
            texts.append({
                'player': player_name,
                'content': text
            })

        return texts

class OutfieldDataProcessor:
    """
    Class to process outfield player data from CSV files and prepare it for the RAG system.
    Handles forwards, midfielders, and defenders.
    """

    def __init__(self, data_dir: str = "data/stats", position_filter: str = None):
        """
        Initialize the data processor.

        Args:
            data_dir: Directory containing the player statistics CSV files
            position_filter: Filter by specific position (e.g., 'Forward', 'Midfielder', 'Defender')
        """
        self.data_dir = data_dir
        self.position_filter = position_filter
        self.all_data = None
        self.player_data = {}

    def load_data(self) -> pd.DataFrame:
        """
        Load all outfield player data from CSV files in the data directory.

        Returns:
            DataFrame containing all outfield player data
        """
        # Get all CSV files in the data directory
        csv_files = glob.glob(os.path.join(self.data_dir, "*.csv"))

        all_data = []

        for file in csv_files:
            # Extract player name from filename
            filename = os.path.basename(file)

            # Handle different filename formats
            if " - " in filename:
                # Format: "Team - Player Name (Stats).csv"
                parts = filename.split(" - ")
                if len(parts) >= 2:
                    team = parts[0]
                    player_name = parts[1].split(" (Stats)")[0]
                else:
                    continue
            elif filename.startswith("Player stats "):
                # Format: "Player stats Player Name.csv"
                player_name = filename.replace("Player stats ", "").replace(".csv", "")
                team = "Unknown"
            else:
                # Skip files that don't match expected formats
                continue

            # Read the CSV file
            try:
                df = pd.read_csv(file)

                # Check if this is outfield player data
                # Must have Position column AND outfield-specific columns
                required_outfield_columns = ['Goals', 'Assists', 'Passes']
                has_position = 'Position' in df.columns
                has_outfield_stats = all(col in df.columns for col in required_outfield_columns)

                # Skip if this looks like goalkeeper data
                goalkeeper_columns = ['Saves', 'Conceded goals', 'Shots against']
                is_goalkeeper_data = any(col in df.columns for col in goalkeeper_columns)

                # Debug info (can be removed later)
                # print(f"  File: {filename}")
                # print(f"    Has position: {has_position}")
                # print(f"    Has outfield stats: {has_outfield_stats}")
                # print(f"    Is goalkeeper data: {is_goalkeeper_data}")

                if has_position and has_outfield_stats and not is_goalkeeper_data:
                    # Filter out goalkeepers by position
                    df = df[~df['Position'].str.contains('Goalkeeper|GK|Goalie', case=False, na=False)]

                    # Apply position filter if specified (using regex for exact position matching)
                    if self.position_filter:
                        # Use regex to match exact position codes
                        df = df[df['Position'].str.contains(self.position_filter, case=False, na=False, regex=True)]

                    if not df.empty:
                        # Add team and player name columns
                        df['Team'] = team
                        df['Player'] = player_name
                        all_data.append(df)

            except Exception as e:
                print(f"Error loading {file}: {e}")

        if all_data:
            self.all_data = pd.concat(all_data, ignore_index=True)
            return self.all_data
        else:
            print("No outfield player data loaded.")
            return pd.DataFrame()

    def process_data(self) -> Dict[str, Any]:
        """
        Process the loaded data to create structured player profiles with comprehensive statistics.

        Returns:
            Dictionary mapping player names to their statistics
        """
        if self.all_data is None:
            self.load_data()

        # Handle case where no data was loaded
        if self.all_data is None or self.all_data.empty:
            return {}

        # Group by player
        player_groups = self.all_data.groupby('Player')

        for player_name, player_df in player_groups:
            # Calculate aggregate statistics with safe column access
            total_matches = len(player_df)

            # Helper function to safely sum columns
            def safe_sum(column_name):
                return player_df[column_name].sum() if column_name in player_df.columns else 0

            # Basic match info
            total_minutes = safe_sum('Minutes played')

            # General stats
            total_actions = safe_sum('Total actions')
            total_actions_successful = safe_sum('Total actions successful')

            # Offensive stats
            total_goals = safe_sum('Goals')
            total_assists = safe_sum('Assists')
            total_shots = safe_sum('Shots')
            total_shots_on_target = safe_sum('Shots on target')
            total_xg = safe_sum('xG')

            # Passing stats
            total_passes = safe_sum('Passes')
            total_passes_accurate = safe_sum('Passes accurate')
            total_long_passes = safe_sum('Long passes')
            total_long_passes_accurate = safe_sum('Long passes accurate')

            # Crossing stats
            total_crosses = safe_sum('Crosses')
            total_crosses_accurate = safe_sum('Crosses accurate')

            # Dribbling stats
            total_dribbles = safe_sum('Dribbles')
            total_dribbles_successful = safe_sum('Dribbles successful')

            # Dueling stats
            total_duels = safe_sum('Duels')
            total_duels_won = safe_sum('Duels won')
            total_aerial_duels = safe_sum('Aerial duels')
            total_aerial_duels_won = safe_sum('Aerial duels won')

            # Defensive stats
            total_interceptions = safe_sum('Interceptions')
            total_losses = safe_sum('Losses')
            total_losses_own_half = safe_sum('Losses own half')
            total_recoveries = safe_sum('Recoveries')
            total_recoveries_opp_half = safe_sum('Recoveries opp. half')

            # Calculate success rates (only for available combinations)
            total_actions_success_rate = (total_actions_successful / total_actions * 100) if total_actions > 0 else 0
            pass_accuracy = (total_passes_accurate / total_passes * 100) if total_passes > 0 else 0
            long_pass_accuracy = (total_long_passes_accurate / total_long_passes * 100) if total_long_passes > 0 else 0
            cross_accuracy = (total_crosses_accurate / total_crosses * 100) if total_crosses > 0 else 0
            dribble_success_rate = (total_dribbles_successful / total_dribbles * 100) if total_dribbles > 0 else 0
            duel_success_rate = (total_duels_won / total_duels * 100) if total_duels > 0 else 0
            aerial_duel_success_rate = (total_aerial_duels_won / total_aerial_duels * 100) if total_aerial_duels > 0 else 0

            # Additional derived metrics
            shot_accuracy = (total_shots_on_target / total_shots * 100) if total_shots > 0 else 0

            # Calculate per 90 minutes statistics
            def per_90(value):
                return (value / total_minutes * 90) if total_minutes > 0 else 0

            # Per 90 stats
            goals_per_90 = per_90(total_goals)
            assists_per_90 = per_90(total_assists)
            shots_per_90 = per_90(total_shots)
            shots_on_target_per_90 = per_90(total_shots_on_target)
            xg_per_90 = per_90(total_xg)
            passes_per_90 = per_90(total_passes)
            passes_accurate_per_90 = per_90(total_passes_accurate)
            long_passes_per_90 = per_90(total_long_passes)
            long_passes_accurate_per_90 = per_90(total_long_passes_accurate)
            crosses_per_90 = per_90(total_crosses)
            crosses_accurate_per_90 = per_90(total_crosses_accurate)
            dribbles_per_90 = per_90(total_dribbles)
            dribbles_successful_per_90 = per_90(total_dribbles_successful)
            duels_per_90 = per_90(total_duels)
            duels_won_per_90 = per_90(total_duels_won)
            aerial_duels_per_90 = per_90(total_aerial_duels)
            aerial_duels_won_per_90 = per_90(total_aerial_duels_won)
            interceptions_per_90 = per_90(total_interceptions)
            losses_per_90 = per_90(total_losses)
            losses_own_half_per_90 = per_90(total_losses_own_half)
            recoveries_per_90 = per_90(total_recoveries)
            recoveries_opp_half_per_90 = per_90(total_recoveries_opp_half)
            total_actions_per_90 = per_90(total_actions)
            total_actions_successful_per_90 = per_90(total_actions_successful)

            # Get the most recent team and position
            most_recent_match = player_df.sort_values('Date', ascending=False).iloc[0]
            current_team = most_recent_match['Team']
            position = most_recent_match['Position']

            # Handle yellow and red cards (convert minutes to counts)
            yellow_cards = 0
            red_cards = 0
            for _, match in player_df.iterrows():
                if 'Yellow card' in match and pd.notna(match.get('Yellow card', np.nan)) and match['Yellow card'] > 0:
                    yellow_cards += 1
                if 'Red card' in match and pd.notna(match.get('Red card', np.nan)) and match['Red card'] > 0:
                    red_cards += 1

            # Create comprehensive player profile
            self.player_data[player_name] = {
                # Basic info
                'name': player_name,
                'team': current_team,
                'position': position,
                'matches': total_matches,
                'minutes': total_minutes,

                # General stats
                'total_actions': total_actions,
                'total_actions_successful': total_actions_successful,

                # Offensive stats
                'goals': total_goals,
                'assists': total_assists,
                'shots': total_shots,
                'shots_on_target': total_shots_on_target,
                'xg': total_xg,

                # Passing stats
                'passes': total_passes,
                'passes_accurate': total_passes_accurate,
                'long_passes': total_long_passes,
                'long_passes_accurate': total_long_passes_accurate,

                # Crossing stats
                'crosses': total_crosses,
                'crosses_accurate': total_crosses_accurate,

                # Dribbling stats
                'dribbles': total_dribbles,
                'dribbles_successful': total_dribbles_successful,

                # Dueling stats
                'duels': total_duels,
                'duels_won': total_duels_won,
                'aerial_duels': total_aerial_duels,
                'aerial_duels_won': total_aerial_duels_won,

                # Defensive stats
                'interceptions': total_interceptions,
                'losses': total_losses,
                'losses_own_half': total_losses_own_half,
                'recoveries': total_recoveries,
                'recoveries_opp_half': total_recoveries_opp_half,

                # Cards
                'yellow_cards': yellow_cards,
                'red_cards': red_cards,

                # Success rates
                'total_actions_success_rate': total_actions_success_rate,
                'pass_accuracy': pass_accuracy,
                'long_pass_accuracy': long_pass_accuracy,
                'cross_accuracy': cross_accuracy,
                'dribble_success_rate': dribble_success_rate,
                'duel_success_rate': duel_success_rate,
                'aerial_duel_success_rate': aerial_duel_success_rate,
                'shot_accuracy': shot_accuracy,

                # Per 90 minutes stats
                'goals_per_90': goals_per_90,
                'assists_per_90': assists_per_90,
                'shots_per_90': shots_per_90,
                'shots_on_target_per_90': shots_on_target_per_90,
                'xg_per_90': xg_per_90,
                'passes_per_90': passes_per_90,
                'passes_accurate_per_90': passes_accurate_per_90,
                'long_passes_per_90': long_passes_per_90,
                'long_passes_accurate_per_90': long_passes_accurate_per_90,
                'crosses_per_90': crosses_per_90,
                'crosses_accurate_per_90': crosses_accurate_per_90,
                'dribbles_per_90': dribbles_per_90,
                'dribbles_successful_per_90': dribbles_successful_per_90,
                'duels_per_90': duels_per_90,
                'duels_won_per_90': duels_won_per_90,
                'aerial_duels_per_90': aerial_duels_per_90,
                'aerial_duels_won_per_90': aerial_duels_won_per_90,
                'interceptions_per_90': interceptions_per_90,
                'losses_per_90': losses_per_90,
                'losses_own_half_per_90': losses_own_half_per_90,
                'recoveries_per_90': recoveries_per_90,
                'recoveries_opp_half_per_90': recoveries_opp_half_per_90,
                'total_actions_per_90': total_actions_per_90,
                'total_actions_successful_per_90': total_actions_successful_per_90,

                # Match data for detailed analysis
                'match_data': player_df.to_dict('records')
            }

        return self.player_data

    def get_player_text_representation(self, player_name: str) -> str:
        """
        Create a comprehensive text representation of a player's data for embedding.
        Includes playing style analysis, role-based comparisons, and tactical insights.

        Args:
            player_name: Name of the player

        Returns:
            Rich text representation of the player's data with tactical analysis
        """
        if not self.player_data:
            self.process_data()

        if player_name not in self.player_data:
            return ""

        player = self.player_data[player_name]
        position = player.get('position', 'Unknown')

        # Create comprehensive text representation
        text = f"Player Profile: {player['name']}\n"
        text += f"Team: {player['team']}\n"
        text += f"Position: {position}\n"
        text += f"Experience: {player['matches']} matches, {player['minutes']} minutes played\n\n"

        # Add playing style analysis based on position
        text += self._get_playing_style_analysis(player, position)

        # Add comprehensive statistics
        text += f"\n=== COMPREHENSIVE STATISTICS ===\n"

        # General Performance
        text += f"\nGeneral Performance:\n"
        text += f"- Match Appearances: {player['matches']} matches\n"
        text += f"- Minutes Played: {player['minutes']} minutes ({player['minutes']/player['matches']:.1f} avg per match)\n"

        # Position-specific statistics
        if 'GK' in position or 'Goalkeeper' in position:
            # Goalkeeper-specific statistics
            text += f"\nGoalkeeping Performance:\n"
            text += f"- Goals Conceded: {player.get('conceded_goals', 0)} ({player.get('goals_conceded_per_90', 0):.2f} per 90 min)\n"
            if 'xcg' in player:
                text += f"- Expected Goals Conceded (xCG): {player['xcg']:.2f} ({player.get('xcg_per_90', 0):.2f} per 90 min)\n"
                xcg_diff = player.get('xcg_difference', 0)
                if xcg_diff < -1:
                    text += f"- Performance vs Expected: Overperforming by {abs(xcg_diff):.1f} goals (excellent)\n"
                elif xcg_diff > 1:
                    text += f"- Performance vs Expected: Underperforming by {xcg_diff:.1f} goals\n"
                else:
                    text += f"- Performance vs Expected: Performing as expected\n"

            # Add league-specific xG against stats if available
            if 'xg_against' in player and player['xg_against'] > 0:
                text += f"- Expected Goals Against (League): {player['xg_against']:.2f} ({player.get('xg_against_per_90', 0):.2f} per 90 min)\n"

            # Add prevented goals if available
            if 'prevented_goals' in player:
                text += f"- Prevented Goals: {player['prevented_goals']:.2f} ({player.get('prevented_goals_per_90', 0):.3f} per 90 min)\n"

            text += f"- Shots Faced: {player.get('shots_against', 0)} ({player.get('shots_against_per_90', 0):.1f} per 90 min)\n"
            text += f"- Saves: {player.get('saves', 0)} ({player.get('save_percentage', 0):.1f}% save rate)\n"

            # Add league save rate if different/available
            if 'save_rate_percent' in player and player['save_rate_percent'] != player.get('save_percentage', 0):
                text += f"- Save Rate (League): {player['save_rate_percent']:.1f}%\n"

            if 'saves_with_reflexes' in player:
                text += f"- Reflex Saves: {player['saves_with_reflexes']} ({player.get('saves_with_reflexes_per_90', 0):.1f} per 90 min)\n"

            # Add clean sheets information
            if 'clean_sheets' in player:
                text += f"- Clean Sheets: {player['clean_sheets']} ({player.get('clean_sheet_percentage', 0):.1f}% of matches)\n"

            text += f"\nDistribution and Passing:\n"
            if 'long_passes' in player:
                text += f"- Long Passes: {player['long_passes']} ({player.get('long_passes_accurate', 0)} accurate, {player.get('long_pass_accuracy', 0):.1f}% accuracy)\n"
            if 'short_passes' in player:
                text += f"- Short Passes: {player['short_passes']} ({player.get('short_passes_accurate', 0)} accurate, {player.get('short_pass_accuracy', 0):.1f}% accuracy)\n"

            text += f"\nSweeping and Activity:\n"
            if 'exits' in player:
                text += f"- Exits: {player['exits']} ({player.get('exits_per_90', 0):.1f} per 90 min)\n"

            # Add aerial duels from league data if available
            if 'aerial_duels_per_90' in player and player['aerial_duels_per_90'] > 0:
                text += f"- Aerial Duels: {player['aerial_duels_per_90']:.1f} per 90 min\n"

            if 'goal_kicks' in player:
                text += f"- Goal Kicks: {player['goal_kicks']} ({player.get('short_goal_kicks', 0)} short, {player.get('long_goal_kicks', 0)} long)\n"

            # Add age information if available from league data
            if 'age' in player and player['age'] > 0:
                text += f"- Age: {player['age']} years old\n"

        else:
            # Outfield player statistics
            if 'total_actions' in player:
                text += f"- Total Actions: {player['total_actions']} ({player.get('total_actions_success_rate', 0):.1f}% success rate)\n"

            # Offensive Contribution
            text += f"\nOffensive Contribution:\n"
            text += f"- Goals: {player.get('goals', 0)} ({player.get('goals_per_90', 0):.2f} per 90 min)\n"
            text += f"- Assists: {player.get('assists', 0)} ({player.get('assists_per_90', 0):.2f} per 90 min)\n"
            text += f"- Shots: {player.get('shots', 0)} ({player.get('shots_on_target', 0)} on target, {player.get('shot_accuracy', 0):.1f}% accuracy)\n"
            if 'xg' in player:
                text += f"- Expected Goals (xG): {player['xg']:.2f} ({player.get('xg_per_90', 0):.2f} per 90 min)\n"
                if player.get('goals', 0) > 0 and player['xg'] > 0:
                    xg_ratio = player['goals'] / player['xg']
                    if xg_ratio > 1.1:
                        text += f"- Finishing: Clinical finisher (outperforming xG by {((xg_ratio-1)*100):.1f}%)\n"
                    elif xg_ratio < 0.9:
                        text += f"- Finishing: Underperforming xG by {((1-xg_ratio)*100):.1f}%\n"
                    else:
                        text += f"- Finishing: Performing as expected relative to xG\n"

            # Passing and Distribution
            text += f"\nPassing and Distribution:\n"
            text += f"- Passes: {player.get('passes', 0)} ({player.get('passes_accurate', 0)} accurate, {player.get('pass_accuracy', 0):.1f}% accuracy)\n"
            if 'long_passes' in player:
                text += f"- Long Passes: {player['long_passes']} ({player.get('long_passes_accurate', 0)} accurate, {player.get('long_pass_accuracy', 0):.1f}% accuracy)\n"
            if 'crosses' in player:
                text += f"- Crosses: {player['crosses']} ({player.get('crosses_accurate', 0)} accurate, {player.get('cross_accuracy', 0):.1f}% accuracy)\n"

            # Dribbling and Individual Skills
            text += f"\nDribbling and Individual Skills:\n"
            text += f"- Dribbles: {player.get('dribbles', 0)} ({player.get('dribbles_successful', 0)} successful, {player.get('dribble_success_rate', 0):.1f}% success rate)\n"

            # Defensive Actions
            text += f"\nDefensive Actions:\n"
            text += f"- Duels: {player.get('duels', 0)} ({player.get('duels_won', 0)} won, {player.get('duel_success_rate', 0):.1f}% success rate)\n"
            if 'aerial_duels' in player:
                text += f"- Aerial Duels: {player['aerial_duels']} ({player.get('aerial_duels_won', 0)} won, {player.get('aerial_duel_success_rate', 0):.1f}% success rate)\n"
            text += f"- Interceptions: {player.get('interceptions', 0)}\n"
            text += f"- Recoveries: {player.get('recoveries', 0)}\n"
            if 'recoveries_opp_half' in player:
                text += f"- Recoveries in Opposition Half: {player['recoveries_opp_half']}\n"
            if 'losses' in player:
                text += f"- Ball Losses: {player['losses']} ({player.get('losses_own_half', 0)} in own half)\n"

            # Disciplinary Record
            text += f"\nDisciplinary Record:\n"
            text += f"- Yellow Cards: {player.get('yellow_cards', 0)}\n"
            text += f"- Red Cards: {player.get('red_cards', 0)}\n"
            if player['matches'] > 0:
                cards_per_match = (player.get('yellow_cards', 0) + player.get('red_cards', 0)) / player['matches']
                if cards_per_match > 0.3:
                    text += f"- Discipline: High card rate ({cards_per_match:.2f} cards per match)\n"
                elif cards_per_match < 0.1:
                    text += f"- Discipline: Excellent discipline ({cards_per_match:.2f} cards per match)\n"
                else:
                    text += f"- Discipline: Average discipline ({cards_per_match:.2f} cards per match)\n"

        # Add role-based comparison
        text += self._get_role_based_comparison(player, position)

        # Add recent form analysis
        text += self._get_recent_form_analysis(player)

        return text

    def _get_playing_style_analysis(self, player: Dict, position: str) -> str:
        """
        Analyze player's playing style based on statistics and position.
        """
        text = f"\n=== PLAYING STYLE ANALYSIS ===\n"

        # Position-specific analysis
        if 'CB' in position or 'Center Back' in position or position == 'Defenders':
            text += self._analyze_center_back_style(player)
        elif 'CF' in position or 'Center Forward' in position or position == 'Forwards':
            text += self._analyze_center_forward_style(player)
        elif 'GK' in position or 'Goalkeeper' in position:
            text += self._analyze_goalkeeper_style(player)
        elif any(pos in position for pos in ['LB', 'RB', 'LWB', 'RWB']):
            text += self._analyze_fullback_style(player)
        elif any(pos in position for pos in ['CM', 'CDM', 'CAM', 'LM', 'RM']):
            text += self._analyze_midfielder_style(player)
        elif any(pos in position for pos in ['LW', 'RW', 'LWF', 'RWF']):
            text += self._analyze_winger_style(player)
        else:
            text += self._analyze_generic_outfield_style(player)

        return text

    def _analyze_center_back_style(self, player: Dict) -> str:
        """Analyze center back playing style."""
        text = "\nCenter Back Style Analysis:\n"

        # Calculate key ratios for style determination
        passes_per_90 = player.get('passes_per_90', player.get('passes', 0) * 90 / max(player.get('minutes', 1), 1))
        long_passes_per_90 = player.get('long_passes_per_90', player.get('long_passes', 0) * 90 / max(player.get('minutes', 1), 1))
        aerial_duels_per_90 = player.get('aerial_duels_per_90', player.get('aerial_duels', 0) * 90 / max(player.get('minutes', 1), 1))
        pass_accuracy = player.get('pass_accuracy', 0)
        aerial_success = player.get('aerial_duel_success_rate', 0)

        # Determine playing style
        if passes_per_90 > 60 and pass_accuracy > 85 and long_passes_per_90 > 8:
            style = "Ball Playing Defender"
            text += f"- Primary Style: {style}\n"
            text += f"- Characteristics: Excellent distribution ({passes_per_90:.1f} passes per 90, {pass_accuracy:.1f}% accuracy)\n"
            text += f"- Strengths: Long passing ({long_passes_per_90:.1f} per 90), building play from the back\n"
        elif aerial_duels_per_90 > 4 and aerial_success > 65:
            style = "No-Nonsense Centre-Back"
            text += f"- Primary Style: {style}\n"
            text += f"- Characteristics: Strong aerial presence ({aerial_duels_per_90:.1f} aerial duels per 90, {aerial_success:.1f}% success)\n"
            text += f"- Strengths: Physical defending, winning headers, clearing danger\n"
        elif pass_accuracy > 80 and passes_per_90 > 45:
            style = "Central Defender"
            text += f"- Primary Style: {style}\n"
            text += f"- Characteristics: Balanced approach with good passing ({pass_accuracy:.1f}% accuracy)\n"
            text += f"- Strengths: Reliable distribution, solid defensive fundamentals\n"
        else:
            style = "Defensive Specialist"
            text += f"- Primary Style: {style}\n"
            text += f"- Characteristics: Focus on defensive actions and positioning\n"
            text += f"- Strengths: Interceptions, recoveries, defensive stability\n"

        # Add tactical insights
        interceptions_per_90 = player.get('interceptions_per_90', player.get('interceptions', 0) * 90 / max(player.get('minutes', 1), 1))
        if interceptions_per_90 > 1.5:
            text += f"- Tactical Note: High interception rate ({interceptions_per_90:.1f} per 90) suggests excellent reading of the game\n"

        return text

    def _analyze_center_forward_style(self, player: Dict) -> str:
        """Analyze center forward playing style."""
        text = "\nCenter Forward Style Analysis:\n"

        # Calculate key metrics
        goals_per_90 = player.get('goals_per_90', 0)
        shots_per_90 = player.get('shots_per_90', player.get('shots', 0) * 90 / max(player.get('minutes', 1), 1))
        assists_per_90 = player.get('assists_per_90', 0)
        dribbles_per_90 = player.get('dribbles_per_90', player.get('dribbles', 0) * 90 / max(player.get('minutes', 1), 1))
        duels_per_90 = player.get('duels_per_90', player.get('duels', 0) * 90 / max(player.get('minutes', 1), 1))

        # Determine style
        if goals_per_90 > 0.7 and shots_per_90 > 4:
            if assists_per_90 < 0.3:
                style = "Poacher"
                text += f"- Primary Style: {style}\n"
                text += f"- Characteristics: Clinical finisher ({goals_per_90:.2f} goals per 90, {shots_per_90:.1f} shots per 90)\n"
                text += f"- Strengths: Positioning in the box, converting chances\n"
            else:
                style = "Complete Forward"
                text += f"- Primary Style: {style}\n"
                text += f"- Characteristics: Goals and assists ({goals_per_90:.2f} goals, {assists_per_90:.2f} assists per 90)\n"
                text += f"- Strengths: Finishing and creating for teammates\n"
        elif assists_per_90 > 0.4 or dribbles_per_90 > 3:
            style = "Deep-lying Forward"
            text += f"- Primary Style: {style}\n"
            text += f"- Characteristics: Creative contribution ({assists_per_90:.2f} assists, {dribbles_per_90:.1f} dribbles per 90)\n"
            text += f"- Strengths: Link-up play, creating chances for others\n"
        elif duels_per_90 > 8:
            style = "Pressing Forward"
            text += f"- Primary Style: {style}\n"
            text += f"- Characteristics: High work rate ({duels_per_90:.1f} duels per 90)\n"
            text += f"- Strengths: Pressing, physical presence, disrupting opposition\n"
        else:
            style = "Advance Forward"
            text += f"- Primary Style: {style}\n"
            text += f"- Characteristics: Balanced attacking approach\n"
            text += f"- Strengths: Versatile attacking contribution\n"

        return text

    def _analyze_generic_outfield_style(self, player: Dict) -> str:
        """Analyze generic outfield player style."""
        text = f"\n{player.get('position', 'Outfield')} Style Analysis:\n"

        # Calculate key metrics
        passes_per_90 = player.get('passes_per_90', player.get('passes', 0) * 90 / max(player.get('minutes', 1), 1))
        dribbles_per_90 = player.get('dribbles_per_90', player.get('dribbles', 0) * 90 / max(player.get('minutes', 1), 1))
        duels_per_90 = player.get('duels_per_90', player.get('duels', 0) * 90 / max(player.get('minutes', 1), 1))
        goals_assists_per_90 = player.get('goals_per_90', 0) + player.get('assists_per_90', 0)

        # Determine primary characteristics
        if passes_per_90 > 50:
            text += f"- Primary Trait: Playmaker (high passing volume: {passes_per_90:.1f} per 90)\n"
        if dribbles_per_90 > 3:
            text += f"- Primary Trait: Skillful dribbler ({dribbles_per_90:.1f} dribbles per 90)\n"
        if duels_per_90 > 8:
            text += f"- Primary Trait: Physical player (high duel involvement: {duels_per_90:.1f} per 90)\n"
        if goals_assists_per_90 > 0.5:
            text += f"- Primary Trait: Goal contributor ({goals_assists_per_90:.2f} goals+assists per 90)\n"

        return text

    def _analyze_goalkeeper_style(self, player: Dict) -> str:
        """Analyze goalkeeper playing style with comprehensive role-based analysis."""
        text = "\nGoalkeeper Style Analysis:\n"

        # Calculate key metrics for style determination
        save_percentage = player.get('save_percentage', 0)
        long_pass_accuracy = player.get('long_pass_accuracy', 0)
        short_pass_accuracy = player.get('short_pass_accuracy', 0)
        exits_per_90 = player.get('exits_per_90', player.get('exits', 0) * 90 / max(player.get('minutes', 1), 1))
        long_passes_per_90 = player.get('long_passes_per_90', player.get('long_passes', 0) * 90 / max(player.get('minutes', 1), 1))
        short_passes_per_90 = player.get('short_passes_per_90', player.get('short_passes', 0) * 90 / max(player.get('minutes', 1), 1))
        saves_with_reflexes_per_90 = player.get('saves_with_reflexes_per_90', player.get('saves_with_reflexes', 0) * 90 / max(player.get('minutes', 1), 1))
        xcg_difference = player.get('xcg_difference', 0)

        # Determine goalkeeper style based on characteristics
        if long_pass_accuracy > 70 and long_passes_per_90 > 15:
            if short_pass_accuracy > 85 and short_passes_per_90 > 20:
                style = "Complete Sweeper Keeper"
                text += f"- Primary Style: {style}\n"
                text += f"- Characteristics: Excellent distribution (long: {long_pass_accuracy:.1f}%, short: {short_pass_accuracy:.1f}%)\n"
                text += f"- Strengths: Both long and short passing, modern goalkeeper with feet\n"
            else:
                style = "Distribution Specialist"
                text += f"- Primary Style: {style}\n"
                text += f"- Characteristics: Strong long passing ({long_pass_accuracy:.1f}% accuracy, {long_passes_per_90:.1f} per 90)\n"
                text += f"- Strengths: Long-range distribution, launching attacks from the back\n"
        elif short_pass_accuracy > 85 and short_passes_per_90 > 25:
            style = "Ball-Playing Goalkeeper"
            text += f"- Primary Style: {style}\n"
            text += f"- Characteristics: Excellent short passing ({short_pass_accuracy:.1f}% accuracy, {short_passes_per_90:.1f} per 90)\n"
            text += f"- Strengths: Building play from the back, comfortable with feet\n"
        elif exits_per_90 > 1.5:
            style = "Sweeper Keeper"
            text += f"- Primary Style: {style}\n"
            text += f"- Characteristics: Active off the line ({exits_per_90:.1f} exits per 90)\n"
            text += f"- Strengths: Reading the game, coming out to clear danger\n"
        elif save_percentage > 75 or saves_with_reflexes_per_90 > 2:
            style = "Shot Stopper"
            text += f"- Primary Style: {style}\n"
            text += f"- Characteristics: Excellent shot stopping ({save_percentage:.1f}% save rate)\n"
            text += f"- Strengths: Reflexes, positioning, making crucial saves\n"
        else:
            style = "Traditional Goalkeeper"
            text += f"- Primary Style: {style}\n"
            text += f"- Characteristics: Balanced approach to goalkeeping\n"
            text += f"- Strengths: Reliable shot stopping and basic distribution\n"

        # Add performance analysis
        if xcg_difference < -2:
            text += f"- Performance Note: Overperforming expected goals conceded by {abs(xcg_difference):.1f} goals\n"
        elif xcg_difference > 2:
            text += f"- Performance Note: Underperforming expected goals conceded by {xcg_difference:.1f} goals\n"
        else:
            text += f"- Performance Note: Performing close to expected level\n"

        # Add tactical insights
        total_passes_per_90 = long_passes_per_90 + short_passes_per_90
        if total_passes_per_90 > 40:
            text += f"- Tactical Note: High passing volume ({total_passes_per_90:.1f} per 90) indicates involvement in build-up play\n"

        return text

    def _analyze_fullback_style(self, player: Dict) -> str:
        """Analyze fullback playing style."""
        text = "\nFullback Style Analysis:\n"
        crosses_per_90 = player.get('crosses_per_90', player.get('crosses', 0) * 90 / max(player.get('minutes', 1), 1))
        assists_per_90 = player.get('assists_per_90', 0)

        if crosses_per_90 > 3 or assists_per_90 > 0.3:
            text += f"- Style: Attacking Fullback (offensive contribution)\n"
        else:
            text += f"- Style: Defensive Fullback (defensive focus)\n"

        return text

    def _analyze_midfielder_style(self, player: Dict) -> str:
        """Analyze midfielder playing style."""
        text = "\nMidfielder Style Analysis:\n"
        passes_per_90 = player.get('passes_per_90', player.get('passes', 0) * 90 / max(player.get('minutes', 1), 1))
        goals_assists_per_90 = player.get('goals_per_90', 0) + player.get('assists_per_90', 0)

        if passes_per_90 > 60:
            text += f"- Style: Deep-lying Playmaker (high passing volume)\n"
        elif goals_assists_per_90 > 0.4:
            text += f"- Style: Attacking Midfielder (goal contribution)\n"
        else:
            text += f"- Style: Box-to-Box Midfielder (balanced contribution)\n"

        return text

    def _analyze_winger_style(self, player: Dict) -> str:
        """Analyze winger playing style."""
        text = "\nWinger Style Analysis:\n"
        dribbles_per_90 = player.get('dribbles_per_90', player.get('dribbles', 0) * 90 / max(player.get('minutes', 1), 1))
        crosses_per_90 = player.get('crosses_per_90', player.get('crosses', 0) * 90 / max(player.get('minutes', 1), 1))

        if dribbles_per_90 > 4:
            text += f"- Style: Skillful Winger (high dribbling)\n"
        elif crosses_per_90 > 4:
            text += f"- Style: Traditional Winger (crossing focus)\n"
        else:
            text += f"- Style: Inside Forward (cutting inside)\n"

        return text

    def _get_role_based_comparison(self, player: Dict, position: str) -> str:
        """
        Generate role-based comparison text for the player.
        """
        text = f"\n=== ROLE-BASED COMPARISON ===\n"

        if 'GK' in position or 'Goalkeeper' in position:
            text += "\nGoalkeeper Role Comparison:\n"
            text += "- Complete Sweeper Keeper: Excellent in all areas - shot stopping, distribution, and sweeping\n"
            text += "- Ball-Playing Goalkeeper: Focuses on short passing and building play from the back\n"
            text += "- Distribution Specialist: Strong long passing to launch attacks quickly\n"
            text += "- Sweeper Keeper: Active off the line, reads the game well, clears danger\n"
            text += "- Shot Stopper: Traditional goalkeeper focused on making saves and reflexes\n"
            text += "- Traditional Goalkeeper: Balanced approach with reliable shot stopping\n"

            # Determine best fit for goalkeepers
            save_percentage = player.get('save_percentage', 0)
            long_pass_accuracy = player.get('long_pass_accuracy', 0)
            short_pass_accuracy = player.get('short_pass_accuracy', 0)
            exits_per_90 = player.get('exits_per_90', player.get('exits', 0) * 90 / max(player.get('minutes', 1), 1))
            long_passes_per_90 = player.get('long_passes_per_90', player.get('long_passes', 0) * 90 / max(player.get('minutes', 1), 1))
            short_passes_per_90 = player.get('short_passes_per_90', player.get('short_passes', 0) * 90 / max(player.get('minutes', 1), 1))

            if long_pass_accuracy > 70 and long_passes_per_90 > 15 and short_pass_accuracy > 85 and short_passes_per_90 > 20:
                text += f"\nBest Role Fit: Complete Sweeper Keeper (excellent in all areas)\n"
            elif short_pass_accuracy > 85 and short_passes_per_90 > 25:
                text += f"\nBest Role Fit: Ball-Playing Goalkeeper (excellent short passing)\n"
            elif long_pass_accuracy > 70 and long_passes_per_90 > 15:
                text += f"\nBest Role Fit: Distribution Specialist (strong long passing)\n"
            elif exits_per_90 > 1.5:
                text += f"\nBest Role Fit: Sweeper Keeper (active off the line)\n"
            elif save_percentage > 75:
                text += f"\nBest Role Fit: Shot Stopper (excellent save percentage)\n"
            else:
                text += f"\nBest Role Fit: Traditional Goalkeeper (balanced profile)\n"

        elif 'CB' in position or 'Center Back' in position:
            text += "\nCenter Back Role Comparison:\n"
            text += "- Ball Playing Defender: Focuses on distribution and building play from the back\n"
            text += "- Central Defender: Balanced approach with solid defending and decent passing\n"
            text += "- No-Nonsense Centre-Back: Physical defender who clears danger and wins aerial duels\n"
            text += "- Wide Defender: Covers wide areas and supports fullbacks\n"

            # Determine best fit
            passes_per_90 = player.get('passes_per_90', player.get('passes', 0) * 90 / max(player.get('minutes', 1), 1))
            aerial_success = player.get('aerial_duel_success_rate', 0)

            if passes_per_90 > 60:
                text += f"\nBest Role Fit: Ball Playing Defender (based on high passing volume)\n"
            elif aerial_success > 65:
                text += f"\nBest Role Fit: No-Nonsense Centre-Back (based on aerial dominance)\n"
            else:
                text += f"\nBest Role Fit: Central Defender (balanced profile)\n"

        elif 'CF' in position or 'Center Forward' in position:
            text += "\nCenter Forward Role Comparison:\n"
            text += "- Advance Forward: Versatile attacker who contributes in multiple ways\n"
            text += "- Pressing Forward: High work rate, disrupts opposition play\n"
            text += "- Deep-lying Forward: Drops deep to create and link play\n"
            text += "- Poacher: Specialist finisher who focuses on scoring goals\n"

            # Determine best fit
            goals_per_90 = player.get('goals_per_90', 0)
            assists_per_90 = player.get('assists_per_90', 0)
            duels_per_90 = player.get('duels_per_90', player.get('duels', 0) * 90 / max(player.get('minutes', 1), 1))

            if goals_per_90 > 0.7 and assists_per_90 < 0.3:
                text += f"\nBest Role Fit: Poacher (high goal rate, low assists)\n"
            elif assists_per_90 > 0.4:
                text += f"\nBest Role Fit: Deep-lying Forward (creative contribution)\n"
            elif duels_per_90 > 8:
                text += f"\nBest Role Fit: Pressing Forward (high work rate)\n"
            else:
                text += f"\nBest Role Fit: Advance Forward (balanced profile)\n"
        else:
            text += f"\nGeneric Role Analysis for {position}:\n"
            text += "- Role-specific analysis available for Center Backs and Center Forwards\n"
            text += "- This player shows versatile characteristics for their position\n"

        return text

    def _get_recent_form_analysis(self, player: Dict) -> str:
        """
        Analyze player's recent form based on match data.
        """
        text = f"\n=== RECENT FORM ANALYSIS ===\n"

        match_data = player.get('match_data', [])
        if not match_data:
            text += "No recent match data available.\n"
            return text

        # Analyze last 5 matches
        recent_matches = match_data[-5:] if len(match_data) >= 5 else match_data

        text += f"\nLast {len(recent_matches)} Matches Analysis:\n"

        # Calculate recent form metrics
        recent_goals = sum(match.get('Goals', 0) for match in recent_matches)
        recent_assists = sum(match.get('Assists', 0) for match in recent_matches)
        recent_minutes = sum(match.get('Minutes played', 0) for match in recent_matches)

        if recent_minutes > 0:
            recent_goals_per_90 = (recent_goals * 90) / recent_minutes
            recent_assists_per_90 = (recent_assists * 90) / recent_minutes

            text += f"- Recent Goal Rate: {recent_goals_per_90:.2f} per 90 minutes\n"
            text += f"- Recent Assist Rate: {recent_assists_per_90:.2f} per 90 minutes\n"

            # Compare with season average
            season_goals_per_90 = player.get('goals_per_90', 0)
            season_assists_per_90 = player.get('assists_per_90', 0)

            if recent_goals_per_90 > season_goals_per_90 * 1.2:
                text += f"- Form: Hot streak in front of goal (above season average)\n"
            elif recent_goals_per_90 < season_goals_per_90 * 0.8:
                text += f"- Form: Below usual goal scoring rate\n"
            else:
                text += f"- Form: Consistent with season performance\n"

        # Add match-by-match summary
        text += f"\nRecent Match Details:\n"
        for match in recent_matches[-3:]:  # Last 3 matches
            text += f"- {match.get('Match', 'Unknown')} ({match.get('Date', 'Unknown')}): "
            text += f"{match.get('Minutes played', 0)} min, {match.get('Goals', 0)} goals, {match.get('Assists', 0)} assists\n"

        return text

    def get_all_player_texts(self) -> List[Dict[str, str]]:
        """
        Get text representations for all players.

        Returns:
            List of dictionaries with player names and their text representations
        """
        if not self.player_data:
            self.process_data()

        texts = []
        for player_name in self.player_data:
            text = self.get_player_text_representation(player_name)
            texts.append({
                'player': player_name,
                'content': text
            })

        return texts


if __name__ == "__main__":
    # Test the data processor
    processor = GoalkeeperDataProcessor()
    data = processor.load_data()
    print(f"Loaded data for {len(data['Player'].unique())} players")

    processor.process_data()

    # Print a sample player text representation
    if processor.player_data:
        sample_player = list(processor.player_data.keys())[0]
        print(f"\nSample text representation for {sample_player}:")
        print(processor.get_player_text_representation(sample_player))
