import streamlit as st
import pandas as pd
import yfinance as yf
import datetime as dt
import functions as fn
import pandas_datareader.data as web
import plotly.express as px

st.markdown('### Calculate Beta Value and Return of an individual stock')

col1, col2 = st.columns([1, 1])
with col1:
    selected_stock = st.selectbox(
    "Choose a stock",
    ["TSLA", "AAPL", "NFLX", "MSFT", "MGM", "AMZN", "NVDA", "GOOGL"],
    index=2,  # Set the default index or remove this line to have no default value
)
st.write("Selected stock:", selected_stock)
with col2:
    selected_num_of_years = st.number_input("Number of years", 1, 10)



def get_beta_and_return(selected_stock, selected_num_of_years):

    currentDate = dt.date.today()
    end = dt.date.today()
    start = dt.date(
        currentDate.year - selected_num_of_years, currentDate.month, currentDate.day
    )

    # Download data for S&P 500
    sp500 = web.DataReader(["sp500"], "fred", start, end)

    # Download data for the selected stock
    stock_data = yf.download(selected_stock, period=f"{selected_num_of_years}y")

    stocks_df = pd.DataFrame()
    stocks_df[selected_stock] = stock_data["Close"]

    stocks_df.reset_index(inplace=True)
    sp500.reset_index(inplace=True)
    sp500.columns = ["Date", "sp500"]
    stocks_df["Date"] = stocks_df["Date"].astype("datetime64[ns]")
    stocks_df["Date"] = stocks_df["Date"].apply(lambda x: str(x)[:10])
    stocks_df["Date"] = pd.to_datetime(stocks_df["Date"])
    stocks_df = pd.merge(stocks_df, sp500, on="Date", how="inner")

    # Calculate daily returns
    stocks_daily_return = fn.daily_return(stocks_df)

    # Calculate beta and alpha
    beta, alpha = fn.calculate_beta(stocks_daily_return, selected_stock)

    # Calculate expected return using CAPM
    rf = 0
    rm = stocks_daily_return["sp500"].mean() * 252
    expected_return = round(rf + (beta * (rm - rf)), 2)

    return beta, expected_return

   

beta_value, return_value = get_beta_and_return(selected_stock, selected_num_of_years)

# print(f"Beta value for {selected_stock}: {beta_value}")
# print(f"Expected return for {selected_stock}: {return_value}")

st.markdown(f'### Beta value for {selected_stock} : {beta_value}')
st.markdown(f"### Expected return for {selected_stock} : {return_value}")



# def plot_scatter(selected_stock, beta_value, return_value):
#     # Create a DataFrame with selected stock, beta, and return
#     data = pd.DataFrame({
#         'Stock': [selected_stock],
#         'Beta Value': [beta_value],
#         'Expected Return': [return_value]
#     })

#     # Create a scatter plot using Plotly Express
#     fig = px.scatter(data, x='Beta Value', y='Expected Return', text='Stock',
#                      title=f'Scatter Plot: {selected_stock} vs S&P 500',
#                      labels={'Beta Value': 'Beta Value', 'Expected Return': 'Expected Return'})

#     # Customize the layout
#     fig.update_traces(textposition='top center')
#     fig.update_layout(title_text=f'Scatter Plot: {selected_stock} vs S&P 500',
#                       xaxis_title='Beta Value', yaxis_title='Expected Return')

#     # Plot the scatter plot using Plotly
#     st.plotly_chart(fig, use_container_width=True)



# def plot_scatter(selected_stock, beta_value):
#     data = pd.DataFrame({
#         'Stock': [selected_stock],
#         'Beta Value': [beta_value],
#     })

#     fig = px.scatter(data, x="Stock", y="Beta Value", title=f"Scatter Plot: {selected_stock} vs S&P 500",
#                         labels={selected_stock: f"{selected_stock} Price", "sp500": "S&P 500 Price"},
#                         trendline="ols",  # Ordinary Least Squares regression line
#                         )
#     st.plotly_chart(fig)


















# def main():

#         st.plotly_chart(plot_scatter(selected_stock, beta_value))

# if __name__ == '__main__':
#     main()
