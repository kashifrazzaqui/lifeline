# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Lifeline is a Python CLI tool that calculates how long savings will last given a principal amount, annual return rate, and monthly expenses. It factors in a 2.5% annual charity contribution and projects up to 30 years.

## Running the Application

```bash
# Pretty output with defaults ($1.5M, 10% return, $10K/mo expense)
python lifeline.py --pretty

# Custom parameters
python lifeline.py --principal 2000000 --annual_return 0.08 --monthly_expense 8000 --pretty

# Simple console output (legacy)
python lifeline.py --print_console

# Interactive mode
python lifeline.py --ui

# Output to CSV
python lifeline.py --output_csv
```

## Running Tests

```bash
python -m unittest test_lifeline -v
```

## Architecture

Single-file application (`lifeline.py`) with:

**Core Functions:**
- `calculate_lifeline()` - Core calculation with compound interest, returns result dict
- `calculate_sustainable_expense()` - Max monthly expense for indefinite sustainability
- `calculate_required_return()` - Min return needed for indefinite sustainability

**Display Functions:**
- `render_dashboard()` - Summary with inputs, results, and break-even analysis
- `render_ascii_chart()` - Visual trajectory of principal over time
- `render_pretty_table()` - Unicode table with colors and YoY changes

**Formatting Helpers:**
- `fmt_currency()`, `fmt_percent()`, `colorize_principal()`, `Colors` class

No external dependencies beyond Python standard library.
