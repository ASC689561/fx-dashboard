import pandas as pd
import streamlit as st
from direct_redis import DirectRedis
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout='wide')
count = st_autorefresh(interval=10000, limit=1000, key="fizzbuzzcounter")

st.write('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

r = DirectRedis(host='45.77.19.225', port=6379, password='eYVX7EwVmmxKPCDmwMtyKVge8oLd2t81')
df = r.get('mt5_table')
current_positions = r.get('mt5_current_position')
living_stragies = r.get('mt5_living_strategies')


df['time'] = pd.to_datetime(df['time'], unit='s')
df_group = df.groupby(["account", 'magic'])


data = {}
START_MAGIC = 1000
ignore = st.secrets["IGNORE_MAGIC"].split(',')
ignore = [int(x) for x in ignore if len(x) > 0]


def format_df(df):
    df = df[['time', 'volume', 'type', 'price', 'commission', 'profit', 'symbol', 'comment']]
    df['type'] = df['type'].replace({1: 'SELL', 0: 'BUY'})
    df.sort_values('time', inplace=True)
    return df.style.background_gradient(axis=0, gmap=df['profit'], cmap='YlGn')


running_magic_set = set([x[1] for x in living_stragies])

col1, col2 = st.columns([2, 3])
with col1:

    st.header("Current positions")

    position_df = pd.DataFrame(current_positions)
    if len(position_df) > 0:
        position_df['time'] = pd.to_datetime(position_df['time'], unit='s')
        position_df['type'] = position_df['type'].replace({1: 'SELL', 0: 'BUY'})
        position_df = position_df[['symbol', 'magic', 'time', 'type', 'profit', 'comment']]
        st.dataframe(position_df)

with col2:
    st.header("Strategies")

    show_only_running_bool = st.checkbox("Only running", True)
    for (acc, magic), v in df_group:
        if acc not in data:
            data[acc] = {}
        if magic < START_MAGIC or magic in ignore:
            continue
        if show_only_running_bool and magic not in running_magic_set:
            continue
        data[acc][magic] = v

    selected_acc = st.selectbox('select account', list(data.keys()))

    all_magic = list(data[acc].keys())
    selected_magic = st.multiselect('Select magic', all_magic)
    if len(selected_magic) == 0:
        selected_magic = all_magic

    sharpe_arr = []
    for magic, df in data[selected_acc].items():
        sharpe = df['profit'].mean()/df['profit'].std()
        if pd.isna(sharpe):
            continue

        sharpe_arr.append((magic, sharpe))
    sharpe_arr = sorted(sharpe_arr, key=lambda x: x[1], reverse=True)

    for magic, sharpe in sharpe_arr:
        if magic not in selected_magic:
            continue
        df = data[selected_acc][magic]
        df.reset_index(inplace=True)
        total_profit = df["profit"].sum()
        total_trade = df['profit'].count()

        color = 'red' if total_profit < 0 else 'green'
        title = f'magic: :blue[{magic}] total profit: :{color}[{total_profit:.1f}] total trade: :{color}[{total_trade}] sharpe: :{color}[{sharpe:.2f}] '
        exp = st.expander(label=title, expanded=False)
        with exp:
            df = format_df(df)
            st.write(df)
