# Data Format Guide

This guide explains the expected format for player statistics CSV files.

## File Structure

### Directory Layout

```
data/
├── stats/                     # Main player statistics
│   ├── Team - Player Name (Stats).csv
│   └── Player stats Player Name.csv
└── stats_league/             # League-wide statistics
    └── #Rank - Competition_position_stats.csv
```

## Goalkeeper Data Format

### Required Columns

| Column | Description | Type | Example |
|--------|-------------|------|---------|
| Match | Match identifier | String | "vs Team A" |
| Competition | Competition name | String | "Liga 1" |
| Date | Match date | Date | "2024-01-15" |
| Position | Player position | String | "GK" |
| Minutes played | Minutes in match | Integer | 90 |
| Conceded goals | Goals conceded | Integer | 1 |
| xCG | Expected Conceded Goals | Float | 1.2 |
| Shots against | Shots faced | Integer | 5 |
| Saves | Saves made | Integer | 4 |
| Saves with reflexes | Reflex saves | Integer | 2 |
| Exits | Goalkeeper exits | Integer | 3 |
| Long passes | Long passes attempted | Integer | 15 |
| Long passes accurate | Accurate long passes | Integer | 12 |
| Short passes | Short passes attempted | Integer | 25 |
| Short passes accurate | Accurate short passes | Integer | 23 |
| Goal kicks | Goal kicks taken | Integer | 8 |
| Short goal kicks | Short goal kicks | Integer | 5 |
| Long goal kicks | Long goal kicks | Integer | 3 |

### Optional Enhanced Columns

| Column | Description | Type |
|--------|-------------|------|
| xG against | Expected Goals Against | Float |
| xG against per 90 | xG Against per 90 min | Float |
| Prevented goals | Goals prevented | Float |
| Prevented goals per 90 | Prevented goals per 90 | Float |
| Clean sheets | Clean sheets | Integer |
| Save rate % | Save percentage | Float |
| Aerial duels per 90 | Aerial duels per 90 | Float |

## Outfield Player Data Format

### Required Columns

| Column | Description | Type | Example |
|--------|-------------|------|---------|
| Match | Match identifier | String | "vs Team A" |
| Competition | Competition name | String | "Liga 1" |
| Date | Match date | Date | "2024-01-15" |
| Position | Player position | String | "CF", "CM", "CB" |
| Minutes played | Minutes in match | Integer | 90 |
| Goals | Goals scored | Integer | 1 |
| Assists | Assists made | Integer | 0 |
| Shots | Shots attempted | Integer | 4 |
| Shots on target | Shots on target | Integer | 2 |
| xG | Expected Goals | Float | 0.8 |
| Passes | Passes attempted | Integer | 45 |
| Passes accurate | Accurate passes | Integer | 38 |
| Long passes | Long passes attempted | Integer | 8 |
| Long passes accurate | Accurate long passes | Integer | 6 |
| Crosses | Crosses attempted | Integer | 3 |
| Crosses accurate | Accurate crosses | Integer | 1 |
| Dribbles | Dribbles attempted | Integer | 5 |
| Dribbles successful | Successful dribbles | Integer | 3 |
| Duels | Duels contested | Integer | 12 |
| Duels won | Duels won | Integer | 7 |
| Aerial duels | Aerial duels contested | Integer | 6 |
| Aerial duels won | Aerial duels won | Integer | 4 |
| Interceptions | Interceptions made | Integer | 2 |
| Losses | Ball losses | Integer | 8 |
| Losses own half | Losses in own half | Integer | 3 |
| Recoveries | Ball recoveries | Integer | 6 |
| Recoveries opp half | Recoveries in opp half | Integer | 2 |
| Total actions | Total actions | Integer | 65 |
| Total actions successful | Successful actions | Integer | 52 |
| Yellow card | Yellow cards (minutes) | Integer | 0 |
| Red card | Red cards (minutes) | Integer | 0 |

## File Naming Conventions

### Standard Format
- `Team Name - Player Name (Stats).csv`
- Example: `PERSIB - Kevin Mendoza (Stats).csv`

### Alternative Format
- `Player stats Player Name.csv`
- Example: `Player stats Alex Martins.csv`

## Data Quality Requirements

### Mandatory Fields
- All matches must have valid dates
- Position field must be populated
- Minutes played must be > 0 for meaningful analysis

### Data Validation
- Numeric fields should contain valid numbers
- Dates should be in YYYY-MM-DD format
- Position codes should follow standard conventions

### Missing Data Handling
- Empty cells are treated as 0
- Invalid numeric values are converted to 0
- Missing position data will prevent proper categorization

## Position Codes

### Goalkeepers
- `GK` - Goalkeeper

### Defenders
- `CB` - Centre Back
- `LB` - Left Back
- `RB` - Right Back
- `LWB` - Left Wing Back
- `RWB` - Right Wing Back
- `SW` - Sweeper

### Midfielders
- `CM` - Centre Midfielder
- `CDM` - Central Defensive Midfielder
- `CAM` - Central Attacking Midfielder
- `LM` - Left Midfielder
- `RM` - Right Midfielder
- `LWM` - Left Wing Midfielder
- `RWM` - Right Wing Midfielder

### Forwards
- `CF` - Centre Forward
- `LWF` - Left Wing Forward
- `RWF` - Right Wing Forward
- `ST` - Striker
- `LF` - Left Forward
- `RF` - Right Forward

## Example CSV Structure

```csv
Match,Competition,Date,Position,Minutes played,Goals,Assists,Shots,xG
vs Team A,Liga 1,2024-01-15,CF,90,1,0,4,0.8
vs Team B,Liga 1,2024-01-22,CF,85,0,1,3,0.6
```

## Tips for Data Preparation

1. **Consistency**: Ensure consistent naming across files
2. **Completeness**: Include all required columns
3. **Accuracy**: Verify data accuracy before processing
4. **Format**: Use standard date and number formats
5. **Encoding**: Save files in UTF-8 encoding to handle special characters
