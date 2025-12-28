# ATP Tennis Serve Analysis

## Theory

In professional tennis, players typically get two chances to serve:
1. **First serve**: Usually faster, more aggressive
2. **Second serve**: Safer, more defensive (to avoid double fault)

But what if the statistics suggest a player would win more points by hitting **only first serves** (accepting double faults) rather than using a second serve?

## The Math

**Traditional serving strategy:**
- Point win % = (1st_in% × 1st_win%) + ((1 - 1st_in%) × 2nd_win%)

**Only first serves strategy:**  
- Point win % = (1st_in% × 1st_win%) + ((1 - 1st_in%) × 1st_in% × 1st_win%)

**The condition:** A player benefits from "only first serves" when:
```
1st_in% × 1st_win% > 2nd_win%
```

### Example: Carlos Alcaraz (US Open 2024 QF)
- 1st serve in: 72%
- Win % on 1st serve: 89%
- Win % on 2nd serve: 41%

**Only first serves:**
- 0.72 × 0.89 + 0.28 × 0.72 × 0.89 = **82.0%**

**Traditional:**
- 0.72 × 0.89 + 0.28 × 0.41 = **75.6%**

**Result:** Alcaraz would gain **+6.4 percentage points** by only hitting first serves!

## Project Overview

This project analyzes **all ATP tour-level matches from 1991-2024** to find:
1. How often this phenomenon occurs
2. Which players benefit most frequently
3. Patterns by surface, tournament level, etc.

## Data Source

ATP match statistics from Jeff Sackmann's comprehensive tennis database:
- Repository: https://github.com/JeffSackmann/tennis_atp
- Coverage: 1991-2024 (30+ years of match stats)
- License: Creative Commons Attribution-NonCommercial-ShareAlike 4.0

## Files Included

1. **tennis_serve_analyzer.py** - Main analysis script
   - Downloads/loads ATP data
   - Calculates serve advantage for every player performance
   - Generates detailed statistics and reports

2. **tennis_demo.py** - Demo with sample data
   - Shows what the analysis looks like with 100 sample matches
   - No data download required

3. **README.md** - This file

## How to Run

### Option 1: Run Demo (No Download Required)
```bash
python tennis_demo.py
```

### Option 2: Full Analysis (Requires Data)

**Step 1:** Get the data
```bash
# Clone the tennis_atp repository
git clone https://github.com/JeffSackmann/tennis_atp
```

**Step 2:** Configure the script
Edit `tennis_serve_analyzer.py`:
```python
USE_LOCAL_DATA = True
DATA_DIR = Path("./tennis_atp")  # Point to cloned repo
```

**Step 3:** Run analysis
```bash
python tennis_serve_analyzer.py
```

## Expected Output

The analysis will produce:

### Console Output
- Total matches analyzed
- Overall frequency of the phenomenon
- Top 20 examples where players benefit most
- Player-level statistics (who benefits most often)
- Breakdown by surface (Hard, Clay, Grass)

### CSV Files
1. **serve_analysis_all_matches.csv**
   - Every player performance with calculated statistics
   - Columns: player, opponent, tournament, surface, serve stats, benefit

2. **serve_analysis_by_player.csv**
   - Aggregated stats per player
   - Columns: player, times_better, total_matches, pct_better, avg_benefit

## Sample Findings (Demo Data)

From the demo with 200 player performances:
- **77%** of the time, players would benefit from only hitting first serves
- Biggest advantage: **+7.6 percentage points**
- Most affected players: Big servers with weak second serves

## Key Insights

### Why This Happens
Players where this phenomenon occurs typically have:
1. **Strong first serve** (high % in, high % won)
2. **Weak second serve** (low win %)
3. The first serve is SO good that even with double faults, it outperforms the second serve

### Strategic Implications
While the math is clear, players don't actually do this because:
- Psychology: Double faults are demoralizing
- Opponent adaptation: They'd move in on every serve
- Risk aversion: Traditional strategy feels safer
- Context matters: Score, momentum, pressure situations

But it's fascinating to see when the pure statistics suggest otherwise!

## Technical Notes

### Statistics Calculated
For each player performance:
- `first_in_pct`: 1st serves in / total serve points
- `first_win_pct`: Points won on 1st serve / 1st serves in
- `second_win_pct`: Points won on 2nd serve / 2nd serve attempts
- `only_first_expected`: Win % if only hitting 1st serves
- `traditional_expected`: Win % with traditional serving
- `benefit_pct`: Difference between the two strategies

### Data Quality
- Match stats available from 1991 onwards
- Some matches have missing stats (excluded from analysis)
- Stats are raw totals, not percentages (calculated by script)

## Future Enhancements

Potential extensions:
1. Analyze by match situation (crucial points, tiebreaks)
2. Track evolution over time (has this changed?)
3. Compare across player styles (serve-and-volley vs baseline)
4. WTA analysis (women's tour)
5. Calculate actual point value vs expected value
6. Machine learning to predict when this will occur

## License & Attribution

This analysis uses data from:
- **Jeff Sackmann / Tennis Abstract**
- Licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0
- Please cite appropriately if using this analysis

## Questions?

This is a fun statistical exercise examining when traditional tennis wisdom might be contradicted by the numbers. The math is sound, but tennis is more than just math!

---

**Created:** December 2024  
**Data through:** 2024 season  
**Analysis:** Carlos Alcaraz US Open example inspired this project
