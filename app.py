import streamlit as st
import pandas as pd

st.set_page_config(page_title="Durak Paneli", page_icon="🚕", layout="centered")

st.title("🚕 Durak Paneli")
st.caption("Duraktaki taksilerin anlık durumu")

taksiler = pd.DataFrame({
    "Plaka": ["34 AB 123", "34 CD 456", "34 EF 789"],
    "Şoför": ["Ahmet", "Mehmet", "Ali"],
    "Durum": ["Boşta", "Dolu", "Boşta"],
    "Sıra": [1, 2, 3]
})

# Üstte özet sayılar
bosta_sayisi = (taksiler["Durum"] == "Boşta").sum()
dolu_sayisi = (taksiler["Durum"] == "Dolu").sum()

col1, col2, col3 = st.columns(3)
col1.metric("Toplam Taksi", len(taksiler))
col2.metric("Boşta", int(bosta_sayisi))
col3.metric("Dolu", int(dolu_sayisi))

st.divider()

# Sırasına göre diz
taksiler = taksiler.sort_values("Sıra")

# Durumu renklendiren fonksiyon
def renklendir(durum):
    if durum == "Boşta":
        return "background-color: #d4edda; color: #155724"
    else:
        return "background-color: #f8d7da; color: #721c24"

st.dataframe(
    taksiler.style.applymap(renklendir, subset=["Durum"]),
    use_container_width=True,
    hide_index=True
)
