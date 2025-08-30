import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
 
 

# Configuración de la página
st.set_page_config(
    page_title="Consulta de Certificados",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    /* Fondo con imagen y glassmorphism */
    .stApp {
        background: linear-gradient(
            rgba(17, 96, 84, 0.8),
            rgba(0, 0, 0, 0.7)
        ), url('https://raw.githubusercontent.com/MagnoEfren/PyQt5/refs/heads/main/Calculadora%20Basica%20PyQt5/fondo.jpg');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        min-height: 100vh;
        color: white;
        font-family: 'Inter', sans-serif;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }

    /* Contenedor principal */
    .main-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem 1rem;
    }

    /* Estilo para el título */
    h1 {
        color: white;
        text-align: center;
        font-size: clamp(1.8rem, 5vw, 2.5rem);
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }

    /* Estilo para el subtítulo */
    p.subtitle {
        color: #ffffffcc;
        text-align: center;
        font-size: clamp(1rem, 3vw, 1.2rem);
        margin-bottom: 2rem;
    }

    /* Glassmorphism para el input de DNI */
    .stTextInput input {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 0.8rem;
        font-size: clamp(1rem, 3vw, 1.1rem);
        text-align: center;
        color: white;
        transition: all 0.3s ease;
    }

    .stTextInput input:focus {
        border-color: #9cc13d;
        outline: none;
        box-shadow: 0 0 8px rgba(156, 193, 61, 0.5);
    }

    .stTextInput input::placeholder {
        color: #ffffff99;
    }

    /* Estilo para todos los botones */
    .stButton button {
        background: rgba(17, 96, 84, 0.8); /* #116054 */
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem;
        font-size: clamp(1rem, 3vw, 1.1rem);
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
        max-width: 300px;
        margin: 1rem auto;
        display: block;
    }

    .stButton button:hover {
        background: rgba(13, 74, 63, 0.9); /* #0d4a3f */
        color: #9cc13d;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    /* Tarjetas con fondo degradado */
    .card {
        background: linear-gradient(135deg, #116054 0%, #0d4a3f 100%);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        color: white;
        transition: transform 0.3s ease;
    }

    .card:hover {
        transform: translateY(-5px);
    }

    .success-card h2, .error-card h2 {
        color: #9cc13d;
        text-align: center;
        margin: 0 0 0.5rem 0;
        font-size: clamp(1.4rem, 4vw, 1.8rem);
    }

    .card p {
        margin: 0.5rem 0;
        font-size: clamp(0.9rem, 2.5vw, 1rem);
        text-align: center;
        color: #ffffffcc;
    }

    /* Tarjeta de error */
    .error-card {
        background: linear-gradient(135deg, #0d4a3f 0%, #092e2b 100%);
        border: 2px solid #116054;
    }

    /* Estilo para el logo */
    .logo {
        display: block;
        margin: 0 auto 1rem auto;
        max-width: 120px;
        height: auto;
    }

    /* Responsividad */
    @media (max-width: 600px) {
        .stApp {
            background-size: cover;
            background-position: center;
        }
        .main-container {
            padding: 1rem;
        }
        h1 {
            font-size: clamp(1.5rem, 6vw, 2rem);
        }
        .stButton button {
            padding: 0.6rem;
            font-size: clamp(0.9rem, 3vw, 1rem);
        }
        .card {
            padding: 1rem;
        }
    }

    @media (min-width: 601px) and (max-width: 1024px) {
        .stApp {
            background-size: cover;
            background-position: center;
        }
    }
</style>
""", unsafe_allow_html=True)

# CONEXIÓN SEGURA CON SECRETS
def conectar_google_sheets():
    try:
        # Obtener credenciales de los secrets
        if 'GOOGLE_SHEETS_CREDENTIALS' in st.secrets:
            creds_dict = dict(st.secrets['GOOGLE_SHEETS_CREDENTIALS'])
            spreadsheet_id = st.secrets['SPREADSHEET_ID']
       
        
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(spreadsheet_id)
        worksheet = sheet.get_worksheet(0)
        
        return worksheet
    
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# Función para buscar DNI
def buscar_dni(dni_buscar, worksheet):
    try:
        datos = worksheet.get_all_records()
        df = pd.DataFrame(datos)
        
        if 'DNI' not in df.columns:
            return None
            
        df['DNI'] = df['DNI'].astype(str).str.strip()
        resultado = df[df['DNI'] == dni_buscar]
        
        if not resultado.empty:
            return resultado.iloc[0].to_dict()
        return None
            
    except Exception:
        return None

# Función principal
def main():
    if 'pagina_actual' not in st.session_state:
        st.session_state.pagina_actual = "principal"
    if 'dni_buscado' not in st.session_state:
        st.session_state.dni_buscado = ""

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    if st.session_state.pagina_actual == "principal":
        mostrar_pagina_principal()
    elif st.session_state.pagina_actual == "resultado":
        mostrar_resultado()
    elif st.session_state.pagina_actual == "no_encontrado":
        mostrar_no_encontrado()
        
    st.markdown('</div>', unsafe_allow_html=True)

def mostrar_pagina_principal():
    try:
        st.image("assets/logo.png", width=120, output_format="auto", caption="", use_container_width=False, clamp=True)
    except:
        pass
    
    st.markdown("<h1>📋 Consulta de Certificados</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Ingresa tu número de DNI para verificar tu certificado</p>", unsafe_allow_html=True)
    
    with st.form("form_dni"):
        dni = st.text_input(
            "", 
            max_chars=8, 
            key="input_dni",
            placeholder="Ingresa tu DNI (8 dígitos)",
            help="Solo números, sin espacios ni puntos"
        )
        
        buscar = st.form_submit_button("🔍 Buscar Certificado")
    
    if buscar:
        if dni and dni.isdigit() and len(dni) == 8:
            st.session_state.dni_buscado = dni
            with st.spinner("Buscando en nuestros registros..."):
                worksheet = conectar_google_sheets()
                if worksheet:
                    resultado = buscar_dni(dni, worksheet)
                    if resultado:
                        st.session_state.resultado = resultado
                        st.session_state.pagina_actual = "resultado"
                        st.rerun()
                    else:
                        st.session_state.pagina_actual = "no_encontrado"
                        st.rerun()
        else:
            st.markdown("""
            <div class="card error-card">
                <h2>❌ DNI Inválido</h2>
                <p>Por favor, ingresa un DNI válido de 8 dígitos.</p>
            </div>
            """, unsafe_allow_html=True)

def mostrar_resultado():
    resultado = st.session_state.resultado
    
    try:
        st.image("assets/logo.png", width=120, output_format="auto", caption="", use_container_width=False, clamp=True)
    except:
        pass
    
    st.markdown(f"""
    <div class="card success-card">
        <h2>✅ Certificado Encontrado</h2>
        <p>DNI: <strong>{st.session_state.dni_buscado}</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    nombre = resultado.get('NOMBRE', 'No especificado')
    curso = resultado.get('CURSO', 'No especificado')
    fecha = resultado.get('FECHA', 'No especificada')
    
    st.markdown(f"""
    <div class="card">
        <h3>👤 Nombre Completo</h3>
        <p><strong>{nombre}</strong></p>
        <h3>📚 Curso</h3>
        <p><strong>{curso}</strong></p>
        <h3>📅 Fecha de Certificación</h3>
        <p><strong>{fecha}</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("← Volver a Consultar", key="volver_resultado", help="Volver al formulario"):
        st.session_state.pagina_actual = "principal"
        st.rerun()

def mostrar_no_encontrado():
    try:
        st.image("assets/logo.png", width=120, output_format="auto", caption="", use_container_width=False, clamp=True)
    except:
        pass
    
    st.markdown(f"""
    <div class="card error-card">
        <h2>❌ Certificado No Encontrado</h2>
        <p>DNI: <strong>{st.session_state.dni_buscado}</strong></p>
        <p>No encontramos registros con este DNI en nuestro sistema.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <p>ℹ️ <strong>Sugerencias:</strong></p>
        <ul style='margin: 0; padding-left: 20px;'>
            <li>Verifica que el DNI esté correctamente escrito</li>
            <li>Asegúrate de haber completado el curso</li>
            <li>Contacta con soporte si el problema persiste</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("← Volver a Consultar", key="volver_error", help="Volver al formulario"):
        st.session_state.pagina_actual = "principal"
        st.rerun()

if __name__ == "__main__":
    main()