import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="YKS Branş & Konu Analiz Paneli", layout="wide")

KONULAR = {
    "Türkçe": ["Paragraf", "Dil Bilgisi", "Yazım Kuralları", "Noktalama İşaretleri", "Sözcükte Anlam", "Cümlede Anlam"],
    "Matematik": ["Temel Kavramlar", "Problemler", "Fonksiyonlar", "PKOB", "Üslü-Köklü", "Geometri - Üçgenler", "Geometri - Çokgenler/Çember"],
    "Fizik": ["Vektörler/Kuvvet", "Mekanik/Hareket", "Elektrik ve Manyetizma", "Dalgalar", "Optik", "Modern Fizik"],
    "Kimya": ["Atom ve Periyodik Sistem", "Kimyasal Türler Arası Etkileşimler", "Mol Kavramı / Tepkimeler", "Çözeltiler", "Kimya ve Enerji / Hız"],
    "Biyoloji": ["Hücre ve Organeller", "Canlıların Sınıflandırılması", "Kalıtım", "Ekoloji", "Sistemler (Anatomi)", "Bitki Biyolojisi"]
}

DATA_FILE = "deneme_verileri.csv"

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Tarih", "Deneme Adı", "Tür", "Ders", "Konu", "Doğru", "Yanlış", "Boş", "Net"])

st.title("📊 YKS Branş & Konu Analiz Paneli")

st.sidebar.header("📝 Yeni Sonuç Ekle")
deneme_adi = st.sidebar.text_input("Deneme / Yayın Adı", "Özdebir 1")
tur = st.sidebar.selectbox("Sınav Türü", ["Branş Denemesi", "Genel TYT", "Genel AYT"])
ders = st.sidebar.selectbox("Ders Seçin", list(KONULAR.keys()))

st.sidebar.subheader(f"📌 {ders} Konu Başarısı")
konu = st.sidebar.selectbox("Konu Seçin", KONULAR[ders])

col1, col2, col3 = st.sidebar.columns(3)
dogru = col1.number_input("Doğru", min_value=0, max_value=40, value=1)
yanlis = col2.number_input("Yanlış", min_value=0, max_value=40, value=0)
bos = col3.number_input("Boş", min_value=0, max_value=40, value=0)

net = dogru - (yanlis * 0.25)

if st.sidebar.button("Kaydet ve Analize Ekle"):
    yeni_veri = pd.DataFrame([{
        "Tarih": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "Deneme Adı": deneme_adi,
        "Tür": tur,
        "Ders": ders,
        "Konu": konu,
        "Doğru": dogru,
        "Yanlış": yanlis,
        "Boş": bos,
        "Net": net
    }])
    df = pd.concat([df, yeni_veri], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.sidebar.success("Veri kaydedildi!")
    st.rerun()

if not df.empty:
    tab1, tab2 = st.tabs(["📉 Konu Analizi & Eksikler", "📋 Tüm Kayıtlar"])
    
    with tab1:
        st.subheader("⚠️ En Çok Yanlış / Boş Yapılan Konular")
        df["Hata Sayısı"] = df["Yanlış"] + df["Boş"]
        konu_ozt = df.groupby(["Ders", "Konu"])[["Doğru", "Yanlış", "Boş", "Hata Sayısı"]].sum().reset_index()
        
        fig = px.bar(
            konu_ozt, 
            x="Konu", 
            y=["Yanlış", "Boş"], 
            color_discrete_sequence=["#EF553B", "#FFA15A"],
            title="Konulara Göre Hata (Yanlış + Boş) Dağılımı",
            barmode="stack",
            facet_col="Ders"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with tab2:
        st.dataframe(df, use_container_width=True)
else:
    st.info("Henüz veri girilmedi. Sol taraftaki menüden ders ve konuları seçip deneme sonucunu ekleyebilirsin.")
