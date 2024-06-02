import streamlit as st
"""hist = ticker_needed.history(period="1mo")

    # show meta information about the history (requires history() to be called first)
    ticker_needed.history_metadata

    # show actions (dividends, splits, capital gains)
    ticker_needed.actions
    ticker_needed.dividends
    ticker_needed.splits
    ticker_needed.capital_gains  # only for mutual funds & etfs

    # show share count
    ticker_needed.get_shares_full(start="2022-01-01", end=None)

    # show financials:
    # - income statement
    ticker_needed.income_stmt
    ticker_needed.quarterly_income_stmt
    # - balance sheet
    ticker_needed.balance_sheet
    ticker_needed.quarterly_balance_sheet
    # - cash flow statement
    ticker_needed.cashflow
    ticker_needed.quarterly_cashflow
    # see `Ticker.get_income_stmt()` for more options

    # show holders
    ticker_needed.major_holders
    ticker_needed.institutional_holders
    ticker_needed.mutualfund_holders
    ticker_needed.insider_transactions
    ticker_needed.insider_purchases
    ticker_needed.insider_roster_holders

    # show recommendations
    ticker_needed.recommendations
    ticker_needed.recommendations_summary
    ticker_needed.upgrades_downgrades"""