import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="YKS Detaylı Analiz Paneli", layout="wide")

# GENİŞLETİLMİŞ VE DERİNLATILMIŞ KONU LİSTESİ
KONULAR = {
    "Türkçe": [
        "Sözcükte Anlam & Yorum", "Cümlede Anlam & Yorum", "Paragrafta Ana Fikir & Yardımcı Fikirler",
        "Paragrafta Yapı & Anlatım Teknikleri", "Ses Bilgisi", "Yazım Kuralları", "Noktalama İşaretleri",
        "Sözcük Türleri (İsim, Sıfat, Zamir)", "Zarf, Edat, Bağlaç, Ünlem", "Fiiller & Fiilde Çatı",
        "Cümlenin Ögeleri", "Cümle Türleri", "Anlatım Bozuklukları"
    ],
    "Matematik": [
        "Temel Kavramlar & Sayı Kümeleri", "Bölme & Bölünebilme Rules", "EBOB - EKOK",
        "Birinci Dereceden Denklem ve Eşitsizlikler", "Mutlak Değer", "Üslü & Köklü İfadeler",
        "Çarpanlara Ayırma", "Oran - Orantı", "Sayı & Kesir Problemleri", "Yaş Problemleri",
        "Yüzde, Kar-Zarar & Faiz Problemleri", "Karışım Problemleri", "Hareket Problemleri",
        "İşçi & Havuz Problemleri", "Mantar & Rutin Olmayan Problemler", "Kümeler & Mantık",
        "Mantık", "Fonksiyonlar (Temel & Grafikler)", "Polinomlar", "İkinci Dereceden Denklemler",
        "Karmaşık Sayılar", "Parabol", "Eşitsizlikler", "Trigonometri", "Permütasyon & Kombinasyon", "Olasılık",
        "Logaritma", "Diziler & Seriler", "Limit & Süreklilik", "Türev & Uygulamaları", "İntegral & Alan"
    ],
    "Geometri": [
        "Doğruda & Üçgende Açılar", "Özel Üçgenler (Dik, İkizkenar, Eşkenar)", "Üçgende Alan & Açıortay/Kenarortay",
        "Üçgende Benzerlik", "Çokgenler & Dörtgenler", "Yamuk & Paralelkenar", "Eşkenar Dörtgen & Deltoid",
        "Dikdörtgen & Kare", "Çemberde Açı & Uzunluk", "Dairede Çevre ve Alan", "Analitik Geometri",
        "Katı Cisimler (Prizma, Piramit, Küre)", "Çemberin Analitiği"
    ],
    "Fizik": [
        "Fizik Bilimine Giriş & Madde Özellikleri", "Vektörler & Tork / Denge", "Kütle Merkezi & Basit Makineler",
        "Hareket & Dinamik (Newton Laws)", "İş, Güç ve Enerji", "Atışlar", "İtme ve Momentum",
        "Basınç & Kaldırma Kuvveti", "Isı, Sıcaklık & Genleşme", "Elektrostatik & Elektrik Akımı",
        "Mıknatıs & Manyetizma", "Alternatif Akım & Transformatörler", "Çembersel Hareket & Kepler",
        "Basit Harmonik Hareket", "Dalgalar & Optik", "Atom Fizigi & Radyoaktivite", "Modern Fizik & Teknolojik Uygulamalar"
    ],
    "Kimya": [
        "Kimya Bilimi & Atomun Yapısı", "Periyodik Sistem", "Kimyasal Türler Arası Etkileşimler",
        "Maddenin Halleri & Gazlar", "Mol Kavramı & Kimyasal Hesaplamalar", "Çözeltiler & Çözünürlük",
        "Kimya ve Enerji (Tepkime Isısı)", "Tepkime Hızları & Kimyasal Denge", "Asitler, Bazlar ve Tuzlar",
        "Çözünürlük Dengesi (KÇÇ)", "Kimya ve Elektrik (Piller & Elektroliz)", "Organik Kimyaya Giriş & Hibritleşme",
        "Hidrokarbonlar & Fonksiyonel Gruplar"
    ],
    "Biyoloji": [
        "Yaşam Bilimi Biyoloji & Hücre", "Canlıların Sınıflandırılması", "Hücre Bölünmeleri & Üreme",
        "Kalıtım & Ekosistem Ekolojisi", "Hücresel Solunum & Fotosentez/Kemosentez", "İnsan Fizyolojisi (Sistemler)",
        "Nükleik Asitler & Protein Sentezi", "Biyoteknoloji & Gen Mühendisliği"
    ],
    "Tarih": [
        "Tarih Bilimi & İlk Çağ Uygarlıkları", "İslam Öncesi & İslam Tarihi", "İlk Türk-İslam Devletleri",
        "Osmanlı Devleti Kuruluş & Yükselme", "Osmanlı Kültür ve Medeniyeti", "20. Yüzyıl Başlarında Osmanlı",
        "Milli Mücadele Dönemi & İnkılaplar", "Atatürkçülük & Çağdaş Türk ve Dünya Tarihi"
    ],
    "Coğrafya": [
        "Doğa ve İnsan & Harita Bilgisi", "Dünyanın Şekli ve Hareketleri", "Coğrafi Konum & İklim Bilgisi",
        "Yerin Şekillenmesi (İç & Dış Kuvvetler)", "Nüfus ve Yerleşme", "Türkiye'nin Fiziki & Beşeri Özellikleri",
        "Küresel Ortam: Bölgeler ve Ülkeler", "Çevre ve Toplum"
    ],
    "Felsefe & Din": [
        "Felsefeyi Tanıma & Bilgi Felsefesi", "Varlık & Ahlak Felsefesi", "Sanat, Din & Siyaset Felsefesi",
        "15.-17. Yüzyıl Felsefesi & Modern Düşünce", "Kur'an-ı Kerim ve Temel Kavramlar", "Hz. Muhammed'in Hayatı & Ahlakı",
        "İslam Düşüncesinde Yorumlar & Mezhepler"
    ]
}

DATA_FILE = "deneme_verileri.csv"

def verileri_yukle():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["Tarih", "Yayın/Deneme Adı", "Kayıt Türü", "Ders", "Doğru", "Yanlış", "Net", "Hatalı Konular"])

def veri_kaydet(df):
    df.to_csv(DATA_FILE, index=False)

df_veriler = verileri_yukle()

st.title("🎓 YKS Detaylı Analiz & Deneme Takip Paneli")

# SOL MENÜ - VERİ GİRİŞİ
with st.sidebar:
    st.header("📝 Yeni Deneme Ekle")
    tarih = st.date_input("Deneme Tarihi")
    yayin = st.text_input("Yayın / Deneme Adı", placeholder="Örn: 3D Türkiye Geneli 1")
    
    # AYRILMIŞ TYT / AYT SEÇİM EKRANI
    kayit_turu = st.radio("Kayıt Türü Seçin", ["Genel TYT Denemesi", "Genel AYT Denemesi", "Tek Branş Denemesi"])
    
    yeni_kayitlar = []
    
    if kayit_turu == "Genel TYT Denemesi":
        st.subheader("📚 Toplu TYT Netleri")
        tyt_dersler = ["Türkçe", "Matematik", "Geometri", "Fizik", "Kimya", "Biyoloji", "Tarih", "Coğrafya", "Felsefe & Din"]
        
        for ders in tyt_dersler:
            with st.expander(f"📌 {ders}"):
                c1, c2 = st.columns(2)
                d = c1.number_input(f"{ders} D", min_value=0, max_value=40, value=0, key=f"d_{ders}")
                y = c2.number_input(f"{ders} Y", min_value=0, max_value=40, value=0, key=f"y_{ders}")
                net = d - (y * 0.25)
                
                konular = KONULAR.get(ders, [])
                hatalar = st.multiselect(f"{ders} Eksik Konular", konular, key=f"h_{ders}")
                
                if d > 0 or y > 0:
                    yeni_kayitlar.append({
                        "Tarih": tarih, "Yayın/Deneme Adı": yayin, "Kayıt Türü": "Genel TYT Denemesi",
                        "Ders": ders, "Doğru": d, "Yanlış": y, "Net": net, "Hatalı Konular": ", ".join(hatalar)
                    })

    elif kayit_turu == "Genel AYT Denemesi":
        st.subheader("📚 Toplu AYT Netleri")
        ayt_dersler = ["Matematik", "Geometri", "Fizik", "Kimya", "Biyoloji", "Tarih", "Coğrafya", "Felsefe & Din"]
        
        for ders in ayt_dersler:
            with st.expander(f"📌 AYT {ders}"):
                c1, c2 = st.columns(2)
                d = c1.number_input(f"AYT {ders} D", min_value=0, max_value=40, value=0, key=f"d_ayt_{ders}")
                y = c2.number_input(f"AYT {ders} Y", min_value=0, max_value=40, value=0, key=f"y_ayt_{ders}")
                net = d - (y * 0.25)
                
                konular = KONULAR.get(ders, [])
                hatalar = st.multiselect(f"AYT {ders} Eksik Konular", konular, key=f"h_ayt_{ders}")
                
                if d > 0 or y > 0:
                    yeni_kayitlar.append({
                        "Tarih": tarih, "Yayın/Deneme Adı": yayin, "Kayıt Türü": "Genel AYT Denemesi",
                        "Ders": ders, "Doğru": d, "Yanlış": y, "Net": net, "Hatalı Konular": ", ".join(hatalar)
                    })

    else:
        st.subheader("🎯 Tek Branş Denemesi")
        secilen_ders = st.selectbox("Ders Seçin", list(KONULAR.keys()))
        c1, c2 = st.columns(2)
        d = c1.number_input("Doğru", min_value=0, max_value=40, value=0)
        y = c2.number_input("Yanlış", min_value=0, max_value=40, value=0)
        net = d - (y * 0.25)
        
        hatalar = st.multiselect("Eksik Konular", KONULAR[secilen_ders])
        
        if d > 0 or y > 0:
            yeni_kayitlar.append({
                "Tarih": tarih, "Yayın/Deneme Adı": yayin, "Kayıt Türü": "Tek Branş Denemesi",
                "Ders": secilen_ders, "Doğru": d, "Yanlış": y, "Net": net, "Hatalı Konular": ", ".join(hatalar)
            })

    if st.button("💾 Kaydet"):
        if yayin and yeni_kayitlar:
            yeni_df = pd.DataFrame(yeni_kayitlar)
            df_veriler = pd.concat([df_veriler, yeni_df], ignore_index=True)
            veri_kaydet(df_veriler)
            st.success("Deneme başarıyla kaydedildi!")
            st.rerun()
        else:
            st.warning("Lütfen yayın adını girin ve en az bir ders neti ekleyin.")

# ANA EKRAN - SEKME BAZLI DETAYLI ANALİZ
if not df_veriler.empty:
    tab_tyt, tab_ayt, tab_brans, tab_konu, tab_veri = st.tabs([
        "📊 TYT Analizi", "📈 AYT Analizi", "🎯 Branş Analizi", "⚠️ Konu Analizi", "📋 Tüm Veriler"
    ])

    with tab_tyt:
        st.header("📊 Genel TYT Deneme Analizi")
        tyt_df = df_veriler[df_veriler["Kayıt Türü"] == "Genel TYT Denemesi"]
        
        if not tyt_df.empty:
            toplam_tyt = tyt_df.groupby(["Tarih", "Yayın/Deneme Adı"])["Net"].sum().reset_index()
            fig = px.line(toplam_tyt, x="Tarih", y="Net", text="Net", hover_data=["Yayın/Deneme Adı"],
                          title="TYT Toplam Net Gelişimi", markers=True)
            fig.update_traces(textposition="top center")
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Ders Bazlı TYT Ortalamaları")
            ders_ort = tyt_df.groupby("Ders")["Net"].mean().reset_index()
            st.bar_chart(ders_ort.set_index("Ders"))
        else:
            st.info("Henüz kaydedilmiş Genel TYT Denemesi bulunamadı.")

    with tab_ayt:
        st.header("📈 Genel AYT Deneme Analizi")
        ayt_df = df_veriler[df_veriler["Kayıt Türü"] == "Genel AYT Denemesi"]
        
        if not ayt_df.empty:
            toplam_ayt = ayt_df.groupby(["Tarih", "Yayın/Deneme Adı"])["Net"].sum().reset_index()
            fig_ayt = px.line(toplam_ayt, x="Tarih", y="Net", text="Net", hover_data=["Yayın/Deneme Adı"],
                              title="AYT Toplam Net Gelişimi", markers=True)
            fig_ayt.update_traces(textposition="top center")
            st.plotly_chart(fig_ayt, use_container_width=True)
            
            st.subheader("Ders Bazlı AYT Ortalamaları")
            ders_ort_ayt = ayt_df.groupby("Ders")["Net"].mean().reset_index()
            st.bar_chart(ders_ort_ayt.set_index("Ders"))
        else:
            st.info("Henüz kaydedilmiş Genel AYT Denemesi bulunamadı.")

    with tab_brans:
        st.header("🎯 Branş Bazlı İlerleme")
        secilen_brans = st.selectbox("Analiz Edilecek Dersi Seçin", list(KONULAR.keys()))
        brans_df = df_veriler[df_veriler["Ders"] == secilen_brans]
        
        if not brans_df.empty:
            fig_brans = px.line(brans_df, x="Tarih", y="Net", color="Kayıt Türü",
                                hover_data=["Yayın/Deneme Adı"], title=f"{secilen_brans} Net Gelişimi", markers=True)
            st.plotly_chart(fig_brans, use_container_width=True)
        else:
            st.info(f"{secilen_brans} dersine ait kayıt bulunamadı.")

    with tab_konu:
        st.header("⚠️ En Çok Hata Yapılan Konular")
        tum_hatalar = []
        for hatalar in df_veriler["Hatalı Konular"].dropna():
            if hatalar:
                tum_hatalar.extend([h.strip() for h in hatalar.split(",") if h.strip()])
        
        if tum_hatalar:
            hata_df = pd.Series(tum_hatalar).value_counts().reset_index()
            hata_df.columns = ["Konu", "Hata Sayısı"]
            fig_hata = px.bar(hata_df.head(15), x="Hata Sayısı", y="Konu", orientation="h",
                              title="En Sık Soru Kaçırılan 15 Konu", color="Hata Sayısı")
            st.plotly_chart(fig_hata, use_container_width=True)
        else:
            st.info("Henüz konu hatası kaydedilmedi.")

    with tab_veri:
        st.header("📋 Tüm Kayıtlar")
        st.dataframe(df_veriler, use_container_width=True)
        
        if st.button("🗑️ Tüm Verileri Sıfırla"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
                st.success("Tüm veriler silindi!")
                st.rerun()
else:
    st.info("Henüz hiç deneme kaydı eklenmedi. Sol taraftaki menüden ilk denemenizi ekleyebilirsiniz.")
