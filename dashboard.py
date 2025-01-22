# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Аналитика продаж", layout="wide")

# Заголовок дашборда
st.title('📊 Аналитика продаж')

# Загрузка данных
@st.cache_data  # Кэширование для быстрой загрузки
def load_data():
    df = pd.read_excel('Финансовый отчет 22 янв 2025.xlsx')
    df['Дата статуса'] = pd.to_datetime(df['Дата статуса'], format='%d.%m.%Y %H:%M:%S')
    df['Месяц'] = df['Дата статуса'].dt.strftime('%Y-%m')
    return df

df = load_data()

# Создаем две колонки для основных метрик
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Общий оборот", f"{df['Сумма заказа'].sum():,.0f} ₸")
with col2:
    st.metric("Количество заказов", f"{len(df):,}")
with col3:
    st.metric("Уникальных клиентов", f"{df['Контактный телефон'].nunique():,}")

# График продаж по месяцам
st.subheader('Динамика продаж по месяцам')
monthly_stats = df.groupby('Месяц').agg({
    'Заказ': 'count',
    'Сумма заказа': 'sum'
}).reset_index()

fig1 = make_subplots(specs=[[{"secondary_y": True}]])
fig1.add_trace(
    go.Bar(x=monthly_stats['Месяц'], y=monthly_stats['Заказ'], 
           name="Количество заказов"),
    secondary_y=False
)
fig1.add_trace(
    go.Scatter(x=monthly_stats['Месяц'], y=monthly_stats['Сумма заказа'], 
               name="Оборот", line=dict(color='red')),
    secondary_y=True
)
fig1.update_layout(height=400)
st.plotly_chart(fig1, use_container_width=True)

# Создаем два столбца для графиков
col1, col2 = st.columns(2)

with col1:
    st.subheader('Распределение оборота по магазинам')
    shop_sales = df.groupby('Магазин')['Сумма заказа'].sum().sort_values(ascending=False)
    top_5_shops = shop_sales.head(5)
    other_shops = pd.Series({'Другие': shop_sales[5:].sum()})
    pie_data = pd.concat([top_5_shops, other_shops])
    fig2 = px.pie(values=pie_data.values, names=pie_data.index)
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader('Распределение оборота по категориям')
    category_sales = df.groupby('group')['Сумма заказа'].sum()
    fig4 = px.pie(values=category_sales.values, names=category_sales.index)
    st.plotly_chart(fig4, use_container_width=True)

# Средний чек по магазинам и категориям
st.subheader('Средний чек по магазинам и категориям')
avg_check = df.pivot_table(
    values='Сумма заказа',
    index='Магазин',
    columns='group',
    aggfunc='mean',
    fill_value=0
).round(2)
fig3 = px.bar(avg_check)
st.plotly_chart(fig3, use_container_width=True)

# Добавляем фильтры в сайдбар
st.sidebar.header('Фильтры')
selected_shops = st.sidebar.multiselect(
    'Выберите магазины:',
    options=df['Магазин'].unique(),
    default=df['Магазин'].unique()
)

selected_categories = st.sidebar.multiselect(
    'Выберите категории:',
    options=df['group'].unique(),
    default=df['group'].unique()
)

# Опциональная таблица с данными
if st.checkbox('Показать детальные данные'):
    st.subheader('Детальные данные')
    st.dataframe(df)