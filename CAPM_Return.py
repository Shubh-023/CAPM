# importing libraries

import streamlit as st
import pandas as pd
import yfinance as yf
import datetime as dt
import functions as fn
import pandas_datareader.data as web

st.set_page_config(
    page_title="CAPM", page_icon="chart_with_upward_trends", layout="wide"
)

st.title("Capital Asset Pricing Model")

# getting input from user

col1, col2 = st.columns([1, 1])
with col1:
    stockList = st.multiselect(
        "Choose 4 stocks",
        ["TSLA", "AAPL", "NFLX", "MSFT", "MGM", "AMZN", "NVDA", "GOOGL"],
        ["TSLA", "AAPL", "AMZN", "GOOGL"],
    )
with col2:
    selectedNumOfYear = st.number_input("Number of years", 1, 10)

# download data for S&P 500
try:
    currentDate = dt.date.today()
    end = dt.date.today()
    start = dt.date(
        currentDate.year - selectedNumOfYear, currentDate.month, currentDate.day
    )

    sp500 = web.DataReader(["sp500"], "fred", start, end)

    stocks_df = pd.DataFrame()

    for stock in stockList:
        data = yf.download(stock, period=f"{selectedNumOfYear}y")
        stocks_df[f"{stock}"] = data["Close"]

    stocks_df.reset_index(inplace=True)
    sp500.reset_index(inplace=True)
    sp500.columns = ["Date", "sp500"]
    stocks_df["Date"] = stocks_df["Date"].astype("datetime64[ns]")
    stocks_df["Date"] = stocks_df["Date"].apply(lambda x: str(x)[:10])
    stocks_df["Date"] = pd.to_datetime(stocks_df["Date"])
    stocks_df = pd.merge(stocks_df, sp500, on="Date", how="inner")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Dataframe head")
        st.dataframe(stocks_df.head(), use_container_width=True)
    with col2:
        st.markdown("### Dataframe tail")
        st.dataframe(stocks_df.tail(), use_container_width=True)


    st.markdown("### Price of all Stocks")
    st.plotly_chart(fn.interactive_plot(stocks_df))

    st.markdown("### Price of all Stocks (After Normalizing)")
    st.plotly_chart(fn.interactive_plot(fn.normalize(stocks_df)))

    stocks_daily_return = fn.daily_return(stocks_df)

    beta = {}
    alpha = {}

    for i in stocks_daily_return.columns:
        if i != "Date" and i != "sp500":
            b, a = fn.calculate_beta(stocks_daily_return, i)

            beta[i] = b
            alpha[i] = a
    print(beta, alpha)

    beta_df = pd.DataFrame(columns=["Stock", "Beta Value"])
    beta_df["Stock"] = beta.keys()
    beta_df["Beta Value"] = [str(round(i, 2)) for i in beta.values()]

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Calculated Beta Value")
        st.dataframe(beta_df, use_container_width=True)

    rf = 0
    rm = stocks_daily_return["sp500"].mean() * 252

    return_df = pd.DataFrame()
    return_value = []
    for stocks, value in beta.items():
        return_value.append(str(round(rf + (value * (rm - rf)), 2)))
    return_df["Stock"] = stockList

    return_df["Return Value"] = return_value

    with col2:
        st.markdown("### Calculated return using CAPM")
        st.dataframe(return_df, use_container_width=True)

except:
    st.write('Please select the valid input')
