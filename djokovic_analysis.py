#!/usr/bin/env python3
"""
Show Djokovic matches from the tennis serve analysis demo
"""

import pandas as pd
import numpy as np

# Recreate the same sample data (same seed for reproducibility)
np.random.seed(42)

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
    
    w_svpt = np.random.randint(80, 150)
    w_1stIn = int(w_svpt * np.random.uniform(0.55, 0.75))
    w_1stWon = int(w_1stIn * np.random.uniform(0.65, 0.85))
    w_2ndWon = int((w_svpt - w_1stIn) * np.random.uniform(0.35, 0.55))
    
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

# Analyze
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
                'round': row['round'],
                'player': row['winner_name'],
                'opponent': row['loser_name'],
                'won_match': True,
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
                'round': row['round'],
                'player': row['loser_name'],
                'opponent': row['winner_name'],
                'won_match': False,
                'first_in_pct': first_in_pct * 100,
                'first_win_pct': first_win_pct * 100,
                'second_win_pct': second_win_pct * 100,
                'only_first_expected': only_first * 100,
                'traditional_expected': traditional * 100,
                'benefit_pct': (only_first - traditional) * 100,
                'only_first_better': only_first_better
            })

results_df = pd.DataFrame(results)

# Filter for Djokovic
djokovic_df = results_df[results_df['player'] == 'Novak Djokovic'].copy()
djokovic_df = djokovic_df.sort_values('benefit_pct', ascending=False)

print("="*80)
print("NOVAK DJOKOVIC - SERVE ANALYSIS")
print("="*80)

print(f"\nTotal matches: {len(djokovic_df)}")
print(f"Would benefit from only 1st serves: {djokovic_df['only_first_better'].sum()} ({djokovic_df['only_first_better'].sum()/len(djokovic_df)*100:.1f}%)")

print("\n" + "-"*80)
print("ALL DJOKOVIC MATCHES (sorted by benefit)")
print("-"*80)

for idx, row in djokovic_df.iterrows():
    result = "WON" if row['won_match'] else "LOST"
    better = "✓ BETTER" if row['only_first_better'] else "✗ WORSE"
    
    print(f"\nvs {row['opponent']} ({result})")
    print(f"  {row['tourney_name']} - {row['round']} ({row['surface']})")
    print(f"  1st In: {row['first_in_pct']:.1f}% | 1st Win: {row['first_win_pct']:.1f}% | 2nd Win: {row['second_win_pct']:.1f}%")
    print(f"  Only 1st: {row['only_first_expected']:.1f}% vs Traditional: {row['traditional_expected']:.1f}%")
    print(f"  Benefit: {row['benefit_pct']:+.2f}pp {better}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"\nAverage benefit when 'only 1st' is better: +{djokovic_df[djokovic_df['only_first_better']]['benefit_pct'].mean():.2f}pp")
print(f"Best match: +{djokovic_df['benefit_pct'].max():.2f}pp")
print(f"Worst match: {djokovic_df['benefit_pct'].min():.2f}pp")

print("\nNote: This is random demo data. Real ATP data would show Djokovic's actual")
print("serving patterns across his entire career!")
