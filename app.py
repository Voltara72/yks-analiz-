import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="YKS Detaylı Analiz Paneli", layout="wide")

# GENİŞLETİLMİŞ VE DERİNLATİLMİŞ KONU LİSTESİ
KONULAR = {
    "Türkçe": [
        "Sözcükte Anlam & Yorum", "Cümlede Anlam & Yorum", "Paragrafta Ana Fikir & Yardımcı Fikir",
        "Paragrafta Yapı & Anlatım Teknikleri", "Ses Bilgisi", "Yazım Kuralları", "Noktalama İşaretleri",
        "Sözcük Türleri (İsim, Sıfat, Zamir)", "Zarf, Edat, Bağlaç, Ünlem", "Fiiller & Fiilde Çatı",
        "Cümlenin Ögeleri", "Cümle Türleri", "Anlatım Bozuklukları"
    ],
    "Matematik": [
        "Temel Kavramlar & Sayı Kümeleri", "Bölme & Bölünebilme Rules", "EBOB - EKOK", "Rasyonel & Ondalık Sayılar",
        "Birinci Dereceden Denklem ve Eşitsizlikler", "Mutlak Değer", "Üslü İfadeler", "Köklü İfadeler",
        "Çarpanlara Ayırma", "Oran - Orantı", "Sayı & Kesir Problemleri", "Yaş Problemleri",
        "Yüzde, Kar-Zarar & Faiz Problemleri", "Karışım Problemleri", "Hareket / Hız Problemleri",
        "İşçi & Havuz Problemleri", "Mantar & Rutin Olmayan Problemler", "Kümeler & Kartezyen Çarpım",
        "Mantık", "Fonksiyonlar (Temel & Grafikler)", "Polinomlar", "İkinci Dereceden Denklemler",
        "Karmaşık Sayılar", "Parabol", "Eşitsizlikler", "Permütasyon & Kombinasyon", "Olasılık & Binom",
        "Logaritma", "Diziler & Seriler", "Limit & Süreklilik", "Türev & Uygulamaları", "İntegral & Alan Hesabı"
    ],
    "Geometri": [
        "Doğroda ve Üçgende Açılar", "Özel Üçgenler (Dik, İkizkenar, Eşkenar)", "Üçgende Alan & Açıortay/Kenarortay",
        "Üçgende Benzerlik", "Çokgenler & Dörtgenler", "Paralelkenar & Eşkenar Dörtgen", "Dikdörtgen & Kare",
        "Yamuk & Deltoid", "Çemberde Açı ve Uzunluk", "Dairede Çevre ve Alan", "Analitik Geometri (Nokta & Doğru)",
        "Dönüşüm Geometrisi", "Katı Cisimler (Prizma, Piramit, Silindir, Koni, Küre)", "Çemberin Analitiği"
    ],
    "Fizik": [
        "Fizik Bilimine Giriş", "Madde ve Özellikleri", "Sıvıların Kaldırma Kuvveti", "Basınç",
        "Isı, Sıcaklık ve Genleşme", "Vektörler & Bağıl Hareket", "Newton'un Hareket Yasaları", "Bir Boyutta Sabit İvmeli Hareket",
        "Atışlar", "İş, Güç ve Enerji", "İtme ve Momentum", "Tork & Denge & Kütle Merkezi",
        "Basit Makineler", "Elektrostatik & Elektrik Alan/Potansiyel", "Elektrik Akımı & Direnç/Devreler",
        "Manyetizma & İndüksiyon", "Alternatif Akım & Transformatörler", "Düzgün Çemberel Hareket",
        "Basit Harmonik Hareket", "Dalga Mekaniği & Su/Ses/Işık Dalgaları", "Optik (Gölge, Yansıma, Kırılma, Mercekler)",
        "Aydınlanma & Renk", "Atom Fizigi & Radyoaktivite", "Modern Fizik & Photoelektrik/Compton", "Modern Fizigin Teknolojideki Uygulamaları"
    ],
    "Kimya": [
        "Kimya Bilimi & Güvenlik", "Atomun Yapısı ve Periyodik Sistem", "Kimyasal Türler Arası Etkileşimler",
        "Maddenin Halleri (Gazlar, Sıvılar, Katılar)", "Doğa ve Kimya", "Kimyasal Hesaplamalar & Mol Kavramı",
        "Asitler, Bazlar ve Tuzlar", "Karışımlar & Ayırma Yöntemleri", "Kimya Her Yerde",
        "Sıvı Çözeltiler ve Çözünürlük", "Kimyasal Tepkimelerde Enerji", "Kimyasal Tepkimelerde Hız",
        "Kimyasal Denge & Sulu Çözelti Dengeleri", "Kimya ve Elektrik (Piller & Elektroliz)",
        "Karbon Kimyasına Giriş", "Organik Kimya (Hidrokarbonlar & Fonksiyonel Gruplar)"
    ],
    "Biyoloji": [
        "Yaşam Bilimi Biyoloji & Canlıların Bileşikleri", "Hücre Yapısı, Organeller ve Hücre Zarı", "Canlıların Sınıflandırılması",
        "Hücre Bölünmeleri (Mitoz & Mayoz)", "Eşeysiz ve Eşeyli Üreme", "Kalıtım Genel İlkeleri",
        "Ekosistem Ekolojisi & Güncel Çevre Sorunları", "İnsan Fizyolojisi (Denetleyici/Düzenleyici Sistemler)",
        "Destek ve Hareket Sistemi", "Sindirim Sistemi", "Dolaşım ve Bağışıklık Sistemi",
        "Solunum Sistemi", "Boşaltım Sistemi (Üriner Sistem)", "Göz, Kulak vb. Duyu Organları",
        "Bitki Biyolojisi (Yapı, Beslenme, Taşıma, Üreme)", "Nükleik Asitler & Protein Sentezi",
        "Canlılarda Enerji Dönüşümleri (Fotosentez, Kemosentez, Hücresel Solunum)", "Canlılar ve Çevre / Biyoteknoloji"
    ],
    "Edebiyat & Sosyal": [
        "Güzel Sanatlar ve Edebiyat", "Metinlerin Sınıflandırılması", "Şiir Bilgisi & Edebi Sanatlar",
        "İslamiyet Öncesi & Geçiş Dönemi Türk Edebiyatı", "Halk Edebiyatı", "Divan Edebiyatı",
        "Tanzimat Edebiyatı", "Servet-i Fünun & Fecr-i Ati", "Milli Edebiyat", "Cumhuriyet Dönemi Türk Edebiyatı",
        "Tarih Bilimi & İlk Çağ Uygarlıkları", "Türk-İslam Tarihi", "Osmanlı Tarihi (Kuruluş, Yükselme, Duraklama, Dağılma)",
        "İnkılap Tarihi & Atatürkçülük", "Coğrafya: Harita Bilgisi & İklim Şekilleri", "Coğrafya: Türkiye'nin Yerşekilleri & Nüfusu",
        "Felsefe: Bilgi, Varlık, Ahlak, Din Felsefesi", "Din Kültürü ve Ahlak Bilgisi"
    ]
}

DATA_DENEME = "deneme_toplam.csv"
DATA_KONU = "konu_eksikleri.csv"

if os.path.exists(DATA_DENEME):
    df_deneme = pd.read_csv(DATA_DENEME)
else:
    df_deneme = pd.DataFrame(columns=["Tarih", "Deneme Adı", "Sınav Türü", "Türkçe Net", "Matematik Net", "Fen Net", "Sosyal Net", "Toplam Net"])

if os.path.exists(DATA_KONU):
    df_konu = pd.read_csv(DATA_KONU)
else:
    df_konu = pd.DataFrame(columns=["Tarih", "Deneme Adı", "Ders", "Konu", "Doğru", "Yanlış", "Boş", "Net"])

st.title("📊 YKS Gelişmiş Genel & Branş Deneme Analizi")

st.sidebar.header("📝 Deneme / Branş Kaydı")
deneme_adi = st.sidebar.text_input("Deneme / Yayın Adı", "Özdebir 1")
sinav_turu = st.sidebar.radio("Kayıt Türü Seçin", ["Genel TYT/AYT Denemesi", "Tek Branş Denemesi"])

if sinav_turu == "Genel TYT/AYT Denemesi":
    st.sidebar.subheader("📚 Toplu Ders Netleri")
    
    col_t, col_m = st.sidebar.columns(2)
    turkce_net = col_t.number_input("Türkçe Net", min_value=0.0, max_value=40.0, value=20.0, step=0.25)
    mat_net = col_m.number_input("Matematik Net", min_value=0.0, max_value=40.0, value=18.0, step=0.25)
    
    col_f, col_s = st.sidebar.columns(2)
    fen_net = col_f.number_input("Fen Net", min_value=0.0, max_value=40.0, value=10.0, step=0.25)
    sosyal_net = col_s.number_input("Sosyal Net", min_value=0.0, max_value=40.0, value=12.0, step=0.25)
    
    toplam_net = turkce_net + mat_net + fen_net + sosyal_net
    st.sidebar.success(f"🎯 **Hesaplanan Toplam Net: {toplam_net:.2f}**")
    
    if st.sidebar.button("💾 Genel Denemeyi Kaydet"):
        tarih = pd.Timestamp.now().strftime("%Y-%m-%d")
        yeni_deneme = pd.DataFrame([{
            "Tarih": tarih,
            "Deneme Adı": deneme_adi,
            "Sınav Türü": "Genel Sınav",
            "Türkçe Net": turkce_net,
            "Matematik Net": mat_net,
            "Fen Net": fen_net,
            "Sosyal Net": sosyal_net,
            "Toplam Net": toplam_net
        }])
        df_deneme = pd.concat([df_deneme, yeni_deneme], ignore_index=True)
        df_deneme.to_csv(DATA_DENEME, index=False)
        st.sidebar.success("Genel deneme netlerin kaydedildi!")
        st.rerun()

else:
    st.sidebar.subheader("🎯 Branş & Konu Detay Analizi")
    secilen_ders = st.sidebar.selectbox("Ders Seçin", list(KONULAR.keys()))
    secilen_konu = st.sidebar.selectbox(f"📌 {secilen_ders} Detaylı Konu Başlığı", KONULAR[secilen_ders])
    
    col_d, col_y, col_b = st.sidebar.columns(3)
    b_dogru = col_d.number_input("Doğru", min_value=0, max_value=40, value=1)
    b_yanlis = col_y.number_input("Yanlış", min_value=0, max_value=40, value=0)
    b_bos = col_b.number_input("Boş", min_value=0, max_value=40, value=0)
    
    b_net = b_dogru - (b_yanlis * 0.25)
    st.sidebar.info(f"Konu Netiniz: **{b_net:.2f}**")
    
    if st.sidebar.button("💾 Branş/Konu Verisini Kaydet"):
        tarih = pd.Timestamp.now().strftime("%Y-%m-%d")
        yeni_konu = pd.DataFrame([{
            "Tarih": tarih,
            "Deneme Adı": deneme_adi,
            "Ders": secilen_ders,
            "Konu": secilen_konu,
            "Doğru": b_dogru,
            "Yanlış": b_yanlis,
            "Boş": b_bos,
            "Net": b_net
        }])
        df_konu = pd.concat([df_konu, yeni_konu], ignore_index=True)
        df_konu.to_csv(DATA_KONU, index=False)
        st.sidebar.success("Branş konu analizi kaydedildi!")
        st.rerun()

# ANA SAYFA / SEKMELER
tab1, tab2, tab3 = st.tabs(["📈 Genel Deneme Net Trendi", "🎯 Branş & Detaylı Konu Analizi", "📋 Tüm Veriler"])

with tab1:
    if not df_deneme.empty:
        st.subheader("📊 Genel Denemeler Net Gelişimi")
        fig = px.bar(
            df_deneme, 
            x="Deneme Adı", 
            y=["Türkçe Net", "Matematik Net", "Fen Net", "Sosyal Net"],
            title="Genel Deneme Netleri (Ders Kırılımlı)",
            barmode="stack"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_deneme, use_container_width=True)
    else:
        st.info("Henüz genel deneme kaydı yapılmadı.")

with tab2:
    if not df_konu.empty:
        st.subheader("⚠️ Konu Bazlı Doğru, Yanlış ve Boş Dağılımı")
        fig_konu = px.bar(
            df_konu, 
            x="Konu", 
            y=["Doğru", "Yanlış", "Boş"], 
            color_discrete_sequence=["#2CA02C", "#D62728", "#FF7F0E"],
            title="Konulara Göre Soru Başarısı",
            barmode="group",
            facet_col="Ders"
        )
        st.plotly_chart(fig_konu, use_container_width=True)
        st.dataframe(df_konu, use_container_width=True)
    else:
        st.info("Henüz branş/konu kaydı yapılmadı.")

with tab3:
    st.write("### Genel Deneme Kayıtları", df_deneme)
    st.write("### Branş & Konu Kayıtları", df_konu)
