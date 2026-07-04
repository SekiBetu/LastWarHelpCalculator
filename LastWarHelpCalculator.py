"""
Last War Alliance Help Time Critical Point Calculator
======================================================
Each help reduces time by: max(remaining_time * percent, fixed_time)
Uses binary search to find the initial time threshold where Plan A
overtakes Plan B in total time saved.
"""

# ---- Fixed constants (not user-input) ----
PERCENT_RATIO = 0.005   # 0.5%
EPSILON = 0.001         # binary search precision in minutes

# ---- Input defaults (used when user presses Enter) ----
DEFAULT_N1 = 37
DEFAULT_T1 = 32.5
DEFAULT_N2 = 35
DEFAULT_T2 = 48.5


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


def simulate_help(initial_time, help_count, fixed_time, percent_ratio=PERCENT_RATIO):
    """Simulate total time reduced after multiple helps."""
    current_time = initial_time
    for _ in range(help_count):
        reduction = max(current_time * percent_ratio, fixed_time)
        current_time -= reduction
    return initial_time - current_time


def find_critical_point(n1, t1, n2, t2, percent_ratio=PERCENT_RATIO, epsilon=EPSILON):
    """Binary search for the critical initial time where both plans yield
    equal total reduction. Returns critical_minutes."""
    low = 0.0
    high = 1000000.0

    while high - low > epsilon:
        mid_time = (low + high) / 2
        reduction1 = simulate_help(mid_time, n1, t1, percent_ratio)
        reduction2 = simulate_help(mid_time, n2, t2, percent_ratio)

        if reduction1 > reduction2:
            high = mid_time
        else:
            low = mid_time

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


def print_plan_summary(n1, t1, n2, t2):
    """Print plan overview."""
    print()
    print("=" * 55)
    print("  Plan Overview")
    print("=" * 55)
    print(f"  Percentage reduction: {PERCENT_RATIO*100:.1f}%")
    print(f"  Plan A: {n1} helps, {t1} min fixed each")
    print(f"  Plan B: {n2} helps, {t2} min fixed each")
    print("=" * 55)


def print_result(n1, t1, n2, t2, critical_minutes):
    """Print calculation result with day/hour/min format."""
    critical_dhm = format_duration(critical_minutes)
    print()
    print("=" * 55)
    print("  Result")
    print("=" * 55)
    print(f"  Critical point: {critical_dhm}")
    print("-" * 55)
    print(f"  When initial time > {critical_dhm}")
    print(f"    -> Plan A ({n1}x/{t1}m) saves more time")
    print(f"  When initial time < {critical_dhm}")
    print(f"    -> Plan B ({n2}x/{t2}m) saves more time")
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
    t1 = get_float_input("  Fixed reduction per help (min)", default=DEFAULT_T1)

    # Plan B
    print("\n--- Plan B ---")
    n2 = get_int_input("  Number of helps", default=DEFAULT_N2)
    t2 = get_float_input("  Fixed reduction per help (min)", default=DEFAULT_T2)

    # Summary
    print_plan_summary(n1, t1, n2, t2)

    # Calculate
    critical_minutes = find_critical_point(n1, t1, n2, t2)

    # Output
    print_result(n1, t1, n2, t2, critical_minutes)


if __name__ == "__main__":
    while True:
        main()
        print()
        again = input("Recalculate? (y/n, Enter to exit): ").strip().lower()
        if again != "y":
            print("Goodbye!")
            break
