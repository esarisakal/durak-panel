import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Durak Paneli", page_icon="🚕", layout="centered")

st.title("🚕 Durak Paneli")
st.caption("Duraktaki taksilerin anlık durumu")

taksiler = pd.DataFrame({
    "Plaka": ["34 AB 123", "34 CD 456", "34 EF 789"],
    "Şoför": ["Ahmet", "Mehmet", "Ali"],
    "Durum": ["Boşta", "Dolu", "Boşta"],
    "Sıra": [1, 2, 3]
})

bosta_sayisi = (taksiler["Durum"] == "Boşta").sum()
dolu_sayisi = (taksiler["Durum"] == "Dolu").sum()

col1, col2, col3 = st.columns(3)
col1.metric("Toplam Taksi", len(taksiler))
col2.metric("Boşta", int(bosta_sayisi))
col3.metric("Dolu", int(dolu_sayisi))

st.divider()

taksiler = taksiler.sort_values("Sıra")

def renklendir(durum):
    if durum == "Boşta":
        return "background-color: #d4edda; color: #155724"
    else:
        return "background-color: #f8d7da; color: #721c24"

st.dataframe(
    taksiler.style.map(renklendir, subset=["Durum"]),
    use_container_width=True,
    hide_index=True
)

st.divider()
st.subheader("📍 Müşteri Adresi")

adres = st.text_input("Adres girin (örn: Kadıköy Moda, İstanbul)")

if adres:
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
    else:
        st.warning("Adres bulunamadı, biraz daha farklı yazmayı dene.")
