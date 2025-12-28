#!/usr/bin/env python3
"""
ATP Tennis Serve Analysis
Analyzes when players would benefit from hitting only 1st serves

INSTRUCTIONS FOR LOCAL USE:
1. Clone or download data from: https://github.com/JeffSackmann/tennis_atp
2. Place CSV files in a local directory (e.g., ./data/)
3. Update DATA_DIR below to point to your local data directory
4. Run: python tennis_serve_analyzer.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Configuration
USE_LOCAL_DATA = True  # Set to True if using local CSV files
DATA_DIR = Path("./tennis_atp")  # Update this to your data directory
YEARS = range(2024, 2026)  # 2024-2025 (present)
BASE_URL = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_{}.csv"

# Monte Carlo simulation settings
NUM_SIMULATIONS = 1000  # Number of simulations per match
np.random.seed(42)  # For reproducibility

def download_data():
    """Download ATP match data from GitHub or load from local files"""
    print("Loading ATP match data...")
    dfs = []
    
    for year in YEARS:
        try:
            if USE_LOCAL_DATA:
                # Load from local CSV
                filepath = DATA_DIR / f"atp_matches_{year}.csv"
                if filepath.exists():
                    df = pd.read_csv(filepath)
                    dfs.append(df)
                    print(f"  ✓ {year}: {len(df)} matches (local)")
                else:
                    print(f"  ✗ {year}: File not found at {filepath}")
            else:
                # Download from GitHub
                url = BASE_URL.format(year)
                df = pd.read_csv(url)
                dfs.append(df)
                print(f"  ✓ {year}: {len(df)} matches (downloaded)")
        except Exception as e:
            print(f"  ✗ {year}: {e}")
    
    if not dfs:
        print("\nERROR: No data loaded!")
        print("\nPlease either:")
        print("1. Clone the repo: git clone https://github.com/JeffSackmann/tennis_atp")
        print("2. Set USE_LOCAL_DATA = True and DATA_DIR to point to the cloned repo")
        print("3. Or download individual CSV files from the repo")
        sys.exit(1)
    
    all_matches = pd.concat(dfs, ignore_index=True)
    print(f"\nTotal matches loaded: {len(all_matches):,}")
    return all_matches

def simulate_match_outcome(first_in_pct, first_win_pct, second_win_pct, service_points, best_of=3, num_sims=NUM_SIMULATIONS):
    """
    Monte Carlo simulation to estimate match win probability with different serving strategies.
    
    Returns:
        traditional_wins: Number of times player wins with traditional serving (out of num_sims)
        only_first_wins: Number of times player wins with only first serves (out of num_sims)
        traditional_prob: Win probability with traditional serving
        only_first_prob: Win probability with only first serves
    """
    traditional_wins = 0
    only_first_wins = 0
    
    # Calculate probabilities for each strategy
    # Traditional: use first serve, then second serve if miss
    # Only first: use first serve both times, double fault if both miss
    
    for _ in range(num_sims):
        # Simulate service games won with each strategy
        # Simplified model: assume winning X% of service points translates to games won
        # This is approximate - doesn't model actual game/set structure
        
        # Traditional strategy
        trad_points_won = 0
        for _ in range(service_points):
            if np.random.random() < first_in_pct:
                # First serve in
                if np.random.random() < first_win_pct:
                    trad_points_won += 1
            else:
                # Second serve
                if np.random.random() < second_win_pct:
                    trad_points_won += 1
        
        # Only first serves strategy
        only_first_points_won = 0
        for _ in range(service_points):
            if np.random.random() < first_in_pct:
                # First serve in
                if np.random.random() < first_win_pct:
                    only_first_points_won += 1
            else:
                # Missed first serve, try again (second attempt)
                if np.random.random() < first_in_pct:
                    if np.random.random() < first_win_pct:
                        only_first_points_won += 1
                # Else: double fault, point lost
        
        # Very simplified: assume holding ~60-70% of service points means winning match
        # This is a rough heuristic - proper simulation would model games/sets/tiebreaks
        # Adjust threshold based on best of 3 vs best of 5
        win_threshold = 0.58 if best_of == 3 else 0.56
        
        trad_service_pct = trad_points_won / service_points if service_points > 0 else 0
        only_first_service_pct = only_first_points_won / service_points if service_points > 0 else 0
        
        if trad_service_pct > win_threshold:
            traditional_wins += 1
        if only_first_service_pct > win_threshold:
            only_first_wins += 1
    
    return {
        'traditional_wins': traditional_wins,
        'only_first_wins': only_first_wins,
        'traditional_prob': traditional_wins / num_sims,
        'only_first_prob': only_first_wins / num_sims,
        'num_simulations': num_sims
    }

def calculate_serve_advantage(df):
    """
    Calculate whether players would benefit from only hitting 1st serves
    
    For each player in each match, calculate:
    - 1st serve %: w_1stIn / w_svpt
    - 1st serve win %: w_1stWon / w_1stIn
    - 2nd serve win %: w_2ndWon / (w_svpt - w_1stIn)
    
    Condition: 1st_in% × 1st_win% > 2nd_win%
    """
    print("\nCalculating serve statistics...")
    
    # Columns needed:
    # w_1stIn, w_1stWon, w_2ndWon, w_svpt (winner stats)
    # l_1stIn, l_1stWon, l_2ndWon, l_svpt (loser stats)
    
    required_cols = ['w_1stIn', 'w_1stWon', 'w_2ndWon', 'w_svpt',
                     'l_1stIn', 'l_1stWon', 'l_2ndWon', 'l_svpt']
    
    # Check if columns exist
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        print(f"Missing columns: {missing}")
        return None
    
    # Drop rows with missing serve stats
    df_clean = df.dropna(subset=required_cols).copy()
    print(f"Matches with complete serve stats: {len(df_clean):,}")
    
    results = []
    
    # Analyze winner's serves
    for idx, row in df_clean.iterrows():
        # Winner stats
        if row['w_svpt'] > 0 and row['w_1stIn'] > 0:
            first_in_pct = row['w_1stIn'] / row['w_svpt']
            first_win_pct = row['w_1stWon'] / row['w_1stIn']
            
            second_serve_points = row['w_svpt'] - row['w_1stIn']
            if second_serve_points > 0:
                second_win_pct = row['w_2ndWon'] / second_serve_points
                
                # Calculate expected win rates
                only_first = first_in_pct * first_win_pct + (1 - first_in_pct) * first_in_pct * first_win_pct
                traditional = first_in_pct * first_win_pct + (1 - first_in_pct) * second_win_pct
                
                # Simplified condition
                only_first_better = (first_in_pct * first_win_pct) > second_win_pct
                
                # Estimate impact on match result
                # This is a simplified approximation: if service points won changes significantly,
                # it could flip close matches
                service_point_diff = (only_first - traditional) * row['w_svpt']
                
                # Very rough heuristic: if the match was won and benefit is negative (worse serve),
                # or if match was lost and benefit is positive (better serve),
                # check if the point difference could have changed the outcome
                # This is approximate since we don't know exact game/set scores
                could_flip_result = abs(service_point_diff) > 10  # Arbitrary threshold
                
                # Determine if Grand Slam (Best of 5) or regular tour (Best of 3)
                # Grand Slams: Australian Open, Roland Garros, Wimbledon, US Open
                tourney_name = row.get('tourney_name', '').lower()
                is_grand_slam = any(slam in tourney_name for slam in 
                                   ['australian open', 'roland garros', 'wimbledon', 'us open', 
                                    'australian', 'french', 'us open', 'championships'])
                best_of = 5 if is_grand_slam else 3
                
                # Run Monte Carlo simulation
                sim_results = simulate_match_outcome(
                    first_in_pct, 
                    first_win_pct, 
                    second_win_pct, 
                    int(row['w_svpt']),
                    best_of=best_of
                )
                
                # Determine if result would likely flip
                prob_diff = sim_results['only_first_prob'] - sim_results['traditional_prob']
                could_flip_result = abs(prob_diff) > 0.15  # If >15% probability difference
                
                results.append({
                    'match_id': row.get('match_id', idx),
                    'tourney_name': row.get('tourney_name', 'Unknown'),
                    'tourney_date': row.get('tourney_date', 'Unknown'),
                    'surface': row.get('surface', 'Unknown'),
                    'round': row.get('round', 'Unknown'),
                    'score': row.get('score', 'Unknown'),
                    'best_of': best_of,
                    'player': row.get('winner_name', 'Unknown'),
                    'opponent': row.get('loser_name', 'Unknown'),
                    'won_match': True,
                    'first_in_pct': first_in_pct * 100,
                    'first_win_pct': first_win_pct * 100,
                    'second_win_pct': second_win_pct * 100,
                    'only_first_expected': only_first * 100,
                    'traditional_expected': traditional * 100,
                    'benefit_pct': (only_first - traditional) * 100,
                    'only_first_better': only_first_better,
                    'service_points_played': row['w_svpt'],
                    'estimated_point_swing': service_point_diff,
                    'could_flip_result': could_flip_result,
                    'sim_traditional_prob': sim_results['traditional_prob'] * 100,
                    'sim_only_first_prob': sim_results['only_first_prob'] * 100,
                    'sim_prob_diff': prob_diff * 100,
                    'num_simulations': sim_results['num_simulations']
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
                
                service_point_diff = (only_first - traditional) * row['l_svpt']
                
                # Determine Best of 3 or 5
                tourney_name = row.get('tourney_name', '').lower()
                is_grand_slam = any(slam in tourney_name for slam in 
                                   ['australian open', 'roland garros', 'wimbledon', 'us open', 
                                    'australian', 'french', 'us open', 'championships'])
                best_of = 5 if is_grand_slam else 3
                
                # Run Monte Carlo simulation
                sim_results = simulate_match_outcome(
                    first_in_pct, 
                    first_win_pct, 
                    second_win_pct, 
                    int(row['l_svpt']),
                    best_of=best_of
                )
                
                prob_diff = sim_results['only_first_prob'] - sim_results['traditional_prob']
                could_flip_result = abs(prob_diff) > 0.15
                
                results.append({
                    'match_id': row.get('match_id', idx),
                    'tourney_name': row.get('tourney_name', 'Unknown'),
                    'tourney_date': row.get('tourney_date', 'Unknown'),
                    'surface': row.get('surface', 'Unknown'),
                    'round': row.get('round', 'Unknown'),
                    'score': row.get('score', 'Unknown'),
                    'best_of': best_of,
                    'player': row.get('loser_name', 'Unknown'),
                    'opponent': row.get('winner_name', 'Unknown'),
                    'won_match': False,
                    'first_in_pct': first_in_pct * 100,
                    'first_win_pct': first_win_pct * 100,
                    'second_win_pct': second_win_pct * 100,
                    'only_first_expected': only_first * 100,
                    'traditional_expected': traditional * 100,
                    'benefit_pct': (only_first - traditional) * 100,
                    'only_first_better': only_first_better,
                    'service_points_played': row['l_svpt'],
                    'estimated_point_swing': service_point_diff,
                    'could_flip_result': could_flip_result,
                    'sim_traditional_prob': sim_results['traditional_prob'] * 100,
                    'sim_only_first_prob': sim_results['only_first_prob'] * 100,
                    'sim_prob_diff': prob_diff * 100,
                    'num_simulations': sim_results['num_simulations']
                })
    
    return pd.DataFrame(results)

def analyze_results(results_df):
    """Generate summary statistics"""
    print("\n" + "="*80)
    print("ANALYSIS RESULTS")
    print("="*80)
    
    total_performances = len(results_df)
    only_first_better_count = results_df['only_first_better'].sum()
    pct_better = (only_first_better_count / total_performances) * 100
    
    print(f"\nTotal player performances analyzed: {total_performances:,}")
    print(f"Times 'only 1st serves' would be better: {only_first_better_count:,} ({pct_better:.2f}%)")
    
    # Top examples where only first serves would help most
    print("\n" + "-"*80)
    print("TOP 20 EXAMPLES - Biggest Advantage from Only Hitting 1st Serves")
    print("-"*80)
    top_20 = results_df.nlargest(20, 'benefit_pct')
    for idx, row in top_20.iterrows():
        print(f"\n{row['player']} vs {row['opponent']}")
        print(f"  Tournament: {row['tourney_name']} ({row['tourney_date']}, {row['surface']})")
        print(f"  1st Serve In: {row['first_in_pct']:.1f}% | 1st Serve Win: {row['first_win_pct']:.1f}%")
        print(f"  2nd Serve Win: {row['second_win_pct']:.1f}%")
        print(f"  Only 1st Serves: {row['only_first_expected']:.1f}% vs Traditional: {row['traditional_expected']:.1f}%")
        print(f"  → Advantage: +{row['benefit_pct']:.2f} percentage points")
    
    # Player-level aggregation
    print("\n" + "-"*80)
    print("PLAYERS WHO MOST FREQUENTLY BENEFIT (min 50 matches)")
    print("-"*80)
    
    player_stats = results_df.groupby('player').agg({
        'only_first_better': ['sum', 'count'],
        'benefit_pct': 'mean'
    }).reset_index()
    player_stats.columns = ['player', 'times_better', 'total_matches', 'avg_benefit']
    player_stats['pct_better'] = (player_stats['times_better'] / player_stats['total_matches']) * 100
    player_stats = player_stats[player_stats['total_matches'] >= 50]
    player_stats = player_stats.sort_values('pct_better', ascending=False)
    
    print(player_stats.head(20).to_string(index=False))
    
    # Surface analysis
    print("\n" + "-"*80)
    print("BREAKDOWN BY SURFACE")
    print("-"*80)
    
    surface_stats = results_df.groupby('surface').agg({
        'only_first_better': ['sum', 'count']
    }).reset_index()
    surface_stats.columns = ['surface', 'times_better', 'total']
    surface_stats['pct_better'] = (surface_stats['times_better'] / surface_stats['total']) * 100
    surface_stats = surface_stats.sort_values('pct_better', ascending=False)
    
    print(surface_stats.to_string(index=False))
    
    # Best of 3 vs Best of 5 analysis
    print("\n" + "-"*80)
    print("BREAKDOWN BY MATCH FORMAT")
    print("-"*80)
    
    bo_stats = results_df.groupby('best_of').agg({
        'only_first_better': ['sum', 'count']
    }).reset_index()
    bo_stats.columns = ['best_of', 'times_better', 'total']
    bo_stats['pct_better'] = (bo_stats['times_better'] / bo_stats['total']) * 100
    bo_stats['format'] = bo_stats['best_of'].apply(lambda x: f'Best of {int(x)}' if x in [3, 5] else 'Unknown')
    bo_stats = bo_stats[['format', 'times_better', 'total', 'pct_better']]
    
    print(bo_stats.to_string(index=False))
    
    # Grand Slam specific analysis
    print("\n" + "-"*80)
    print("GRAND SLAM MATCHES (Best of 5)")
    print("-"*80)
    
    gs_df = results_df[results_df['best_of'] == 5]
    if len(gs_df) > 0:
        print(f"\nTotal Grand Slam performances: {len(gs_df):,}")
        print(f"Would benefit from only 1st serves: {gs_df['only_first_better'].sum():,} ({(gs_df['only_first_better'].sum()/len(gs_df)*100):.2f}%)")
        
        print("\nTop 10 Grand Slam examples:")
        top_gs = gs_df.nlargest(10, 'benefit_pct')
        for idx, row in top_gs.iterrows():
            print(f"\n{row['player']} vs {row['opponent']}")
            print(f"  {row['tourney_name']} - {row['round']} ({row['tourney_date']})")
            print(f"  Benefit: +{row['benefit_pct']:.2f}pp")
    else:
        print("\nNo Grand Slam matches in dataset")
    
    return results_df, player_stats

def main():
    # Download data
    matches_df = download_data()
    
    # Calculate serve advantage
    results_df = calculate_serve_advantage(matches_df)
    
    if results_df is not None:
        # Analyze results
        results_df, player_stats = analyze_results(results_df)
        
        # Save results
        output_dir = Path('./tennis_analysis_results')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results_df.to_csv(output_dir / 'serve_analysis_all_matches.csv', index=False)
        player_stats.to_csv(output_dir / 'serve_analysis_by_player.csv', index=False)
        
        print(f"\n✓ Results saved to {output_dir}/")
        print("  - serve_analysis_all_matches.csv")
        print("  - serve_analysis_by_player.csv")

if __name__ == '__main__':
    main()
