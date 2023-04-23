import streamlit as st
from direct_redis import DirectRedis

st.set_page_config(layout='wide')

st.write('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

r = DirectRedis(host='45.77.19.225', port=6379,password='eYVX7EwVmmxKPCDmwMtyKVge8oLd2t81')
df = r.get('mt5_table')

df_group = df.groupby(["account", 'magic'])
data = {}
START_MAGIC=1000
def format_df(df):
    df=df[[ 'time','type','entry', 'reason','volume','price','commission','profit','symbol','comment']]
    df.sort_values('time',inplace=True) 
    return df.style.background_gradient(axis=0,gmap=df['profit'],cmap='YlGn')   

for (acc, magic), v in df_group:
    if acc not in data:
        data[acc] = {}
    if magic<START_MAGIC:
        continue
    data[acc][magic] = v

# st.write(str( list(data.keys())))
tabs = st.tabs([str(x) for x in data.keys()])
selected_acc = st.selectbox('select account', list(data.keys()))


import pandas as pd
sharpe_arr = []
for magic, df in data[selected_acc].items():
    sharpe = df['profit'].mean()/df['profit'].std()
    if  pd.isna(sharpe):
        continue

    sharpe_arr.append((magic, sharpe))
sharpe_arr = sorted(sharpe_arr, key=lambda x: x[1], reverse=True)

for magic, sharpe in sharpe_arr:
    df = data[selected_acc][magic]
    df.reset_index(inplace=True) 
    total_profit = df["profit"].sum()
    total_trade = df['profit'].count()

    color = 'red' if total_profit < 0 else 'green'
    title = f'magic: :blue[{magic}] total profit: :{color}[{total_profit:.0f}] total trade: :{color}[{total_trade}] sharpe: :{color}[{sharpe:.2f}] '
    # st.write(title)
    exp = st.expander(label=title, expanded=False)
    with exp:
        df = format_df(df)
        st.write(df)

    #     st.write(df)
