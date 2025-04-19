import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

st.set_page_config(page_title="BIST Hisse Tarama Aracı", layout="wide")

st.title("📊 BIST Hisse Tarama ve Analiz Aracı")

# Hisse listesi
@st.cache_data
def get_bist_stocks():
    return sorted([
        "AKBNK", "ARCLK", "ASELS", "BIMAS", "EKGYO", "EREGL", "FROTO", "GARAN", "ISCTR", "KCHOL", "KOZAA",
        "KOZAL", "PGSUS", "SAHOL", "SASA", "SISE", "TCELL", "THYAO", "TOASO", "TTKOM", "TUPRS", "VAKBN", "YKBNK"
    ])

hisseler = get_bist_stocks()

# Çoklu seçim kutusu
secili_hisseler = st.multiselect("Hisse Seç (birden fazla seçebilirsin):", hisseler, default=["SASA", "SISE"])

# Başlat butonu
if st.button("🔍 Analizi Başlat"):

    sonuc_listesi = []

    for hisse in secili_hisseler:
        kod = hisse + ".IS"
        try:
            data = yf.download(kod, start=datetime.now() - timedelta(days=365), progress=False)
            if data.empty:
                st.warning(f"{hisse} için veri bulunamadı.")
                continue

            info = yf.Ticker(kod).info
            fk = info.get("trailingPE", None)

            roe = (data['Close'][-1] - data['Close'][0]) / data['Close'][0] * 100
            data['EMA_50'] = ta.ema(data['Close'], length=50)
            data['EMA_200'] = ta.ema(data['Close'], length=200)
            ema_durum = "EVET" if data['Close'][-1] < data['EMA_200'][-1] else "HAYIR"

            sonuc_listesi.append({
                "Hisse": hisse,
                "ROE (%)": round(roe, 2),
                "200 EMA Altında": ema_durum,
                "F/K": round(fk, 2) if fk else "-"
            })

            # Grafik çiz
            st.subheader(f"📈 {hisse} Grafiği")
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(data['Close'], label='Kapanış')
            ax.plot(data['EMA_50'], label='EMA 50', linestyle='--')
            ax.plot(data['EMA_200'], label='EMA 200', linestyle='--')
            ax.set_title(f"{hisse} - Fiyat & EMA")
            ax.legend()
            st.pyplot(fig)

        except Exception as e:
            st.error(f"{hisse} için hata: {e}")

    # Sonuç tablo olarak göster
    if sonuc_listesi:
        df_sonuc = pd.DataFrame(sonuc_listesi)
        st.subheader("📋 Tarama Sonuçları")
        st.dataframe(df_sonuc)

        # İndirme
        csv = df_sonuc.to_csv(index=False, encoding='utf-8-sig')
        st.download_button("⬇️ CSV olarak indir", csv, "bist_sonuclar.csv", "text/csv")

