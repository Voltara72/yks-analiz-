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

# Hazır YKS Konu Sözlüğü
HAZIR_KONULAR = {
    "TYT Türkçe": ["Paragraf", "Dil Bilgisi", "Yazım Kuralları", "Noktalama İşaretleri", "Sözcükte Anlam", "Cümlede Anlam", "Ses Bilgisi"],
    "TYT Matematik": ["Temel Kavramlar", "Sayı Basamakları", "Bölme-Bölünebilme", "EBOB-EKOK", "Rasyonel Sayılar", "Basit Eşitsizlikler", "Mutlak Değer", "Üslü Sayılar", "Köklü Sayılar", "Çarpanlara Ayırma", "Oran-Orantı", "Problem Türleri", "Mantar & Kümeler", "Fonksiyonlar", "Permütasyon-Kombinasyon", "Olasılık"],
    "TYT Sosyal": ["Tarih Bilimine Giriş", "İlk Türk Devletleri", "İslam Tarihi", "Osmanlı Tarihi", "Milli Mücadele", "Coğrafi Konum", "Harita Bilgisi", "İklim Bilgisi", "Nüfus ve Yerleşme", "Felsefenin Alanı", "Din Kültürü Temel Kavramlar"],
    "TYT Fen": ["Fizik Bilimine Giriş", "Madde ve Özellikleri", "Kuvvet ve Hareket", "İş Güç Enerji", "Isı ve Sıcaklık", "Elektrik ve Magnetizma", "Dalgalar", "Optik", "Kimyanın Temel Kanunları", "Atom ve Periyodik Sistem", "Kimyasal Türler Arası Etkileşim", "Maddenin Halleri", "Asitler Bazlar Tuzlar", "Canlıların Ortak Özellikleri", "Hücre", "Canlıların Sınıflandırılması", "Hücre Bölünmeleri", "Kalıtım", "Ekosistem"],
    "AYT Matematik": ["Polinomlar", "2. Dereceden Denklemler", "Karmaşık Sayılar", "Parabol", "Eşitsizlikler", "Trigonometri", "Logaritma", "Diziler", "Limit ve Süreklilik", "Türev", "İntegral", "Analitik Geometri", "Çember ve Daire", "Katı Cisimler"],
    "AYT Fizik": ["Vektörler", "Bağıl Hareket", "Newton'un Hareket Yasaları", "Bir Boyutta Sabit İvmeli Hareket", "Atışlar", "İş Güç Enerji", "İtme ve Çizgisel Momentum", "Tork ve Denge", "Basit Makineler", "Elektriksel Alan ve Potansiyel", "Kondansatörler", "Manyetizma", "Alternatif Akım", "Çembersel Hareket", "Basit Harmonik Hareket", "Dalga Mekaniği", "Modern Fizik"],
    "AYT Kimya": ["Modern Atom Teorisi", "Gazlar", "Sıvı Çözeltiler", "Kimyasal Tepkimelerde Enerji", "Tepkime Hızları", "Kimyasal Denge", "Asit-Baz Dengesi", "Çözünürlük Dengesi (KÇÇ)", "Kimya ve Elektrik", "Organik Kimyaya Giriş", "Organik Bileşikler"],
    "AYT Biyoloji": ["İnsan Fizyolojisi", "Sinir Sistemi", "Duyu Organları", "Destek ve Hareket Sistemi", "Sindirim Sistemi", "Dolaşım Sistemi", "Solunum Sistemi", "Boşaltım Sistemi", "Üreme Sistemi", "Komünite ve Popülasyon Ekolojisi", "Genden Proteine", "Canlılarda Enerji Dönüşümleri", "Bitki Biyolojisi"],
    "AYT Edebiyat": ["Metinlerin Sınıflandırılması", "Şiir Bilgisi", "Edebi Sanatlar", "İslamiyet Öncesi Türk Edebiyatı", "Halk Edebiyatı", "Divan Edebiyatı", "Tanzimat Edebiyatı", "Servet-i Fünun Edebiyatı", "Milli Edebiyat", "Cumhuriyet Dönemi Türk Edebiyatı"],
    "AYT Tarih": ["Tarih ve Zaman", "İnsanlığın İlk Dönemleri", "Orta Çağ'da Dünya", "İlk ve Orta Çağlarda Türk Dünyası", "İslam Medeniyetinin Doğuşu", "Osmanlı Devleti", "20. Yüzyıl Başlarında Osmanlı", "Milli Mücadele", "Atatürkçülük ve İnkılaplar"],
    "AYT Coğrafya": ["Ekosistem", "Nüfus Politikaları", "Türkiye'de Yerleşme ve Arazi Kullanımı", "Ekonomik Faaliyetler", "Küresel ve Bölgesel Örgütler", "Çevre ve Toplum"],
    "AYT Felsefe Grubu": ["Felsefeyi Tanıma", "Bilgi Felsefesi", "Varlık Felsefesi", "Ahlak Felsefesi", "Psikolojinin Temel Süreçleri", "Sosyolojiye Giriş", "Mantık"]
}

DERS_LISTESI = list(HAZIR_KONULAR.keys())

# ==========================================
# 2. VERİTABANI VE OTURUM YÖNETİMİ
# ==========================================
def register_user(username, password):
    try:
        check = supabase.table("users").select("*").eq("username", username).execute()
        if check.data:
            return False, "Bu kullanıcı adı zaten alınmış."
        res = supabase.table("users").insert({"username": username, "password": password}).execute()
        if res.data:
            return True, "Kullanıcı başarıyla oluşturuldu! Giriş yapabilirsiniz."
        return False, "Kullanıcı oluşturulamadı."
    except Exception as e:
        return False, f"Hata: {e}"

def login_user(username, password):
    try:
        res = supabase.table("users").select("*").eq("username", username).eq("password", password).execute()
        if res.data:
            return True, res.data[0]
        return False, None
    except Exception as e:
        return False, None

def get_denemeler(user_id):
    try:
        res = supabase.table("denemeler").select("*").eq("user_id", user_id).execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Denemeler çekilemedi: {e}")
        return pd.DataFrame()

def get_hatirlaticilar(user_id):
    try:
        res = supabase.table("hatirlaticilar").select("*").eq("user_id", user_id).execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Hatırlatıcılar çekilemedi: {e}")
        return pd.DataFrame()

# Oturum Durumu Başlatma
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None

# Giriş / Kayıt Paneli
if not st.session_state["logged_in"]:
    st.title("🎓 YKS Koçluk & Analiz Paneli")
    tab_login, tab_register = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab_login:
        st.subheader("Kullanıcı Girişi")
        l_user = st.text_input("Kullanıcı Adı", key="l_user")
        l_pass = st.text_input("Şifre", type="password", key="l_pass")
        if st.button("Giriş Yap"):
            ok, user = login_user(l_user, l_pass)
            if ok:
                st.session_state["logged_in"] = True
                st.session_state["user_info"] = user
                st.success("Giriş başarılı!")
                st.rerun()
            else:
                st.error("Hatalı kullanıcı adı veya şifre!")

    with tab_register:
        st.subheader("Yeni Hesap Oluştur")
        r_user = st.text_input("Yeni Kullanıcı Adı", key="r_user")
        r_pass = st.text_input("Yeni Şifre", type="password", key="r_pass")
        if st.button("Kayıt Ol"):
            if r_user and r_pass:
                ok, msg = register_user(r_user, r_pass)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
            else:
                st.warning("Lütfen tüm alanları doldurun.")
    st.stop()

# ==========================================
# 3. UYGULAMA İÇERİĞİ (Giriş Yapılmış)
# ==========================================
user_id = st.session_state["user_info"]["id"]
username = st.session_state["user_info"]["username"]

st.sidebar.title(f"👤 Hoş geldin, {username}!")
if st.sidebar.button("Çıkış Yap"):
    st.session_state["logged_in"] = False
    st.session_state["user_info"] = None
    st.rerun()

st.title("📈 YKS Detaylı Analiz & Takip Sistemi")

tabs = st.tabs([
    "📝 Deneme Ekle & Yönet", 
    "📊 Genel Net Grafikleri", 
    "⚠️ Konu Analizi & Akıllı Uyarı", 
    "🔔 Hatırlatıcılar & Bildirim"
])

# ------------------------------------------
# TAB 1: DENEME EKLE, DÜZENLE & SİL
# ------------------------------------------
with tabs[0]:
    st.header("📝 Deneme Kaydı ve Yönetimi")
    
    sub_tab1, sub_tab2 = st.tabs(["➕ Yeni Deneme Ekle", "⚙️ Denemeleri Düzenle & Sil"])
    
    with sub_tab1:
        st.subheader("Yeni Deneme Sınavı Ekle")
        col1, col2 = st.columns(2)
        with col1:
            tarih = st.date_input("Deneme Tarihi", datetime.now(), key="add_tarih")
            yayin = st.text_input("Yayın Adı", placeholder="Örn: 3D, Bilgi Sarmal, Özdebir", key="add_yayin")
            kayit_turu = st.selectbox("Kayıt Türü", ["TYT Genel", "AYT Genel", "Branş Denemesi"], key="add_kayit_turu")
            ders = st.selectbox("Ders", ["Genel"] + DERS_LISTESI, key="add_ders")
        with col2:
            dogru = st.number_input("Doğru Sayısı", min_value=0.0, step=1.0, key="add_dogru")
            yanlis = st.number_input("Yanlış Sayısı", min_value=0.0, step=1.0, key="add_yanlis")
            net = dogru - (yanlis * 0.25)
            st.metric("Hesaplanan Net", f"{net:.2f}")
            
            # Dinamik Konu Seçici (Hazır listeden seç veya manuel ekle)
            mevcut_konular = HAZIR_KONULAR.get(ders, [])
            secilen_konular = st.multiselect("Hatalı / Boş Bırakılan Konuları Seçin", options=mevcut_konular, key="add_konu_select")
            ek_konu = st.text_input("Listede Yoksa Manuel Ekleyin (Virgülle ayırın)", key="add_ek_konu", placeholder="Örn: Özel Konu 1, Ekstra Konu 2")

        if st.button("Denemeyi Kaydet", use_container_width=True, key="btn_add_deneme"):
            try:
                # Seçilen ve manuel yazılan konuları birleştirme
                tum_hatali = list(secilen_konular)
                if ek_konu.strip():
                    tum_hatali.extend([k.strip() for k in ek_konu.split(",") if k.strip()])
                hatali_str = ", ".join(tum_hatali)

                data = {
                    "user_id": user_id,
                    "tarih": str(tarih),
                    "yayin": yayin,
                    "kayit_turu": kayit_turu,
                    "ders": ders,
                    "dogru": dogru,
                    "yanlis": yanlis,
                    "net": net,
                    "hatali_konular": hatali_str
                }
                supabase.table("denemeler").insert(data).execute()
                st.success("Deneme başarıyla veritabanına eklendi!")
                
                # Telegram Bildirimi
                msg = f"📝 *Yeni Deneme Eklendi!*\n👤 Kullanıcı: {username}\n📅 Tarih: {tarih}\n📚 Yayın/Ders: {yayin} - {ders}\n🎯 Net: {net:.2f}\n⚠️ Hatalı Konular: {hatali_str if hatali_str else 'Yok'}"
                akilli_uyari_gonder(msg)
                st.rerun()
            except Exception as e:
                st.error(f"Deneme eklenirken hata oluştu: {e}")

    with sub_tab2:
        st.subheader("Mevcut Denemeleri Düzenle veya Sil")
        df_denemeler = get_denemeler(user_id)
        
        if df_denemeler.empty:
            st.info("Henüz eklenmiş bir deneme bulunmuyor.")
        else:
            st.dataframe(df_denemeler[["id", "tarih", "yayin", "kayit_turu", "ders", "dogru", "yanlis", "net", "hatali_konular"]], use_container_width=True)
            
            st.markdown("---")
            deneme_id_list = df_denemeler["id"].tolist()
            secilen_id = st.selectbox("İşlem Yapmak İstediğiniz Deneme ID'sini Seçin", deneme_id_list, key="select_deneme_id")
            
            secili_row = df_denemeler[df_denemeler["id"] == secilen_id].iloc[0]
            
            col_edit1, col_edit2 = st.columns(2)
            with col_edit1:
                st.markdown("### ✏️ Düzenleme Modu")
                e_tarih = st.text_input("Tarih Düzenle", value=str(secili_row["tarih"]), key=f"edit_tarih_{secilen_id}")
                e_yayin = st.text_input("Yayın Düzenle", value=str(secili_row["yayin"]), key=f"edit_yayin_{secilen_id}")
                
                kt_list = ["TYT Genel", "AYT Genel", "Branş Denemesi"]
                kt_idx = kt_list.index(secili_row["kayit_turu"]) if secili_row["kayit_turu"] in kt_list else 0
                e_kayit_turu = st.selectbox("Kayıt Türü Düzenle", kt_list, index=kt_idx, key=f"edit_kt_{secilen_id}")
                
                d_list = ["Genel"] + DERS_LISTESI
                d_idx = d_list.index(secili_row["ders"]) if secili_row["ders"] in d_list else 0
                e_ders = st.selectbox("Ders Düzenle", d_list, index=d_idx, key=f"edit_ders_{secilen_id}")
                
                e_dogru = st.number_input("Doğru Düzenle", value=float(secili_row["dogru"]), key=f"edit_dogru_{secilen_id}")
                e_yanlis = st.number_input("Yanlış Düzenle", value=float(secili_row["yanlis"]), key=f"edit_yanlis_{secilen_id}")
                e_net = e_dogru - (e_yanlis * 0.25)
                e_hatali = st.text_area("Hatalı Konular Düzenle (Virgülle ayırın)", value=str(secili_row["hatali_konular"] if secili_row["hatali_konular"] else ""), key=f"edit_hatali_{secilen_id}")
                
                if st.button("Güncellemeleri Kaydet", key=f"btn_update_{secilen_id}"):
                    try:
                        update_data = {
                            "tarih": e_tarih,
                            "yayin": e_yayin,
                            "kayit_turu": e_kayit_turu,
                            "ders": e_ders,
                            "dogru": e_dogru,
                            "yanlis": e_yanlis,
                            "net": e_net,
                            "hatali_konular": e_hatali
                        }
                        supabase.table("denemeler").update(update_data).eq("id", secilen_id).execute()
                        st.success("Deneme başarıyla güncellendi!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Güncelleme hatası: {e}")

            with col_edit2:
                st.markdown("### 🗑️ Deneme Silme")
                st.warning("Seçilen denemeyi silmek istediğinizden emin misiniz?")
                if st.button("🔴 Seçili Denemeyi Kalıcı Olarak Sil", type="primary", key=f"btn_delete_{secilen_id}"):
                    try:
                        supabase.table("denemeler").delete().eq("id", secilen_id).execute()
                        st.success("Deneme silindi!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Silme hatası: {e}")

# ------------------------------------------
# TAB 2: GENEL NET GRAFİKLERİ
# ------------------------------------------
with tabs[1]:
    st.header("📊 Net Gelişim Grafikleri")
    df_denemeler = get_denemeler(user_id)
    
    if df_denemeler.empty:
        st.info("Grafikleri görmek için önce deneme ekleyin.")
    else:
        filtre_turu = st.selectbox("Filtrele", ["Tümü", "TYT Genel", "AYT Genel", "Branş Denemesi"], key="chart_filter")
        df_filtered = df_denemeler if filtre_turu == "Tümü" else df_denemeler[df_denemeler["kayit_turu"] == filtre_turu]
        
        if not df_filtered.empty:
            fig = px.line(df_filtered, x="tarih", y="net", color="kayit_turu", hover_data=["yayin", "ders"], title="Zaman İçindeki Net Değişimi", markers=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Seçilen kategoride deneme bulunamadı.")

# ------------------------------------------
# TAB 3: KONU ANALİZİ & DERS DERS AKILLI UYARI
# ------------------------------------------
with tabs[2]:
    st.header("⚠️ Konu Analizi & Ders Ders Akıllı Uyarı")
    df_denemeler = get_denemeler(user_id)
    
    if df_denemeler.empty:
        st.info("Konu analizi yapılabilmesi için deneme eklenmiş olması gerekir.")
    else:
        secilen_analiz_dersi = st.selectbox("Analiz Etmek İstediğiniz Dersi Seçin", ["Tüm Dersler"] + DERS_LISTESI, key="konu_analiz_ders_select")
        
        if secilen_analiz_dersi == "Tüm Dersler":
            df_konu = df_denemeler
        else:
            df_konu = df_denemeler[df_denemeler["ders"] == secilen_analiz_dersi]
            
        konu_listesi = []
        for index, row in df_konu.iterrows():
            if pd.notna(row["hatali_konular"]) and str(row["hatali_konular"]).strip() != "":
                parcalar = [k.strip().title() for k in str(row["hatali_konular"]).split(",") if k.strip() != ""]
                konu_listesi.extend(parcalar)
                
        if konu_listesi:
            sıklık_df = pd.Series(konu_listesi).value_counts().reset_index()
            sıklık_df.columns = ["Konu", "Hata Frekansı"]
            
            st.subheader(f"📌 {secilen_analiz_dersi} - En Çok Yanlış Yapılan Konular")
            
            col_k1, col_k2 = st.columns([2, 1])
            with col_k1:
                fig_konu = px.bar(sıklık_df, x="Konu", y="Hata Frekansı", color="Hata Frekansı", title="En Çok Hata Yapılan Konular", text_auto=True)
                st.plotly_chart(fig_konu, use_container_width=True)
            with col_k2:
                st.dataframe(sıklık_df, use_container_width=True)
                
            # Akıllı Koçluk Uyarısı
            en_cok_hata = sıklık_df.iloc[0]
            st.error(f"🚨 **Akıllı Uyarı:** {secilen_analiz_dersi} alanında en çok sorun yaşadığın konu **'{en_cok_hata['Konu']}'** (Toplam {en_cok_hata['Hata Frekansı']} kez hata yapıldı). Bu konuyu acilen tekrar etmelisin!")
            
            if st.button("📲 Akıllı Uyarıyı Telegram'a Gönder", key="btn_send_telegram_alert"):
                mesaj = f"⚠️ *YKS Koçluk Akıllı Uyarı*\n👤 Öğrenci: {username}\n📚 Ders: {secilen_analiz_dersi}\n🚨 En Çok Hata Yapılan Konu: *{en_cok_hata['Konu']}* ({en_cok_hata['Hata Frekansı']} kez)\n📌 Öneri: Bu konudan acilen 50 soru çözülmeli ve konu tekrarı yapılmalı!"
                if akilli_uyari_gonder(mesaj):
                    st.success("Uyarı Telegram hesabına gönderildi!")
        else:
            st.success(f"🎉 {secilen_analiz_dersi} için kayıtlı herhangi bir hatalı/boş konu bulunmamaktadır.")

# ------------------------------------------
# TAB 4: HATIRLATICILAR & BİLDİRİM
# ------------------------------------------
with tabs[3]:
    st.header("🔔 Çalışma Hatırlatıcıları")
    
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.subheader("Yeni Görev / Hatırlatıcı Ekle")
        h_tarih = st.date_input("Görev Tarihi", datetime.now(), key="h_tarih")
        h_saat = st.time_input("Görev Saati", datetime.now().time(), key="h_saat")
        h_gorev = st.text_input("Çalışılacak Konu / Görev", placeholder="Örn: 2 Saat AYT Matematik İntegral Çöz", key="h_gorev_input")
        
        if st.button("Hatırlatıcı Oluştur", key="btn_add_hatirlatici"):
            if h_gorev:
                try:
                    data = {
                        "user_id": user_id,
                        "tarih": str(h_tarih),
                        "saat": str(h_saat),
                        "gorev": h_gorev,
                        "durum": "Bekliyor"
                    }
                    supabase.table("hatirlaticilar").insert(data).execute()
                    st.success("Hatırlatıcı eklendi!")
                    
                    # Telegram Bildirimi
                    msg = f"⏰ *Yeni Görev Eklendi!*\n👤 Kullanıcı: {username}\n📅 Tarih/Saat: {h_tarih} {h_saat}\n📌 Görev: {h_gorev}"
                    akilli_uyari_gonder(msg)
                    st.rerun()
                except Exception as e:
                    st.error(f"Hatırlatıcı eklenirken hata oluştu: {e}")
            else:
                st.warning("Lütfen görev açıklaması girin.")

    with col_h2:
        st.subheader("Mevcut Görevleriniz")
        df_hatirlatici = get_hatirlaticilar(user_id)
        if not df_hatirlatici.empty:
            st.dataframe(df_hatirlatici[["id", "tarih", "saat", "gorev", "durum"]], use_container_width=True)
            
            silinecek_h_id = st.selectbox("Silmek İstediğiniz Görev ID", df_hatirlatici["id"].tolist(), key="select_delete_hatirlatici")
            if st.button("Görevi Sil", key="btn_delete_hatirlatici"):
                try:
                    supabase.table("hatirlaticilar").delete().eq("id", silinecek_h_id).execute()
                    st.success("Görev silindi!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Silme hatası: {e}")
        else:
            st.info("Aktif görev bulunmuyor.")
