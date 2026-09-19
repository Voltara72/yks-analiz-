import streamlit as st
import pandas as pd
import plotly.express as px

# Sayfa Yapılandırması
st.set_page_config(page_title="YKS Deneme Analiz Paneli", layout="wide")

st.title("📊 YKS Deneme Analiz Paneli")
st.write("Deneme sonuçlarınızı girin, netlerinizi ve gelişiminizi grafiklerle takip edin.")

# Sidebar - Veri Girişi
st.sidebar.header("📝 Yeni Deneme Ekle")

deneme_adi = st.sidebar.text_input("Deneme Adı", "Örn: Özdebir TYT 1")
tur = st.sidebar.selectbox("Sınav Türü", ["TYT", "AYT"])

st.sidebar.subheader("Netlerinizi Girin")

if tur == "TYT":
    turkce = st.sidebar.number_input("Türkçe Net", 0.0, 40.0, 30.0, step=0.25)
    sosyal = st.sidebar.number_input("Sosyal Net", 0.0, 20.0, 15.0, step=0.25)
    matematik = st.sidebar.number_input("Matematik Net", 0.0, 40.0, 25.0, step=0.25)
    fen = st.sidebar.number_input("Fen Net", 0.0, 20.0, 10.0, step=0.25)
    toplam_net = turkce + sosyal + matematik + fen
    yeni_veri = {
        "Deneme Adı": deneme_adi,
        "Tür": tur,
        "Türkçe": turkce,
        "Sosyal": sosyal,
        "Matematik": matematik,
        "Fen": fen,
        "Toplam Net": toplam_net
    }
else:
    matematik = st.sidebar.number_input("AYT Matematik Net", 0.0, 40.0, 20.0, step=0.25)
    fizik = st.sidebar.number_input("Fizik Net", 0.0, 14.0, 8.0, step=0.25)
    kimya = st.sidebar.number_input("Kimya Net", 0.0, 13.0, 7.0, step=0.25)
    biyoloji = st.sidebar.number_input("Biyoloji Net", 0.0, 13.0, 6.0, step=0.25)
    toplam_net = matematik + fizik + kimya + biyoloji
    yeni_veri = {
        "Deneme Adı": deneme_adi,
        "Tür": tur,
        "Matematik": matematik,
        "Fizik": fizik,
        "Kimya": kimya,
        "Biyoloji": biyoloji,
        "Toplam Net": toplam_net
    }

# Session State ile Veri Tutma
if "denemeler" not in st.session_state:
    st.session_state.denemeler = []

if st.sidebar.button("Denemeyi Kaydet"):
    st.session_state.denemeler.append(yeni_veri)
    st.sidebar.success("Deneme başarıyla eklendi!")

# Veri Gösterimi ve Grafikler
if st.session_state.denemeler:
    df = pd.DataFrame(st.session_state.denemeler)
    
    st.subheader("📋 Kayıtlı Denemeler")
    st.dataframe(df, use_container_width=True)
    
    st.subheader("📈 Net Gelişim Grafiği")
    fig = px.line(df, x="Deneme Adı", y="Toplam Net", color="Tür", markers=True, title="Toplam Net Değişimi")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Henüz eklenmiş bir deneme bulunmuyor. Sol taraftaki menüden ilk denemenizi ekleyebilirsiniz.")
