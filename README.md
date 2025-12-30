# Lifeline

A financial runway calculator that projects how long your savings will last given your principal, expected returns, and monthly expenses.

## Features

- **Accurate Compound Interest**: Uses proper monthly compounding formula `(1 + annual_rate)^(1/12) - 1`
- **Charity Factor**: Automatically accounts for 2.5% annual charitable giving
- **Break-Even Analysis**: Shows sustainable expense levels and required return rates
- **Beautiful Terminal Output**: Color-coded tables, ASCII charts, and formatted currency
- **Multiple Output Modes**: Pretty display, simple console, CSV export, or JSON-compatible dict
- **30-Year Projection**: Projects your financial runway up to 30 years

## Installation

No dependencies required beyond Python 3.6+.

```bash
git clone <repository-url>
cd lifeline
```

## Quick Start

```bash
# Run with pretty output (recommended)
python lifeline.py --pretty

# Run with custom parameters
python lifeline.py --principal 2000000 --annual_return 0.08 --monthly_expense 8000 --pretty
```

## Usage

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--principal` | Starting savings amount | $1,500,000 |
| `--annual_return` | Expected annual return rate (decimal) | 0.10 (10%) |
| `--monthly_expense` | Monthly living expenses | $10,000 |
| `--pretty` | Beautiful formatted output with charts | Off |
| `--print_console` | Simple tabular output | Off |
| `--output_csv` | Export to `yearly_output.csv` | Off |
| `--ui` | Interactive input mode | Off |

### Examples

```bash
# Default scenario: $1.5M, 10% return, $10K/month
python lifeline.py --pretty

# Conservative scenario: 5% return
python lifeline.py --annual_return 0.05 --pretty

# Higher expenses
python lifeline.py --monthly_expense 15000 --pretty

# Different principal
python lifeline.py --principal 2000000 --pretty

# Export to CSV for spreadsheet analysis
python lifeline.py --output_csv

# Interactive mode - enter values when prompted
python lifeline.py --ui
```

## Understanding the Output

### Dashboard Sections

#### 1. Input Parameters
Shows your starting values:
```
▸ INPUT PARAMETERS
  Starting Principal:  $1,500,000
  Annual Return:       10.0%
  Monthly Expense:     $10,000
  Annual Expense:      $120,000
  Charity Rate:        2.5%/year
```

#### 2. Projection Result
Three possible outcomes:

| Result | Meaning |
|--------|---------|
| ★ INDEFINITE SUSTAINABILITY | Your principal grows forever - expenses + charity < returns |
| ◐ LONG RUNWAY (30+ years) | Lasts beyond 30 years but principal is declining |
| Runway: X years, Y months | Will be depleted within the projection period |

#### 3. Break-Even Analysis
Shows sustainability thresholds:
```
▸ BREAK-EVEN ANALYSIS
  Sustainable Monthly Expense: $9,375
    └─ Max expense for infinite runway at 10.0% return
  Required Return Rate: 10.5%
    └─ Min return needed for infinite runway at $10,000/mo
```

- **Sustainable Expense**: Maximum monthly spending that would make your savings last forever
- **Required Return**: Minimum annual return needed to sustain your current spending forever
- **Gap Analysis**: Shows if you're above/below sustainable thresholds

#### 4. Principal Trajectory Chart
ASCII visualization of your principal over 30 years:
```
📈 Principal Trajectory

  $1,500,000 │█▄▄▄▄▄▄▄
             │████████▄▄▄▄▄
             │█████████████▄▄▄
    $750,000 │████████████████████████▄
          $0 │███████████████████████████████
             └───────────────────────────────
              1              15              30
```

#### 5. Year-by-Year Breakdown
Detailed table with:
- **Year**: Year number (1-30)
- **Principal**: Starting balance for that year
- **Returns**: Interest/returns earned during the year
- **Charity**: 2.5% of starting principal donated
- **Expenses**: Total annual expenses (monthly × 12)
- **Ending**: Balance at end of year
- **YoY**: Year-over-year percentage change

Color coding:
- 🟢 Green `▲`: Principal is growing
- 🟡 Yellow `▼`: Principal is declining but positive
- 🔴 Red `✗`: Principal is depleted

## How It Works

### The Calculation Model

Each month:
1. **Earn Returns**: `principal × monthly_rate` where `monthly_rate = (1 + annual_return)^(1/12) - 1`
2. **Pay Expenses**: Deduct monthly expense (or remaining balance if insufficient)
3. **Update Principal**: `new_principal = old_principal + returns - expenses`

At year end:
4. **Pay Charity**: Deduct 2.5% of the year's starting principal (if funds available)

### Break-Even Formulas

**Sustainable Monthly Expense:**
```
sustainable = principal × (annual_return - charity_rate) / 12
```

**Required Annual Return:**
```
required = (monthly_expense × 12 / principal) + charity_rate
```

### Key Assumptions

- Returns compound monthly
- Expenses are paid monthly
- Charity (2.5%) is deducted annually based on year-start principal
- No inflation adjustment (nominal values)
- No taxes on returns
- Consistent return rate (no market volatility)

## Scenarios

### Scenario 1: Indefinite Sustainability
```bash
python lifeline.py --principal 1500000 --annual_return 0.10 --monthly_expense 3000 --pretty
```
With low expenses relative to returns, principal grows forever.

### Scenario 2: Long Runway (30+ years)
```bash
python lifeline.py --principal 1500000 --annual_return 0.10 --monthly_expense 10000 --pretty
```
Lasts beyond 30 years but slowly declining.

### Scenario 3: Moderate Runway
```bash
python lifeline.py --principal 1500000 --annual_return 0.05 --monthly_expense 10000 --pretty
```
Lower returns mean faster depletion (~15 years).

### Scenario 4: Short Runway
```bash
python lifeline.py --principal 500000 --annual_return 0.05 --monthly_expense 10000 --pretty
```
Smaller principal depletes quickly (~5 years).

## Programmatic Usage

```python
from lifeline import calculate_lifeline, calculate_sustainable_expense, calculate_required_return

# Run calculation
result = calculate_lifeline(
    principal=1500000,
    annual_return=0.10,
    monthly_expense=10000
)

print(f"Runway: {result['years']} years, {result['remaining_months']} months")
print(f"Final Principal: ${result['final_principal']:,.2f}")
print(f"Indefinite Growth: {result['indefinite_growth']}")

# Access yearly data
for year_data in result['yearly_data']:
    year, start, ret_pct, returns, charity, expenses, end = year_data
    print(f"Year {year}: ${start:,.0f} → ${end:,.0f}")

# Break-even analysis
sustainable = calculate_sustainable_expense(1500000, 0.10)
print(f"Sustainable expense: ${sustainable:,.2f}/month")

required = calculate_required_return(1500000, 10000)
print(f"Required return: {required:.1%}")
```

### Return Value Structure

```python
{
    'months': 178,                    # Total months until depletion
    'years': 14,                      # Full years
    'remaining_months': 10,           # Additional months
    'final_principal': 0.0,           # Ending balance
    'indefinite_growth': False,       # True if sustainable forever
    'yearly_data': [                  # List of yearly snapshots
        [1, 1500000.0, 10.0, 144595.0, 37500.0, 120000.0, 1487095.0],
        # [year, start, return%, returns, charity, expenses, end]
        ...
    ]
}
```

## Testing

```bash
# Run all tests
python -m unittest test_lifeline -v

# Run specific test class
python -m unittest test_lifeline.TestLifelineCalculations -v
python -m unittest test_lifeline.TestBreakEvenAnalysis -v
python -m unittest test_lifeline.TestFormatting -v
python -m unittest test_lifeline.TestEdgeCases -v
```

### Test Coverage

- **Core Calculations**: Zero expense, zero return, high/low combinations
- **Bug Fixes**: Charity on exhausted funds, expense tracking, compound interest
- **Break-Even Analysis**: Sustainable expense, required return, equilibrium
- **Formatting**: Currency, percentage, color functions
- **Edge Cases**: Zero principal, very small amounts, very high returns

## File Structure

```
lifeline/
├── lifeline.py          # Main application
├── test_lifeline.py     # Test suite (20 tests)
├── README.md            # This file
├── CLAUDE.md            # AI assistant guidance
└── yearly_output.csv    # Generated when using --output_csv
```

## Tips for Financial Planning

1. **Be Conservative**: Use lower return estimates (5-7%) for safer projections
2. **Account for Inflation**: Your real purchasing power decreases ~2-3% annually
3. **Buffer for Volatility**: Markets don't return steady percentages each year
4. **Review Regularly**: Re-run projections as circumstances change
5. **Consider Taxes**: Returns may be taxable depending on account type

## Limitations

- **No Inflation Modeling**: All values are nominal, not inflation-adjusted
- **No Tax Calculations**: Returns shown are pre-tax
- **Fixed Return Rate**: Real markets have variable returns
- **No Income Sources**: Doesn't model Social Security, pensions, or part-time income
- **30-Year Cap**: Projection stops at 30 years

## License

MIT License - Feel free to use, modify, and distribute.
