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
