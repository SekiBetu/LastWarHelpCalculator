# Last War - Alliance Help Time Critical Point Calculator

A tool for the mobile game **Last War: Survival Game** that calculates the critical initial building time at which one alliance-help plan becomes more efficient than another. Available as a **CLI** (Python / Windows EXE) and a **web app** (single HTML file, deployable on GitHub Pages).

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
| Fixed reduction per help | `t1` (`X min Y sec`) | `t2` (`X min Y sec`) |

The tool uses **binary search** to find the initial time where both plans reduce exactly the same amount. The recommendation is **direction-agnostic** — it samples just above and just below the critical point to report which plan actually wins in each region, so it is correct no matter which plan wins at short vs long build times.

## Example

![](planA.jpg)

![](planB.jpg)

Using default values (Plan A: 37 helps × 49 min 2 sec, Plan B: 39 helps × 32 min 30 sec):

```
*******************************************************
  Last War - Alliance Help Time Critical Point Calculator
*******************************************************

Enter parameters for both plans (press Enter to use defaults):

--- Plan A ---
  Number of helps:
  Fixed reduction per help (e.g. 32 min 30 sec):

--- Plan B ---
  Number of helps:
  Fixed reduction per help (e.g. 32 min 30 sec):

=======================================================
  Plan Overview
=======================================================
  Percentage reduction: 0.5%
  Plan A: 37 helps, 49 min 2 sec fixed each
  Plan B: 39 helps, 32 min 30 sec fixed each
=======================================================

=======================================================
  Result
=======================================================
  Critical point: 7d 3h 28m
-------------------------------------------------------
  When initial time > 7d 3h 28m
    -> Plan B (39x / 32 min 30 sec) saves more time
  When initial time < 7d 3h 28m
    -> Plan A (37x / 49 min 2 sec) saves more time
=======================================================

Recalculate? (y/n, Enter to exit):
```

**Interpretation**: With these defaults, if your building upgrade takes more than ~7 days, choose Plan B (more helps, smaller fixed reduction — the percentage reduction dominates). If it takes less than ~7 days, choose Plan A (fewer helps, larger fixed reduction — the fixed reduction dominates).

## Usage

### Option 1: Web App (no install)

Open `index.html` in any browser, or visit the hosted version on GitHub Pages
(see [Deploying to GitHub Pages](#deploying-to-github-pages)).

The web app has the same defaults and algorithm as the CLI. Enter the number of
helps and the fixed reduction (split into **min** and **sec** fields) for each
plan, then click **Calculate**.

### Option 2: Run with Python

```bash
python LastWarHelpCalculator.py
```

Requires Python 3.6+ (no external dependencies).

### Option 3: Standalone EXE (Windows)

Double-click `dist/LastWarHelpCalculator.exe` — no Python installation needed.

### Input Parameters

| Parameter | Description |
|---|---|
| Number of helps (Plan A) | How many alliance helps Plan A provides |
| Fixed reduction per help (Plan A) | Fixed time reduced per help under Plan A, in `X min Y sec` format |
| Number of helps (Plan B) | How many alliance helps Plan B provides |
| Fixed reduction per help (Plan B) | Fixed time reduced per help under Plan B, in `X min Y sec` format |

Press **Enter** on any prompt to accept the default value.

#### Accepted time formats (CLI)

The *fixed reduction per help* prompts accept the `X min Y sec` form and several
convenient equivalents. All of the following are valid and mean **32 minutes 30 seconds**:

| Input | Notes |
|---|---|
| `32 min 30 sec` | English form (recommended) |
| `32m30s` | Compact English form (space optional) |
| `32:30` | Colon separated |
| `32 30` | Space separated (two integers) |
| `32.5` | Plain decimal minutes (backward compatible) |
| `32分30秒` / `32分钟30秒` | Chinese form (also accepted) |

You may also enter minutes or seconds alone:

| Input | Meaning |
|---|---|
| `32 min` / `32m` / `32分` | 32 minutes |
| `30 sec` / `30s` / `30秒` | 30 seconds |
| `32` | 32 minutes (plain number) |

Internally every value is stored as minutes (float), so the calculation is unchanged.

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
- Uses **sign-based bisection** on `(reduction_A − reduction_B)`: it keeps the
  half of the interval where the difference changes sign, so the search is
  **direction-agnostic** (correct no matter which plan wins at short vs long
  build times)
- If both ends have the same sign (one plan wins everywhere), the corresponding
  boundary (`0` or the upper limit) is returned
- Converges to within 0.001 minutes of the true critical point
- The result display samples just above and just below the critical point to
  report which plan actually wins in each region

## Customization

To change the fixed constants or default input values, edit the top of the script:

```python
# ---- Fixed constants ----
PERCENT_RATIO = 0.005   # percentage reduction per help

# ---- Input defaults ----
# Stored internally as minutes (float); displayed/accepted as "X min Y sec".
DEFAULT_N1 = 37            # Plan A default: number of helps
DEFAULT_T1 = 49 + 2/60     # Plan A default: fixed reduction (= 49 min 2 sec)
DEFAULT_N2 = 39            # Plan B default: number of helps
DEFAULT_T2 = 32.5          # Plan B default: fixed reduction (= 32 min 30 sec)
```

> **Note:** `DEFAULT_T1` / `DEFAULT_T2` are kept as decimal minutes so the
> binary-search math is untouched. They are automatically rendered as
> `X min Y sec` (e.g. `49 + 2/60` → `49 min 2 sec`) in the prompts and result.
> For the **web app**, edit the `value="..."` attributes on the input fields in
> `index.html` (the defaults are `49` / `2` for Plan A and `32` / `30` for
> Plan B).

## Building the EXE

If you want to rebuild the standalone Windows executable:

```bash
pip install pyinstaller
pyinstaller --onefile --console --name LastWarHelpCalculator LastWarHelpCalculator.py
```

The output will be in `dist/LastWarHelpCalculator.exe`.

> **Windows console note:** On startup the program calls
> `SetConsoleCP(65001)` / `SetConsoleOutputCP(65001)` and reconfigures
> `stdin`/`stdout` to UTF-8. This makes non-ASCII input work correctly
> whether the exe is double-clicked, run from `cmd`, or fed via a pipe — no
> `PYTHONUTF8` / `PYTHONIOENCODING` environment variables required.

## Web App

`index.html` is a self-contained single-file web app (HTML + CSS + JS, no build
step, no dependencies). It ports the exact same algorithm as the CLI and shares
the same defaults.

- Open `index.html` directly in any modern browser, or
- Host it on GitHub Pages for free (see below).

## Deploying to GitHub Pages

1. Push this repository (including `index.html`) to GitHub.
2. In the repo, go to **Settings → Pages**.
3. Under **Build and deployment → Source**, choose **Deploy from a branch**.
4. Select the **`main`** branch and the **`/ (root)`** folder, then **Save**.
5. Wait ~1 minute. Your app will be live at
   `https://<your-username>.github.io/LastWarHelpCalculator/`.

> If you prefer to keep the web app separate from the CLI source, move
> `index.html` into a `docs/` folder and select the **`/docs`** folder in step 4.

## License

MIT License — feel free to use, modify, and distribute.
