#!/usr/bin/env python3
"""
Tennis Serve Analysis - DEMO with Sample Data
Shows what the analysis output would look like
"""

import pandas as pd
import numpy as np

# Create sample data mimicking ATP match statistics
np.random.seed(42)

# Generate 100 sample matches
sample_data = []

players = ["Carlos Alcaraz", "Novak Djokovic", "Jannik Sinner", "Daniil Medvedev", 
           "Alexander Zverev", "Andrey Rublev", "Taylor Fritz", "Hubert Hurkacz",
           "Stefanos Tsitsipas", "Casper Ruud", "Holger Rune", "Alex de Minaur"]

tournaments = ["Australian Open", "Roland Garros", "Wimbledon", "US Open", 
               "Miami", "Indian Wells", "Madrid", "Rome"]

surfaces = ["Hard", "Clay", "Grass"]

for i in range(100):
    winner = np.random.choice(players)
    loser = np.random.choice([p for p in players if p != winner])
    
    # Winner stats - make some players have strong first serves
    w_svpt = np.random.randint(80, 150)
    w_1stIn = int(w_svpt * np.random.uniform(0.55, 0.75))  # 55-75% first serve in
    w_1stWon = int(w_1stIn * np.random.uniform(0.65, 0.85))  # 65-85% win on 1st serve
    w_2ndWon = int((w_svpt - w_1stIn) * np.random.uniform(0.35, 0.55))  # 35-55% win on 2nd
    
    # Loser stats
    l_svpt = np.random.randint(80, 150)
    l_1stIn = int(l_svpt * np.random.uniform(0.55, 0.75))
    l_1stWon = int(l_1stIn * np.random.uniform(0.60, 0.80))
    l_2ndWon = int((l_svpt - l_1stIn) * np.random.uniform(0.30, 0.50))
    
    sample_data.append({
        'tourney_name': np.random.choice(tournaments),
        'tourney_date': f"2024{np.random.randint(1,13):02d}{np.random.randint(1,28):02d}",
        'surface': np.random.choice(surfaces),
        'round': np.random.choice(['R128', 'R64', 'R32', 'R16', 'QF', 'SF', 'F']),
        'winner_name': winner,
        'loser_name': loser,
        'w_1stIn': w_1stIn,
        'w_1stWon': w_1stWon,
        'w_2ndWon': w_2ndWon,
        'w_svpt': w_svpt,
        'l_1stIn': l_1stIn,
        'l_1stWon': l_1stWon,
        'l_2ndWon': l_2ndWon,
        'l_svpt': l_svpt
    })

df = pd.DataFrame(sample_data)

# Now analyze using the same logic as the main script
results = []

for idx, row in df.iterrows():
    # Winner stats
    if row['w_svpt'] > 0 and row['w_1stIn'] > 0:
        first_in_pct = row['w_1stIn'] / row['w_svpt']
        first_win_pct = row['w_1stWon'] / row['w_1stIn']
        
        second_serve_points = row['w_svpt'] - row['w_1stIn']
        if second_serve_points > 0:
            second_win_pct = row['w_2ndWon'] / second_serve_points
            
            only_first = first_in_pct * first_win_pct + (1 - first_in_pct) * first_in_pct * first_win_pct
            traditional = first_in_pct * first_win_pct + (1 - first_in_pct) * second_win_pct
            
            only_first_better = (first_in_pct * first_win_pct) > second_win_pct
            
            results.append({
                'tourney_name': row['tourney_name'],
                'surface': row['surface'],
                'player': row['winner_name'],
                'opponent': row['loser_name'],
                'first_in_pct': first_in_pct * 100,
                'first_win_pct': first_win_pct * 100,
                'second_win_pct': second_win_pct * 100,
                'only_first_expected': only_first * 100,
                'traditional_expected': traditional * 100,
                'benefit_pct': (only_first - traditional) * 100,
                'only_first_better': only_first_better
            })
    
    # Loser stats
    if row['l_svpt'] > 0 and row['l_1stIn'] > 0:
        first_in_pct = row['l_1stIn'] / row['l_svpt']
        first_win_pct = row['l_1stWon'] / row['l_1stIn']
        
        second_serve_points = row['l_svpt'] - row['l_1stIn']
        if second_serve_points > 0:
            second_win_pct = row['l_2ndWon'] / second_serve_points
            
            only_first = first_in_pct * first_win_pct + (1 - first_in_pct) * first_in_pct * first_win_pct
            traditional = first_in_pct * first_win_pct + (1 - first_in_pct) * second_win_pct
            
            only_first_better = (first_in_pct * first_win_pct) > second_win_pct
            
            results.append({
                'tourney_name': row['tourney_name'],
                'surface': row['surface'],
                'player': row['loser_name'],
                'opponent': row['winner_name'],
                'first_in_pct': first_in_pct * 100,
                'first_win_pct': first_win_pct * 100,
                'second_win_pct': second_win_pct * 100,
                'only_first_expected': only_first * 100,
                'traditional_expected': traditional * 100,
                'benefit_pct': (only_first - traditional) * 100,
                'only_first_better': only_first_better
            })

results_df = pd.DataFrame(results)

# Print analysis
print("="*80)
print("DEMO: ATP TENNIS SERVE ANALYSIS")
print("Sample Data (100 matches, 200 player performances)")
print("="*80)

total = len(results_df)
better_count = results_df['only_first_better'].sum()
pct = (better_count / total) * 100

print(f"\nTotal performances: {total}")
print(f"Times 'only 1st serves' would be better: {better_count} ({pct:.1f}%)")

print("\n" + "-"*80)
print("TOP 10 EXAMPLES - Biggest Advantage from Only Hitting 1st Serves")
print("-"*80)

top_10 = results_df.nlargest(10, 'benefit_pct')
for idx, row in top_10.iterrows():
    print(f"\n{row['player']} vs {row['opponent']}")
    print(f"  Tournament: {row['tourney_name']} ({row['surface']})")
    print(f"  1st In: {row['first_in_pct']:.1f}% | 1st Win: {row['first_win_pct']:.1f}% | 2nd Win: {row['second_win_pct']:.1f}%")
    print(f"  Only 1st: {row['only_first_expected']:.1f}% vs Traditional: {row['traditional_expected']:.1f}%")
    print(f"  → Advantage: +{row['benefit_pct']:.2f}pp" if row['benefit_pct'] > 0 else f"  → Disadvantage: {row['benefit_pct']:.2f}pp")

print("\n" + "-"*80)
print("PLAYER FREQUENCY")
print("-"*80)

player_stats = results_df.groupby('player').agg({
    'only_first_better': ['sum', 'count']
}).reset_index()
player_stats.columns = ['player', 'times_better', 'total_matches']
player_stats['pct_better'] = (player_stats['times_better'] / player_stats['total_matches']) * 100
player_stats = player_stats.sort_values('pct_better', ascending=False)

print(player_stats.to_string(index=False))

print("\n" + "-"*80)
print("BY SURFACE")
print("-"*80)

surface_stats = results_df.groupby('surface').agg({
    'only_first_better': ['sum', 'count']
}).reset_index()
surface_stats.columns = ['surface', 'times_better', 'total']
surface_stats['pct_better'] = (surface_stats['times_better'] / surface_stats['total']) * 100

print(surface_stats.to_string(index=False))

print("\n" + "="*80)
print("This is sample data. The real analysis with 30+ years of ATP data")
print("will show thousands of examples across the entire player base!")
print("="*80)
