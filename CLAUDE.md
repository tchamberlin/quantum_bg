# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Monte Carlo probability calculator for a board game combat system. It simulates dice-based combat with special ability cards to determine win probabilities.

The core combat mechanics involve:
- Ship dice (1-6)
- Combat dice (1-6)
- Special ability cards that modify outcomes
- Counterintuitive rule: **Lower total wins**

## Project Setup

This project uses modern Python tooling with uv and src layout:

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the package and dependencies
uv pip install -e .

# Install dev dependencies (includes pytest)
uv pip install -e ".[dev]"
```

## Common Commands

### Running Simulations

```bash
# Using installed entry points (recommended after installation)
quantum -a ferocious -d stubborn -n 10000
battle 3:2 4:3 -a scrappy -d rational -w any -n 10000
qq 4 3 -a strategic -d stubborn -n 5
roll 2 5 -a 1 -A 3 -n 10000
table 10000

# Or using python -m (works without installation)
python -m quantum_bg.quantum -a ferocious -d stubborn -n 10000
python -m quantum_bg.battle 3:2 4:3 -a scrappy -d rational -w any -n 10000
python -m quantum_bg.qq 4 3 -a strategic -d stubborn -n 5
python -m quantum_bg.roll 2 5 -a 1 -A 3 -n 10000
python -m quantum_bg.table 10000
```

### Common Simulation Options

**quantum / quantum-nologs:**
- Basic: `quantum -a ferocious -d stubborn -n 10000`
- Compare to baseline: `quantum -a strategic --compare-to base_results.pkl -n 10000`
- Save results: `quantum -a cruel -d relentless --save results.pkl -n 10000`
- Test specific rolls: `quantum --rolls 3 4 2 5 -a cruel -d relentless`

**battle (multi-engagement):**
- Win any: `battle 3:2 4:3 -a scrappy -d rational -w any -n 10000`
- Win all: `battle 3:2 4:3 -a scrappy -d rational -w all -n 10000`

**table (lookup generation):**
- Generate: `table 10000` (creates .pkl files)

**qq (query pre-computed):**
- Query: `qq 4 3 -a strategic -d stubborn -n 5`

**roll (reconfiguration):**
- Calculate: `roll 2 5 -a 1 -A 3 -n 10000`
  - Args: current_die desired_die -a abilities -A actions

### Testing

```bash
# Run all tests with uv
uv run pytest

# Or with installed pytest
pytest

# Run specific test files
pytest tests/test_quantum.py
pytest tests/test_roll.py
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

**Project Structure:**
```
quantum_bg/
├── src/
│   └── quantum_bg/
│       ├── __init__.py
│       ├── quantum.py          # Main simulation with logging
│       ├── quantum_nologs.py   # Optimized simulation (no logging)
│       ├── battle.py           # Multi-engagement battles
│       ├── qq.py               # Query pre-computed probabilities
│       ├── roll.py             # Ship reconfiguration calculator
│       └── table.py            # Generate lookup tables
├── tests/
│   ├── test_quantum.py         # Core simulation tests
│   └── test_roll.py            # Reconfiguration tests
└── pyproject.toml              # Project metadata & dependencies
```

**Core Simulation Modules:**
- `src/quantum_bg/quantum.py` - Main simulation with logging (debugging)
- `src/quantum_bg/quantum_nologs.py` - Optimized simulation (performance)
- `src/quantum_bg/battle.py` - Multi-engagement battle calculator
- `src/quantum_bg/roll.py` - Ship reconfiguration probability

**Lookup Tables:**
- `src/quantum_bg/table.py` - Generate pre-computed tables (.pkl files)
- `src/quantum_bg/qq.py` - Query pre-computed probabilities

**Tests:**
- `tests/test_quantum.py` - Core combat simulation tests
- `tests/test_roll.py` - Roll/reconfiguration tests
