# Last War - Alliance Help Time Critical Point Calculator

A CLI tool for the mobile game **Last War: Survival Game** that calculates the critical initial building time at which one alliance-help plan becomes more efficient than another.

## Background

In Last War, alliance members can "help" each other reduce building upgrade time. Each help reduces time by:

```
reduction = max(remaining_time × 0.5%, fixed_time)
```

- **Percentage reduction**: 0.5% of the remaining time (gets smaller as time decreases)
- **Fixed reduction**: a constant value per help (always the same)

The actual reduction per help is the **larger** of the two, meaning:
- When remaining time is long → percentage reduction dominates
- When remaining time is short → fixed reduction dominates

This creates a strategic question: given two different help plans (different number of helps × different fixed reduction), which one saves more total time?

**The answer depends on the initial building time.** This calculator finds the exact threshold (critical point) where the two plans yield equal total savings.

## How It Works

Given two plans:

| | Plan A | Plan B |
|---|---|---|
| Number of helps | `n1` | `n2` |
| Fixed reduction per help | `t1` min | `t2` min |

The tool uses **binary search** to find the initial time where both plans reduce exactly the same amount. Then:

- **Initial time > critical point** → Plan A saves more
- **Initial time < critical point** → Plan B saves more

## Example

Using default values (Plan A: 37 helps × 32.5 min, Plan B: 35 helps × 48.5 min):

```
*******************************************************
  Last War - Alliance Help Time Critical Point Calculator
*******************************************************

Enter parameters for both plans (press Enter to use defaults):

--- Plan A ---
  Number of helps:
  Fixed reduction per help (min):

--- Plan B ---
  Number of helps:
  Fixed reduction per help (min):

=======================================================
  Plan Overview
=======================================================
  Percentage reduction: 0.5%
  Plan A: 37 helps, 32.5 min fixed each
  Plan B: 35 helps, 48.5 min fixed each
=======================================================

=======================================================
  Result
=======================================================
  Critical point: 6d 23h 55m
-------------------------------------------------------
  When initial time > 6d 23h 55m
    -> Plan A (37x/32.5m) saves more time
  When initial time < 6d 23h 55m
    -> Plan B (35x/48.5m) saves more time
=======================================================

Recalculate? (y/n, Enter to exit):
```

**Interpretation**: If your building upgrade takes more than ~7 days, choose Plan A (more helps, smaller fixed reduction). If it takes less than ~7 days, choose Plan B (fewer helps, larger fixed reduction).

## Usage

### Option 1: Run with Python

```bash
python lastwar_help_calculator.py
```

Requires Python 3.6+ (no external dependencies).

### Option 2: Standalone EXE (Windows)

Double-click `LastWarHelpCalculator.exe` — no Python installation needed.

### Input Parameters

| Parameter | Description |
|---|---|
| Number of helps (Plan A) | How many alliance helps Plan A provides |
| Fixed reduction per help (Plan A) | Fixed minutes reduced per help under Plan A |
| Number of helps (Plan B) | How many alliance helps Plan B provides |
| Fixed reduction per help (Plan B) | Fixed minutes reduced per help under Plan B |

Press **Enter** on any prompt to accept the default value.

### Fixed Constants (not configurable)

| Constant | Value | Description |
|---|---|---|
| `PERCENT_RATIO` | 0.005 (0.5%) | Percentage of remaining time reduced per help |
| `EPSILON` | 0.001 min | Binary search precision |

## Algorithm Details

### Time Reduction Simulation (`simulate_help`)

For each help, the reduction is:

```python
reduction = max(current_time * PERCENT_RATIO, fixed_time)
current_time -= reduction
```

This simulates the diminishing returns of percentage-based reduction — early helps shave off large chunks, later helps shave off progressively smaller ones, until the fixed reduction takes over.

### Binary Search (`find_critical_point`)

- Searches the range `[0, 1,000,000]` minutes
- At each midpoint, simulates both plans and compares total reduction
- If Plan A reduces more → critical point is lower (search left)
- If Plan B reduces more → critical point is higher (search right)
- Converges to within 0.001 minutes of the true critical point

## Customization

To change the fixed constants or default input values, edit the top of the script:

```python
# ---- Fixed constants ----
PERCENT_RATIO = 0.005   # percentage reduction per help

# ---- Input defaults ----
DEFAULT_N1 = 37         # Plan A default: number of helps
DEFAULT_T1 = 32.5       # Plan A default: fixed reduction (min)
DEFAULT_N2 = 35         # Plan B default: number of helps
DEFAULT_T2 = 48.5       # Plan B default: fixed reduction (min)
```

## Building the EXE

If you want to rebuild the standalone Windows executable:

```bash
pip install pyinstaller
pyinstaller --onefile --console --name LastWarHelpCalculator lastwar_help_calculator.py
```

The output will be in `dist/LastWarHelpCalculator.exe`.

## License

MIT License — feel free to use, modify, and distribute.
