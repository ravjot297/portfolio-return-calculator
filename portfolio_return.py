import datetime as dt
import yfinance as yf
import pandas as pd
from pyxirr import xirr

import streamlit as st


def del_all_states():
    for key in st.session_state.keys():
        del st.session_state[key]

def get_price(ticker,date):

    start = date
    end = dt.datetime.strptime(date, '%Y-%m-%d') + dt.timedelta(1)

    try:
        stock_data = yf.download(tickers= ticker, start= start, end = end,rounding = 2)
        if stock_data.empty:
            st.write(f"Can't fetch price. Either ticker {ticker} is wrong or Market was closed on {date}. Check the ticker and date again.")
            return
        else:
            # price = stock_data['Close'].iloc[0] #for yfinance version 0.2.48
            price = stock_data[('Close', ticker)].iloc[0]  # for yfinance updated version 0.2.49
            return price
    except Exception as e:
        st.write(f"Error: Either ticker {ticker} is wrong or Market was closed on {date}. Check the ticker and date again.")
        return

def get_price_column(row):
    price = get_price(row['Symbol'], row['Date'])
    return price

def get_latest_price(ticker):
    price = yf.download(tickers=ticker, period="1d", rounding=2)[('Close', ticker)].iloc[0]
    return price

def get_latest_date(ticker):
    date = yf.download(tickers= ticker, period = "1d", rounding=2).reset_index()['Date'].iloc[0]
    return date

# Function to calculate latest price to be added on latest df column
def calculate_latest_price(row):
    price = get_latest_price(row['Symbol'])
    return price

# Function to calculate latest date to be added on latest df column
def calculate_latest_date(row):
    date = get_latest_date(row['Symbol'])
    return date


st.write("## Portfolio Return Calculator")
st.write("### Add/ Remove Stocks")

on = st.toggle("**How To Use The Tool**")
if on:
    st.markdown('''
    ---
    1. _Click the plus icon ➕ in the toolbar, to add new stocks. Alternatively, click inside a shaded cell below the bottom row of the table._
    2. _To delete stocks, select one or more rows using the checkboxes on the left. Click the delete icon 🗑️ or press the delete key on your keyboard._
    3. **Symbol Format** - Symbol is the yahoo finance ticker of a security.
        - For NSE stocks, add **'NS'** at end of stock symbol.
        - For BSE stocks, add **'BO'**  at end of stock symbol.
        - **Example - *For Reliance Share, symbol is RELIANCE.NS for NSE, and RELIANCE.BO for BSE.***
    4. **Note**: _XIRR works well for investments held for long time frame, i.e., more than a year. For investments bought and sold in less than one year, XIRR might display unusual numbers._

    ---
    ''')

df = pd.DataFrame(columns=['Symbol','Date', 'Qty', 'Buy_Sell'])
config = {'Date':st.column_config.DateColumn(format="DD.MM.YYYY", required=True),
          'Qty':st.column_config.NumberColumn(min_value=1, required=True),
          'Buy_Sell': st.column_config.SelectboxColumn(label="Action", options=["Buy", "Sell"], required=True),
          'Symbol': st.column_config.TextColumn(required=True)
          }

col1, col2 = st.columns(2)
with col1:
    edited_df = st.data_editor(df, column_config= config, num_rows="dynamic", key="user_portfolio",
                               use_container_width=True)  # 👈 An editable dataframe


col1, col2 = st.columns(2)
with col1:
    portfolio_key_metric = st.button('Calculate Portfolio Return', type="primary")
with col2:
    st.button('Reset Your Portfolio', type="primary", on_click=del_all_states)



if portfolio_key_metric:
    user_portfolio = st.session_state["user_portfolio"]['added_rows']
    print(f"User Portfolio XXX: {user_portfolio}")
    user_portfolio_df = pd.DataFrame(user_portfolio)
    print(f"User Portfolio DF: {user_portfolio_df}")
    try:
        if user_portfolio_df.empty:
            st.write("Your Portfolio is Empty.")
            st.write("Please Add Stocks in Portfolio")
        else:
            user_portfolio_df['Price'] = user_portfolio_df.apply(get_price_column, axis=1)
            if user_portfolio_df['Price'].isna().any():
                pass
            else:
                user_portfolio_df['Action'] = user_portfolio_df['Buy_Sell'].apply(lambda x: 1.0 if x == 'Buy' else -1.0)


                user_portfolio_df['Price'] = user_portfolio_df['Price'].astype(float)
                user_portfolio_df['Qty'] = user_portfolio_df['Qty'].astype(float)
                user_portfolio_df['Action'] = user_portfolio_df['Action'].astype(float)

                user_portfolio_df['Net_Qty'] = user_portfolio_df['Qty'] * user_portfolio_df['Action']
                user_portfolio_df['Cashflow'] = user_portfolio_df['Price'] * user_portfolio_df['Net_Qty'] * -1

                print(f"Investments DF:{user_portfolio_df}")


                latest_date_df = user_portfolio_df.groupby('Symbol')[['Action', 'Net_Qty']].sum()
                print(f"LATEST DF after group by:{latest_date_df}")
                latest_date_df = latest_date_df.reset_index()
                # latest_date_df = latest_date_df[latest_date_df['Net_Qty'] > 0]
                latest_date_df = latest_date_df[latest_date_df['Net_Qty'] != 0] #check for short stocks in portfolio
                print(f"LATEST DF after group by and filter:{latest_date_df}")

                if latest_date_df.empty:

                    dates = user_portfolio_df['Date'].to_list()
                    amounts = user_portfolio_df['Cashflow'].to_list()
                    print(f"Dates: {dates}")
                    print(f"Amounts: {amounts}")
                    total_value = 0.0
                    portfolio_return = round(xirr(dates, amounts) * 100, 2)
                    col1, col2 = st.columns(2)
                    with col2:
                        st.metric(label="XIRR return (%)", value=f"{portfolio_return} %")
                    with col1:
                        st.metric(label="Investment Value ", value=f"{total_value}")

                    st.dataframe(user_portfolio_df,
                                 column_config={'Buy_Sell': st.column_config.TextColumn(label="Action")},
                                 column_order=("Date", "Symbol", "Price", "Qty", "Buy_Sell", "Cashflow"),
                                 use_container_width=True,
                                 hide_index=True,
                                 )
                    st.write("#### No Stocks In Your Portfolio")

                else:
                    latest_date_df['Latest_Price'] = latest_date_df.apply(calculate_latest_price, axis=1)
                    latest_date_df['Cash_Inflow'] = latest_date_df['Latest_Price'] * latest_date_df['Net_Qty']
                    latest_date_df['Today_Date'] = latest_date_df.apply(calculate_latest_date, axis=1)

                    total_value = round(latest_date_df['Cash_Inflow'].sum(),2)
                    print(f"Today's Value:{total_value}")

                    print(f"Portfolio DF:{latest_date_df}")


                    dates = user_portfolio_df['Date'].to_list() + latest_date_df['Today_Date'].to_list()
                    amounts = user_portfolio_df['Cashflow'].to_list() + latest_date_df['Cash_Inflow'].to_list()

                    print(f"Dates: {dates}")
                    print(f"Amounts: {amounts}")

                    portfolio_return = round(xirr(dates, amounts) * 100, 2)
                    col1, col2 = st.columns(2)
                    with col2:
                        st.metric(label="XIRR return (%)", value=f"{portfolio_return} %")
                    with col1:
                        st.metric(label="Investment Value ", value=f"{total_value}")

                    st.write("### P&L Account")
                    st.dataframe(user_portfolio_df,
                                 column_config={'Buy_Sell': st.column_config.TextColumn(label="Action")},
                                 column_order=("Date", "Symbol", "Price", "Qty", "Buy_Sell", "Cashflow"),
                                 use_container_width=True,
                                 hide_index=True,
                                 )
                    st.write("### Current Portfolio")
                    st.dataframe(latest_date_df,
                                 column_config={'Net_Qty': st.column_config.TextColumn(label="Qty"),
                                                'Latest_Price': st.column_config.TextColumn(label="Latest Price"),
                                                'Cash_Inflow': st.column_config.TextColumn(label="Market Value")},
                                 column_order=("Symbol", "Latest_Price", "Net_Qty", "Cash_Inflow"),
                                 use_container_width=True,
                                 hide_index=True,
                                 )


    except Exception as e:
        st.write("Error")
        st.write(e)

