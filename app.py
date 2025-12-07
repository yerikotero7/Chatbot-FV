import streamlit as st
import google.generativeai as genai # Cambiado de 'from google import genai' para mayor claridad
from google.generativeai.types import GenerationConfig
import os # Para futuras mejoras o lectura de variables de entorno

# --- Configuración de la Página ---
st.set_page_config(page_title="Asistente FV", page_icon="⚡", layout="centered")

st.title("⚡ Asistente Técnico Fotovoltaico (FV)")
st.caption("Soy tu IA especializada en diseño, componentes y normativas de instalaciones de placas solares.")

# 1. ESTABLECER ROL/PROMPT FIJO (Instrucciones para la IA)
SISTEM_PROMPT = """
Tu rol es ser un Asistente Técnico Especializado en Instalaciones Fotovoltaicas. 
Debes responder con precisión, basándote en conocimientos técnicos de:
- Componentes (paneles, inversores, estructuras).
- Diseño de sistemas.
- Cálculos de rendimiento y dimensionamiento.
- Normativas (ej. CTE, REBT, R.D. 244/2019 en España, o equivalentes).
Tu tono debe ser profesional, claro, didáctico y útil. 
Siempre que sea posible, ofrece la respuesta sencilla, pero con la explicación técnica detrás.
Si te preguntan algo fuera de la energía solar fotovoltaica, responde que tu especialidad es únicamente FV.
"""

# --- CONEXIÓN Y VALIDACIÓN DE LA CLAVE API DE GEMINI (CRÍTICO) ---
def setup_gemini():
    """Configura la API de Gemini y valida la clave."""
    try:
        # Intenta obtener la clave API de Streamlit Secrets (online)
        api_key = st.secrets["GEMINI_API_KEY"]
    except KeyError:
        st.error("Error de configuración: La clave 'GEMINI_API_KEY' no se encontró en los secretos de Streamlit Cloud.")
        st.info("Asegúrate de haber configurado tu clave API en 'Manage app -> Settings -> Secrets'.")
        st.stop()
    except Exception as e:
        st.error(f"Error inesperado al leer los secretos de Streamlit: {e}")
        st.stop()

    if not api_key:
        st.error("Error de configuración: La clave 'GEMINI_API_KEY' está vacía. Por favor, revísala en los secretos de Streamlit Cloud.")
        st.stop()

    try:
        genai.configure(api_key=api_key)
        # Intentar una llamada de prueba para validar la clave de inmediato
        # Esto puede fallar si la clave es inválida.
        genai.get_model('gemini-1.5-flash-latest') # Usamos un modelo que sabemos que existe
    except Exception as e:
        st.error(f"Error al conectar con Google Gemini. La clave API puede ser inválida o ha expirado. Detalles: {e}")
        st.info("Por favor, genera una nueva clave API en https://ai.google.dev/gemini-api/docs/api-key y actualiza tus secretos en Streamlit Cloud.")
        st.stop()
    
    return genai.GenerativeModel(
        model_name='gemini-1.5-flash-latest', # Modelo rápido y eficiente para chat
        generation_config=GenerationConfig(
            system_instruction=SISTEM_PROMPT,
            temperature=0.4, # Un valor bajo para respuestas más precisas y menos creativas
            top_p=0.9,
            top_k=40,
        )
    )

# Inicializar el modelo de Gemini solo una vez
if 'gemini_model' not in st.session_state:
    st.session_state.gemini_model = setup_gemini()
    st.session_state.chat = st.session_state.gemini_model.start_chat(history=[])

# Inicializar el historial de chat si no existe
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Ejemplos de Preguntas para No Expertos ---
st.sidebar.header("Ejemplos de Preguntas")
st.sidebar.markdown(
    """
* **¿Por qué mis placas solares no están generando la electricidad que deberían?**
* **¿Qué pasa si mi casa produce más electricidad de la que consume?**
* **¿Cuántas placas necesito para una casa con un consumo normal?**
"""
)

st.info("¡Introduce tu consulta técnica y te ayudaré a dimensionar, calcular o resolver dudas!")

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

    # 2. Llamada a la API de Gemini
    try:
        with st.spinner("El Asistente FV está pensando..."):
            # Enviar el prompt al historial de chat de Gemini
            response = st.session_state.chat.send_message(prompt)
        
        # 3. Agregar la respuesta del modelo al historial y mostrarla
        response_text = response.text
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        
        with st.chat_message("assistant"):
            st.markdown(response_text)

    except Exception as e:
        st.error(f"Ocurrió un error al comunicarse con la IA: {e}. Intenta reiniciar la aplicación o verificar tu clave API.")
        st.exception(e) # Muestra el error completo para depuración
