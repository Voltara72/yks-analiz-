from datetime import datetime
import os
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# ==========================================
# TELEGRAM BOT VE KULLANICI BİLGİLERİ
# ==========================================
TELEGRAM_BOT_TOKEN = "8783937056:AAFtpytdK_hnNRfsRi0DB4V4cOqD0P1EAn0"
TELEGRAM_CHAT_ID = "6250328228"


def akilli_uyari_gonder(mesaj: str) -> bool:
  """Telegram üzerinden anlık akıllı uyarı / bildirim gönderir."""
  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
  payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mesaj, "parse_mode": "Markdown"}
  try:
    response = requests.post(url, json=payload, timeout=5)
    return response.status_code == 200
  except Exception as e:
    st.error(f"Bildirim gönderilemedi: {e}")
    return False


st.set_page_config(page_title="YKS Detaylı Analiz & Koçluk Paneli", layout="wide")

# KONU LİSTESİ
KONULAR = {
    "Türkçe": [
        "Sözcükte Anlam & Yorum",
        "Cümlede Anlam & Yorum",
        "Paragrafta Ana Fikir & Yardımcı Fikirler",
        "Paragrafta Yapı & Anlatım Teknikleri",
        "Ses Bilgisi",
        "Yazım Kuralları",
        "Noktalama İşaretleri",
        "Sözcük Türleri (İsim, Sıfat, Zamir)",
        "Zarf, Edat, Bağlaç, Ünlem",
        "Fiiller & Fiilde Çatı",
        "Cümlenin Ögeleri",
        "Cümle Türleri",
        "Anlatım Bozuklukları",
    ],
    "Matematik": [
        "Temel Kavramlar & Sayı Kümeleri",
        "Bölme & Bölünebilme Kuralları",
        "EBOB - EKOK",
        "Birinci Dereceden Denklem ve Eşitsizlikler",
        "Mutlak Değer",
        "Üslü & Köklü İfadeler",
        "Çarpanlara Ayırma",
        "Oran - Orantı",
        "Sayı & Kesir Problemleri",
        "Yaş Problemleri",
        "Yüzde, Kar-Zarar & Faiz Problemleri",
        "Karışım Problemleri",
        "Hareket Problemleri",
        "İşçi & Havuz Problemleri",
        "Rutin Olmayan Problemler",
        "Kümeler & Mantık",
        "Fonksiyonlar (Temel & Grafikler)",
        "Polinomlar",
        "İkinci Dereceden Denklemler",
        "Karmaşık Sayılar",
        "Parabol",
        "Eşitsizlikler",
        "Trigonometri",
        "Permütasyon & Kombinasyon",
        "Olasılık",
        "Logaritma",
        "Diziler & Seriler",
        "Limit & Süreklilik",
        "Türev & Uygulamaları",
        "İntegral & Alan",
    ],
    "Geometri": [
        "Doğruda & Üçgende Açılar",
        "Özel Üçgenler (Dik, İkizkenar, Eşkenar)",
        "Üçgende Alan & Açıortay/Kenarortay",
        "Üçgende Benzerlik",
        "Çokgenler & Dörtgenler",
        "Yamuk & Paralelkenar",
        "Eşkenar Dörtgen & Deltoid",
        "Dikdörtgen & Kare",
        "Çemberde Açı & Uzunluk",
        "Dairede Çevre ve Alan",
        "Analitik Geometri",
        "Katı Cisimler (Prizma, Piramit, Küre)",
        "Çemberin Analitiği",
    ],
    "Fizik": [
        "Fizik Bilimine Giriş & Madde Özellikleri",
        "Vektörler & Tork / Denge",
        "Kütle Merkezi & Basit Makineler",
        "Hareket & Dinamik",
        "İş, Güç ve Enerji",
        "Atışlar",
        "İtme ve Momentum",
        "Basınç & Kaldırma Kuvveti",
        "Isı, Sıcaklık & Genleşme",
        "Elektrostatik & Elektrik Akımı",
        "Mıknatıs & Manyetizma",
        "Alternatif Akım & Transformatörler",
        "Çembersel Hareket & Kepler",
        "Basit Harmonik Hareket",
        "Dalgalar & Optik",
        "Modern Fizik",
    ],
    "Kimya": [
        "Kimya Bilimi & Atomun Yapısı",
        "Periyodik Sistem",
        "Kimyasal Türler Arası Etkileşimler",
        "Maddenin Halleri & Gazlar",
        "Mol Kavramı & Kimyasal Hesaplamalar",
        "Çözeltiler & Çözünürlük",
        "Kimya ve Enerji",
        "Tepkime Hızları & Kimyasal Denge",
        "Asitler, Bazlar ve Tuzlar",
        "Çözünürlük Dengesi (KÇÇ)",
        "Kimya ve Elektrik",
        "Organik Kimyaya Giriş",
        "Hidrokarbonlar",
    ],
    "Biyoloji": [
        "Yaşam Bilimi Biyoloji & Hücre",
        "Canlıların Sınıflandırılması",
        "Hücre Bölünmeleri & Üreme",
        "Kalıtım & Ekosistem Ekolojisi",
        "Hücresel Solunum & Fotosentez",
        "İnsan Fizyolojisi (Sistemler)",
        "Nükleik Asitler & Protein Sentezi",
        "Biyoteknoloji",
    ],
    "Tarih": [
        "Tarih Bilimi & İlk Çağ Uygarlıkları",
        "İslam Öncesi & İslam Tarihi",
        "İlk Türk-İslam Devletleri",
        "Osmanlı Devleti Kuruluş & Yükselme",
        "Osmanlı Kültür ve Medeniyeti",
        "20. Yüzyıl Başlarında Osmanlı",
        "Milli Mücadele Dönemi & İnkılaplar",
        "Atatürkçülük",
    ],
    "Coğrafya": [
        "Doğa ve İnsan & Harita Bilgisi",
        "Dünyanın Şekli ve Hareketleri",
        "Coğrafi Konum & İklim Bilgisi",
        "Yerin Şekillenmesi",
        "Nüfus ve Yerleşme",
        "Türkiye'nin Fiziki & Beşeri Özellikleri",
        "Küresel Ortam",
        "Çevre ve Toplum",
    ],
    "Felsefe & Din": [
        "Felsefeyi Tanıma & Bilgi Felsefesi",
        "Varlık & Ahlak Felsefesi",
        "Sanat, Din & Siyaset Felsefesi",
        "15.-17. Yüzyıl Felsefesi",
        "Kur'an-ı Kerim ve Temel Kavramlar",
        "Hz. Muhammed'in Hayatı & Ahlakı",
        "İslam Düşüncesinde Yorumlar",
    ],
}

DATA_FILE = "deneme_verileri.csv"
REMINDER_FILE = "hatirlaticilar.csv"
PROGRAM_IMG_FILE = "ders_programi.png"


def verileri_yukle():
  if os.path.exists(DATA_FILE):
    return pd.read_csv(DATA_FILE)
  return pd.DataFrame(columns=[
      "Tarih",
      "Yayın/Deneme Adı",
      "Kayıt Türü",
      "Ders",
      "Doğru",
      "Yanlış",
      "Net",
      "Hatalı Konular",
  ])


def hatirlaticilari_yukle():
  if os.path.exists(REMINDER_FILE):
    return pd.read_csv(REMINDER_FILE)
  return pd.DataFrame(columns=["Tarih", "Saat", "Görev / Ders", "Durum"])


df_veriler = verileri_yukle()
df_hatirlatici = hatirlaticilari_yukle()

st.title("🎓 YKS Detaylı Analiz & Akıllı Koçluk Paneli")

# SOL MENÜ - VERİ GİRİŞİ
with st.sidebar:
  st.header("📝 Yeni Deneme Ekle")
  tarih = st.date_input("Deneme Tarihi")
  yayin = st.text_input(
      "Yayın / Deneme Adı", placeholder="Örn: 3D Türkiye Geneli 1"
  )
  kayit_turu = st.radio(
      "Kayıt Türü Seçin",
      ["Genel TYT Denemesi", "Genel AYT Denemesi", "Tek Branş Denemesi"],
  )

  yeni_kayitlar = []

  if kayit_turu == "Genel TYT Denemesi":
    st.subheader("📚 Toplu TYT Netleri")
    tyt_dersler = [
        "Türkçe",
        "Matematik",
        "Geometri",
        "Fizik",
        "Kimya",
        "Biyoloji",
        "Tarih",
        "Coğrafya",
        "Felsefe & Din",
    ]
    for ders in tyt_dersler:
      with st.expander(f"📌 {ders}"):
        c1, c2 = st.columns(2)
        d = c1.number_input(
            f"{ders} D", min_value=0, max_value=40, value=0, key=f"d_{ders}"
        )
        y = c2.number_input(
            f"{ders} Y", min_value=0, max_value=40, value=0, key=f"y_{ders}"
        )
        net = d - (y * 0.25)
        hatalar = st.multiselect(
            f"{ders} Eksik Konular", KONULAR.get(ders, []), key=f"h_{ders}"
        )
        if d > 0 or y > 0:
          yeni_kayitlar.append({
              "Tarih": tarih,
              "Yayın/Deneme Adı": yayin,
              "Kayıt Türü": "Genel TYT Denemesi",
              "Ders": ders,
              "Doğru": d,
              "Yanlış": y,
              "Net": net,
              "Hatalı Konular": ", ".join(hatalar),
          })

  elif kayit_turu == "Genel AYT Denemesi":
    st.subheader("📚 Toplu AYT Netleri")
    ayt_dersler = [
        "Matematik",
        "Geometri",
        "Fizik",
        "Kimya",
        "Biyoloji",
        "Tarih",
        "Coğrafya",
        "Felsefe & Din",
    ]
    for ders in ayt_dersler:
      with st.expander(f"📌 AYT {ders}"):
        c1, c2 = st.columns(2)
        d = c1.number_input(
            f"AYT {ders} D",
            min_value=0,
            max_value=40,
            value=0,
            key=f"d_ayt_{ders}",
        )
        y = c2.number_input(
            f"AYT {ders} Y",
            min_value=0,
            max_value=40,
            value=0,
            key=f"y_ayt_{ders}",
        )
        net = d - (y * 0.25)
        hatalar = st.multiselect(
            f"AYT {ders} Eksik Konular",
            KONULAR.get(ders, []),
            key=f"h_ayt_{ders}",
        )
        if d > 0 or y > 0:
          yeni_kayitlar.append({
              "Tarih": tarih,
              "Yayın/Deneme Adı": yayin,
              "Kayıt Türü": "Genel AYT Denemesi",
              "Ders": ders,
              "Doğru": d,
              "Yanlış": y,
              "Net": net,
              "Hatalı Konular": ", ".join(hatalar),
          })

  else:
    st.subheader("🎯 Tek Branş Denemesi")
    secilen_ders = st.selectbox("Ders Seçin", list(KONULAR.keys()))
    c1, c2 = st.columns(2)
    d = c1.number_input("Doğru", min_value=0, max_value=40, value=0)
    y = c2.number_input("Yanlış", min_value=0, max_value=40, value=0)
    net = d - (y * 0.25)

    # Matematik seçilirse Geometri konuları da listeye dahil edilsin
    secilen_konular_listesi = KONULAR[secilen_ders]
    if secilen_ders == "Matematik":
      secilen_konular_listesi = (
          KONULAR["Matematik"] + KONULAR["Geometri"]
      )  # Matematik + Geometri birleşti

    hatalar = st.multiselect("Eksik Konular", secilen_konular_listesi)
    if d > 0 or y > 0:
      yeni_kayitlar.append({
          "Tarih": tarih,
          "Yayın/Deneme Adı": yayin,
          "Kayıt Türü": "Tek Branş Denemesi",
          "Ders": secilen_ders,
          "Doğru": d,
          "Yanlış": y,
          "Net": net,
          "Hatalı Konular": ", ".join(hatalar),
      })

  if st.button("💾 Denemeyi Kaydet ve Telegram'a Bildir"):
    if yayin and yeni_kayitlar:
      yeni_df = pd.DataFrame(yeni_kayitlar)
      df_veriler = pd.concat([df_veriler, yeni_df], ignore_index=True)
      df_veriler.to_csv(DATA_FILE, index=False)

      toplam_eklenen_net = sum([item["Net"] for item in yeni_kayitlar])
      telegram_mesaj = (
          f"🚀 **Yeni Deneme Kaydedildi!**\n\n📌 Yayın: {yayin}\n📋 Tür:"
          f" {kayit_turu}\n📊 Toplam Net: *{toplam_eklenen_net:.2f}*\n\n💪"
          " Çalışmalara tam gaz devam!"
      )
      akilli_uyari_gonder(telegram_mesaj)

      st.success("Deneme kaydedildi ve Telegram'a bildirildi!")
      st.rerun()

# ANA SEKMELER
tab_tyt, tab_ayt, tab_brans, tab_konu, tab_program, tab_hatirlatici = (
    st.tabs([
        "📊 TYT Analizi",
        "📈 AYT Analizi",
        "🎯 Branş Analizi",
        "⚠️ Konu & Akıllı Uyarı",
        "📅 Ders Programım",
        "⏰ Saatlik Hatırlatıcı",
    ])
)

# 1. TYT ANALİZİ
with tab_tyt:
  st.header("📊 Genel TYT Deneme Analizi")
  tyt_df = df_veriler[df_veriler["Kayıt Türü"] == "Genel TYT Denemesi"]
  if not tyt_df.empty:
    toplam_tyt = (
        tyt_df.groupby(["Tarih", "Yayın/Deneme Adı"])["Net"].sum().reset_index()
    )
    fig = px.line(
        toplam_tyt,
        x="Tarih",
        y="Net",
        text="Net",
        hover_data=["Yayın/Deneme Adı"],
        title="TYT Toplam Net Gelişimi",
        markers=True,
    )
    st.plotly_chart(fig, use_container_width=True)
  else:
    st.info("Henüz TYT denemesi eklenmedi.")

# 2. AYT ANALİZİ
with tab_ayt:
  st.header("📈 Genel AYT Deneme Analizi")
  ayt_df = df_veriler[df_veriler["Kayıt Türü"] == "Genel AYT Denemesi"]
  if not ayt_df.empty:
    toplam_ayt = (
        ayt_df.groupby(["Tarih", "Yayın/Deneme Adı"])["Net"].sum().reset_index()
    )
    fig_ayt = px.line(
        toplam_ayt,
        x="Tarih",
        y="Net",
        text="Net",
        hover_data=["Yayın/Deneme Adı"],
        title="AYT Toplam Net Gelişimi",
        markers=True,
    )
    st.plotly_chart(fig_ayt, use_container_width=True)
  else:
    st.info("Henüz AYT denemesi eklenmedi.")

# 3. BRANŞ ANALİZİ
with tab_brans:
  st.header("🎯 Branş Bazlı İlerleme")
  secilen_brans = st.selectbox(
      "Analiz Edilecek Dersi Seçin", list(KONULAR.keys())
  )
  brans_df = df_veriler[df_veriler["Ders"] == secilen_brans]
  if not brans_df.empty:
    fig_brans = px.line(
        brans_df,
        x="Tarih",
        y="Net",
        color="Kayıt Türü",
        hover_data=["Yayın/Deneme Adı"],
        title=f"{secilen_brans} Net Gelişimi",
        markers=True,
    )
    st.plotly_chart(fig_brans, use_container_width=True)
  else:
    st.info(f"Henüz {secilen_brans} branşına ait veri girilmedi.")

# 4. AKILLI UYARI VE KONU ANALİZİ
with tab_konu:
  st.header("⚠️ Akıllı Koçluk Uyarısı & Hatalı Konular")
  tum_hatalar = []
  for hatalar in df_veriler["Hatalı Konular"].dropna():
    if hatalar:
      tum_hatalar.extend([h.strip() for h in hatalar.split(",") if h.strip()])

  if tum_hatalar:
    hata_df = pd.Series(tum_hatalar).value_counts().reset_index()
    hata_df.columns = ["Konu", "Hata Sayısı"]

    kritik_konular = hata_df[hata_df["Hata Sayısı"] >= 2]
    if not kritik_konular.empty:
      st.error(
          "🚨 **AKILLI KOÇ UYARISI:** Aşağıdaki konularda üst üste hatalar"
          " yapıyorsunuz!"
      )
      for _, row in kritik_konular.iterrows():
        st.warning(f"👉 {row['Konu']}: Toplam {row['Hata Sayısı']} kez yanlış!")

    fig_hata = px.bar(
        hata_df.head(15),
        x="Hata Sayısı",
        y="Konu",
        orientation="h",
        title="En Çok Soru Kaçırılan Konular",
        color="Hata Sayısı",
    )
    st.plotly_chart(fig_hata, use_container_width=True)
  else:
    st.info("Henüz konu hatası kaydedilmedi.")

  if st.button("📲 Telegram'a Test Uyarı Gönder"):
    test_mesaji = (
        "🤖 **AKILLI KOÇ UYARISI**\n\n✅ Test mesajı başarıyla"
        " gönderildi!\n🎯 Çalışmalara tam gaz devam."
    )
    if akilli_uyari_gonder(test_mesaji):
      st.success("Test bildirimi Telegram'a iletildi!")

# 5. DERS PROGRAMI (RESİM YÜKLEME)
with tab_program:
  st.header("📅 Haftalık Ders Çalışma Programım (Görsel)")
  st.write("Galerinden ders programı fotoğrafını (PNG/JPG) yükleyebilirsin:")

  yuklenen_dosya = st.file_uploader(
      "Ders Programı Görseli Seç", type=["png", "jpg", "jpeg"]
  )

  if yuklenen_dosya is not None:
    with open(PROGRAM_IMG_FILE, "wb") as f:
      f.write(yuklenen_dosya.getbuffer())
    st.success("Ders programı görseli başarıyla yüklendi!")

  if os.path.exists(PROGRAM_IMG_FILE):
    st.image(
        PROGRAM_IMG_FILE,
        caption="Yüklediğin Ders Programı",
        use_container_width=True,
    )
    if st.button("🗑️ Program Görselini Kaldır"):
      os.remove(PROGRAM_IMG_FILE)
      st.rerun()
  else:
    st.info(
        "Henüz bir ders programı görseli yüklenmedi. Yukarıdan dosya seçip"
        " ekleyebilirsin."
    )

# 6. SAATLİK HATIRLATICI / BİLDİRİM SİSTEMİ
with tab_hatirlatici:
  st.header("⏰ Tarihli & Saatlik Görev Hatırlatıcı")
  st.write(
      "İstediğin tarihe ve saate özel hatırlatıcılar kur (Kurduğun an"
      " Telegram'a gelecektir):"
  )

  col_t, col_s1, col_s2, col_s3 = st.columns([2, 2, 4, 2])
  tarih_input = col_t.date_input("Tarih", value=datetime.today())
  saat_input = col_s1.text_input("Saat (Örn: 16:00)", value="16:00")
  gorev_input = col_s2.text_input(
      "Görev / Ders / Konu", placeholder="Örn: Trigonometri 50 Soru"
  )

  if col_s3.button("➕ Hatırlatıcı Ekle"):
    if saat_input and gorev_input:
      yeni_h = pd.DataFrame([{
          "Tarih": str(tarih_input),
          "Saat": saat_input,
          "Görev / Ders": gorev_input,
          "Durum": "Bekliyor",
      }])
      df_hatirlatici = pd.concat([df_hatirlatici, yeni_h], ignore_index=True)
      df_hatirlatici.to_csv(REMINDER_FILE, index=False)

      tg_mesaj = (
          f"⏰ **Yeni Hatırlatıcı Kuruldu!**\n\n📅 Tarih:"
          f" {tarih_input}\n📌 Saat: {saat_input}\n🎯 Görev: {gorev_input}"
      )
      akilli_uyari_gonder(tg_mesaj)

      st.success("Hatırlatıcı eklendi ve Telegram'a bildirildi!")
      st.rerun()

  st.subheader("📋 Ekli Hatırlatıcılar")
  if not df_hatirlatici.empty:
    st.dataframe(df_hatirlatici, use_container_width=True)
    if st.button("🗑️ Tüm Hatırlatıcıları Temizle"):
      if os.path.exists(REMINDER_FILE):
        os.remove(REMINDER_FILE)
        st.rerun()
  else:
    st.info("Henüz kurulmuş bir hatırlatıcı yok.")
