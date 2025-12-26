import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Metals Dashboard", layout="wide")
st.title("📈 Аналіз цін на дорогоцінні метали")

if not firebase_admin._apps:
    cred = credentials.Certificate("credentials.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://metals-analysis-default-rtdb.europe-west1.firebasedatabase.app/' 
    })

def load_data():
    ref = db.reference('/')
    data = ref.get()
    
    if isinstance(data, list):
        return pd.DataFrame(data)
    elif isinstance(data, dict):
        return pd.DataFrame(data)
    return pd.DataFrame()

df = load_data()

if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])

st.sidebar.header("Фільтри")

all_metals = [col for col in df.columns if col != 'date']
selected_metals = st.sidebar.multiselect("Оберіть метали", all_metals, default=all_metals[:1])

if 'date' in df.columns:
    min_date = df['date'].min().to_pydatetime()
    max_date = df['date'].max().to_pydatetime()
    start_date, end_date = st.sidebar.date_input("Період", [min_date, max_date])
    
    mask = (df['date'] >= pd.Timestamp(start_date)) & (df['date'] <= pd.Timestamp(end_date))
    filtered_df = df.loc[mask]
else:
    filtered_df = df

days_count = st.sidebar.number_input("Кількість попередніх днів для тексту", min_value=1, max_value=10, value=3)

st.subheader("Графік цін")
fig = px.line(filtered_df, x='date', y=selected_metals, labels={'value': 'Ціна', 'date': 'Дата'})
st.plotly_chart(fig, use_container_width=True)

st.subheader(f"Ціни за останні {days_count} записів")
for metal in selected_metals:
    st.write(f"**{metal.upper()}**")
    last_prices = filtered_df[['date', metal]].tail(days_count)
    for _, row in last_prices.iterrows():
        st.write(f"- {row['date'].strftime('%Y-%m-%d')}: {row[metal]}")
