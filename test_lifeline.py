#!/usr/bin/env python3
"""Tests for lifeline.py calculations."""

import unittest
from lifeline import (
    calculate_lifeline,
    calculate_sustainable_expense,
    calculate_required_return,
    fmt_currency,
    fmt_percent
)


class TestLifelineCalculations(unittest.TestCase):
    """Test the core lifeline calculation logic."""

    def test_zero_expense_indefinite_growth(self):
        """With zero expenses, principal should grow indefinitely."""
        result = calculate_lifeline(
            principal=100000,
            annual_return=0.05,
            monthly_expense=0
        )
        self.assertTrue(result['indefinite_growth'])
        self.assertGreater(result['final_principal'], 100000)
        self.assertEqual(result['months'], 360)  # 30 years

    def test_zero_return_depletes_linearly(self):
        """With zero return, principal depletes by monthly expense."""
        result = calculate_lifeline(
            principal=12000,
            annual_return=0.0,
            monthly_expense=1000
        )
        # 12000 / 1000 = 12 months, minus 2.5% charity after year 1
        # Year 1: 12000 - 12*1000 = 0, but charity = 0 (no principal left)
        self.assertEqual(result['months'], 12)
        self.assertEqual(result['years'], 1)
        self.assertEqual(result['remaining_months'], 0)
        self.assertFalse(result['indefinite_growth'])

    def test_high_return_low_expense_indefinite(self):
        """High return with low expense should result in indefinite growth."""
        result = calculate_lifeline(
            principal=1000000,
            annual_return=0.10,  # 10% annual
            monthly_expense=1000  # Only 12k/year expense
        )
        self.assertTrue(result['indefinite_growth'])
        # Returns (~100k/yr) far exceed expenses (12k/yr) + charity (25k/yr)
        self.assertGreater(result['final_principal'], 1000000)

    def test_expense_exceeds_principal_immediate_depletion(self):
        """When first expense exceeds principal, should deplete in 1 month."""
        result = calculate_lifeline(
            principal=500,
            annual_return=0.05,
            monthly_expense=1000
        )
        self.assertEqual(result['months'], 1)
        self.assertFalse(result['indefinite_growth'])

    def test_charity_not_deducted_on_zero_principal(self):
        """Bug 1 fix: Charity should not be deducted when principal is exhausted."""
        result = calculate_lifeline(
            principal=6000,
            annual_return=0.0,
            monthly_expense=1000
        )
        # After 6 months, principal = 0. Charity should NOT make it negative.
        self.assertGreaterEqual(result['final_principal'], 0)

    def test_expense_tracking_accurate_in_final_month(self):
        """Bug 2 fix: Total expense should reflect actual amount spent."""
        result = calculate_lifeline(
            principal=1500,
            annual_return=0.0,
            monthly_expense=1000
        )
        # Month 1: 1500 - 1000 = 500
        # Month 2: 500 available, only 500 can be spent (not full 1000)
        yearly_data = result['yearly_data']
        total_expense = yearly_data[0][5]  # Annual Expense column
        # Should be 1500 (1000 + 500), not 2000 (1000 + 1000)
        self.assertEqual(total_expense, 1500)

    def test_compound_interest_calculation(self):
        """Bug 5 fix: Verify proper compound interest is used."""
        # With proper compounding, 5% annual should yield slightly less monthly
        # than simple division (0.05/12 = 0.4167% vs ~0.4074% compound)
        result = calculate_lifeline(
            principal=100000,
            annual_return=0.05,
            monthly_expense=0
        )
        # After 1 year with proper 5% compound, principal should be ~102,500
        # 100000 * 1.05 = 105000, then charity = 100000 * 0.025 = 2500
        # Ending = 105000 - 2500 = 102500
        year1_data = result['yearly_data'][0]
        year1_ending = year1_data[6]
        self.assertAlmostEqual(year1_ending, 102500, delta=50)

    def test_yearly_data_structure(self):
        """Verify yearly_data contains expected columns."""
        result = calculate_lifeline(
            principal=100000,
            annual_return=0.05,
            monthly_expense=5000
        )
        self.assertGreater(len(result['yearly_data']), 0)
        first_row = result['yearly_data'][0]
        # [Year, Starting Principal, Annual Return %, Returns Amount,
        #  Charity Amount, Annual Expense, Ending Principal]
        self.assertEqual(len(first_row), 7)
        self.assertEqual(first_row[0], 1)  # Year 1
        self.assertEqual(first_row[1], 100000)  # Starting principal

    def test_30_year_projection_completes(self):
        """Ensure indefinite growth scenarios complete 30 year projection."""
        result = calculate_lifeline(
            principal=10000000,  # 10 million
            annual_return=0.08,
            monthly_expense=10000
        )
        self.assertTrue(result['indefinite_growth'])
        self.assertEqual(len(result['yearly_data']), 30)
        self.assertEqual(result['months'], 360)

    def test_negative_return_accelerates_depletion(self):
        """Negative returns should cause faster depletion."""
        result_positive = calculate_lifeline(
            principal=100000,
            annual_return=0.05,
            monthly_expense=2000
        )
        result_negative = calculate_lifeline(
            principal=100000,
            annual_return=-0.05,
            monthly_expense=2000
        )
        self.assertGreater(result_positive['months'], result_negative['months'])


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def test_zero_principal(self):
        """Zero principal should result in zero months."""
        result = calculate_lifeline(
            principal=0,
            annual_return=0.05,
            monthly_expense=1000
        )
        self.assertEqual(result['months'], 0)
        self.assertFalse(result['indefinite_growth'])

    def test_very_small_principal(self):
        """Very small principal should handle gracefully."""
        result = calculate_lifeline(
            principal=1,
            annual_return=0.05,
            monthly_expense=1000
        )
        self.assertEqual(result['months'], 1)

    def test_very_high_return(self):
        """Very high return rate should not cause errors."""
        result = calculate_lifeline(
            principal=100000,
            annual_return=1.0,  # 100% annual return
            monthly_expense=1000
        )
        self.assertTrue(result['indefinite_growth'])


class TestBreakEvenAnalysis(unittest.TestCase):
    """Test break-even calculations."""

    def test_sustainable_expense_calculation(self):
        """Verify sustainable expense calculation."""
        # With 1M principal, 5% return, 2.5% charity = 2.5% net
        # Sustainable = 1M * 0.025 / 12 = ~$2,083/month
        sustainable = calculate_sustainable_expense(1000000, 0.05, 0.025)
        self.assertAlmostEqual(sustainable, 2083.33, delta=1)

    def test_sustainable_expense_zero_when_return_below_charity(self):
        """No sustainable expense when return <= charity rate."""
        sustainable = calculate_sustainable_expense(1000000, 0.02, 0.025)
        self.assertEqual(sustainable, 0)

    def test_required_return_calculation(self):
        """Verify required return calculation."""
        # 10K/mo expense on 1M principal = 12% annual + 2.5% charity = 14.5%
        required = calculate_required_return(1000000, 10000, 0.025)
        self.assertAlmostEqual(required, 0.145, delta=0.001)

    def test_sustainable_equals_expense_at_equilibrium(self):
        """At exact break-even, sustainable should equal expense."""
        principal = 1000000
        expense = 2083.33
        charity = 0.025
        # Calculate what return would make this sustainable
        required = calculate_required_return(principal, expense, charity)
        # Now check sustainable at that return
        sustainable = calculate_sustainable_expense(principal, required, charity)
        self.assertAlmostEqual(sustainable, expense, delta=1)


class TestFormatting(unittest.TestCase):
    """Test formatting helper functions."""

    def test_fmt_currency_basic(self):
        """Test basic currency formatting."""
        self.assertEqual(fmt_currency(1000000), "$1,000,000")
        self.assertEqual(fmt_currency(1234.56), "$1,235")

    def test_fmt_currency_with_cents(self):
        """Test currency formatting with cents."""
        self.assertEqual(fmt_currency(1234.56, show_cents=True), "$1,234.56")

    def test_fmt_percent(self):
        """Test percentage formatting."""
        self.assertEqual(fmt_percent(5.0), "5.0%")
        self.assertEqual(fmt_percent(10.55), "10.6%")


if __name__ == '__main__':
    unittest.main()
