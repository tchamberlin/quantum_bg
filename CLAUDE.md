# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Monte Carlo probability calculator for a board game combat system. It simulates dice-based combat with special ability cards to determine win probabilities.

The core combat mechanics involve:
- Ship dice (1-6)
- Combat dice (1-6)
- Special ability cards that modify outcomes
- Counterintuitive rule: **Lower total wins**

## Common Commands

### Running Simulations

```bash
# Basic combat simulation (default 1000 trials)
python quantum.py -a ferocious -d stubborn -n 10000

# Compare results to baseline pickle file
python quantum.py -a strategic --compare-to base_results.pkl -n 10000

# Save results to pickle file
python quantum.py -a cruel -d relentless --save results.pkl -n 10000

# Test specific roll outcomes (deterministic)
python quantum.py --rolls 3 4 2 5 -a cruel -d relentless
```

### Multi-Engagement Battles

```bash
# Battle with multiple engagements (format: attacker:defender)
python battle.py 3:2 4:3 -a scrappy -d rational -w any -n 10000

# Win conditions:
#   -w any  = Win at least one engagement
#   -w all  = Win all engagements
```

### Pre-computed Probability Lookups

```bash
# Generate lookup table (creates .pkl files)
python table.py 10000

# Query pre-computed probabilities from pickle files
python qq.py 4 3 -a strategic -d stubborn -n 5
```

### Ship Reconfiguration Probabilities

```bash
# Calculate probability of reaching desired ship die value
python roll.py 2 5 -a 1 -A 3 -n 10000
# Args: current_die desired_die -a abilities -A actions
```

### Testing

```bash
# Run all tests
pytest

# Run specific test files
pytest test_quantum.py
pytest test_roll.py
```

## Architecture

### Core Combat Simulation (`quantum.py`, `quantum_nologs.py`)

**Classes:**
- `Side` - Base class for combat participants with ship_die, combat_die, and ability cards
- `Attacker(Side)` - Implements `attack()` method with card resolution logic
- `Defender(Side)` - Simple subclass of Side

**Combat Resolution Order:**
1. Both sides roll combat dice (random 1-6, or deterministic via `combat_die_rolls` parameter)
2. Calculate totals (ship_die + combat_die, modified by cards)
3. Process card abilities in specific order:
   - **Relentless**: Loser re-rolls
   - **Scrappy**: Attacking loser re-rolls (attacker only!)
   - **Cruel**: Loser forces winner to re-roll
   - **Stubborn**: Defender breaks ties (defender only!)

**Card Modifiers:**
- `strategic`: -2 to effective total
- `ferocious`: -1 to effective total
- `rational`: Always rolls 3 on combat die (deterministic)
- **Lower total wins in this game** (counterintuitive!)

**Key Functions:**
- `do_iterations(attacker, defender, num_trials)` - Main Monte Carlo simulation loop (quantum_nologs.py:253)
- `get_results()` - Run simulations across multiple ship die combinations
- `Side.roll()` - Dice rolling with card logic
- `Attacker.attack()` - Full combat resolution

### Monte Carlo Simulation

The core technique uses repeated random sampling to calculate probabilities:

```python
def do_iterations(attacker, defender, num_trials):
    attacker_win_count = 0
    for __ in range(num_trials):
        attacker.reset()
        defender.reset()
        result = attacker.attack(defender)
        attacker_win_count += int(result)

    return attacker_win_count

# Calculate win ratio
attacker_win_ratio = attacker_win_count / num_trials
```

**Why Monte Carlo?**
- Card interactions create complex probability trees
- Conditional re-rolls make exact calculation difficult
- Simulation handles arbitrary complexity easily
- 10,000 trials gives ~±1% accuracy

### Probability Calculations

**Single Engagement:**
- Monte Carlo simulation via `do_iterations()`
- Results can be saved to pickle files for later lookup

**Multi-Engagement Battles (`qq.py`, `battle.py`):**
- **"any" win condition**: `prob_of_win2()` - Probability of winning at least 1 fight
  - Formula: `1 - Π(1 - p_i)` for all probabilities p_i
- **"all" win condition**: `prob_of_win_all()` - Probability of winning all fights
  - Formula: `Π(p_i)` for all probabilities p_i

### Lookup Table Generation (`table.py`)

- Generates all possible hand combinations (0-3 cards)
- Runs simulations for all combinations
- Saves results to pickle files for fast lookups
- Used by `qq.py` to query pre-computed probabilities

## Important Implementation Details

### Combat Mechanics
- **Attacker wins on ties** by default (unless defender has Stubborn)
- **Lower total wins** (counterintuitive - this is an inverted combat system)
- Cards can only trigger on specific conditions:
  - Scrappy only works for **attacking** loser
  - Stubborn only works for **defending** loser
  - Rational always forces roll of 3

### Testing Approach
- Use `combat_die_rolls` parameter for deterministic tests
- Pass list of predetermined rolls: `combat_die_rolls=[4, 5]`
- `predefined_combat_die_rolls` ensures test reproducibility
- Tests verify card interactions and combat resolution order

### File Organization

**Core Simulation:**
- `quantum.py` - Main simulation with logging (use for debugging)
- `quantum_nologs.py` - Optimized simulation without logging (use for performance)
- `battle.py` - Multi-engagement battle calculator
- `roll.py` - Ship reconfiguration probability calculator

**Lookup Tables:**
- `table.py` - Generate pre-computed probability tables (saves to .pkl files)
- `qq.py` - Query pre-computed probabilities from pickle files

**Tests:**
- `test_quantum.py` - Core combat simulation tests
- `test_roll.py` - Roll/reconfiguration tests
