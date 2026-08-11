import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Durak Paneli", page_icon="🚕", layout="centered")

st.title("🚕 Durak Paneli")
st.caption("Duraktaki taksilerin anlık durumu")

if "taksiler" not in st.session_state:
    st.session_state.taksiler = pd.DataFrame({
        "Plaka": ["34 AB 123", "34 CD 456", "34 EF 789"],
        "Şoför": ["Ahmet", "Mehmet", "Ali"],
        "Durum": ["Boşta", "Dolu", "Boşta"],
        "Sıra": [1, 2, 3]
    })

if "son_guncelleme_id" not in st.session_state:
    st.session_state.son_guncelleme_id = None

if "son_mesaj" not in st.session_state:
    st.session_state.son_mesaj = None

taksiler = st.session_state.taksiler

bosta_sayisi = (taksiler["Durum"] == "Boşta").sum()
dolu_sayisi = (taksiler["Durum"] == "Dolu").sum()

col1, col2, col3 = st.columns(3)
col1.metric("Toplam Taksi", len(taksiler))
col2.metric("Boşta", int(bosta_sayisi))
col3.metric("Dolu", int(dolu_sayisi))

st.divider()

taksiler_sirali = taksiler.sort_values("Sıra")

def renklendir(durum):
    if durum == "Boşta":
        return "background-color: #d4edda; color: #155724"
    else:
        return "background-color: #f8d7da; color: #721c24"

st.dataframe(
    taksiler_sirali.style.map(renklendir, subset=["Durum"]),
    use_container_width=True,
    hide_index=True
)

st.divider()
st.subheader("📨 Telegram Mesajları")

TOKEN = st.secrets["TELEGRAM_TOKEN"]

if st.button("🔄 Yeni mesajları kontrol et"):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {}
    if st.session_state.son_guncelleme_id:
        params["offset"] = st.session_state.son_guncelleme_id + 1

    yanit = requests.get(url, params=params)
    veri = yanit.json()

    mesajlar = [g for g in veri.get("result", []) if "message" in g and "text" in g["message"]]

    if mesajlar:
        son = mesajlar[-1]
        st.session_state.son_guncelleme_id = son["update_id"]
        st.session_state.son_mesaj = son["message"]["text"]
        gonderen = son["message"]["from"].get("first_name", "Bilinmeyen")
        st.success(f"{gonderen} adlı kullanıcıdan yeni mesaj: \"{st.session_state.son_mesaj}\"")
    else:
        st.info("Yeni mesaj yok.")

if st.session_state.son_mesaj:
    adres = st.session_state.son_mesaj
    st.write(f"İşlenecek adres: **{adres}**")

    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": adres, "format": "json", "limit": 1}
    headers = {"User-Agent": "durak-panel-prototip"}

    response = requests.get(url, params=params, headers=headers)
    sonuclar = response.json()

    if sonuclar:
        lat = float(sonuclar[0]["lat"])
        lon = float(sonuclar[0]["lon"])
        st.success(f"Adres bulundu: {sonuclar[0]['display_name']}")

        konum_df = pd.DataFrame({"lat": [lat], "lon": [lon]})
        st.map(konum_df, zoom=14)

        bostakiler = taksiler[taksiler["Durum"] == "Boşta"].sort_values("Sıra")

        if not bostakiler.empty:
            siradaki = bostakiler.iloc[0]
            st.info(f"Sıradaki boş taksi: {siradaki['Plaka']} ({siradaki['Şoför']})")

            if st.button(f"🚕 {siradaki['Plaka']} plakalı taksiyi gönder", key="ata_buton"):
                idx = siradaki.name
                st.session_state.taksiler.loc[idx, "Durum"] = "Dolu"
                st.session_state.son_mesaj = None
                st.rerun()
        else:
            st.warning("Şu an boşta taksi yok.")
    else:
        st.warning("Adres bulunamadı, mesajı farklı yazmayı dene.")
