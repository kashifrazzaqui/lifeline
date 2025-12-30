#!/usr/bin/env python3

import csv
import argparse
import sys
import os

# ============================================================================
# ANSI Color Codes
# ============================================================================
class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Foreground
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright foreground
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_CYAN = '\033[96m'

    @classmethod
    def disable(cls):
        """Disable colors (for non-TTY output)."""
        for attr in dir(cls):
            if not attr.startswith('_') and attr.isupper():
                setattr(cls, attr, '')


# Disable colors if not a TTY
if not sys.stdout.isatty():
    Colors.disable()


# ============================================================================
# Formatting Helpers
# ============================================================================
def fmt_currency(amount, show_cents=False):
    """Format number as currency with thousand separators."""
    if show_cents:
        return f"${amount:,.2f}"
    return f"${amount:,.0f}"


def fmt_percent(value):
    """Format as percentage."""
    return f"{value:.1f}%"


def fmt_change(current, previous):
    """Format year-over-year change with color."""
    if previous == 0:
        return f"{Colors.DIM}—{Colors.RESET}"
    change = ((current - previous) / previous) * 100
    if change > 0:
        return f"{Colors.BRIGHT_GREEN}+{change:.1f}%{Colors.RESET}"
    elif change < 0:
        return f"{Colors.BRIGHT_RED}{change:.1f}%{Colors.RESET}"
    return f"{Colors.DIM}0.0%{Colors.RESET}"


def colorize_principal(amount, start_amount):
    """Color code principal based on remaining percentage."""
    if amount <= 0:
        return f"{Colors.BRIGHT_RED}{fmt_currency(amount)}{Colors.RESET}"
    pct = (amount / start_amount) * 100
    if pct > 100:
        return f"{Colors.BRIGHT_GREEN}{fmt_currency(amount)}{Colors.RESET}"
    elif pct > 50:
        return f"{Colors.GREEN}{fmt_currency(amount)}{Colors.RESET}"
    elif pct > 25:
        return f"{Colors.YELLOW}{fmt_currency(amount)}{Colors.RESET}"
    else:
        return f"{Colors.RED}{fmt_currency(amount)}{Colors.RESET}"


# ============================================================================
# Break-Even Analysis
# ============================================================================
def calculate_sustainable_expense(principal, annual_return, charity_rate=0.025):
    """Calculate the maximum monthly expense for indefinite sustainability."""
    # Annual return must exceed charity rate for any sustainability
    net_return = annual_return - charity_rate
    if net_return <= 0:
        return 0
    # Sustainable annual expense = principal * net annual return
    sustainable_annual = principal * net_return
    return sustainable_annual / 12


def calculate_required_return(principal, monthly_expense, charity_rate=0.025):
    """Calculate the minimum annual return needed for indefinite sustainability."""
    annual_expense = monthly_expense * 12
    # Required return = (annual_expense / principal) + charity_rate
    required = (annual_expense / principal) + charity_rate
    return required


# ============================================================================
# ASCII Chart
# ============================================================================
def render_ascii_chart(yearly_data, width=60, height=12):
    """Render an ASCII chart of principal over time."""
    if not yearly_data:
        return ""

    principals = [row[1] for row in yearly_data]  # Starting principals
    principals.append(yearly_data[-1][6])  # Add final ending principal

    max_val = max(principals)
    min_val = min(0, min(principals))  # Include 0 or negative
    val_range = max_val - min_val if max_val != min_val else 1

    # Build chart
    lines = []
    chart_chars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']

    # Title
    lines.append(f"{Colors.BOLD}📈 Principal Trajectory{Colors.RESET}")
    lines.append("")

    # Y-axis labels and chart area
    for row in range(height, -1, -1):
        threshold = min_val + (val_range * row / height)

        # Y-axis label (only at top, middle, bottom)
        if row == height:
            label = fmt_currency(max_val)
        elif row == height // 2:
            label = fmt_currency((max_val + min_val) / 2)
        elif row == 0:
            label = fmt_currency(min_val)
        else:
            label = ""

        label = f"{label:>12} │"

        # Chart row
        row_chars = []
        for i, val in enumerate(principals):
            normalized = (val - min_val) / val_range
            bar_height = int(normalized * height)

            if bar_height >= row:
                # Color based on trend
                if i > 0 and principals[i] < principals[i-1]:
                    char = f"{Colors.RED}█{Colors.RESET}"
                else:
                    char = f"{Colors.GREEN}█{Colors.RESET}"
            elif bar_height == row - 1 and row > 0:
                char = f"{Colors.DIM}▄{Colors.RESET}"
            else:
                char = " "
            row_chars.append(char)

        lines.append(label + "".join(row_chars))

    # X-axis
    x_axis = " " * 13 + "└" + "─" * len(principals)
    lines.append(x_axis)

    # X-axis labels
    x_labels = " " * 14
    for i in range(len(principals)):
        if i == 0:
            x_labels += "1"
        elif i == len(principals) - 1:
            x_labels += str(len(yearly_data))
        elif i == len(principals) // 2:
            x_labels += str(len(yearly_data) // 2)
        else:
            x_labels += " "
    lines.append(f"{x_labels}")
    lines.append(f"{Colors.DIM}{'Year':^{14 + len(principals)}}{Colors.RESET}")

    return "\n".join(lines)


# ============================================================================
# Pretty Table
# ============================================================================
def render_pretty_table(yearly_data, initial_principal):
    """Render a beautiful Unicode table with colors."""
    if not yearly_data:
        return ""

    # Box drawing characters
    TL, TR, BL, BR = '╭', '╮', '╰', '╯'
    H, V = '─', '│'
    LT, RT, TT, BT, X = '├', '┤', '┬', '┴', '┼'

    # Column widths
    cols = [
        ("Year", 6),
        ("Principal", 14),
        ("Returns", 11),
        ("Charity", 10),
        ("Expenses", 11),
        ("Ending", 15),
        ("YoY", 9),
    ]

    total_width = sum(w for _, w in cols) + len(cols) + 1

    lines = []

    # Title
    lines.append("")
    lines.append(f"{Colors.BOLD}📊 Year-by-Year Breakdown{Colors.RESET}")
    lines.append("")

    # Top border
    header_border = TL
    for i, (_, w) in enumerate(cols):
        header_border += H * w
        header_border += TT if i < len(cols) - 1 else TR
    lines.append(f"{Colors.DIM}{header_border}{Colors.RESET}")

    # Header row
    header = V
    for name, w in cols:
        header += f"{Colors.BOLD}{name:^{w}}{Colors.RESET}{V}"
    lines.append(header)

    # Header separator
    sep = LT
    for i, (_, w) in enumerate(cols):
        sep += H * w
        sep += X if i < len(cols) - 1 else RT
    lines.append(f"{Colors.DIM}{sep}{Colors.RESET}")

    # Data rows
    prev_principal = initial_principal
    for row in yearly_data:
        year, start_p, ret_pct, returns, charity, expenses, end_p = row

        # Determine row color based on trajectory
        if end_p > start_p:
            row_indicator = f"{Colors.GREEN}▲{Colors.RESET}"
        elif end_p > 0:
            row_indicator = f"{Colors.YELLOW}▼{Colors.RESET}"
        else:
            row_indicator = f"{Colors.RED}✗{Colors.RESET}"

        # Calculate plain change value for proper spacing
        if prev_principal == 0:
            change_pct = 0
        else:
            change_pct = ((end_p - prev_principal) / prev_principal) * 100

        data_row = f"{Colors.DIM}{V}{Colors.RESET}"
        data_row += f"{row_indicator} {year:<4}{Colors.DIM}{V}{Colors.RESET}"
        data_row += f"{fmt_currency(start_p):>13} {Colors.DIM}{V}{Colors.RESET}"
        data_row += f"{Colors.GREEN}{fmt_currency(returns):>10}{Colors.RESET} {Colors.DIM}{V}{Colors.RESET}"
        data_row += f"{Colors.CYAN}{fmt_currency(charity):>9}{Colors.RESET} {Colors.DIM}{V}{Colors.RESET}"
        data_row += f"{Colors.RED}{fmt_currency(expenses):>10}{Colors.RESET} {Colors.DIM}{V}{Colors.RESET}"
        data_row += f"{colorize_principal(end_p, initial_principal):>24} {Colors.DIM}{V}{Colors.RESET}"

        # Format change with color
        if change_pct > 0:
            change_str = f"{Colors.BRIGHT_GREEN}{change_pct:>+6.1f}%{Colors.RESET}"
        elif change_pct < 0:
            change_str = f"{Colors.BRIGHT_RED}{change_pct:>+6.1f}%{Colors.RESET}"
        else:
            change_str = f"{Colors.DIM}  0.0%{Colors.RESET}"
        data_row += f" {change_str}{Colors.DIM}{V}{Colors.RESET}"

        lines.append(data_row)
        prev_principal = end_p

    # Bottom border
    bottom = BL
    for i, (_, w) in enumerate(cols):
        bottom += H * w
        bottom += BT if i < len(cols) - 1 else BR
    lines.append(f"{Colors.DIM}{bottom}{Colors.RESET}")

    return "\n".join(lines)


# ============================================================================
# Summary Dashboard
# ============================================================================
def render_dashboard(result, principal, annual_return, monthly_expense, charity_rate=0.025):
    """Render a summary dashboard with key metrics."""
    lines = []

    # Header
    lines.append("")
    lines.append(f"{Colors.BOLD}{'═' * 60}{Colors.RESET}")
    lines.append(f"{Colors.BOLD}{'LIFELINE FINANCIAL PROJECTION':^60}{Colors.RESET}")
    lines.append(f"{Colors.BOLD}{'═' * 60}{Colors.RESET}")
    lines.append("")

    # Input Parameters
    lines.append(f"{Colors.CYAN}▸ INPUT PARAMETERS{Colors.RESET}")
    lines.append(f"  Starting Principal:  {Colors.BOLD}{fmt_currency(principal)}{Colors.RESET}")
    lines.append(f"  Annual Return:       {Colors.BOLD}{fmt_percent(annual_return * 100)}{Colors.RESET}")
    lines.append(f"  Monthly Expense:     {Colors.BOLD}{fmt_currency(monthly_expense)}{Colors.RESET}")
    lines.append(f"  Annual Expense:      {fmt_currency(monthly_expense * 12)}")
    lines.append(f"  Charity Rate:        {fmt_percent(charity_rate * 100)}/year")
    lines.append("")

    # Result
    lines.append(f"{Colors.CYAN}▸ PROJECTION RESULT{Colors.RESET}")
    if result['indefinite_growth']:
        lines.append(f"  {Colors.BRIGHT_GREEN}★ INDEFINITE SUSTAINABILITY ★{Colors.RESET}")
        lines.append(f"  Your savings will {Colors.BOLD}grow forever{Colors.RESET}!")
        lines.append(f"  Principal at year 30: {Colors.BRIGHT_GREEN}{fmt_currency(result['final_principal'])}{Colors.RESET}")
    elif result['months'] >= 360:  # Survived 30 years but declining
        lines.append(f"  {Colors.YELLOW}◐ LONG RUNWAY (30+ years){Colors.RESET}")
        lines.append(f"  Savings will last beyond 30 years but are {Colors.YELLOW}declining{Colors.RESET}")
        lines.append(f"  Principal at year 30: {Colors.YELLOW}{fmt_currency(result['final_principal'])}{Colors.RESET}")
    else:
        years = result['years']
        months = result['remaining_months']
        lines.append(f"  Runway: {Colors.BOLD}{Colors.YELLOW}{years} years, {months} months{Colors.RESET}")
        lines.append(f"  Final Principal: {Colors.RED}{fmt_currency(result['final_principal'])}{Colors.RESET}")
    lines.append("")

    # Break-even Analysis
    sustainable = calculate_sustainable_expense(principal, annual_return, charity_rate)
    required = calculate_required_return(principal, monthly_expense, charity_rate)

    lines.append(f"{Colors.CYAN}▸ BREAK-EVEN ANALYSIS{Colors.RESET}")
    lines.append(f"  Sustainable Monthly Expense: {Colors.GREEN}{fmt_currency(sustainable)}{Colors.RESET}")
    lines.append(f"    └─ Max expense for infinite runway at {fmt_percent(annual_return * 100)} return")
    lines.append(f"  Required Return Rate: {Colors.YELLOW}{fmt_percent(required * 100)}{Colors.RESET}")
    lines.append(f"    └─ Min return needed for infinite runway at {fmt_currency(monthly_expense)}/mo")

    # Gap analysis
    expense_gap = monthly_expense - sustainable
    return_gap = required - annual_return

    lines.append("")
    if expense_gap > 0:
        lines.append(f"  {Colors.RED}⚠ Expense Gap: {fmt_currency(expense_gap)}/mo over sustainable{Colors.RESET}")
    else:
        lines.append(f"  {Colors.GREEN}✓ Expenses are within sustainable limit{Colors.RESET}")

    if return_gap > 0:
        lines.append(f"  {Colors.RED}⚠ Return Gap: Need {fmt_percent(return_gap * 100)} more return{Colors.RESET}")
    else:
        lines.append(f"  {Colors.GREEN}✓ Returns exceed minimum required{Colors.RESET}")

    lines.append("")
    lines.append(f"{Colors.DIM}{'─' * 60}{Colors.RESET}")

    return "\n".join(lines)


# ============================================================================
# Core Calculation
# ============================================================================
def calculate_lifeline(principal, annual_return, monthly_expense, output_csv=False, print_console=False, pretty=False):
    months = 0
    # Bug 5 fix: Use proper compound interest conversion
    monthly_return_rate = (1 + annual_return) ** (1/12) - 1
    charity_rate = 0.025
    remaining_principal = principal

    # List to store yearly data if CSV or console output is required
    yearly_data = []

    year = 1
    indefinite_growth = False
    while remaining_principal > 0 and year <= 30:
        starting_principal = remaining_principal
        total_interest = 0
        total_expense = 0

        for _ in range(12):
            if remaining_principal <= 0:
                break
            interest_earned = remaining_principal * monthly_return_rate
            available_for_expense = remaining_principal + interest_earned

            # Bug 2 fix: Only count actual expense that can be paid
            if available_for_expense >= monthly_expense:
                actual_expense = monthly_expense
            else:
                actual_expense = max(0, available_for_expense)

            remaining_principal = available_for_expense - actual_expense
            total_interest += interest_earned
            total_expense += actual_expense
            months += 1

        # Bug 1 fix: Only deduct charity if principal is positive, and only up to available amount
        if remaining_principal > 0:
            charity_amount = min(starting_principal * charity_rate, remaining_principal)
            remaining_principal -= charity_amount
        else:
            charity_amount = 0

        yearly_data.append([
            year, round(starting_principal, 2), round(annual_return * 100, 2), round(total_interest, 2),
            round(charity_amount, 2), round(total_expense, 2), round(remaining_principal, 2)
        ])

        # Bug 3 fix: Check for indefinite growth each year, not just at year 30
        if remaining_principal > starting_principal:
            if year == 30:
                indefinite_growth = True
            # Continue to year 30 to show full projection even if growing

        year += 1

    # Mark as indefinite only if principal is actually growing (not just lasting 30 years)
    # True indefinite means ending > starting, not just surviving 30 years
    if year > 30 and remaining_principal > principal:
        indefinite_growth = True

    # Build result dict for testing/programmatic use
    result = {
        'months': months,
        'years': months // 12,
        'remaining_months': months % 12,
        'final_principal': remaining_principal,
        'indefinite_growth': indefinite_growth,
        'yearly_data': yearly_data
    }

    if output_csv:
        with open('yearly_output.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Year', 'Starting Principal', 'Annual Return %', 'Annual Returns Amount', 'Charity Amount', 'Annual Expense', 'Ending Year Principal'])
            writer.writerows(yearly_data)
        print("Yearly output saved to 'yearly_output.csv'.")

    if pretty:
        # Full pretty output with dashboard, chart, and table
        print(render_dashboard(result, principal, annual_return, monthly_expense, charity_rate))
        print(render_ascii_chart(yearly_data))
        print(render_pretty_table(yearly_data, principal))
        print("")
    elif print_console:
        # Simple console output (legacy)
        print(f"{'Year':<5} {'Starting Principal':<20} {'Annual Return %':<15} {'Annual Returns Amount':<20} {'Charity Amount':<15} {'Annual Expense':<15} {'Ending Year Principal':<20}")
        for row in yearly_data:
            print(f"{row[0]:<5} {row[1]:<20} {row[2]:<15} {row[3]:<20} {row[4]:<15} {row[5]:<15} {row[6]:<20}")

        if indefinite_growth:
            print(f"\nThe principal will grow indefinitely. Principal at 30 years will be approximately {remaining_principal:.2f}.")
        else:
            years = months // 12
            remaining_months = months % 12
            print(f"\nYour savings will last for approximately {years} years and {remaining_months} months.")

    return result


def main():
    parser = argparse.ArgumentParser(
        description='Calculate how long your savings will last with given parameters.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python lifeline.py --pretty                           # Use defaults ($1.5M, 10%, $10K/mo)
  python lifeline.py --annual_return 0.07 --pretty      # Lower return rate
  python lifeline.py --monthly_expense 5000 --pretty    # Lower expenses
        """
    )
    parser.add_argument('--principal', type=float, default=1500000, help='Principal saving amount (default: 1,500,000)')
    parser.add_argument('--annual_return', type=float, default=0.10, help='Annual return rate (as a decimal, e.g., 0.10 for 10%%) (default: 0.10)')
    parser.add_argument('--monthly_expense', type=float, default=10000, help='Monthly expense (default: 10,000)')
    parser.add_argument('--output_csv', action='store_true', help='Generate a yearly output CSV file')
    parser.add_argument('--print_console', action='store_true', help='Print simple yearly output to the console')
    parser.add_argument('--pretty', action='store_true', help='Print beautiful formatted output with charts and analysis')
    parser.add_argument('--ui', action='store_true', help='Provide input through the console interactively')

    args = parser.parse_args()

    if args.ui:
        principal = input(f"Enter the principal saving amount (default: {args.principal}): ") or args.principal
        annual_return = input(f"Enter the annual return rate (as a decimal, e.g., 0.05 for 5%%) (default: {args.annual_return}): ") or args.annual_return
        monthly_expense = input(f"Enter the monthly expense (default: {args.monthly_expense}): ") or args.monthly_expense
        output_csv = input("Do you want to generate a yearly output CSV file? (yes/no) (default: no): ").strip().lower() == 'yes'
        pretty = input("Do you want pretty formatted output? (yes/no) (default: yes): ").strip().lower() != 'no'

        principal = float(principal)
        annual_return = float(annual_return)
        monthly_expense = float(monthly_expense)
        print_console = False
    else:
        principal = args.principal
        annual_return = args.annual_return
        monthly_expense = args.monthly_expense
        output_csv = args.output_csv
        print_console = args.print_console
        pretty = args.pretty

    calculate_lifeline(
        principal,
        annual_return,
        monthly_expense,
        output_csv,
        print_console,
        pretty
    )

if __name__ == "__main__":
    main()

