import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Настройка страницы
st.set_page_config(page_title='Анализ брошенных корзин', layout='wide')

# Функция для загрузки и подготовки данных
@st.cache_data
def load_data():
    # Загрузка данных из Excel
    df = pd.read_excel('combined_report.xlsx')
    
    # Правильное преобразование даты с указанием формата
    df['Дата'] = pd.to_datetime(df['Дата статуса'], format='%d.%m.%Y %H:%M:%S').dt.date
    
    return df

# Функция форматирования чисел
def format_number(num):
    if num >= 1_000_000:
        return f'{num/1_000_000:.1f}M ₸'
    elif num >= 1_000:
        return f'{num/1_000:.1f}K ₸'
    return f'{num:.0f} ₸'

try:
    # Загрузка данных
    df = load_data()

    # Заголовок
    st.title('Анализ брошенных корзин')

    # Основные метрики
    col1, col2, col3 = st.columns(3)

    total_amount = df['Сумма заказа'].sum()
    total_orders = len(df)
    avg_check = total_amount / total_orders

    with col1:
        st.metric('Общая сумма потерь', format_number(total_amount))

    with col2:
        st.metric('Количество корзин', f'{total_orders:,}')

    with col3:
        st.metric('Средний чек', format_number(avg_check))

    # Топ-5 магазинов
    st.header('Топ-5 магазинов')

    # Агрегация данных по магазинам
    store_stats = df.groupby('Магазин').agg({
        'Сумма заказа': 'sum',
        'Магазин': 'count'
    }).rename(columns={
        'Магазин': 'Количество корзин',
        'Сумма заказа': 'Сумма заказов'
    }).reset_index()

    store_stats['Средний чек'] = store_stats['Сумма заказов'] / store_stats['Количество корзин']
    top_5_stores = store_stats.nlargest(5, 'Сумма заказов')

    # График топ-5 магазинов
    fig1 = go.Figure()

    # Добавляем столбцы для суммы заказов
    fig1.add_trace(go.Bar(
        x=top_5_stores['Магазин'],
        y=top_5_stores['Сумма заказов'],
        name='Сумма заказов',
        marker_color='#8884d8'
    ))

    # Добавляем столбцы для количества корзин
    fig1.add_trace(go.Bar(
        x=top_5_stores['Магазин'],
        y=top_5_stores['Количество корзин'],
        name='Количество корзин',
        marker_color='#82ca9d',
        yaxis='y2'
    ))

    # Настройка макета
    fig1.update_layout(
        title='Топ-5 магазинов: сумма заказов и количество корзин',
        yaxis=dict(
            title='Сумма заказов',
            title_font=dict(color='#8884d8'),
            tickfont=dict(color='#8884d8')
        ),
        yaxis2=dict(
            title='Количество корзин',
            title_font=dict(color='#82ca9d'),
            tickfont=dict(color='#82ca9d'),
            overlaying='y',
            side='right'
        ),
        barmode='group',
        height=600
    )

    st.plotly_chart(fig1, use_container_width=True)

    # График среднего чека по магазинам
    fig2 = px.bar(
        top_5_stores,
        x='Магазин',
        y='Средний чек',
        title='Средний чек по магазинам',
        height=400
    )
    fig2.update_traces(marker_color='#ffc658')
    st.plotly_chart(fig2, use_container_width=True)

    # График по дням
    st.header('Динамика по дням')

    # Агрегация данных по дням
    daily_stats = df.groupby('Дата').agg({
        'Сумма заказа': 'sum',
        'Магазин': 'count'
    }).rename(columns={
        'Магазин': 'Количество корзин',
        'Сумма заказа': 'Сумма заказов'
    }).reset_index()

    # График динамики по дням
    fig3 = go.Figure()

    # Добавляем линию для суммы заказов
    fig3.add_trace(go.Scatter(
        x=daily_stats['Дата'],
        y=daily_stats['Сумма заказов'],
        name='Сумма заказов',
        line=dict(color='#8884d8')
    ))

    # Добавляем линию для количества корзин
    fig3.add_trace(go.Scatter(
        x=daily_stats['Дата'],
        y=daily_stats['Количество корзин'],
        name='Количество корзин',
        line=dict(color='#82ca9d'),
        yaxis='y2'
    ))

    # Настройка макета
    fig3.update_layout(
        title='Динамика брошенных корзин по дням',
        yaxis=dict(
            title='Сумма заказов',
            title_font=dict(color='#8884d8'),
            tickfont=dict(color='#8884d8')
        ),
        yaxis2=dict(
            title='Количество корзин',
            title_font=dict(color='#82ca9d'),
            tickfont=dict(color='#82ca9d'),
            overlaying='y',
            side='right'
        ),
        height=500
    )

    st.plotly_chart(fig3, use_container_width=True)

except Exception as e:
    st.error(f'Произошла ошибка: {str(e)}')
    st.write('Детали ошибки:', e)