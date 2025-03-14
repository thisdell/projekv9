import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set konfigurasi halaman di bagian paling atas
st.set_page_config(page_title="E-Commerce Dashboard", page_icon="🛒", layout="wide")

# Atur gaya visualisasi
sns.set_theme(style="darkgrid", context="notebook")

# Load data dari file CSV
@st.cache_data
def ambil_data():
    file_path = os.path.join(os.getcwd(), 'dashboard', 'final_data.csv')
    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, parse_dates=['order_purchase_timestamp'])
            return df
        else:
            st.error(f"⚠️ File CSV tidak ditemukan di path: `{file_path}`")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error saat membaca file CSV: {e}")
        return pd.DataFrame()

# Ambil data
df = ambil_data()

# Judul utama
st.title('🛒 E-Commerce Dashboard')

# Sidebar untuk filter
st.sidebar.title('🚀 Filter Data')

if not df.empty:
    # Konversi kolom tanggal ke datetime
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

    # Filter berdasarkan rentang tanggal
    min_date = df['order_purchase_timestamp'].min().date()
    max_date = df['order_purchase_timestamp'].max().date()

    date_range = st.sidebar.date_input(
        "Pilih rentang tanggal:",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df['order_purchase_timestamp'].dt.date >= start_date) & 
                (df['order_purchase_timestamp'].dt.date <= end_date)]

    # Pilihan visualisasi
    sidebar_option = st.sidebar.selectbox(
        'Pilih opsi untuk ditampilkan:',
        ['Distribusi Metode Pembayaran', 'Metode Pembayaran Paling Sering Digunakan', 'RFM Analysis']
    )

    if 'payment_type' in df.columns:
        if sidebar_option == 'Distribusi Metode Pembayaran':
            st.subheader('📊 Distribusi Metode Pembayaran')
            payment_distribution = df['payment_type'].value_counts().sort_values(ascending=False)

            if not payment_distribution.empty:
                fig, ax = plt.subplots(figsize=(8, 5))
                payment_distribution.plot(
                    kind='bar', 
                    color='skyblue', 
                    ax=ax
                )
                ax.set_xlabel('Metode Pembayaran')
                ax.set_ylabel('Jumlah Transaksi')
                ax.set_title('Distribusi Metode Pembayaran')
                ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

                st.pyplot(fig)
            else:
                st.warning("⚠️ Tidak ada data metode pembayaran yang valid.")

        elif sidebar_option == 'Metode Pembayaran Paling Sering Digunakan':
            st.subheader('💳 Metode Pembayaran Paling Sering Digunakan')
            payment_distribution = df['payment_type'].value_counts()

            if not payment_distribution.empty:
                most_common_payment = payment_distribution.idxmax()
                most_common_count = payment_distribution.max()
                other_count = payment_distribution.iloc[1:].sum()

                pie_data = pd.Series({
                    most_common_payment: most_common_count,
                    'Lainnya': other_count
                })

                st.markdown(f"Metode pembayaran yang paling sering digunakan adalah **{most_common_payment}** dengan **{most_common_count} transaksi**.")

                fig, ax = plt.subplots()
                pie_data.plot(
                    kind='pie', 
                    autopct='%1.1f%%', 
                    startangle=90, 
                    ax=ax, 
                    colors=sns.color_palette('pastel')
                )
                ax.axis('equal')
                ax.set_ylabel('')
                ax.set_title('Proporsi Metode Pembayaran')

                st.pyplot(fig)
            else:
                st.warning("⚠️ Tidak ada data metode pembayaran yang valid.")

        elif sidebar_option == 'RFM Analysis':
            st.subheader('📈 RFM Analysis')

            # Hitung RFM Metrics
            rfm = df.groupby('customer_id').agg({
                'order_purchase_timestamp': lambda x: (df['order_purchase_timestamp'].max() - x.max()).days,
                'order_id': 'count',
                'payment_value': 'sum'
            }).rename(columns={
                'order_purchase_timestamp': 'Recency',
                'order_id': 'Frequency',
                'payment_value': 'Monetary'
            }).reset_index()

            # Skoring RFM (pakai `pd.cut` untuk menangani data tidak cukup beragam)
            rfm['R_Score'] = pd.cut(rfm['Recency'], bins=4, labels=[4, 3, 2, 1])
            rfm['F_Score'] = pd.cut(rfm['Frequency'], bins=4, labels=[1, 2, 3, 4])
            rfm['M_Score'] = pd.cut(rfm['Monetary'], bins=4, labels=[1, 2, 3, 4])

            # Isi nilai NaN dengan nilai tengah
            rfm['R_Score'].fillna(2, inplace=True)
            rfm['F_Score'].fillna(2, inplace=True)
            rfm['M_Score'].fillna(2, inplace=True)

            # Buat Segmen
            rfm['Segment'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)

            # Tampilkan hasil RFM
            st.write(rfm[['customer_id', 'Recency', 'Frequency', 'Monetary', 'Segment']])

            # Visualisasi Segmentasi
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.countplot(x='Segment', data=rfm, order=rfm['Segment'].value_counts().index, palette='viridis')
            ax.set_title('Distribusi Segmen Pelanggan')
            ax.set_xlabel('Segmen')
            ax.set_ylabel('Jumlah Pelanggan')
            st.pyplot(fig)

else:
    st.error("❌ Data tidak ditemukan atau kolom tidak lengkap!")

# Menambahkan footer
st.markdown("""
---
Made with ❤️ by Dellanda
""")
