"""
Last War Alliance Help Time Critical Point Calculator
======================================================
Each help reduces time by: max(remaining_time * percent, fixed_time)
Uses binary search to find the initial time threshold where Plan A
overtakes Plan B in total time saved.
"""

import re
import sys


def setup_windows_utf8_console():
    """On Windows, switch the console code page to UTF-8 and reconfigure
    Python's standard streams to UTF-8.

    This guarantees that non-ASCII input (e.g. '32 min 30 sec' typed via an
    IME, or any localized format) and output work correctly whether the
    program is run interactively, from a pipe, or as a PyInstaller-built exe.
    Does nothing on non-Windows platforms.
    """
    if sys.platform != "win32":
        return
    # Switch the console input/output code page to UTF-8 (65001) so that
    # text typed through an IME is delivered to stdin as UTF-8 bytes.
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleCP(65001)
        kernel32.SetConsoleOutputCP(65001)
    except Exception:
        pass
    # Reconfigure Python's own streams to decode/encode UTF-8.
    for stream in (sys.stdin, sys.stdout):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


# ---- Fixed constants (not user-input) ----
PERCENT_RATIO = 0.005   # 0.5%
EPSILON = 0.001         # binary search precision in minutes

# ---- Input defaults (used when user presses Enter) ----
# Values are stored internally as minutes (float). They are displayed and
# accepted as "X min Y sec" on input/output.
DEFAULT_N1 = 37
DEFAULT_T1 = 49 + 2/60   # = 49 min 2 sec
DEFAULT_N2 = 39
DEFAULT_T2 = 32.5        # = 32 min 30 sec


def format_duration(total_minutes):
    """Convert total minutes into a 'Xd Xh Xm' string."""
    days = int(total_minutes // (24 * 60))
    remaining = total_minutes % (24 * 60)
    hours = int(remaining // 60)
    minutes = int(round(remaining % 60))

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0 or days > 0:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    return " ".join(parts)


def parse_min_sec_input(raw):
    """Parse a time value that may be given as 'X min Y sec' (or several
    equivalent forms) and return the total minutes as a float.

    Accepted forms (all case-insensitive on the ASCII letters):
      - '32 min 30 sec' / '32m30s' / '32分30秒' / '32分钟30秒'
      - '32 min' / '32m' / '32分' / '32分钟'   (minutes only)
      - '30 sec' / '30s' / '30秒'              (seconds only)
      - '32:30'                              (colon separated)
      - '32 30'                              (space separated, two ints)
      - '32.5' / '32'                        (plain decimal minutes,
                                             kept for backward compatibility)

    Returns None when the input cannot be parsed.
    """
    if raw is None:
        return None
    raw = raw.strip()
    if raw == "":
        return None

    text = raw.lower()

    # --- Chinese form: X分[Y]钟Y秒 (both parts) ---
    m = re.match(r"^(\d+)\s*分(?:钟)?\s*(\d+)\s*秒$", text)
    if m:
        return int(m.group(1)) + int(m.group(2)) / 60.0

    # --- English form: X min Y sec / XmYs (both parts, space optional) ---
    m = re.match(
        r"^(\d+)\s*(?:minutes?|min|m)\s*(\d+)\s*(?:seconds?|sec|s)$", text
    )
    if m:
        return int(m.group(1)) + int(m.group(2)) / 60.0

    # --- Minutes only: 'X分' / 'X分钟' / 'X min' / 'Xm' ---
    m = re.match(r"^(\d+)\s*分(?:钟)?$", text)
    if m:
        return float(int(m.group(1)))
    m = re.match(r"^(\d+(?:\.\d+)?)\s*(?:minutes?|min|m)$", text)
    if m:
        return float(m.group(1))

    # --- Seconds only: 'Y秒' / 'Y sec' / 'Ys' ---
    m = re.match(r"^(\d+)\s*秒$", text)
    if m:
        return int(m.group(1)) / 60.0
    m = re.match(r"^(\d+(?:\.\d+)?)\s*(?:seconds?|sec|s)$", text)
    if m:
        return float(m.group(1)) / 60.0

    # --- Colon form: 'X:Y' ---
    if ":" in text:
        parts = text.split(":")
        if len(parts) == 2:
            try:
                return int(parts[0]) + int(parts[1]) / 60.0
            except ValueError:
                return None

    # --- Space separated: 'X Y' (two integers) ---
    parts = text.split()
    if len(parts) == 2:
        try:
            return int(parts[0]) + int(parts[1]) / 60.0
        except ValueError:
            pass

    # --- Plain decimal minutes (backward compatible) ---
    try:
        return float(raw)
    except ValueError:
        return None


def format_min_sec(total_minutes):
    """Convert a minutes value (float) into a 'X min Y sec' string.

    Examples:
        49.0333 -> '49 min 2 sec'
        32.5    -> '32 min 30 sec'
        5       -> '5 min'
        0.5     -> '30 sec'
        0       -> '0 min'
    """
    if total_minutes is None:
        return "0 min"
    total_seconds = int(round(total_minutes * 60))
    if total_seconds < 0:
        total_seconds = 0
    minutes = total_seconds // 60
    seconds = total_seconds % 60

    if minutes > 0 and seconds > 0:
        return f"{minutes} min {seconds} sec"
    if minutes > 0:
        return f"{minutes} min"
    if seconds > 0:
        return f"{seconds} sec"
    return "0 min"


def simulate_help(initial_time, help_count, fixed_time, percent_ratio=PERCENT_RATIO):
    """Simulate total time reduced after multiple helps."""
    current_time = initial_time
    for _ in range(help_count):
        reduction = max(current_time * percent_ratio, fixed_time)
        current_time -= reduction
    return initial_time - current_time


def find_critical_point(n1, t1, n2, t2, percent_ratio=PERCENT_RATIO, epsilon=EPSILON):
    """Binary search for the critical initial time where both plans yield
    equal total reduction. Returns critical_minutes.

    Direction-agnostic: works no matter which plan wins at short vs long
    build times. Uses sign-based bisection on (reduction_A - reduction_B),
    maintaining the invariant that the difference has opposite signs at the
    two ends of the search interval. If one plan wins across the entire
    search range (no sign change), the corresponding boundary is returned.
    """
    low = 0.0
    high = 1000000.0

    diff_low = simulate_help(low, n1, t1, percent_ratio) - simulate_help(low, n2, t2, percent_ratio)
    diff_high = simulate_help(high, n1, t1, percent_ratio) - simulate_help(high, n2, t2, percent_ratio)

    # No sign change -> one plan dominates the whole range.
    if diff_low * diff_high > 0:
        # Plan A wins everywhere -> critical point at 0 (Plan A wins for any time > 0).
        # Plan B wins everywhere -> critical point at the upper limit.
        return 0.0 if diff_low > 0 else high

    while high - low > epsilon:
        mid_time = (low + high) / 2
        diff_mid = simulate_help(mid_time, n1, t1, percent_ratio) - simulate_help(mid_time, n2, t2, percent_ratio)

        # Keep the half where the sign differs from diff_low (root is there).
        if diff_low * diff_mid <= 0:
            high = mid_time
            diff_high = diff_mid
        else:
            low = mid_time
            diff_low = diff_mid

    return (low + high) / 2


def get_float_input(prompt, default=None):
    """Prompt user for a float. Default is used silently when Enter is pressed."""
    while True:
        raw = input(f"{prompt}: ").strip()
        if raw == "" and default is not None:
            return default
        try:
            return float(raw)
        except ValueError:
            print("  Invalid input. Please enter a number.")


def get_int_input(prompt, default=None):
    """Prompt user for a positive integer. Default is used silently when Enter is pressed."""
    while True:
        raw = input(f"{prompt}: ").strip()
        if raw == "" and default is not None:
            return default
        try:
            val = int(raw)
            if val <= 0:
                print("  Number of helps must be a positive integer.")
                continue
            return val
        except ValueError:
            print("  Invalid input. Please enter a positive integer.")


def get_min_sec_input(prompt, default=None):
    """Prompt user for a time value in 'X min Y sec' form.

    Accepts a wide range of equivalent formats (see parse_min_sec_input).
    The default is used silently when Enter is pressed. Internally the
    value is stored as minutes (float) so the rest of the calculation is
    unchanged.
    """
    while True:
        raw = input(f"{prompt}: ").strip()
        if raw == "" and default is not None:
            return default
        value = parse_min_sec_input(raw)
        if value is not None and value >= 0:
            return value
        print("  Invalid input. Please use the format 'X min Y sec' (e.g. 32 min 30 sec).")


def print_plan_summary(n1, t1, n2, t2):
    """Print plan overview."""
    print()
    print("=" * 55)
    print("  Plan Overview")
    print("=" * 55)
    print(f"  Percentage reduction: {PERCENT_RATIO*100:.1f}%")
    print(f"  Plan A: {n1} helps, {format_min_sec(t1)} fixed each")
    print(f"  Plan B: {n2} helps, {format_min_sec(t2)} fixed each")
    print("=" * 55)


def print_result(n1, t1, n2, t2, critical_minutes):
    """Print calculation result with day/hour/min format.

    Direction-agnostic: samples just above and just below the critical
    point to determine which plan actually wins in each region, so the
    recommendation is correct regardless of which plan wins at short vs
    long build times.
    """
    critical_dhm = format_duration(critical_minutes)

    # Determine the winner above and below the critical point by sampling.
    if critical_minutes <= 0.001:
        # Critical at 0: one plan wins for every positive time.
        diff = simulate_help(1.0, n1, t1) - simulate_help(1.0, n2, t2)
        above = below = "A" if diff >= 0 else "B"
    elif critical_minutes >= 999999.0:
        # Critical at the upper limit: one plan wins for every practical time.
        diff = simulate_help(100.0, n1, t1) - simulate_help(100.0, n2, t2)
        above = below = "A" if diff >= 0 else "B"
    else:
        diff_above = simulate_help(critical_minutes * 1.001 + 0.5, n1, t1) - \
                     simulate_help(critical_minutes * 1.001 + 0.5, n2, t2)
        diff_below = simulate_help(critical_minutes * 0.999, n1, t1) - \
                     simulate_help(critical_minutes * 0.999, n2, t2)
        above = "A" if diff_above > 0 else "B"
        below = "A" if diff_below > 0 else "B"

    def plan_label(plan):
        if plan == "A":
            return f"Plan A ({n1}x / {format_min_sec(t1)})"
        return f"Plan B ({n2}x / {format_min_sec(t2)})"

    print()
    print("=" * 55)
    print("  Result")
    print("=" * 55)
    print(f"  Critical point: {critical_dhm}")
    print("-" * 55)
    print(f"  When initial time > {critical_dhm}")
    print(f"    -> {plan_label(above)} saves more time")
    print(f"  When initial time < {critical_dhm}")
    print(f"    -> {plan_label(below)} saves more time")
    print("=" * 55)


def main():
    print()
    print("*" * 55)
    print("  Last War - Alliance Help Time Critical Point Calculator")
    print("*" * 55)
    print()
    print("Enter parameters for both plans (press Enter to use defaults):")

    # Plan A
    print("\n--- Plan A ---")
    n1 = get_int_input("  Number of helps", default=DEFAULT_N1)
    t1 = get_min_sec_input("  Fixed reduction per help (e.g. 32 min 30 sec)", default=DEFAULT_T1)

    # Plan B
    print("\n--- Plan B ---")
    n2 = get_int_input("  Number of helps", default=DEFAULT_N2)
    t2 = get_min_sec_input("  Fixed reduction per help (e.g. 32 min 30 sec)", default=DEFAULT_T2)

    # Summary
    print_plan_summary(n1, t1, n2, t2)

    # Calculate
    critical_minutes = find_critical_point(n1, t1, n2, t2)

    # Output
    print_result(n1, t1, n2, t2, critical_minutes)


if __name__ == "__main__":
    setup_windows_utf8_console()
    while True:
        main()
        print()
        again = input("Recalculate? (y/n, Enter to exit): ").strip().lower()
        if again != "y":
            print("Goodbye!")
            break
