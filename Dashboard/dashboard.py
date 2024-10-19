# -*- coding: utf-8 -*-
"""Dashboard.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1nvGr283HinU2o3JzBJqIfUCxaCNrPlrm
"""

# Import library yang dibutuhkan
import streamlit as st  # Untuk membuat aplikasi web interaktif
import pandas as pd  # Untuk manipulasi dan analisis data
import seaborn as sns  # Untuk visualisasi data
import matplotlib.pyplot as plt  # Untuk membuat plot
from babel.numbers import format_currency  # Untuk format mata uang
import gzip  # Untuk membuka file .gz
import io  # Untuk operasi I/O dengan file
import requests  # Untuk mengunduh file dari URL

# Mengatur gaya tampilan grafik dengan tema 'darkgrid'
sns.set(style='darkgrid')

# Fungsi Helper

# Fungsi untuk membuat DataFrame dengan penjualan bulanan
def create_monthly_sales_df(df):
    monthly_sales = df.groupby(['order_purchase_year', 'order_purchase_month'])['price'].sum().reset_index()
    monthly_sales['month_year'] = monthly_sales['order_purchase_year'].astype(str) + '-' + monthly_sales['order_purchase_month'].astype(str)
    return monthly_sales

# Fungsi untuk membuat DataFrame dengan penjualan produk berdasarkan kategori
def create_product_sales_df(df):
    product_sales = df['product_category_name_english'].value_counts().reset_index()
    product_sales.columns = ['product_category_name_english', 'order_item_id']
    return product_sales

# Fungsi untuk membuat DataFrame RFM (Recency, Frequency, Monetary)
def create_rfm_df(df):
    df['days_since_last_purchase'] = (df['order_purchase_timestamp'].max() - df['order_purchase_timestamp']).dt.days
    recency = df.groupby('customer_id')['days_since_last_purchase'].min().reset_index()
    frequency = df.groupby('customer_id')['order_id'].nunique().reset_index()
    monetary = df.groupby('customer_id')['order_value'].sum().reset_index()
    rfm = recency.merge(frequency, on='customer_id').merge(monetary, on='customer_id')
    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    return rfm

# Fungsi untuk membuat DataFrame penjual dengan total penjualan tertinggi
def create_top_sellers_df(df):
    top_sellers = df.groupby('seller_id')['order_value'].sum().sort_values(ascending=False).reset_index().head(10)
    return top_sellers

# Fungsi untuk menghitung Customer Lifetime Value (CLV)
def calculate_clv(df):
    first_purchase = df.groupby('customer_id')['order_purchase_timestamp'].min().reset_index()
    first_purchase.columns = ['customer_id', 'first_purchase_date']
    df = df.merge(first_purchase, on='customer_id')
    df['days_since_first_purchase'] = (pd.to_datetime('today') - df['first_purchase_date']).dt.days
    clv = df.groupby('customer_id')['order_value'].sum().reset_index()
    clv.columns = ['customer_id', 'customer_lifetime_value']
    return df.merge(clv, on='customer_id', how='left')

# Load Data

# URL file .gz dari GitHub
url = 'https://raw.githubusercontent.com/bino1kromo/Project-data-analysis-meysi/246a8f513863306690d02f6d538e6449ee2a9c1e/Dashboard/sales_data.gz'

# Mengunduh dan membaca data dari file .gz langsung dari URL
response = requests.get(url)
with gzip.open(io.BytesIO(response.content), 'rt') as file:
    sales_data = pd.read_csv(file)

# Mengonversi kolom waktu menjadi tipe datetime
sales_data['order_purchase_timestamp'] = pd.to_datetime(sales_data['order_purchase_timestamp'])
sales_data['order_estimated_delivery_date'] = pd.to_datetime(sales_data['order_estimated_delivery_date'])
sales_data['order_delivered_customer_date'] = pd.to_datetime(sales_data['order_delivered_customer_date'])

# Menambahkan kolom bulan dan tahun
sales_data['order_purchase_month'] = sales_data['order_purchase_timestamp'].dt.month
sales_data['order_purchase_year'] = sales_data['order_purchase_timestamp'].dt.year

# Sidebar Filters

min_date = sales_data['order_purchase_timestamp'].min()
max_date = sales_data['order_purchase_timestamp'].max()

with st.sidebar:
    st.image("https://raw.githubusercontent.com/bino1kromo/project-brazilian-ecommerce/6b76b91f13b21ad5f2e38b8d5f014f431ffce9e9/Dashboard/logo-olist.png")
    start_date, end_date = st.date_input("Rentang Waktu", min_value=min_date, max_value=max_date, value=[min_date, max_date])

# Menyaring data
filtered_data = sales_data[(sales_data['order_purchase_timestamp'] >= str(start_date)) & (sales_data['order_purchase_timestamp'] <= str(end_date))]

# Main Dashboard

st.title("Brazilian E-Commerce Dashboard")

# Monthly Sales
monthly_sales_df = create_monthly_sales_df(filtered_data)
st.subheader("Performa Revenue Bulanan")
fig, ax = plt.subplots(figsize=(14, 7))
sns.lineplot(data=monthly_sales_df, x='month_year', y='price', ax=ax, color='#008000')
plt.xticks(rotation=45)
st.pyplot(fig)

# Top Product Sales
product_sales_df = create_product_sales_df(filtered_data)
st.subheader("Top 10 Kategori Produk Terlaris")
fig, ax = plt.subplots(figsize=(14, 7))
sns.barplot(data=product_sales_df.head(10), 
            x='order_item_id', 
            y='product_category_name_english', 
            palette=['#A9DFBF' if i < 9 else '#1D8348' for i in range(10)], 
            ax=ax)
st.pyplot(fig)

# RFM Analysis
rfm_df = create_rfm_df(filtered_data)
st.subheader("Distribusi Recency")
fig, ax = plt.subplots(figsize=(12, 6))
sns.histplot(rfm_df['recency'], bins=20, kde=True, color='#008000', ax=ax)
st.pyplot(fig)

st.subheader("Distribusi Frequency")
fig, ax = plt.subplots(figsize=(12, 6))
sns.histplot(rfm_df['frequency'], bins=20, kde=True, color='#008000', ax=ax)
st.pyplot(fig)

st.subheader("Distribusi Monetary")
fig, ax = plt.subplots(figsize=(12, 6))
sns.histplot(rfm_df['monetary'], bins=20, kde=True, color='#008000', ax=ax)
st.pyplot(fig)

# Top Sellers
top_sellers_df = create_top_sellers_df(filtered_data)
st.subheader("Top 10 Penjual Berdasarkan Penjualan")
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x=top_sellers_df['seller_id'], 
            y=top_sellers_df['order_value'], 
            palette=['#AED6F1' if i < 9 else '#2E86C1' for i in range(10)], 
            ax=ax)
st.pyplot(fig)

# Menghitung Customer Lifetime Value dan menambahkan kolom ke sales_data
sales_data = calculate_clv(filtered_data)

# Visualisasi Tenure
st.subheader("Distribusi Tenure")
fig, axes = plt.subplots(1, 2, figsize=(18, 6))
sns.histplot(sales_data['days_since_first_purchase'], bins=20, kde=True, color='#008000', ax=axes[0])
axes[0].set_title('Tenure Distribution', fontsize=16, fontweight='bold')
axes[0].set_xlabel('Days Since First Purchase', fontsize=12)
axes[0].set_ylabel('Number of Customers', fontsize=12)
axes[0].tick_params(axis='x', rotation=45)

# Visualisasi Customer Lifetime Value (CLV)
sns.histplot(sales_data['customer_lifetime_value'], bins=20, kde=True, color='#008000', ax=axes[1])
axes[1].set_title('Customer Lifetime Value Distribution', fontsize=16, fontweight='bold')
axes[1].set_xlabel('Customer Lifetime Value', fontsize=12)
axes[1].set_ylabel('Number of Customers', fontsize=12)
axes[1].tick_params(axis='x', rotation=45)

plt.tight_layout()
st.pyplot(fig)

# Distribusi status pesanan
st.subheader("Distribusi Status Pesanan")
order_status_count = sales_data['order_status'].value_counts()
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x=order_status_count.index, y=order_status_count.values, color='#008000', ax=ax)
ax.set_title('Order Status Distribution', fontsize=16, fontweight='bold')
ax.set_xlabel('Order Status', fontsize=12)
ax.set_ylabel('Number of Orders', fontsize=12)
plt.xticks(rotation=45)
st.pyplot(fig)

# Waktu pengiriman sebenarnya vs perkiraan
sales_data['delivery_diff_days'] = (sales_data['order_estimated_delivery_date'] - sales_data['order_delivered_customer_date']).dt.days
st.subheader("Perbedaan Waktu Pengiriman")
fig, ax = plt.subplots(figsize=(12, 6))
sns.histplot(sales_data['delivery_diff_days'], bins=20, kde=True, color='#008000', ax=ax)
ax.set_title('Delivery Time Difference (Estimated - Actual)', fontsize=16, fontweight='bold')
ax.set_xlabel('Days', fontsize=12)
ax.set_ylabel('Number of Deliveries', fontsize=12)
st.pyplot(fig)

# Segmentasi Pelanggan Berdasarkan Frekuensi
bins = [0, 1, 3, 10, 50, float('inf')]
labels = ['New', 'Occasional', 'Regular', 'Frequent', 'VIP']
sales_data['frequency_segment'] = pd.cut(sales_data.groupby('customer_id')['order_id'].transform('count'), bins=bins, labels=labels)

# Visualisasi Segmen Pelanggan
st.subheader("Segmentasi Pelanggan Berdasarkan Frekuensi Pembelian")
fig, ax = plt.subplots(figsize=(12, 6))
sns.countplot(x='frequency_segment', data=sales_data, color='#008000', ax=ax)
ax.set_title('Customer Segmentation', fontsize=16, fontweight='bold')
ax.set_xlabel('Customer Segment', fontsize=12)
ax.set_ylabel('Number of Customers', fontsize=12)
st.pyplot(fig)
