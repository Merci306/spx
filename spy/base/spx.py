import yfinance as yf
data = yf.download("^SPX", start="2000-01-01", end="2026-04-06")
data.to_csv("spx_data.csv")