#!/usr/bin/env python3

import csv
import argparse

def calculate_lifeline(principal, annual_return, monthly_expense, output_csv=False, print_console=True):
    months = 0
    monthly_return_rate = annual_return / 12
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
            remaining_principal += interest_earned - monthly_expense
            total_interest += interest_earned
            total_expense += monthly_expense
            months += 1

        charity_amount = starting_principal * charity_rate
        remaining_principal -= charity_amount

        if output_csv or print_console:
            yearly_data.append([
                year, round(starting_principal, 2), round(annual_return * 100, 2), round(total_interest, 2),
                round(charity_amount, 2), round(total_expense, 2), round(remaining_principal, 2)
            ])

        if remaining_principal > starting_principal and year == 30:
            indefinite_growth = True
            break

        year += 1

    if output_csv:
        with open('yearly_output.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Year', 'Starting Principal', 'Annual Return %', 'Annual Returns Amount', 'Charity Amount', 'Annual Expense', 'Ending Year Principal'])
            writer.writerows(yearly_data)
        print("Yearly output saved to 'yearly_output.csv'.")

    if print_console:
        print(f"{'Year':<5} {'Starting Principal':<20} {'Annual Return %':<15} {'Annual Returns Amount':<20} {'Charity Amount':<15} {'Annual Expense':<15} {'Ending Year Principal':<20}")
        for row in yearly_data:
            print(f"{row[0]:<5} {row[1]:<20} {row[2]:<15} {row[3]:<20} {row[4]:<15} {row[5]:<15} {row[6]:<20}")

    if indefinite_growth:
        print(f"\nThe principal will grow indefinitely. Principal at 30 years will be approximately {remaining_principal:.2f}.")
    else:
        years = months // 12
        remaining_months = months % 12
        print(f"\nYour savings will last for approximately {years} years and {remaining_months} months.")

def main():
    parser = argparse.ArgumentParser(description='Calculate how long your savings will last with given parameters.')
    parser.add_argument('--principal', type=float, default=1000000, help='Principal saving amount (default: 1,000,000)')
    parser.add_argument('--annual_return', type=float, default=0.05, help='Annual return rate (as a decimal, e.g., 0.05 for 5%) (default: 0.05)')
    parser.add_argument('--monthly_expense', type=float, default=7000, help='Monthly expense (default: 7,000)')
    parser.add_argument('--output_csv', action='store_true', help='Generate a yearly output CSV file')
    parser.add_argument('--print_console', action='store_true', help='Print the yearly output to the console')
    parser.add_argument('--ui', action='store_true', help='Provide input through the console interactively')

    args = parser.parse_args()

    if args.ui:
        principal = input(f"Enter the principal saving amount (default: {args.principal}): ") or args.principal
        annual_return = input(f"Enter the annual return rate (as a decimal, e.g., 0.05 for 5%) (default: {args.annual_return}): ") or args.annual_return
        monthly_expense = input(f"Enter the monthly expense (default: {args.monthly_expense}): ") or args.monthly_expense
        output_csv = input("Do you want to generate a yearly output CSV file? (yes/no) (default: no): ").strip().lower() == 'yes'
        print_console = input("Do you want to print the yearly output to the console? (yes/no) (default: no): ").strip().lower() == 'yes'

        principal = float(principal)
        annual_return = float(annual_return)
        monthly_expense = float(monthly_expense)
    else:
        principal = args.principal
        annual_return = args.annual_return
        monthly_expense = args.monthly_expense
        output_csv = args.output_csv
        print_console = args.print_console

    calculate_lifeline(
        principal,
        annual_return,
        monthly_expense,
        output_csv,
        print_console
    )

if __name__ == "__main__":
    main()

