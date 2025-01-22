# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Аналитика продаж", layout="wide")

@st.cache_data
def load_data():
    # Загружаем оба файла
    df_orders = pd.read_excel('orders.xlsx')
    df_products = pd.read_excel('products.xlsx')
    
    # Преобразование дат
    df_orders['Дата статуса'] = pd.to_datetime(df_orders['Дата статуса'])
    df_products['Дата статуса'] = pd.to_datetime(df_products['Дата статуса'])
    return df_orders, df_products

# Загрузка данных
df_orders, df_products = load_data()

# Заголовок дашборда
st.title('📊 Аналитика продаж')

# Основные метрики из первого датасета
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Общий оборот", f"{df_orders['Сумма заказа'].sum():,.0f} ₸")
with col2:
    st.metric("Количество заказов", f"{len(df_orders):,}")
with col3:
    st.metric("Уникальных клиентов", f"{df_orders['Контактный телефон'].nunique():,}")

# Анализ товаров
st.header('Анализ товаров')

# 1. Таблица топ товаров по частоте добавления в корзину
top_products = df_products.groupby('Наименование').size()\
    .sort_values(ascending=False).head(10).reset_index()
top_products.columns = ['Наименование', 'Количество добавлений в корзину']

st.subheader('Топ-10 товаров по частоте добавления в корзину')
st.dataframe(top_products, use_container_width=True)

# 2. Круговая диаграмма по группам товаров
col1, col2 = st.columns(2)

with col1:
    st.subheader('Распределение добавлений в корзину по группам')
    group_counts = df_products.groupby('Группа').size()
    fig_groups = px.pie(values=group_counts.values, 
                       names=group_counts.index,
                       title='Распределение добавлений в корзину по группам товаров')
    st.plotly_chart(fig_groups, use_container_width=True)

# 3. Топ товаров по магазинам
with col2:
    st.subheader('Топ товаров по магазинам')
    selected_shop = st.selectbox('Выберите магазин:', 
                               df_products['Магазин'].unique())
    
    top_products_by_shop = df_products[df_products['Магазин'] == selected_shop]\
        .groupby('Наименование').size()\
        .sort_values(ascending=False).head(5)
    
    fig_top_by_shop = px.bar(x=top_products_by_shop.index, 
                            y=top_products_by_shop.values,
                            title=f'Топ-5 товаров по добавлению в корзину в магазине {selected_shop}')
    fig_top_by_shop.update_layout(
        xaxis_title="Наименование товара",
        yaxis_title="Количество добавлений в корзину"
    )
    st.plotly_chart(fig_top_by_shop, use_container_width=True)

# Фильтры в сайдбаре
st.sidebar.header('Фильтры')
date_range = st.sidebar.date_input('Выберите период:',
                                 [df_products['Дата статуса'].min(),
                                  df_products['Дата статуса'].max()])

selected_groups = st.sidebar.multiselect(
    'Выберите группы товаров:',
    df_products['Группа'].unique(),
    default=df_products['Группа'].unique()
)

# Применение фильтров
filtered_products = df_products[
    (df_products['Дата статуса'].dt.date.between(date_range[0], date_range[1])) &
    (df_products['Группа'].isin(selected_groups))
]

# Опция просмотра детальных данных
if st.checkbox('Показать детальные данные по товарам'):
    st.dataframe(filtered_products)