import streamlit as st
import google.generativeai as genai
import openai
# import anthropic  # Deixamos comentado por enquanto, mas a biblioteca está instalada
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Global Copy AI", page_icon="🌍")

# --- DICIONÁRIO DE TRADUÇÃO ---
translations = {
    "English": {
        "title": "🌍 Global AI Copy Hub",
        "desc": "The universal AI to sell like a local, anywhere.",
        "login": "Enter your email:",
        "enter": "ACCESS TOOL",
        "product": "What are you selling?",
        "target_lang": "Target Language",
        "target_country": "Target Country/Region",
        "vibe": "Tone of Voice",
        "button": "GENERATE GLOBAL COPY 🚀",
        "error": "Access Denied. Check your email or upgrade.",
        "buy": "Buy Lifetime Access",
        "api_gemini": "Google Gemini API Key:",
        "api_gpt": "OpenAI (GPT) API Key:",
        "api_claude": "Anthropic (Claude) API Key:"
    },
    "Português": {
        "title": "🌍 Hub Global de Copy AI",
        "desc": "A IA universal para vender como um nativo, em qualquer lugar.",
        "login": "Digite seu e-mail:",
        "enter": "ACESSAR FERRAMENTA",
        "product": "O que você vende?",
        "target_lang": "Idioma de Destino",
        "target_country": "País/Região Alvo",
        "vibe": "Tom de Voz",
        "button": "GERAR COPY GLOBAL 🚀",
        "error": "Acesso Negado. Verifique seu e-mail ou faça upgrade.",
        "buy": "Comprar Acesso Vitalício",
        "api_gemini": "Chave API Google Gemini:",
        "api_gpt": "Chave API OpenAI (GPT):",
        "api_claude": "Chave API Anthropic (Claude):"
    }
}

# --- PLANOS E CONDIÇÕES (Simulação de Acesso) ---
PLANOS = {
    "Free": {"requests": 3, "modelos": ["Google Gemini"], "msg": "Seu plano é FREE. Faça upgrade para desbloquear GPT e Claude."},
    "Pro": {"requests": 100, "modelos": ["Google Gemini", "OpenAI GPT"], "msg": "Seu plano é PRO. Use GPT para velocidade."},
    "Master": {"requests": 500, "modelos": ["Google Gemini", "OpenAI GPT", "Claude AI"], "msg": "Seu plano é MASTER. Use qualquer IA."}
}

# Na vida real, você buscará o plano do e-mail na Planilha.
# Aqui, simulamos que todo mundo logado é 'Master' para poder testar as chaves.
def simular_plano(email):
    if email.endswith("@teste.com"): # Exemplo de como segmentar
        return "Master" 
    return "Free"

UPGRADE_URL = "https://seu-link-de-upgrade.com"

# --- VARIÁVEIS DE SESSÃO E LOGIN ---
interface_lang = st.sidebar.selectbox("Interface Language / Idioma", ["Português", "English"])
t = translations[interface_lang]

if 'logado' not in st.session_state:
    st.session_state.logado = False
if 'consumo' not in st.session_state:
    st.session_state.consumo = 0

# --- LOGIN SIMPLES COM SIMULAÇÃO DE PLANO ---
if not st.session_state.logado:
    st.title(t["title"])
    st.caption(t["desc"])
    email_input = st.text_input(t["login"])
    if st.button(t["enter"]):
        if "@" in email_input:
            st.session_state.logado = True
            st.session_state.email = email_input
            st.session_state.consumo = 0
            st.session_state.plano = simular_plano(email_input)
            st.rerun()
        else:
            st.error(t["error"])
            st.link_button(t["buy"], UPGRADE_URL)

# --- APP PRINCIPAL ---
if st.session_state.logado:
    st.title(t["title"])
    plano_atual = st.session_state.plano
    limite = PLANOS[plano_atual]["requests"]
    
    st.sidebar.header("🔑 Configurações")
    
    # --- CHAVES DE API (SÓ APARECE SE O PLANO SUPORTAR) ---
    user_api_gemini = st.sidebar.text_input(t["api_gemini"], type="password")
    
    opcoes_modelos = PLANOS[plano_atual]["modelos"]
    
    if "OpenAI GPT" in opcoes_modelos:
        user_api_gpt = st.sidebar.text_input(t["api_gpt"], type="password")
    else:
        user_api_gpt = None # Desliga se o plano não permite
    
    if "Claude AI" in opcoes_modelos:
        user_api_claude = st.sidebar.text_input(t["api_claude"], type="password")
    else:
        user_api_claude = None # Desliga se o plano não permite

    st.sidebar.markdown("---")
    st.sidebar.info(PLANOS[plano_atual]["msg"])
    
    provedor = st.selectbox("Selecione o Cérebro da IA:", opcoes_modelos)
    
    # Botão de Logout
    if st.sidebar.button("Logout"):
        st.session_state.logado = False
        st.rerun()

    produto = st.text_input(t["product"])
    
    c1, c2 = st.columns(2)
    idioma_alvo = c1.selectbox(t["target_lang"], ["Portuguese", "English", "Spanish"])
    pais_alvo = c2.selectbox(t["target_country"], ["Brazil - SP", "USA - New York", "Portugal - Lisbon"])
    tom = st.selectbox(t["vibe"], ["Sales/Persuasive", "Viral/Funny", "Professional"])
    
    # Limite de Consumo
    if limite <= st.session_state.consumo:
        st.warning(f"Você já usou seus {limite} pedidos. Por favor, faça upgrade.")
        st.link_button("🔓 Upgrade / Compra", UPGRADE_URL)
        st.stop()

    # --- BOTÃO DE GERAÇÃO (ROTEADOR DE IA) ---
    if st.button(t["button"]):
        
        # 1. Validação da Chave
        if provedor == "Google Gemini" and not user_api_gemini:
             st.warning("⚠️ Insira a Chave Gemini na lateral.")
             st.stop()
        if provedor == "OpenAI GPT" and not user_api_gpt:
             st.warning("⚠️ Insira a Chave GPT na lateral.")
             st.stop()
        if provedor == "Claude AI" and not user_api_claude:
             st.warning("⚠️ Insira a Chave Claude na lateral.")
             st.stop()
             
        # 2. PROMPT UNIVERSAL
        prompt = f"""
        Você é um Copywriter Sênior. Sua missão é gerar uma copy de vendas para o produto: {produto}.
        Sua audiência está em {pais_alvo}.
        Adapte a linguagem, gírias e a cultura local de {pais_alvo} no idioma {idioma_alvo}.
        O tom de voz deve ser {tom}.
        Gere apenas o texto da copy.
        """
        
        # 3. ROTEAMENTO E CHAMADA DA IA
        try:
            with st.spinner(f"Gerando copy com {provedor}... 🌍"):
                
                if provedor == "Google Gemini":
                    genai.configure(api_key=user_api_gemini)
                    model = genai.GenerativeModel("gemini-pro") # Usamos o Pro estável
                    response = model.generate_content(prompt)
                    copy_text = response.text
                
                elif provedor == "OpenAI GPT":
                    # Configuração para GPT-3.5-turbo (A mais rápida/barata)
                    openai.api_key = user_api_gpt
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a senior copywriter."},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    copy_text = response.choices[0].message.content
                    
                elif provedor == "Claude AI":
                    st.warning("Funcionalidade Claude em desenvolvimento. Usando Gemini como fallback.")
                    # anthropic.api_key = user_api_claude
                    # [Código da Chamada Claude ficaria aqui]
                    
                    # Fallback
                    genai.configure(api_key=user_api_gemini)
                    model = genai.GenerativeModel("gemini-pro")
                    response = model.generate_content(prompt)
                    copy_text = f"[CLAUDE FALLBACK] {response.text}"
                    
                st.subheader("Resultado da Copy:")
                st.text_area("Copy:", value=copy_text, height=350)
                
                st.session_state.consumo += 1
                st.info(f"Usos restantes: {limite - st.session_state.consumo} / {limite}")

        except Exception as e:
            st.error(f"Erro: {e}")
            
