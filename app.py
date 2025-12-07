import streamlit as st
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
import os

# --- Configuración de la Página ---
st.set_page_config(page_title="Asistente FV", page_icon="⚡", layout="centered")
st.title("⚡ Asistente Técnico Fotovoltaico (FV)")
st.caption("Soy tu IA especializada en diseño, componentes y normativas de instalaciones de placas solares.")

# 1. ESTABLECER ROL/PROMPT FIJO
SISTEM_PROMPT = """
Tu rol es ser un Asistente Técnico Especializado en Instalaciones Fotovoltaicas. 
Debes responder con precisión, basándote en conocimientos técnicos de:
- Componentes (paneles, inversores, estructuras).
- Diseño de sistemas.
- Cálculos de rendimiento y dimensionamiento.
- Normativas (ej. CTE, REBT, R.D. 244/2019 en España, o equivalentes).
Tu tono debe ser profesional, claro, didáctico y útil. 
"""

# --- CONEXIÓN Y MODELO ESTABLE ---
try:
    # 1. Obtener clave de Streamlit Secrets
    API_KEY = st.secrets["GEMINI_API_KEY"]
    
    # 2. Configurar el cliente Gemini
    genai.configure(api_key=API_KEY)

    # 3. Configuración de generación
    config = GenerationConfig(
        system_instruction=SISTEM_PROMPT,
        temperature=0.4,
    )

    # 4. Inicializar el modelo estable y el chat (CORRECCIÓN DE MODELO)
    MODEL_NAME = 'gemini-2.5-flash'
    client = genai.GenerativeModel(
        model_name=MODEL_NAME, 
        generation_config=config
    )
    
    # Inicializar el chat si no existe
    if 'chat' not in st.session_state:
        st.session_state.chat = client.start_chat(history=[])

except Exception as e:
    # Si hay algún error (clave inválida, modelo no encontrado, etc.)
    st.error(f"Error al inicializar el chatbot. Por favor, asegúrate de que tu clave GEMINI_API_KEY sea válida y esté en Streamlit Secrets. Detalles: {e}")
    st.stop()
    
# --- Historial de Mensajes ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes anteriores
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capturar nueva entrada del usuario
if prompt := st.chat_input("Escribe tu consulta aquí..."):
    
    # 1. Agregar el mensaje del usuario al historial y mostrarlo
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Llamada a la API
    try:
        with st.spinner("El Asistente FV está pensando..."):
            response = st.session_state.chat.send_message(prompt)
        
        # 3. Agregar la respuesta del modelo al historial y mostrarla
        response_text = response.text
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        
        with st.chat_message("assistant"):
            st.markdown(response_text)

    except Exception as e:
        st.error(f"Ocurrió un error al comunicarse con la IA. Intenta reiniciar la aplicación.")
        st.exception(e)
