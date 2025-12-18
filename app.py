import streamlit as st
import pickle
import numpy as np
from featureextraction import FeatureExtraction
import time
import os
import streamlit as st


# Konfigurasi halaman
st.set_page_config(
    page_title="Phishing URL Detection",
    page_icon="🔒",
    layout="wide"
)

# Custom CSS untuk styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .feature-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Load model
@st.cache_resource
def load_model():
    st.write("Working dir:", os.getcwd())
    st.write("Files here:", os.listdir())
    try:
        with open('gradient_boosting_model.pkl', 'rb') as file:
            model = pickle.load(file)
        return model
    except FileNotFoundError:
        st.error("❌ Model file 'gradient_boosting_model.pkl' tidak ditemukan!")
        return None
    except Exception as e:
        st.error(f"❌ Error loading model: {str(e)}")
        return None

# Header
st.title("🔒 Phishing URL Detection System")
st.markdown("---")
st.markdown("""
    Sistem ini menggunakan **Machine Learning** untuk mendeteksi apakah sebuah URL adalah phishing atau legitimate.
    Masukkan URL yang ingin Anda periksa di bawah ini.
""")

# Sidebar
with st.sidebar:
    st.header("ℹ️ Informasi")
    st.markdown("""
    ### Tentang Aplikasi
    Aplikasi ini menganalisis **30 fitur** dari URL untuk mendeteksi phishing:
    
    - **Fitur URL**: Panjang, karakter khusus, dll
    - **Fitur Domain**: Usia, registrasi, DNS
    - **Fitur HTML**: Form, script, iframe
    - **Fitur Eksternal**: Traffic, PageRank
    
    ### Cara Penggunaan
    1. Masukkan URL lengkap (dengan http/https)
    2. Klik tombol "Analisis URL"
    3. Lihat hasil prediksi
    """)
    
    st.markdown("---")
    st.markdown("**Model**: Gradient Boosting Classifier")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    url_input = st.text_input(
        "🌐 Masukkan URL",
        placeholder="https://example.com",
        help="Masukkan URL lengkap yang ingin dianalisis"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_button = st.button("🔍 Analisis URL", type="primary", use_container_width=True)

# Load model
model = load_model()

if analyze_button and url_input:
    if model is None:
        st.error("Model tidak dapat dimuat. Pastikan file 'gradient_boosting_model.pkl' ada di direktori yang sama.")
    else:
        # Validasi input
        if not url_input.startswith(('http://', 'https://')):
            st.warning("⚠️ URL harus dimulai dengan http:// atau https://")
        else:
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Extract features
                status_text.text("🔄 Mengekstrak fitur dari URL...")
                progress_bar.progress(30)
                
                obj = FeatureExtraction(url_input)
                features = obj.getFeaturesList()
                
                progress_bar.progress(60)
                status_text.text("🤖 Melakukan prediksi...")
                
                # Reshape features untuk prediksi
                features_array = np.array(features).reshape(1, -1)
                
                # Prediksi
                prediction = model.predict(features_array)[0]
                probability = model.predict_proba(features_array)[0]
                
                progress_bar.progress(100)
                status_text.text("✅ Analisis selesai!")
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
                
                # Hasil prediksi
                st.markdown("---")
                st.subheader("📊 Hasil Analisis")
                
                col_result1, col_result2, col_result3 = st.columns(3)
                
                with col_result1:
                    st.metric("URL yang Dianalisis", "✓ Berhasil")
                
                with col_result2:
                    if prediction == 1:
                        st.metric("Status", "✅ LEGITIMATE", delta="Aman")
                    else:
                        st.metric("Status", "⚠️ PHISHING", delta="Berbahaya", delta_color="inverse")
                
                with col_result3:
                    confidence = max(probability) * 100
                    st.metric("Confidence", f"{confidence:.2f}%")
                
                # Detail hasil
                st.markdown("---")
                
                if prediction == 1:
                    st.success("### ✅ URL INI KEMUNGKINAN AMAN (LEGITIMATE)")
                    st.info(f"""
                    **Probabilitas Legitimate**: {probability[1]*100:.2f}%  
                    **Probabilitas Phishing**: {probability[0]*100:.2f}%
                    
                    URL ini memiliki karakteristik yang mirip dengan website legitimate.
                    """)
                else:
                    st.error("### ⚠️ PERINGATAN: URL INI TERDETEKSI SEBAGAI PHISHING!")
                    st.warning(f"""
                    **Probabilitas Phishing**: {probability[0]*100:.2f}%  
                    **Probabilitas Legitimate**: {probability[1]*100:.2f}%
                    
                    **Jangan** memasukkan informasi pribadi, password, atau data sensitif di website ini!
                    """)
                
                # Tampilkan fitur dalam expander
                with st.expander("🔬 Lihat Detail Fitur yang Diekstrak"):
                    feature_names = [
                        "Using IP Address", "Long URL", "Short URL", "Symbol @",
                        "Redirecting //", "Prefix Suffix", "Sub Domains", "HTTPS",
                        "Domain Registration Length", "Favicon", "Non-Standard Port",
                        "HTTPS in Domain", "Request URL", "Anchor URL", "Links in Script Tags",
                        "Server Form Handler", "Info Email", "Abnormal URL", "Website Forwarding",
                        "Status Bar Customization", "Disable Right Click", "Using Popup Window",
                        "Iframe Redirection", "Age of Domain", "DNS Recording", "Website Traffic",
                        "PageRank", "Google Index", "Links Pointing to Page", "Stats Report"
                    ]
                    
                    # Tampilkan dalam 3 kolom
                    cols = st.columns(3)
                    for idx, (name, value) in enumerate(zip(feature_names, features)):
                        col_idx = idx % 3
                        with cols[col_idx]:
                            if value == 1:
                                st.markdown(f"✅ **{name}**: Aman")
                            elif value == 0:
                                st.markdown(f"⚠️ **{name}**: Suspicious")
                            else:
                                st.markdown(f"❌ **{name}**: Berbahaya")
                
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan saat menganalisis URL: {str(e)}")
                st.info("Pastikan URL valid dan dapat diakses.")

elif analyze_button and not url_input:
    st.warning("⚠️ Silakan masukkan URL terlebih dahulu!")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🔒 Phishing Detection System | Powered by Machine Learning</p>
        <p style='font-size: 0.8rem;'>Selalu verifikasi URL sebelum memasukkan data sensitif</p>
    </div>
""", unsafe_allow_html=True)