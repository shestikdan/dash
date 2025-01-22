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
    df_orders['Месяц'] = df_orders['Дата статуса'].dt.strftime('%Y-%m')
    df_products['Дата статуса'] = pd.to_datetime(df_products['Дата статуса'])
    return df_orders, df_products

# Загрузка данных
df_orders, df_products = load_data()

# Заголовок дашборда
st.title('📊 Аналитика продаж')

# Основные метрики
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Общий оборот", f"{df_orders['Сумма заказа'].sum():,.0f} ₸")
with col2:
    st.metric("Количество заказов", f"{len(df_orders):,}")
with col3:
    st.metric("Уникальных клиентов", f"{df_orders['Контактный телефон'].nunique():,}")

# СЕКЦИЯ 1: АНАЛИЗ ПРОДАЖ
st.header('1. Анализ продаж')

# 1.1 График продаж по месяцам
monthly_stats = df_orders.groupby('Месяц').agg({
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
fig1.update_layout(title='Динамика продаж по месяцам')
st.plotly_chart(fig1, use_container_width=True)

# 1.2 Распределение оборота по магазинам (top-5)
col1, col2 = st.columns(2)
with col1:
    shop_sales = df_orders.groupby('Магазин')['Сумма заказа'].sum().sort_values(ascending=False)
    top_5_shops = shop_sales.head(5)
    other_shops = pd.Series({'Другие': shop_sales[5:].sum()})
    pie_data = pd.concat([top_5_shops, other_shops])
    
    fig2 = px.pie(values=pie_data.values, names=pie_data.index,
                  title='Распределение оборота по магазинам')
    st.plotly_chart(fig2, use_container_width=True)

# 1.3 Средний чек по категориям
with col2:
    avg_check = df_orders.groupby('category')['Сумма заказа'].mean().round(0)
    fig3 = px.bar(x=avg_check.index, y=avg_check.values,
                  title='Средний чек по категориям')
    st.plotly_chart(fig3, use_container_width=True)

# СЕКЦИЯ 2: АНАЛИЗ ТОВАРОВ
st.header('2. Анализ товаров')

# 2.1 Топ товаров по частоте добавления в корзину
top_products = df_products.groupby('Наименование').size()\
    .sort_values(ascending=False).head(10).reset_index()
top_products.columns = ['Наименование', 'Количество добавлений в корзину']

st.subheader('Топ-10 товаров по частоте добавления в корзину')
st.dataframe(top_products, use_container_width=True)

# 2.2 Анализ по группам товаров и магазинам
col1, col2 = st.columns(2)

with col1:
   st.subheader('Распределение добавлений в корзину по группам')
   group_counts = df_products.groupby('Группа').size().sort_values(ascending=False)
   
   # Берем топ 8 групп
   top_8_groups = group_counts.head(8)
   # Суммируем остальные в 'Другие'
   others = pd.Series({'Другие': group_counts[8:].sum()})
   
   # Объединяем топ 8 и 'Другие'
   pie_data = pd.concat([top_8_groups, others])
   
   fig4 = px.pie(values=pie_data.values, 
                 names=pie_data.index,
                 title='Распределение добавлений в корзину по группам товаров')
   fig4.update_traces(textposition='inside', textinfo='percent+label')
   st.plotly_chart(fig4, use_container_width=True)

with col2:
    st.subheader('Топ товаров по магазинам')
    selected_shop = st.selectbox('Выберите магазин:', 
                               df_products['Магазин'].unique())
    
    top_products_by_shop = df_products[df_products['Магазин'] == selected_shop]\
        .groupby('Наименование').size()\
        .sort_values(ascending=False).head(5)
    
    fig5 = px.bar(x=top_products_by_shop.index, 
                  y=top_products_by_shop.values,
                  title=f'Топ-5 товаров по добавлению в корзину в магазине {selected_shop}')
    fig5.update_layout(
        xaxis_title="Наименование товара",
        yaxis_title="Количество добавлений в корзину"
    )
    st.plotly_chart(fig5, use_container_width=True)

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

# Детальные данные
if st.checkbox('Показать детальные данные'):
    tab1, tab2 = st.tabs(["Данные по заказам", "Данные по товарам"])
    with tab1:
        st.dataframe(df_orders)
    with tab2:
        st.dataframe(df_products)