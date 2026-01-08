#!/usr/bin/env python3
"""
Update Tennis Serve Analyzer Data
Pulls latest ATP + WTA data, runs analysis, rebuilds site
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import subprocess
import sys

# Configuration
YEARS = range(2024, 2026)
NUM_SIMULATIONS = 1000
np.random.seed(42)

ATP_URL = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_{}.csv"
WTA_URL = "https://raw.githubusercontent.com/JeffSackmann/tennis_wta/master/wta_matches_{}.csv"

def download_tour_data(tour='ATP'):
    """Download match data from GitHub"""
    print(f"\nLoading {tour} data...")
    url_template = ATP_URL if tour == 'ATP' else WTA_URL
    dfs = []

    for year in YEARS:
        try:
            url = url_template.format(year)
            df = pd.read_csv(url)
            df['tour'] = tour
            dfs.append(df)
            print(f"  {year}: {len(df)} matches")
        except Exception as e:
            print(f"  {year}: {e}")

    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return None

def simulate_match_outcome(first_in_pct, first_win_pct, second_win_pct, service_points, best_of=3):
    """Monte Carlo simulation for win probability"""
    traditional_wins = 0
    only_first_wins = 0

    for _ in range(NUM_SIMULATIONS):
        # Traditional strategy
        trad_points_won = 0
        for _ in range(service_points):
            if np.random.random() < first_in_pct:
                if np.random.random() < first_win_pct:
                    trad_points_won += 1
            else:
                if np.random.random() < second_win_pct:
                    trad_points_won += 1

        # Only first serves strategy
        only_first_points_won = 0
        for _ in range(service_points):
            if np.random.random() < first_in_pct:
                if np.random.random() < first_win_pct:
                    only_first_points_won += 1
            else:
                if np.random.random() < first_in_pct:
                    if np.random.random() < first_win_pct:
                        only_first_points_won += 1

        win_threshold = 0.58 if best_of == 3 else 0.56

        if service_points > 0:
            if trad_points_won / service_points > win_threshold:
                traditional_wins += 1
            if only_first_points_won / service_points > win_threshold:
                only_first_wins += 1

    return {
        'traditional_prob': traditional_wins / NUM_SIMULATIONS,
        'only_first_prob': only_first_wins / NUM_SIMULATIONS,
    }

def calculate_serve_advantage(df):
    """Calculate serve statistics for all matches"""
    print("\nCalculating serve statistics...")

    required_cols = ['w_1stIn', 'w_1stWon', 'w_2ndWon', 'w_svpt',
                     'l_1stIn', 'l_1stWon', 'l_2ndWon', 'l_svpt']

    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        print(f"Missing columns: {missing}")
        return None

    df_clean = df.dropna(subset=required_cols).copy()
    print(f"Matches with complete serve stats: {len(df_clean):,}")

    results = []
    total = len(df_clean)

    for i, (idx, row) in enumerate(df_clean.iterrows()):
        if i % 500 == 0:
            print(f"  Processing {i}/{total}...")

        tour = row.get('tour', 'ATP')
        tourney_name = row.get('tourney_name', '').lower()

        # Determine best of (Grand Slams are BO5 for ATP men only)
        is_grand_slam = any(slam in tourney_name for slam in
                          ['australian open', 'roland garros', 'wimbledon', 'us open'])
        best_of = 5 if (is_grand_slam and tour == 'ATP') else 3

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

                sim = simulate_match_outcome(first_in_pct, first_win_pct, second_win_pct, int(row['w_svpt']), best_of)
                prob_diff = sim['only_first_prob'] - sim['traditional_prob']

                results.append({
                    'tour': tour,
                    'p': row.get('winner_name', 'Unknown'),
                    'o': row.get('loser_name', 'Unknown'),
                    'w': 1,
                    't': row.get('tourney_name', 'Unknown'),
                    'd': str(row.get('tourney_date', '')),
                    'b': str(best_of),
                    's': row.get('surface', '?'),
                    'sc': row.get('score', ''),
                    'fi': round(first_in_pct * 100, 2),
                    'fw': round(first_win_pct * 100, 2),
                    'sw': round(second_win_pct * 100, 2),
                    'bp': round((only_first - traditional) * 100, 2),
                    'ob': 1 if only_first_better else 0,
                    'cf': 1 if abs(prob_diff) > 0.15 else 0,
                    'sd': round(prob_diff * 100, 2),
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

                sim = simulate_match_outcome(first_in_pct, first_win_pct, second_win_pct, int(row['l_svpt']), best_of)
                prob_diff = sim['only_first_prob'] - sim['traditional_prob']

                results.append({
                    'tour': tour,
                    'p': row.get('loser_name', 'Unknown'),
                    'o': row.get('winner_name', 'Unknown'),
                    'w': 0,
                    't': row.get('tourney_name', 'Unknown'),
                    'd': str(row.get('tourney_date', '')),
                    'b': str(best_of),
                    's': row.get('surface', '?'),
                    'sc': row.get('score', ''),
                    'fi': round(first_in_pct * 100, 2),
                    'fw': round(first_win_pct * 100, 2),
                    'sw': round(second_win_pct * 100, 2),
                    'bp': round((only_first - traditional) * 100, 2),
                    'ob': 1 if only_first_better else 0,
                    'cf': 1 if abs(prob_diff) > 0.15 else 0,
                    'sd': round(prob_diff * 100, 2),
                })

    return results

def update_html(data):
    """Embed data into HTML file"""
    print("\nUpdating HTML...")

    html_path = Path('/Users/MM/projects/tennis-analyzer/tennis_player_view-embedded.html')
    html = html_path.read_text()

    # Find and replace the data
    import re
    pattern = r'const MATCH_DATA = \[.*?\];'
    json_data = json.dumps(data, separators=(',', ':'))
    new_code = f'const MATCH_DATA = {json_data};'

    html = re.sub(pattern, new_code, html, flags=re.DOTALL)
    html_path.write_text(html)

    print(f"  HTML updated: {len(data)} records, {len(html)/1024/1024:.1f}MB")

def deploy():
    """Deploy to Vercel"""
    print("\nDeploying to Vercel...")
    result = subprocess.run(
        ['npx', 'vercel', '--prod', '--yes'],
        cwd='/Users/MM/projects/tennis-analyzer',
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("  Deployed successfully!")
    else:
        print(f"  Deploy failed: {result.stderr}")

def main():
    print("="*60)
    print("TENNIS SERVE ANALYZER - DATA UPDATE")
    print("="*60)

    # Download ATP and WTA data
    atp_df = download_tour_data('ATP')
    wta_df = download_tour_data('WTA')

    # Combine
    dfs = [df for df in [atp_df, wta_df] if df is not None]
    if not dfs:
        print("No data loaded!")
        sys.exit(1)

    all_matches = pd.concat(dfs, ignore_index=True)
    print(f"\nTotal matches: {len(all_matches):,}")

    # Calculate serve stats
    results = calculate_serve_advantage(all_matches)

    # Filter out retirements
    results = [r for r in results if not any(x in (r.get('sc') or '') for x in ['RET', 'W/O', 'DEF'])]
    print(f"\nFiltered results: {len(results):,}")

    # Update HTML
    update_html(results)

    # Deploy
    deploy()

    print("\nDone!")

if __name__ == '__main__':
    main()
