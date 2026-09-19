from datetime import datetime
import os
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from supabase import create_client, Client

# ==========================================
# 1. SUPABASE VE TELEGRAM BİLGİLERİ
# ==========================================
SUPABASE_URL = "https://kelreflqssbrhcsrjxgv.supabase.co"
SUPABASE_KEY = "sb_publishable_kARDYIzMzBNAyykzKlgFYg_m0FKtnJ9"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TELEGRAM_BOT_TOKEN = "8783937056:AAFtpytdK_hnNRfsRi0DB4V4cOqD0P1EAn0"
TELEGRAM_CHAT_ID = "6250328228"

def akilli_uyari_gonder(mesaj: str) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mesaj, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Bildirim gönderilemedi: {e}")
        return False

st.set_page_config(page_title="YKS Detaylı Analiz & Koçluk Paneli", layout="wide")

# ==========================================
# 2. VERİTABANI YÖNETİMİ (Supabase)
# ==========================================
def register_user(username, password):
    try:
        check = supabase.table("users").select("*").eq("username", username).execute()
        if len(check.data) > 0:
            return False
        supabase.table("users").insert({"username": username, "password": password}).execute()
        return True
    except Exception as e:
        st.error(f"Kayıt hatası: {e}")
        return False

def login_user(username, password):
    try:
        res = supabase.table("users").select("id").eq("username", username).eq("password", password).execute()
        if len(res.data) > 0:
            return res.data[0]["id"]
        return None
    except Exception as e:
        st.error(f"Giriş hatası: {e}")
        return None

# Oturum Durumu Kontrolü
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None

# ==========================================
# 3. GİRİŞ / KAYIT EKRANI
# ==========================================
if st.session_state.user_id is None:
    st.title("🎓 YKS Detaylı Analiz & Koçluk Paneli")
    st.info("Devam etmek için lütfen giriş yapın veya yeni bir hesap oluşturun.")
    
    col1, col2 = st.columns(2)
    with col1:
        secim = st.radio("İşlem Seçin", ["Giriş Yap", "Kayıt Ol"])
        kullanici_adi = st.text_input("Kullanıcı Adı")
        sifre = st.text_input("Şifre", type="password")
        
        if secim == "Kayıt Ol":
            if st.button("Hesap Oluştur"):
                if kullanici_adi and sifre:
                    if register_user(kullanici_adi, sifre):
                        st.success("Hesap başarıyla oluşturuldu! Şimdi 'Giriş Yap' seçeneğiyle girebilirsin.")
                    else:
                        st.error("Bu kullanıcı adı zaten alınmış.")
                else:
                    st.warning("Lütfen tüm alanları doldurun.")
        else:
            if st.button("Giriş Yap"):
                user_id = login_user(kullanici_adi, sifre)
                if user_id:
                    st.session_state.user_id = user_id
                    st.session_state.username = kullanici_adi
                    st.rerun()
                else:
                    st.error("Kullanıcı adı veya şifre hatalı.")

# ==========================================
# 4. ANA UYGULAMA (Giriş Yapıldıktan Sonra)
# ==========================================
else:
    st.sidebar.title(f"👤 Merhaba, {st.session_state.username}")
    if st.sidebar.button("🚪 Çıkış Yap"):
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()

    # KONU LİSTESİ
    KONULAR = {
        "Türkçe": ["Sözcükte Anlam & Yorum", "Cümlede Anlam & Yorum", "Paragrafta Ana Fikir & Yardımcı Fikirler", "Paragrafta Yapı & Anlatım Teknikleri", "Ses Bilgisi", "Yazım Kuralları", "Noktalama İşaretleri", "Sözcük Türleri (İsim, Sıfat, Zamir)", "Zarf, Edat, Bağlaç, Ünlem", "Fiiller & Fiilde Çatı", "Cümlenin Ögeleri", "Cümle Türleri", "Anlatım Bozuklukları"],
        "Matematik": ["Temel Kavramlar & Sayı Kümeleri", "Bölme & Bölünebilme Kuralları", "EBOB - EKOK", "Birinci Dereceden Denklem ve Eşitsizlikler", "Mutlak Değer", "Üslü & Köklü İfadeler", "Çarpanlara Ayırma", "Oran - Orantı", "Sayı & Kesir Problemleri", "Yaş Problemleri", "Yüzde, Kar-Zarar & Faiz Problemleri", "Karışım Problemleri", "Hareket Problemleri", "İşçi & Havuz Problemleri", "Rutin Olmayan Problemler", "Kümeler & Mantık", "Fonksiyonlar (Temel & Grafikler)", "Polinomlar", "İkinci Dereceden Denklemler", "Karmaşık Sayılar", "Parabol", "Eşitsizlikler", "Trigonometri", "Permütasyon & Kombinasyon", "Olasılık", "Logaritma", "Diziler & Seriler", "Limit & Süreklilik", "Türev & Uygulamaları", "İntegral & Alan"],
        "Geometri": ["Doğruda & Üçgende Açılar", "Özel Üçgenler (Dik, İkizkenar, Eşkenar)", "Üçgende Alan & Açıortay/Kenarortay", "Üçgende Benzerlik", "Çokgenler & Dörtgenler", "Yamuk & Paralelkenar", "Eşkenar Dörtgen & Deltoid", "Dikdörtgen & Kare", "Çemberde Açı & Uzunluk", "Dairede Çevre ve Alan", "Analitik Geometri", "Katı Cisimler (Prizma, Piramit, Küre)", "Çemberin Analitiği"],
        "Fizik": ["Fizik Bilimine Giriş & Madde Özellikleri", "Vektörler & Tork / Denge", "Kütle Merkezi & Basit Makineler", "Hareket & Dinamik", "İş, Güç ve Enerji", "Atışlar", "İtme ve Momentum", "Basınç & Kaldırma Kuvveti", "Isı, Sıcaklık & Genleşme", "Elektrostatik & Elektrik Akımı", "Mıknatıs & Manyetizma", "Alternatif Akım & Transformatörler", "Çembersel Hareket & Kepler", "Basit Harmonik Hareket", "Dalgalar & Optik", "Modern Fizik"],
        "Kimya": ["Kimya Bilimi & Atomun Yapısı", "Periyodik Sistem", "Kimyasal Türler Arası Etkileşimler", "Maddenin Halleri & Gazlar", "Mol Kavramı & Kimyasal Hesaplamalar", "Çözeltiler & Çözünürlük", "Kimya ve Enerji", "Tepkime Hızları & Kimyasal Denge", "Asitler, Bazlar ve Tuzlar", "Çözünürlük Dengesi (KÇÇ)", "Kimya ve Elektrik", "Organik Kimyaya Giriş", "Hidrokarbonlar"],
        "Biyoloji": ["Yaşam Bilimi Biyoloji & Hücre", "Canlıların Sınıflandırılması", "Hücre Bölünmeleri & Üreme", "Kalıtım & Ekosistem Ekolojisi", "Hücresel Solunum & Fotosentez", "İnsan Fizyolojisi (Sistemler)", "Nükleik Asitler & Protein Sentezi", "Biyoteknoloji"],
        "Tarih": ["Tarih Bilimi & İlk Çağ Uygarlıkları", "İslam Öncesi & İslam Tarihi", "İlk Türk-İslam Devletleri", "Osmanlı Devleti Kuruluş & Yükselme", "Osmanlı Kültür ve Medeniyeti", "20. Yüzyıl Başlarında Osmanlı", "Milli Mücadele Dönemi & İnkılaplar", "Atatürkçülük"],
        "Coğrafya": ["Doğa ve İnsan & Harita Bilgisi", "Dünyanın Şekli ve Hareketleri", "Coğrafi Konum & İklim Bilgisi", "Yerin Şekillenmesi", "Nüfus ve Yerleşme", "Türkiye'nin Fiziki & Beşeri Özellikleri", "Küresel Ortam", "Çevre ve Toplum"],
        "Felsefe & Din": ["Felsefeyi Tanıma & Bilgi Felsefesi", "Varlık & Ahlak Felsefesi", "Sanat, Din & Siyaset Felsefesi", "15.-17. Yüzyıl Felsefesi", "Kur'an-ı Kerim ve Temel Kavramlar", "Hz. Muhammed'in Hayatı & Ahlakı", "İslam Düşüncesinde Yorumlar"]
    }

    # Kullanıcı Verilerini Supabase'den Çekme
    try:
        deneme_data = supabase.table("denemeler").select("*").eq("user_id", st.session_state.user_id).execute().data
        df_veriler = pd.DataFrame(deneme_data)
    except Exception:
        df_veriler = pd.DataFrame()

    try:
        hatirlatici_data = supabase.table("hatirlaticilar").select("*").eq("user_id", st.session_state.user_id).execute().data
        df_hatirlatici = pd.DataFrame(hatirlatici_data)
    except Exception:
        df_hatirlatici = pd.DataFrame()

    st.title("🎓 YKS Detaylı Analiz & Akıllı Koçluk Paneli")

    # SOL MENÜ - VERİ GİRİŞİ
    with st.sidebar:
        st.header("📝 Yeni Deneme Ekle")
        tarih = st.date_input("Deneme Tarihi")
        yayin = st.text_input("Yayın / Deneme Adı", placeholder="Örn: 3D Türkiye Geneli 1")
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
                    hatalar = st.multiselect(f"{ders} Eksik Konular", KONULAR.get(ders, []), key=f"h_{ders}")
                    if d > 0 or y > 0:
                        yeni_kayitlar.append({
                            "user_id": st.session_state.user_id,
                            "tarih": str(tarih),
                            "yayin": yayin,
                            "kayit_turu": kayit_turu,
                            "ders": ders,
                            "dogru": d,
                            "yanlis": y,
                            "net": net,
                            "hatali_konular": ", ".join(hatalar)
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
                    hatalar = st.multiselect(f"AYT {ders} Eksik Konular", KONULAR.get(ders, []), key=f"h_ayt_{ders}")
                    if d > 0 or y > 0:
                        yeni_kayitlar.append({
                            "user_id": st.session_state.user_id,
                            "tarih": str(tarih),
                            "yayin": yayin,
                            "kayit_turu": kayit_turu,
                            "ders": ders,
                            "dogru": d,
                            "yanlis": y,
                            "net": net,
                            "hatali_konular": ", ".join(hatalar)
                        })
        else:
            st.subheader("🎯 Tek Branş Denemesi")
            secilen_ders = st.selectbox("Ders Seçin", list(KONULAR.keys()))
            c1, c2 = st.columns(2)
            d = c1.number_input("Doğru", min_value=0, max_value=40, value=0)
            y = c2.number_input("Yanlış", min_value=0, max_value=40, value=0)
            net = d - (y * 0.25)
            secilen_konular_listesi = KONULAR[secilen_ders]
            if secilen_ders == "Matematik":
                secilen_konular_listesi = KONULAR["Matematik"] + KONULAR["Geometri"]
            hatalar = st.multiselect("Eksik Konular", secilen_konular_listesi)
            if d > 0 or y > 0:
                yeni_kayitlar.append({
                    "user_id": st.session_state.user_id,
                    "tarih": str(tarih),
                    "yayin": yayin,
                    "kayit_turu": kayit_turu,
                    "ders": secilen_ders,
                    "dogru": d,
                    "yanlis": y,
                    "net": net,
                    "hatali_konular": ", ".join(hatalar)
                })

        if st.button("💾 Denemeyi Kaydet ve Telegram'a Bildir"):
            if yayin and yeni_kayitlar:
                supabase.table("denemeler").insert(yeni_kayitlar).execute()
                toplam_eklenen_net = sum([item["net"] for item in yeni_kayitlar])
                telegram_mesaj = f"🚀 **{st.session_state.username} Yeni Deneme Kaydetti!**\n\n📌 Yayın: {yayin}\n📋 Tür: {kayit_turu}\n📊 Toplam Net: *{toplam_eklenen_net:.2f}*\n\n💪 Çalışmalara tam gaz devam!"
                akilli_uyari_gonder(telegram_mesaj)
                st.success("Deneme kaydedildi ve Telegram'a bildirildi!")
                st.rerun()

    # ANA SEKMELER
    tab_tyt, tab_ayt, tab_brans, tab_konu, tab_program, tab_hatirlatici = st.tabs([
        "📊 TYT Analizi", "📈 AYT Analizi", "🎯 Branş Analizi", "⚠️ Konu & Akıllı Uyarı", "📅 Ders Programım", "⏰ Saatlik Hatırlatıcı"
    ])

    # 1. TYT ANALİZİ
    with tab_tyt:
        st.header("📊 Genel TYT Deneme Analizi")
        tyt_df = df_veriler[df_veriler["kayit_turu"] == "Genel TYT Denemesi"] if not df_veriler.empty else pd.DataFrame()
        if not tyt_df.empty:
            toplam_tyt = tyt_df.groupby(["tarih", "yayin"])["net"].sum().reset_index()
            grafik_turu = st.radio("TYT İçin Grafik Türü Seçin:", ["Çizgi Grafiği", "Pasta Grafik (Pie)"], horizontal=True, key="tyt_grafik_tipi")
            if grafik_turu == "Çizgi Grafiği":
                fig = px.line(toplam_tyt, x="tarih", y="net", text="net", hover_data=["yayin"], title="TYT Toplam Net Gelişimi", markers=True)
            else:
                fig = px.pie(toplam_tyt, names="yayin", values="net", title="TYT Yayın Bazlı Net Dağılımı (Pasta Grafik)", hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Henüz TYT denemesi eklenmedi.")

    # 2. AYT ANALİZİ
    with tab_ayt:
        st.header("📈 Genel AYT Deneme Analizi")
        ayt_df = df_veriler[df_veriler["kayit_turu"] == "Genel AYT Denemesi"] if not df_veriler.empty else pd.DataFrame()
        if not ayt_df.empty:
            toplam_ayt = ayt_df.groupby(["tarih", "yayin"])["net"].sum().reset_index()
            grafik_turu_ayt = st.radio("AYT İçin Grafik Türü Seçin:", ["Çizgi Grafiği", "Pasta Grafik (Pie)"], horizontal=True, key="ayt_grafik_tipi")
            if grafik_turu_ayt == "Çizgi Grafiği":
                fig_ayt = px.line(toplam_ayt, x="tarih", y="net", text="net", hover_data=["yayin"], title="AYT Toplam Net Gelişimi", markers=True)
            else:
                fig_ayt = px.pie(toplam_ayt, names="yayin", values="net", title="AYT Yayın Bazlı Net Dağılımı (Pasta Grafik)", hole=0.3)
            st.plotly_chart(fig_ayt, use_container_width=True)
        else:
            st.info("Henüz AYT denemesi eklenmedi.")

    # 3. BRANŞ ANALİZİ
    with tab_brans:
        st.header("🎯 Branş Bazlı İlerleme")
        secilen_brans = st.selectbox("Analiz Edilecek Dersi Seçin", list(KONULAR.keys()))
        brans_df = df_veriler[df_veriler["ders"] == secilen_brans] if not df_veriler.empty else pd.DataFrame()
        if not brans_df.empty:
            grafik_turu_brans = st.radio("Branş İçin Grafik Türü Seçin:", ["Çizgi Grafiği", "Pasta Grafik (Pie)"], horizontal=True, key="brans_grafik_tipi")
            if grafik_turu_brans == "Çizgi Grafiği":
                fig_brans = px.line(brans_df, x="tarih", y="net", color="kayit_turu", hover_data=["yayin"], title=f"{secilen_brans} Net Gelişimi", markers=True)
            else:
                fig_brans = px.pie(brans_df, names="yayin", values="net", title=f"{secilen_brans} Yayın Bazlı Net Dağılımı (Pasta Grafik)", hole=0.3)
            st.plotly_chart(fig_brans, use_container_width=True)
        else:
            st.info(f"Henüz {secilen_brans} branşına ait veri girilmedi.")

    # 4. AKILLI UYARI VE KONU ANALİZİ
    with tab_konu:
        st.header("⚠️ Akıllı Koçluk Uyarısı & Hatalı Konular")
        tum_hatalar = []
        if not df_veriler.empty and "hatali_konular" in df_veriler.columns:
            for hatalar in df_veriler["hatali_konular"].dropna():
                if hatalar:
                    tum_hatalar.extend([h.strip() for h in hatalar.split(",") if h.strip()])
        
        if tum_hatalar:
            hata_df = pd.Series(tum_hatalar).value_counts().reset_index()
            hata_df.columns = ["Konu", "Hata Sayısı"]
            kritik_konular = hata_df[hata_df["Hata Sayısı"] >= 2]
            if not kritik_konular.empty:
                st.error("🚨 **AKILLI KOÇ UYARISI:** Aşağıdaki konularda üst üste hatalar yapıyorsunuz!")
                for _, row in kritik_konular.iterrows():
                    st.warning(f"👉 {row['Konu']}: Toplam {row['Hata Sayısı']} kez yanlış!")
            
            grafik_turu_konu = st.radio("Konu Analizi İçin Grafik Türü Seçin:", ["Yatay Sütun Grafiği", "Pasta Grafik (Pie)"], horizontal=True, key="konu_grafik_tipi")
            if grafik_turu_konu == "Yatay Sütun Grafiği":
                fig_hata = px.bar(hata_df.head(15), x="Hata Sayısı", y="Konu", orientation="h", title="En Çok Soru Kaçırılan Konular", color="Hata Sayısı")
            else:
                fig_hata = px.pie(hata_df.head(10), names="Konu", values="Hata Sayısı", title="En Çok Soru Kaçırılan Konular (Pasta Grafik)", hole=0.3)
            st.plotly_chart(fig_hata, use_container_width=True)
        else:
            st.info("Henüz konu hatası kaydedilmedi.")
        
        if st.button("📲 Telegram'a Test Uyarı Gönder"):
            test_mesaji = f"🤖 **AKILLI KOÇ UYARISI ({st.session_state.username})**\n\n✅ Test mesajı başarıyla gönderildi!\n🎯 Çalışmalara tam gaz devam."
            if akilli_uyari_gonder(test_mesaji):
                st.success("Test bildirimi Telegram'a iletildi!")

    # 5. DERS PROGRAMI
    with tab_program:
        st.header("📅 Haftalık Ders Çalışma Programım (Görsel)")
        program_img_file = f"ders_programi_{st.session_state.user_id}.png"
        yuklenen_dosya = st.file_uploader("Ders Programı Görseli Seç", type=["png", "jpg", "jpeg"])
        if yuklenen_dosya is not None:
            with open(program_img_file, "wb") as f:
                f.write(yuklenen_dosya.getbuffer())
            st.success("Ders programı görseli başarıyla yüklendi!")
        if os.path.exists(program_img_file):
            st.image(program_img_file, caption="Yüklediğin Ders Programı", use_container_width=True)
            if st.button("🗑️ Program Görselini Kaldır"):
                os.remove(program_img_file)
                st.rerun()
        else:
            st.info("Henüz bir ders programı görseli yüklenmedi.")

    # 6. SAATLİK HATIRLATICI
    with tab_hatirlatici:
        st.header("⏰ Tarihli & Saatlik Görev Hatırlatıcı")
        col_t, col_s1, col_s2, col_s3 = st.columns([2, 2, 4, 2])
        tarih_input = col_t.date_input("Tarih", value=datetime.today())
        saat_input = col_s1.text_input("Saat (Örn: 16:00)", value="16:00")
        gorev_input = col_s2.text_input("Görev / Ders / Konu", placeholder="Örn: Trigonometri 50 Soru")
        
        if col_s3.button("➕ Hatırlatıcı Ekle"):
            if saat_input and gorev_input:
                supabase.table("hatirlaticilar").insert({
                    "user_id": st.session_state.user_id,
                    "tarih": str(tarih_input),
                    "saat": saat_input,
                    "gorev": gorev_input,
                    "durum": "Bekliyor"
                }).execute()
                
                tg_mesaj = f"⏰ **{st.session_state.username} için Yeni Hatırlatıcı!**\n\n📅 Tarih: {tarih_input}\n📌 Saat: {saat_input}\n🎯 Görev: {gorev_input}"
                akilli_uyari_gonder(tg_mesaj)
                st.success("Hatırlatıcı eklendi ve Telegram'a bildirildi!")
                st.rerun()

        st.subheader("📋 Ekli Hatırlatıcılar")
        if not df_hatirlatici.empty:
            st.dataframe(df_hatirlatici[["tarih", "saat", "gorev", "durum"]], use_container_width=True)
            if st.button("🗑️ Tüm Hatırlatıcılarımı Temizle"):
                supabase.table("hatirlaticilar").delete().eq("user_id", st.session_state.user_id).execute()
                st.rerun()
        else:
            st.info("Henüz kurulmuş bir hatırlatıcı yok.")
