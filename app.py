import streamlit as st
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- DICIONÁRIO DE TRADUÇÃO ---
translations = {
    "English": {
        "title": "🌍 Global Sales Copy AI",
        "desc": "Sell like a local anywhere in the world.",
        "login": "Enter your purchase email:",
        "enter": "ACCESS TOOL",
        "product": "What are you selling?",
        "target_lang": "Target Language",
        "target_country": "Target Country/Region",
        "vibe": "Tone of Voice",
        "button": "GENERATE GLOBAL COPY 🚀",
        "error": "Access Denied. Please check your email.",
        "buy": "Buy Lifetime Access"
    },
    "Português": {
        "title": "🌍 Vendedor Global AI",
        "desc": "Venda como um nativo em qualquer lugar do mundo.",
        "login": "Digite seu e-mail de compra:",
        "enter": "ACESSAR FERRAMENTA",
        "product": "O que você vende?",
        "target_lang": "Idioma de Destino",
        "target_country": "País/Região Alvo",
        "vibe": "Tom de Voz",
        "button": "GERAR COPY GLOBAL 🚀",
        "error": "Acesso Negado. Verifique seu e-mail.",
        "buy": "Comprar Acesso Vitalício"
    },
    "Español": {
        "title": "🌍 Redactor Global IA",
        "desc": "Vende como un local en cualquier parte del mundo.",
        "login": "Ingrese su correo de compra:",
        "enter": "ACCEDER",
        "product": "¿Qué vendes?",
        "target_lang": "Idioma de Destino",
        "target_country": "País/Región Objetivo",
        "vibe": "Tono de Voz",
        "button": "GENERAR TEXTO 🚀",
        "error": "Acceso Denegado.",
        "buy": "Comprar Acceso de Por Vida"
    }
}

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Global Copy AI", page_icon="🌍")

# Seletor de Idioma
interface_lang = st.sidebar.selectbox("Interface Language / Idioma", ["English", "Português", "Español"])
t = translations[interface_lang]

# --- VERIFICAÇÃO DE LOGIN (Simples) ---
def verificar_acesso(email_usuario):
    # Conecta na planilha
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="clientes_vip", ttl=5) # ttl=5 garante atualização rápida
        emails_validos = df['email'].str.lower().str.strip().values
        if email_usuario.lower().strip() in emails_validos:
            return True
    except:
        # Se der erro na planilha (ainda não configurada), deixa passar para teste se tiver @
        if "@" in email_usuario: return True 
    return False

if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title(t["title"])
    st.caption(t["desc"])
    
    email_input = st.text_input(t["login"])
    
    if st.button(t["enter"]):
        if verificar_acesso(email_input):
            st.session_state.logado = True
            st.rerun()
        else:
            st.error(t["error"])
            st.link_button(t["buy"], "https://gumroad.com/") # Coloque seu link depois

# --- APP GLOBAL ---
if st.session_state.logado:
    with st.sidebar:
        st.divider()
        st.header("Settings")
        # BYOK - Bring Your Own Key
        user_api_key = st.text_input("Google API Key:", type="password")
        st.caption("Get it free: aistudio.google.com")
        if st.button("Logout"):
            st.session_state.logado = False
            st.rerun()

    st.title(t["title"])

    if not user_api_key:
        st.warning("⚠️ Please enter your Google API Key in the sidebar to start.")
        st.stop()

    produto = st.text_input(t["product"])
    
    c1, c2, c3 = st.columns(3)
    idioma_alvo = c1.selectbox(t["target_lang"], ["English", "Portuguese", "Spanish", "French", "German", "Hindi", "Mandarin", "Japanese"])
    pais_alvo = c2.selectbox(t["target_country"], [
        "USA - New York (Corporate)", "USA - Texas (Friendly)", "USA - Gen Z (TikTok)",
        "Brazil - SP (Business)", "Brazil - Rio (Casual)", "Brazil - General",
        "Portugal - Lisbon", "Spain - Madrid", "India - Tech/Business", "China - Business"
    ])
    tom = c3.selectbox(t["vibe"], ["Sales/Persuasive", "Viral/Funny", "Professional", "Storytelling"])

    if st.button(t["button"]):
        try:
            genai.configure(api_key=user_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Act as a native expert copywriter from {pais_alvo}.
            Task: Write a sales copy for: {produto}.
            Language: {idioma_alvo} (Native level).
            Tone: {tom}.
            Context: Use local slang, idioms and cultural references from {pais_alvo}.
            """
            
            with st.spinner("Translating culture... 🌍"):
                response = model.generate_content(prompt)
                st.subheader("Result / Resultado:")
                st.text_area("Copy:", value=response.text, height=250)
                
        except Exception as e:
            st.error(f"Error: {e}")
