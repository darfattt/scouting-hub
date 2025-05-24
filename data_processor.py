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
        self.all_data = None
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

    def process_data(self) -> Dict[str, Any]:
        """
        Process the loaded data to create structured player profiles.

        Returns:
            Dictionary mapping player names to their statistics
        """
        if self.all_data is None:
            self.load_data()

        if self.all_data.empty:
            return {}

        # Group by player
        player_groups = self.all_data.groupby('Player')

        for player_name, player_df in player_groups:
            # Calculate aggregate statistics
            total_matches = len(player_df)
            total_minutes = player_df['Minutes played'].sum()
            total_conceded = player_df['Conceded goals'].sum()
            total_saves = player_df['Saves'].sum()
            total_shots_against = player_df['Shots against'].sum()

            # Calculate derived metrics
            save_percentage = (total_saves / total_shots_against * 100) if total_shots_against > 0 else 0
            goals_conceded_per_90 = (total_conceded / total_minutes * 90) if total_minutes > 0 else 0

            # Get the most recent team
            most_recent_match = player_df.sort_values('Date', ascending=False).iloc[0]
            current_team = most_recent_match['Team']

            # Create player profile
            self.player_data[player_name] = {
                'name': player_name,
                'team': current_team,
                'matches': total_matches,
                'minutes': total_minutes,
                'conceded_goals': total_conceded,
                'saves': total_saves,
                'shots_against': total_shots_against,
                'save_percentage': save_percentage,
                'goals_conceded_per_90': goals_conceded_per_90,
                'match_data': player_df.to_dict('records')
            }

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
        Process the loaded data to create structured player profiles.

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

            total_minutes = safe_sum('Minutes played')
            total_goals = safe_sum('Goals')
            total_assists = safe_sum('Assists')
            total_shots = safe_sum('Shots')
            total_shots_on_target = safe_sum('Shots on target')
            total_passes = safe_sum('Passes')
            total_passes_accurate = safe_sum('Passes accurate')
            total_dribbles = safe_sum('Dribbles')
            total_dribbles_successful = safe_sum('Dribbles successful')
            total_duels = safe_sum('Duels')
            total_duels_won = safe_sum('Duels won')
            total_interceptions = safe_sum('Interceptions')
            total_recoveries = safe_sum('Recoveries')

            # Calculate derived metrics
            goals_per_90 = (total_goals / total_minutes * 90) if total_minutes > 0 else 0
            assists_per_90 = (total_assists / total_minutes * 90) if total_minutes > 0 else 0
            pass_accuracy = (total_passes_accurate / total_passes * 100) if total_passes > 0 else 0
            dribble_success_rate = (total_dribbles_successful / total_dribbles * 100) if total_dribbles > 0 else 0
            duel_success_rate = (total_duels_won / total_duels * 100) if total_duels > 0 else 0
            shot_accuracy = (total_shots_on_target / total_shots * 100) if total_shots > 0 else 0

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

            # Create player profile
            self.player_data[player_name] = {
                'name': player_name,
                'team': current_team,
                'position': position,
                'matches': total_matches,
                'minutes': total_minutes,
                'goals': total_goals,
                'assists': total_assists,
                'shots': total_shots,
                'shots_on_target': total_shots_on_target,
                'passes': total_passes,
                'passes_accurate': total_passes_accurate,
                'dribbles': total_dribbles,
                'dribbles_successful': total_dribbles_successful,
                'duels': total_duels,
                'duels_won': total_duels_won,
                'interceptions': total_interceptions,
                'recoveries': total_recoveries,
                'yellow_cards': yellow_cards,
                'red_cards': red_cards,
                'goals_per_90': goals_per_90,
                'assists_per_90': assists_per_90,
                'pass_accuracy': pass_accuracy,
                'dribble_success_rate': dribble_success_rate,
                'duel_success_rate': duel_success_rate,
                'shot_accuracy': shot_accuracy,
                'match_data': player_df.to_dict('records')
            }

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
        text += f"Position: {player['position']}\n"
        text += f"Statistics Summary:\n"
        text += f"- Matches played: {player['matches']}\n"
        text += f"- Minutes played: {player['minutes']}\n"
        text += f"- Goals: {player['goals']} ({player['goals_per_90']:.2f} per 90 min)\n"
        text += f"- Assists: {player['assists']} ({player['assists_per_90']:.2f} per 90 min)\n"
        text += f"- Shots: {player['shots']} ({player['shots_on_target']} on target, {player['shot_accuracy']:.1f}% accuracy)\n"
        text += f"- Passes: {player['passes']} ({player['passes_accurate']} accurate, {player['pass_accuracy']:.1f}% accuracy)\n"
        text += f"- Dribbles: {player['dribbles']} ({player['dribbles_successful']} successful, {player['dribble_success_rate']:.1f}% success rate)\n"
        text += f"- Duels: {player['duels']} ({player['duels_won']} won, {player['duel_success_rate']:.1f}% success rate)\n"
        text += f"- Interceptions: {player['interceptions']}\n"
        text += f"- Recoveries: {player['recoveries']}\n"
        text += f"- Disciplinary: {player['yellow_cards']} yellow cards, {player['red_cards']} red cards\n\n"

        # Add match-by-match data (limit to last 10 matches for brevity)
        text += "Recent Matches:\n"
        for match in player['match_data'][-10:]:
            text += f"- {match['Match']} ({match['Date']}): {match['Minutes played']} minutes, {match['Goals']} goals, {match['Assists']} assists\n"

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
