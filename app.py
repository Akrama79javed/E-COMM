import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.cache_data()
def load():
    df = pd.read_csv('dataset/data-2.csv')
    return df

df = load()

st.title('E-COMMERCE DATA ANALYSIS')

if st.sidebar.checkbox("View Dataset"):
    st.dataframe(df)

st.sidebar.write(df.describe())

df_msn = pd.DataFrame(df.isna().sum())
df_msn['Features'] = df_msn.index
df_msn['MissingValues'] = df_msn[0]
fig = px.bar(df_msn, 
            title='Missing Values by Features',
             x = 'Features', 
             y = 'MissingValues', 
             color='Features',
            text='MissingValues',
            text_auto='.2s')
fig.update_yaxes(title='Count of Missing Values')
st.plotly_chart(fig)

customer_msn = (df['CustomerID'].isna().sum() / len(df['CustomerID'])) * 100
description_msn = (df['Description'].isna().sum() / len(df['CustomerID'])) * 100


df.drop(df[df['CustomerID'].isna() | df['Description'].isna()].index, inplace=True)
df.drop(df.query('Country == "Unspecified"').index, inplace=True)
df = df.astype({'InvoiceDate':'datetime64[ns]','CustomerID':'int'})

qty = st.number_input("find item by quantity", min_value=-1000, max_value=1000, value=0)
st.dataframe(df.query(f'Quantity > {qty}'))

df.drop(df.query('Description in ["POSTAGE", "CARRIAGE", "Discount", "DOTCOM POSTAGE", "CRUK Commission", "Manual"]').index, axis=0, inplace=True)

countries = df.Country.unique().tolist()
df['Revenue'] = abs(df['UnitPrice'] * df['Quantity'])
df['Year'] = df['InvoiceDate'].dt.year
df['Month'] = df['InvoiceDate'].dt.month_name()
df['Date'] = df[['Month','Year']].astype(str).apply('-'.join, axis=1)
df['Day'] = df['InvoiceDate'].dt.day_name()
df['Hour'] = df['InvoiceDate'].dt.hour

def formatTime(h):
    return h.Hour+':00'

CURRENCY = '£'
TICKANGLE = 30

Sales = df[~df['InvoiceNo'].str.contains('C')]
st.dataframe(Sales.head(5))

total_revenue = Sales.groupby('Date', as_index=False)['Revenue'].sum().round(2)
order_list = ["05","09","01","13","03","02","08","07","04","06","12","11","10"]
total_revenue['Order'] = order_list
total_revenue.sort_values(by='Order', inplace=True)
total_revenue.reset_index(drop=True, inplace=True)
total_revenue.drop('Order', axis=1, inplace=True)

fig = go.Figure()
fig.add_traces(go.Scatter(x=total_revenue.Date,y=total_revenue.Revenue,line=dict(color='crimson')))
fig.update_traces(name='Revenue')
fig.update_layout(title='Total Sales Revenue')
fig.update_xaxes(tickangle=TICKANGLE)
fig.update_yaxes(tickprefix=CURRENCY, title='Revenue')
st.plotly_chart(fig)


country_revenue = Sales.groupby('Country', as_index=False)['Revenue'].sum().round(2)
country_revenue.sort_values(by=['Revenue'], ascending=False, inplace=True)

fig = px.bar(country_revenue[:10].reset_index(),
             title='Top 10 Countries by Revenue',
             x='Country',
             y='Revenue',
             text='Revenue',
             text_auto='.3s',
             color='Country')
fig.update_yaxes(title='Revenue', tickprefix=CURRENCY)
st.plotly_chart(fig)

products_revenue = Sales.groupby(['StockCode','Description'], as_index=False)['Revenue'] \
.sum().round(2) \
.sort_values('Revenue', ascending=False) \
.head(20) \
.reset_index(drop=True)

fig = px.bar(products_revenue,
            title='Top 20 Products by Revenue',
            x='StockCode',
            y='Revenue',
            color='StockCode',
            text='Revenue',
            text_auto='.4s')
fig.update_yaxes(tickprefix=CURRENCY)
st.plotly_chart(fig)

product_sales = Sales.groupby('StockCode', as_index=False)['Quantity'].sum()
product_sales.rename(columns={'Quantity':'Sales'}, inplace=True)

product_sales_perf = products_revenue.merge(product_sales, on='StockCode')

fig = px.bar(product_sales_perf.reset_index(),
            title='Sales Quantity for Top 20 Products',
            x='StockCode',
            y='Sales',
            text='StockCode',
            color='StockCode',
            text_auto='.2s')
fig.update_yaxes(title='Quantity')
st.plotly_chart(fig)

unitPrice_grouped = Sales.groupby(['StockCode'], as_index=False)['UnitPrice'].mean()
unit_price = product_sales_perf.merge(unitPrice_grouped, on='StockCode')

fig = px.bar(unit_price,
            title='Average Unit Price of Top 20 Products Sold',
            x='StockCode',
            y='UnitPrice',
            color='StockCode',
            text='UnitPrice',
            text_auto='.2f')
fig.update_yaxes(tickprefix = '£', title='Unit Price') 
st.plotly_chart(fig)

top_customers = Sales.groupby('CustomerID', as_index=False)['Revenue'].sum() \
.sort_values(by='Revenue', ascending=False) \
.reset_index(drop=True)
top_customers['CustomerID'] = top_customers['CustomerID'].astype(str)

fig = px.bar(top_customers[:10],
            title='Top 10 Customers by Revenue',
            x='CustomerID',
            y='Revenue',
            color='CustomerID',
            text='Revenue',
            text_auto='.4s')
fig.update_yaxes(tickprefix=CURRENCY)
st.plotly_chart(fig)

daily = Sales.groupby('Day', as_index=False)['Revenue'].sum()
# daily.rename(columns={'Quantity':'Sales'}, inplace=True)
daily['Order'] = ['5','1','6','4','2','3']
daily.sort_values(by=['Order'], inplace=True)

fig = px.bar(daily.reset_index(),
            title='Sales Performance by Day',
            x='Day',
            y='Revenue',
            text='Day',
            color='Day',
            text_auto='.2s')
fig.update_yaxes(tickprefix = '£', title='Revenue')
st.plotly_chart(fig)

product_sales = Sales.groupby('Hour', as_index=False)['Revenue'].sum()
# product_sales.rename(columns={'Quantity':'Sales'}, inplace=True)
product_sales['Hour'] = product_sales['Hour'].astype(str)
product_sales['Hour'] = product_sales.apply(lambda h:formatTime(h), axis=1)

fig = px.line(product_sales,
            title='Sales Performance by Hour',
            x='Hour',
            y='Revenue')
fig.update_yaxes(tickprefix = '£', title='Unit Price')
st.plotly_chart(fig)

products_canceled = df.query('(InvoiceNo.str.contains("C"))') \
.groupby(['Date'], as_index=False) \
.Revenue.agg(['count','sum']) \
.reset_index()

products_canceled.rename(columns={'count':'CanceledOrders','sum':'RevenueLost'}, inplace=True)
order_list = ["05","09","01","13","03","02","08","07","04","06","12","11","10"]
products_canceled['Order'] = order_list
products_canceled.sort_values(by='Order', ascending=True, inplace=True)
products_canceled.reset_index(drop=True, inplace=True)
products_canceled.drop('Order', axis=1,inplace=True)

fig = go.Figure()
fig.add_traces(go.Scatter(name='RevenueLost',x=products_canceled.Date,y=products_canceled.RevenueLost,line=dict(color='crimson')))
fig.update_layout(title='Total Sales Revenue Lost (Canceled Orders)')
fig.update_yaxes(tickprefix=CURRENCY, title='Revenue')
st.plotly_chart(fig)

st.markdown('''
<div class="alert alert-block alert-secondary" style='font-size:18px'>
    <ul>
    <li>In September £944.4k, there was a significant increase in revenue compared to the previous month of August (£639.3k), representing a growth of approximately 47.8%. This upward trend continued steadily until November 2011, which recorded the highest sales revenue of £1,145.2k from Dec. 2010 to Dec. 2011. However, December 2011 experienced a 20.4% drop in revenue to £513.7k. Further investigation needs to be conducted to determine the causes behind the surge in revenue and the sharp decline.</li>
    <li>The UK generated the highest revenue of £7.29M from sales between Dec. 2010 and Dec. 2011, which is over 2000% higher than the next best performer at £283.9k. This indicates the need for additional marketing efforts in other countries.</li>
    <li>Between Dec. 2010 and Dec. 2011, the top-grossing product was "PAPER CRAFT, LITTLE BIRDIE," yielding a revenue of £168.5k.</li>
    <li>The products "REGENCY CAKESTAND 3 TIER" and "PICNIC BASKET WICKER 60 PIECES" had relatively high unit prices per product, at £12.48 and £11.20 respectively. These prices should be reviewed.</li>
    <li>The customer with ID 14646 made the most purchases between 2010 and 2011, amounting to £279.1k.</li>
    <li>Customers tend to make more purchases on Thursdays, with the peak hours occurring between 10:00 AM and 12:00 PM. The sales and marketing teams should target their efforts accordingly.</li>
    </ul></div>
            ''', unsafe_allow_html=True)
