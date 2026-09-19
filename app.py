import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="YKS Tam Kapsamlı Analiz Paneli", layout="wide")

KONULAR = {
    "Türkçe": ["Paragraf", "Dil Bilgisi", "Yazım Kuralları", "Noktalama İşaretleri", "Sözcükte Anlam", "Cümlede Anlam"],
    "Matematik": ["Temel Kavramlar", "Problemler", "Fonksiyonlar", "PKOB", "Üslü-Köklü", "Geometri - Üçgenler", "Geometri - Çokgenler/Çember"],
    "Fizik": ["Vektörler/Kuvvet", "Mekanik/Hareket", "Elektrik ve Manyetizma", "Dalgalar", "Optik", "Modern Fizik"],
    "Kimya": ["Atom ve Periyodik Sistem", "Kimyasal Türler Arası Etkileşimler", "Mol Kavramı / Tepkimeler", "Çözeltiler", "Kimya ve Enerji / Hız"],
    "Biyoloji": ["Hücre ve Organeller", "Canlıların Sınıflandırılması", "Kalıtım", "Ekoloji", "Sistemler (Anatomi)", "Bitki Biyolojisi"],
    "Edebiyat / Sosyal": ["Edebiyat - Tarihi Dönemler", "Edebiyat - Şiir Bilgisi", "Tarih - İlk ve Orta Çağ", "Tarih - İnkılap", "Coğrafya - Harita / İklim"]
}

DATA_FILE = "deneme_verileri.csv"

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Tarih", "Deneme Adı", "Kategori", "Ders", "Konu", "Doğru", "Yanlış", "Boş", "Net"])

st.title("📊 YKS Genel & Branş Deneme Analiz Paneli")

# SOL MENÜ - VERİ GİRİŞİ
st.sidebar.header("📝 Deneme / Konu Girişi")
deneme_adi = st.sidebar.text_input("Deneme / Yayın Adı", "Özdebir 1")
kategori = st.sidebar.radio("Sınav Tipi Seçin", ["Genel TYT", "Genel AYT", "Branş Denemesi"])

ders = st.sidebar.selectbox("Ders Seçin", list(KONULAR.keys()))
konu = st.sidebar.selectbox(f"📌 {ders} Konusu", KONULAR[ders])

col1, col2, col3 = st.sidebar.columns(3)
dogru = col1.number_input("Doğru", min_value=0, max_value=40, value=1)
yanlis = col2.number_input("Yanlış", min_value=0, max_value=40, value=0)
bos = col3.number_input("Boş", min_value=0, max_value=40, value=0)

net = dogru - (yanlis * 0.25)
st.sidebar.info(f"Hesaplanan Net: **{net:.2f}**")

if st.sidebar.button("Kaydet ve Ekle"):
    yeni_veri = pd.DataFrame([{
        "Tarih": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "Deneme Adı": deneme_adi,
        "Kategori": kategori,
        "Ders": ders,
        "Konu": konu,
        "Doğru": dogru,
        "Yanlış": yanlis,
        "Boş": bos,
        "Net": net
    }])
    df = pd.concat([df, yeni_veri], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.sidebar.success("Kayıt Başarılı!")
    st.rerun()

# ANA PANEL / SEKMELER
tab1, tab2, tab3 = st.tabs(["📈 Net Gelişimi (TYT/AYT/Branş)", "🎯 Konu Analizi & Eksikler", "📋 Tüm Deneme Kayıtları"])

if not df.empty:
    with tab1:
        st.subheader("📊 Denemelere Göre Toplam / Ders Net Grafiği")
        net_ozt = df.groupby(["Deneme Adı", "Kategori", "Ders"])["Net"].sum().reset_index()
        fig_net = px.bar(
            net_ozt, 
            x="Deneme Adı", 
            y="Net", 
            color="Ders", 
            barmode="group",
            facet_col="Kategori",
            title="Genel ve Branş Deneme Netleri"
        )
        st.plotly_chart(fig_net, use_container_width=True)

    with tab2:
        st.subheader("⚠️ Konu Bazlı Hata (Yanlış + Boş) Dağılımı")
        df["Hata Sayısı"] = df["Yanlış"] + df["Boş"]
        konu_ozt = df.groupby(["Ders", "Konu"])[["Doğru", "Yanlış", "Boş", "Hata Sayısı"]].sum().reset_index()
        
        fig_konu = px.bar(
            konu_ozt, 
            x="Konu", 
            y=["Yanlış", "Boş"], 
            color_discrete_sequence=["#EF553B", "#FFA15A"],
            title="Hangi Konularda Eksik Var?",
            barmode="stack",
            facet_col="Ders"
        )
        st.plotly_chart(fig_konu, use_container_width=True)

    with tab3:
        st.subheader("📝 Tüm Girilen Veriler")
        st.dataframe(df, use_container_width=True)
else:
    st.info("Henüz kayıt bulunmuyor. Sol menüden Genel TYT, Genel AYT veya Branş denemesi seçerek verilerini girmeye başlayabilirsin!")
