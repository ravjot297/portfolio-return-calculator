# portfolio-return-calculator
## Portfolio Return Calculator 

### How to Use the Portfolio Return Calculator

This tool helps you calculate the return on a portfolio of stocks listed on the National Stock Exchange (NSE) and Bombay Stock Exchange (BSE) using real-time data from Yahoo Finance.

#### Getting Started

1. **Adding Stocks**: Click the ➕ icon in the toolbar or click inside a shaded cell below the table to add a new stock entry.
2. **Deleting Stocks**: Use the checkboxes on the left to select rows, then click the 🗑️ icon or press the delete key to remove selected stocks.

#### Ticker Symbol Format

- Enter each stock’s Yahoo Finance ticker symbol:
    - For NSE stocks, append **'.NS'** to the symbol (e.g., `RELIANCE.NS` for Reliance on NSE).
    - For BSE stocks, append **'.BO'** to the symbol (e.g., `RELIANCE.BO` for Reliance on BSE).

#### Important Note

- **XIRR Calculation**: XIRR is designed for investments held over a year or more. For shorter-term investments (under one year), the XIRR calculation may produce unusual results.

### Required Inputs

1. **Stock Symbol**: Enter the ticker symbol from Yahoo Finance.
2. **Investment Date**: Provide the date of the investment.
3. **Quantity**: Enter the number of shares.
4. **Action**: Select whether the action is **buy** or **sell**.

### Outputs

1. **Current Investment Value**: Calculates the portfolio value based on today’s prices.
2. **Portfolio Return (%)**: Shows your return as a percentage.
3. **Investment Records Table**: Displays all past transactions, including purchase and selling prices.
4. **Current Portfolio**: Summarizes your current holdings.