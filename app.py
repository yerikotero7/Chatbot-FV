import streamlit as st
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

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

# --- CONEXIÓN Y VALIDACIÓN DE LA CLAVE API DE GEMINI ---
def setup_gemini():
    """Configura la API de Gemini, valida la clave y maneja errores."""
    MODEL_NAME = 'gemini-pro' # Modelo universal y estable (soluciona error 404)

    try:
        # Intenta obtener la clave API de Streamlit Secrets
        api_key = st.secrets["GEMINI_API_KEY"]
    except KeyError:
        st.error("Error de configuración: La clave 'GEMINI_API_KEY' no se encontró en los secretos de Streamlit Cloud.")
        st.info("Asegúrate de haber configurado tu clave API en 'Manage app -> Settings -> Secrets'.")
        st.stop()
    
    if not api_key or len(api_key) < 30: # Valida que la clave no esté vacía
        st.error("Error de configuración: La clave API está vacía o es demasiado corta. Verifica tus secretos.")
        st.stop()

    try:
        genai.configure(api_key=api_key)
        # Intentar una llamada de prueba con el modelo estable
        genai.get_model(MODEL_NAME) 
    except Exception as e:
        # Esto capturará errores de clave inválida o de conexión
        st.error(f"Error al conectar con Google Gemini. La clave API puede ser inválida, o el modelo no está disponible. Detalles: {e}")
        st.info("Por favor, genera una **clave API nueva** y actualiza tus secretos en Streamlit Cloud.")
        st.stop()
    
    # Si la conexión es exitosa, se inicializa el modelo para el chat
    return genai.GenerativeModel(
        model_name=MODEL_NAME, 
        generation_config=GenerationConfig(
            system_instruction=SISTEM_PROMPT,
            temperature=0.4, 
        )
    )

# Inicializar el modelo de Gemini y el historial de chat (Se ejecuta solo una vez)
if 'gemini_model' not in st.session_state:
    st.session_state.gemini_model = setup_gemini()
    st.session_state.chat = st.session_state.gemini_model.start_chat(history=[])
    st.session_state.messages = [] # Inicialización correcta del historial (soluciona SyntaxError)

# --- Ejemplos de Preguntas ---
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
        st.error(f"Ocurrió un error al comunicarse con la IA. Intenta reiniciar la aplicación o verificar tu clave API.")
        st.exception(e)
