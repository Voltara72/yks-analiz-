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
# GENİŞLETİLMİŞ DETAYLI YKS KONU LİSTESİ
# ==========================================
HAZIR_KONULAR = {
    "TYT Türkçe": [
        "Sözcükte Anlam", "Cümlede Anlam", "Paragrafta Anlam", "Paragrafta Yapı", "Paragrafta Ana Fikir", 
        "Ses Bilgisi", "Yazım Kuralları", "Noktalama İşaretleri", "Sözcük Türleri (İsim, Sıfat, Zamir)", 
        "Fiiller ve Fiilimsiler", "Cümlenin Ögeleri", "Cümle Türleri", "Anlatım Bozuklukları"
    ],
    "TYT Matematik": [
        "Temel Kavramlar", "Sayı Basamakları", "Bölme ve Bölünebilme", "EBOB - EKOK", "Rasyonel Sayılar", 
        "Basit Eşitsizlikler", "Mutlak Değer", "Üslü İfadeler", "Köklü İfadeler", "Çarpanlara Ayırma", 
        "Oran - Orantı", "Denklem Çözme", "Sayı-Kesir Problemleri", "Yaş Problemleri", "Yüzde-Kâr-Zarar Problemleri", 
        "Karışım Problemleri", "Hız-Hareket Problemleri", "İşçi-Havuz Problemleri", "Kümeler ve Mantık", 
        "Fonksiyonlar", "Permütasyon - Kombinasyon", "Olasılık", "İstatistik ve Veri"
    ],
    "TYT Geometri": [
        "Geometrik Kavramlar ve Doğruda Açılar", "Üçgende Açılar", "Dik Üçgen ve Özel Üçgenler", 
        "İkizkenar ve Eşkenar Üçgen", "Üçgende Alan", "Üçgende Benzerlik", "Açıortay ve Kenarortay", 
        "Çokgenler", "Paralelkenar ve Eşkenar Dörtgen", "Dikdörtgen ve Kare", "Yamuk ve Deltoid", 
        "Çember ve Daire", "Katı Cisimler (Prizma, Piramit, Küre)"
    ],
    "TYT Fizik": [
        "Fizik Bilimine Giriş", "Madde ve Özellikleri", "Kuvvet ve Hareket", "İş, Güç ve Enerji", 
        "Isı, Sıcaklık ve Genleşme", "Basınç ve Kaldırma Kuvveti", "Elektrostatik", "Elektrik ve Manyetizma", 
        "Dalgalar", "Optik (Yansıma, Kırılma, Mercekler)"
    ],
    "TYT Kimya": [
        "Kimya Bilimi", "Atom ve Periyodik Sistem", "Kimyasal Türler Arası Etkileşimler", 
        "Maddenin Halleri", "Doğa ve Kimya", "Kimyanın Temel Kanunları", "Mol Kavramı", 
        "Tepkime Türleri ve Hesaplamalar", "Karışımlar", "Asitler, Bazlar ve Tuzlar", "Kimya Her Yerde"
    ],
    "TYT Biyoloji": [
        "Canlıların Ortak Özellikleri", "Canlıların Temel Bileşikleri", "Hücre ve Organeller", 
        "Hücre Zarlarından Madde Geçişi", "Canlıların Sınıflandırılması", "Hücre Bölünmeleri (Mitoz & Mayoz)", 
        "Kalıtım İlkeleri", "Ekosistem Ekolojisi ve Güncel Çevre Sorunları"
    ],
    "TYT Tarih": [
        "Tarih Bilimi", "İlk Çağ Uygarlıkları", "Türk Dünya Tarihi", "İslam Medeniyetinin Doğuşu", 
        "İlk Türk-İslam Devletleri", "Osmanlı Devleti Kuruluş ve Yükselme", "Osmanlı Kültür ve Medeniyeti", 
        "20. Yüzyıl Başlarında Osmanlı", "Milli Mücadele Hazırlık ve Cepheler", "Atatürkçülük ve İnkılaplar"
    ],
    "TYT Coğrafya": [
        "Doğa ve İnsan", "Dünyanın Şekli ve Hareketleri", "Coğrafi Konum", "Harita Bilgisi", 
        "Atmosfer ve İklim", "Yerin Şekillenmesi (İç ve Dış Kuvvetler)", "Nüfus ve Yerleşme", 
        "Türkiye'nin Fiziki Özellikleri", "Doğal Afetler"
    ],
    "TYT Felsefe": [
        "Felsefeyi Tanıma", "Bilgi Felsefesi (Epistemoloji)", "Varlık Felsefesi (Ontoloji)", 
        "Ahlak Felsefesi (Etik)", "Sanat Felsefesi", "Din Felsefesi", "Siyaset Felsefesi", "Bilim Felsefesi"
    ],
    "TYT Din Kültürü": [
        "Bilgi ve İnanç", "İbadet", "Ahlak ve Değerler", "Allah İnsan İlişkisi", 
        "Hz. Muhammed (S.A.V.)", "Vahiy ve Akıl", "İslam ve Bilim", "Anadolu'da İslam"
    ],
    "AYT Matematik": [
        "Polinomlar", "İkinci Dereceden Denklemler", "Karmaşık Sayılar", "Parabol", 
        "Eşitsizlikler", "Trigonometri", "Logaritma", "Diziler", 
        "Limit ve Süreklilik", "Türev ve Uygulamaları", "İntegral ve Uygulamaları"
    ],
    "AYT Geometri": [
        "Doğrunun Analitik İncelenmesi", "Çemberin Analitik İncelenmesi", "Dönüşüm Geometrisi", 
        "Çember ve Daire", "Uzay Geometri ve Katı Cisimler"
    ],
    "AYT Fizik": [
        "Vektörler ve Bağıl Hareket", "Newton'un Hareket Yasaları", "Atışlar", "İş, Güç, Enerji", 
        "İtme ve Momentum", "Tork, Denge ve Kütle Merkezi", "Basit Makineler", "Elektriksel Kuvvet ve Potansiyel", 
        "Kondansatörler", "Manyetizma ve Elektromanyetik İndükleme", "Alternatif Akım ve Transformatörler", 
        "Düzgün Çembersel Hareket", "Basit Harmonik Hareket", "Dalga Mekaniği (Girişim)", "Atom Fiziği ve Modern Fizik"
    ],
    "AYT Kimya": [
        "Modern Atom Teorisi ve Periyodik Sistem", "Gazlar", "Sıvı Çözeltiler ve Çözünürlük", 
        "Kimyasal Tepkimelerde Enerji", "Tepkime Hızları", "Kimyasal Denge", "Asit-Baz Dengesi", 
        "Çözünürlük Dengesi (KÇÇ)", "Kimya ve Elektrik (Redoks, Piller, Elektroliz)", "Organik Kimyaya Giriş", "Organik Bileşikler"
    ],
    "AYT Biyoloji": [
        "Sinir Sistemi", "Duyu Organları", "Endokrin Sistem", "Destek ve Hareket Sistemi", 
        "Sindirim Sistemi", "Dolaşım ve Bağışıklık Sistemi", "Solunum Sistemi", "Boşaltım Sistemi", 
        "Üreme Sistemi ve Gelişme", "Komünite ve Popülasyon Ekolojisi", "Genden Proteine (Nükleik Asitler & Protein Sentezi)", 
        "Canlılarda Enerji Dönüşümleri (Fotosentez, Kemosentez, Hücresel Solunum)", "Bitki Biyolojisi"
    ],
    "AYT Edebiyat": [
        "Güzel Sanatlar ve Edebiyat", "Metinlerin Sınıflandırılması", "Şiir Bilgisi ve Edebi Sanatlar", 
        "İslamiyet Öncesi ve Geçiş Dönemi Türk Edebiyatı", "Halk Edebiyatı", "Divan Edebiyatı", 
        "Tanzimat Edebiyatı", "Servet-i Fünun ve Fecr-i Ati Edebiyatı", "Milli Edebiyat", "Cumhuriyet Dönemi Edebiyatı", "Edebi Akımlar"
    ],
    "AYT Tarih 1 - 2": [
        "Tarih ve Zaman", "İnsanlığın İlk Dönemleri", "Orta Çağ'da Dünya", "İlk ve Orta Çağlarda Türk Dünyası", 
        "İslam Medeniyetinin Doğuşu", "Türklerin İslamiyet'i Kabulü", "Yerleşme ve Devletleşme Sürecinde Selçuklu", 
        "Osmanlı Siyaseti ve Beylikten Devlete", "Dünya Gücü Osmanlı", "20. Yüzyıl Başlarında Osmanlı", 
        "Milli Mücadele", "Atatürkçülük ve İnkılaplar", "İki Dünya Savaşı Arasındaki Dönem", "Soğuk Savaş Dönemi ve Küreselleşen Dünya"
    ],
    "AYT Coğrafya 1 - 2": [
        "Ekosistem ve Madde Döngüleri", "Şehirler ve Etki Alanları", "Türkiye'de Ekonomi ve Sektörler", 
        "Küresel Ticaret ve Turizm", "Türkiye'nin Jeopolitik Konumu", "Bölgesel Kalkınma Projeleri", 
        "Küresel ve Bölgesel Örgütler", "Çevre Sorunları ve Sürdürülebilirlik"
    ],
    "AYT Felsefe Grubu": [
        "Psikolojinin Temel Süreçleri", "Öğrenme, Bellek ve Düşünme", "Ruh Sağlığı", 
        "Sosyolojiye Giriş ve Toplumsal Yapı", "Toplumsal Değişme ve Kültür", "Toplumsal Kurumlar", 
        "Mantığa Giriş", "Klasik Mantık (Kavram, Önerme, Çıkarım)", "Sembolik Mantık"
    ],
    "YDT İngilizce": [
        "Grammar / Dilbilgisi", "Vocabulary / Kelime Bilgisi", "Cloze Test", "Sentence Completion / Cümle Tamamlama", 
        "Reading Comprehension / Paragraf", "Dialogue Completion / Diyalog", "Restatement / Yakın Anlam", 
        "Paragraph Completion / Paragraf Tamamlama", "Irrelevant Sentence / Akışı Bozan Cümle", "Translation / Çeviri"
    ]
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
            
            # Ders Seçici
            ders_secim_listesi = ["Genel / Tüm Dersler"] + DERS_LISTESI
            ders = st.selectbox("Ders Seçin", ders_secim_listesi, key="add_ders")

        with col2:
            dogru = st.number_input("Doğru Sayısı", min_value=0.0, step=1.0, key="add_dogru")
            yanlis = st.number_input("Yanlış Sayısı", min_value=0.0, step=1.0, key="add_yanlis")
            net = dogru - (yanlis * 0.25)
            st.metric("Hesaplanan Net", f"{net:.2f}")
            
            # Dinamik Konu Listesi Filtreleme
            if ders in HAZIR_KONULAR:
                secilen_ders_konulari = HAZIR_KONULAR[ders]
            else:
                # Tüm konuları birleştirip göster (Genel denemeler için)
                tum_konular_listesi = []
                for konuliste in HAZIR_KONULAR.values():
                    tum_konular_listesi.extend(konuliste)
                secilen_ders_konulari = list(set(tum_konular_listesi))
            
            secilen_konular = st.multiselect(
                "Hazır Listeden Hatalı/Boş Konuları Seçin", 
                options=secilen_ders_konulari, 
                key=f"add_konu_select_{ders}"
            )
            ek_konu = st.text_input("Diğer / Manuel Eklemek İstediğiniz Konular (Virgülle ayırın)", key="add_ek_konu", placeholder="Örn: Paragraf, Optik")

        if st.button("Denemeyi Kaydet", use_container_width=True, key="btn_add_deneme"):
            try:
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
                
                d_list = ["Genel / Tüm Dersler"] + DERS_LISTESI
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
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtre_turu = st.selectbox("Kayıt Türüne Göre Filtrele", ["Tümü", "TYT Genel", "AYT Genel", "Branş Denemesi"], key="chart_filter_turu")
        with col_f2:
            filtre_ders = st.selectbox("Derse Göre Filtrele", ["Tüm Dersler"] + DERS_LISTESI, key="chart_filter_ders")
        
        df_filtered = df_denemeler.copy()
        if filtre_turu != "Tümü":
            df_filtered = df_filtered[df_filtered["kayit_turu"] == filtre_turu]
        if filtre_ders != "Tüm Dersler":
            df_filtered = df_filtered[df_filtered["ders"] == filtre_ders]
        
        if not df_filtered.empty:
            fig = px.line(df_filtered, x="tarih", y="net", color="kayit_turu", hover_data=["yayin", "ders"], title="Zaman İçindeki Net Değişimi", markers=True)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df_filtered[["tarih", "yayin", "kayit_turu", "ders", "dogru", "yanlis", "net"]], use_container_width=True)
        else:
            st.warning("Seçilen filtrelerde deneme bulunamadı.")

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
