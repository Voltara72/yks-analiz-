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

DERS_LISTESI = [
    "TYT Türkçe", "TYT Sosyal", "TYT Matematik", "TYT Fen",
    "AYT Matematik", "AYT Fizik", "AYT Kimya", "AYT Biyoloji",
    "AYT Edebiyat", "AYT Tarih", "AYT Coğrafya", "AYT Felsefe Grubu"
]

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
            tarih = st.date_input("Deneme Tarihi", datetime.now())
            yayin = st.text_input("Yayın Adı", placeholder="Örn: 3D, Bilgi Sarmal, Özdebir")
            kayit_turu = st.selectbox("Kayıt Türü", ["TYT Genel", "AYT Genel", "Branş Denemesi"])
            ders = st.selectbox("Ders", ["Genel"] + DERS_LISTESI)
        with col2:
            dogru = st.number_input("Doğru Sayısı", min_value=0.0, step=1.0)
            yanlis = st.number_input("Yanlış Sayısı", min_value=0.0, step=1.0)
            net = dogru - (yanlis * 0.25)
            st.metric("Hesaplanan Net", f"{net:.2f}")
            hatali_konular = st.text_area("Hatalı / Boş Bırakılan Konular", placeholder="Virgülle ayırarak yazın (Örn: Üslü Sayılar, Paragraf, Optik)")

        if st.button("Denemeyi Kaydet", use_container_width=True):
            try:
                data = {
                    "user_id": user_id,
                    "tarih": str(tarih),
                    "yayin": yayin,
                    "kayit_turu": kayit_turu,
                    "ders": ders,
                    "dogru": dogru,
                    "yanlis": yanlis,
                    "net": net,
                    "hatali_konular": hatali_konular
                }
                supabase.table("denemeler").insert(data).execute()
                st.success("Deneme başarıyla veritabanına eklendi!")
                
                # Telegram Bildirimi
                msg = f"📝 *Yeni Deneme Eklendi!*\n👤 Kullanıcı: {username}\n📅 Tarih: {tarih}\n📚 Yayın/Ders: {yayin} - {ders}\n🎯 Net: {net:.2f}"
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
            secilen_id = st.selectbox("İşlem Yapmak İstediğiniz Deneme ID'sini Seçin", deneme_id_list)
            
            secili_row = df_denemeler[df_denemeler["id"] == secilen_id].iloc[0]
            
            col_edit1, col_edit2 = st.columns(2)
            with col_edit1:
                st.markdown("### ✏️ Düzenleme Modu")
                e_tarih = st.text_input("Tarih", value=str(secili_row["tarih"]))
                e_yayin = st.text_input("Yayın", value=str(secili_row["yayin"]))
                e_kayit_turu = st.selectbox("Kayıt Türü", ["TYT Genel", "AYT Genel", "Branş Denemesi"], index=["TYT Genel", "AYT Genel", "Branş Denemesi"].index(secili_row["kayit_turu"]) if secili_row["kayit_turu"] in ["TYT Genel", "AYT Genel", "Branş Denemesi"] else 0)
                e_ders = st.selectbox("Ders", ["Genel"] + DERS_LISTESI, index=(["Genel"] + DERS_LISTESI).index(secili_row["ders"]) if secili_row["ders"] in (["Genel"] + DERS_LISTESI) else 0)
                e_dogru = st.number_input("Doğru", value=float(secili_row["dogru"]))
                e_yanlis = st.number_input("Yanlış", value=float(secili_row["yanlis"]))
                e_net = e_dogru - (e_yanlis * 0.25)
                e_hatali = st.text_area("Hatalı Konular", value=str(secili_row["hatali_konular"] if secili_row["hatali_konular"] else ""))
                
                if st.button("Güncellemeleri Kaydet"):
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
                if st.button("🔴 Seçili Denemeyi Kalıcı Olarak Sil", type="primary"):
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
        filtre_turu = st.selectbox("Filtrele", ["Tümü", "TYT Genel", "AYT Genel", "Branş Denemesi"])
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
        # DERS SEÇME KISMI
        secilen_analiz_dersi = st.selectbox("Analiz Etmek İstediğiniz Dersi Seçin", ["Tüm Dersler"] + DERS_LISTESI)
        
        if secilen_analiz_dersi == "Tüm Dersler":
            df_konu = df_denemeler
        else:
            df_konu = df_denemeler[df_denemeler["ders"] == secilen_analiz_dersi]
            
        konu_listesi = []
        for index, row in df_konu.iterrows():
            if pd.notna(row["hatali_konular"]) and row["hatali_konular"].strip() != "":
                parcalar = [k.strip().title() for k in row["hatali_konular"].split(",") if k.strip() != ""]
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
            
            if st.button("📲 Akıllı Uyarıyı Telegram'a Gönder"):
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
        h_gorev = st.text_input("Çalışılacak Konu / Görev", placeholder="Örn: 2 Saat AYT Matematik İntegral Çöz")
        
        if st.button("Hatırlatıcı Oluştur"):
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
            
            silinecek_h_id = st.selectbox("Silmek İstediğiniz Görev ID", df_hatirlatici["id"].tolist())
            if st.button("Görevi Sil"):
                try:
                    supabase.table("hatirlaticilar").delete().eq("id", silinecek_h_id).execute()
                    st.success("Görev silindi!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Silme hatası: {e}")
        else:
            st.info("Aktif görev bulunmuyor.")
