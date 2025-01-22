import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Настройка страницы
st.set_page_config(page_title="Аналитика продаж", layout="wide")

# Загрузка данных
@st.cache_data
def load_data():
    # Загружаем все файлы
    df_orders = pd.read_excel('orders.xlsx')
    df_products = pd.read_excel('products.xlsx')
    
    # Преобразование дат
    df_orders['Дата статуса'] = pd.to_datetime(df_orders['Дата статуса'])
    df_orders['Месяц'] = df_orders['Дата статуса'].dt.strftime('%Y-%m')
    df_products['Дата статуса'] = pd.to_datetime(df_products['Дата статуса'])
    
    return df_orders, df_products

# Загрузка данных
df_orders, df_products = load_data()

# Заголовок дашборда
st.title('📊 Аналитика продаж')

# Фильтры в сайдбаре
st.sidebar.header('Фильтры')

# Фильтр по датам
date_range = st.sidebar.date_input(
    'Выберите период:',
    [df_products['Дата статуса'].min(), df_products['Дата статуса'].max()]
)

# Фильтры по магазинам и категориям
selected_shops = st.sidebar.multiselect(
    'Выберите магазины:',
    options=df_orders['Магазин'].unique(),
    default=df_orders['Магазин'].unique()
)

selected_groups = st.sidebar.multiselect(
    'Выберите группы товаров:',
    options=df_products['Группа'].unique(),
    default=df_products['Группа'].unique()
)

# Применение фильтров
filtered_orders = df_orders[
    (df_orders['Дата статуса'].dt.date.between(date_range[0], date_range[1])) &
    (df_orders['Магазин'].isin(selected_shops))
]

filtered_products = df_products[
    (df_products['Дата статуса'].dt.date.between(date_range[0], date_range[1])) &
    (df_products['Группа'].isin(selected_groups))
]

# Основные метрики
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Общий оборот", f"{filtered_orders['Сумма заказа'].sum():,.0f} ₸")
with col2:
    st.metric("Количество заказов", f"{len(filtered_orders):,}")
with col3:
    st.metric("Уникальных клиентов", f"{filtered_orders['Контактный телефон'].nunique():,}")

# График продаж по месяцам
st.header('Динамика продаж')
monthly_stats = filtered_orders.groupby('Месяц').agg({
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

# Анализ магазинов
st.header('Анализ по магазинам')
col1, col2 = st.columns(2)

with col1:
    st.subheader('Распределение оборота по магазинам')
    shop_sales = filtered_orders.groupby('Магазин')['Сумма заказа'].sum().sort_values(ascending=False)
    top_5_shops = shop_sales.head(5)
    other_shops = pd.Series({'Другие': shop_sales[5:].sum()})
    pie_data = pd.concat([top_5_shops, other_shops])
    fig2 = px.pie(values=pie_data.values, names=pie_data.index)
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader('Средний чек по магазинам')
    avg_check = filtered_orders.groupby('Магазин')['Сумма заказа'].mean().sort_values(ascending=False)
    fig_avg = px.bar(x=avg_check.index, y=avg_check.values)
    fig_avg.update_layout(
        xaxis_title="Магазин",
        yaxis_title="Средний чек"
    )
    st.plotly_chart(fig_avg, use_container_width=True)

# Анализ товаров
st.header('Анализ товаров')

# Таблица топ товаров по частоте добавления в корзину
top_products = filtered_products.groupby('Наименование').size()\
    .sort_values(ascending=False).head(10).reset_index()
top_products.columns = ['Наименование', 'Количество добавлений в корзину']
st.subheader('Топ-10 товаров по частоте добавления в корзину')
st.dataframe(top_products, use_container_width=True)

# Визуализации по группам товаров
col1, col2 = st.columns(2)

with col1:
    st.subheader('Распределение добавлений в корзину по группам')
    group_counts = filtered_products.groupby('Группа').size().sort_values(ascending=False)
    
    # Выделяем топ 6 групп
    top_6_groups = group_counts.head(10)
    # Суммируем остальные группы
    other_groups = pd.Series({'Другие': group_counts[10:].sum()})
    # Объединяем топ 6 и "Другие"
    final_group_counts = pd.concat([top_6_groups, other_groups])
    
    fig_groups = px.pie(
        values=final_group_counts.values, 
        names=final_group_counts.index,
        title='Распределение добавлений в корзину по группам товаров'
    )
    st.plotly_chart(fig_groups, use_container_width=True)

with col2:
    st.subheader('Топ товаров по магазинам')
    selected_shop = st.selectbox(
        'Выберите магазин:', 
        filtered_products['Магазин'].unique()
    )
    
    top_products_by_shop = filtered_products[filtered_products['Магазин'] == selected_shop]\
        .groupby('Наименование').size()\
        .sort_values(ascending=False).head(5)
    
    fig_top_by_shop = px.bar(
        x=top_products_by_shop.index, 
        y=top_products_by_shop.values,
        title=f'Топ-5 товаров по добавлению в корзину в магазине {selected_shop}'
    )
    fig_top_by_shop.update_layout(
        xaxis_title="Наименование товара",
        yaxis_title="Количество добавлений в корзину"
    )
    st.plotly_chart(fig_top_by_shop, use_container_width=True)

# Детальные данные
tab1, tab2 = st.tabs(["Данные по заказам", "Данные по товарам"])

with tab1:
    if st.checkbox('Показать детальные данные по заказам'):
        st.dataframe(filtered_orders)

with tab2:
    if st.checkbox('Показать детальные данные по товарам'):
        st.dataframe(filtered_products)