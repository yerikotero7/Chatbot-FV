import streamlit as st
from google import genai
from google.genai.types import GenerationConfig

# --- Configuración de la Página ---
st.set_page_config(page_title="Asistente FV", page_icon="⚡")

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

# --- Conexión con Gemini (Se lee la clave API de secrets.toml localmente o de los secretos de Streamlit Cloud) ---
try:
    # Intenta leer la clave API de los secretos de Streamlit (o del archivo secrets.toml local)
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Error: La clave GEMINI_API_KEY no se encontró.")
    st.stop()

# Inicializar el cliente de Gemini
client = genai.Client(api_key=API_KEY)

# Configuración de generación para asegurar la respuesta de la IA
config = GenerationConfig(
    system_instruction=SISTEM_PROMPT,
    temperature=0.4, # Un valor bajo para respuestas más precisas y menos creativas
)

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

    # 2. Preparar el historial para enviarlo a la API
    # La API de Gemini necesita el historial en un formato específico (roles: user/model)
    history_for_api = [
        genai.types.Content(role=m["role"], parts=[genai.types.Part.from_text(m["content"])]) 
        for m in st.session_state.messages
    ]

    # 3. Llamada a la API de Gemini
    try:
        with st.spinner("El Asistente FV está pensando..."):
            response = client.models.generate_content(
                model='gemini-2.5-flash', # Modelo rápido y eficiente para chat
                contents=history_for_api,
                config=config,
            )
        
        # 4. Agregar la respuesta del modelo al historial y mostrarla
        response_text = response.text
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        
        with st.chat_message("assistant"):
            st.markdown(response_text)

    except Exception as e:
        st.error(f"Ocurrió un error al comunicarse con la IA: {e}")