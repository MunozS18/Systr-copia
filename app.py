import streamlit as st
import pandas as pd
import mysql.connector
from config import DB_CONFIG
from modelo_recomendacion import SistemaRecomendacion
import os
from PIL import Image
from datetime import datetime

# Función para obtener la imagen del hotel como objeto PIL Image
def obtener_imagen_hotel(id_hotel):
    ruta_imagen = f"static/images/hoteles/{id_hotel}.jpg"
    if os.path.exists(ruta_imagen):
        try:
            return Image.open(ruta_imagen)
        except Exception as e:
            print(f"Error al abrir imagen {ruta_imagen}: {e}")
            # Si hay un error al abrir la imagen específica, intentar con la por defecto
            ruta_default = "static/images/hoteles/default.jpg"
            if os.path.exists(ruta_default):
                try:
                    return Image.open(ruta_default)
                except Exception as e:
                    print( f"Error al abrir imagen por defecto {ruta_default}: {e}")
                    return None
            return None # O manejar el error de otra forma si la por defecto tampoco existe
    else:
        # Si la imagen específica no existe, usar la por defecto
        ruta_default = "static/images/hoteles/default.jpg"
        if os.path.exists(ruta_default):
            try:
                return Image.open(ruta_default)
            except Exception as e:
                print(f"Error al abrir imagen por defecto {ruta_default}: {e}")
                return None
        return None # Manejar el caso si no hay imagen por defecto

# Configuración de la página
st.set_page_config(
    page_title="Sistema Recomendador de Hoteles",
    page_icon="🏨",
    layout="wide"
)

# Estilos para el fondo de la aplicación principal
st.markdown("""
    <style>

    /* Asegurar que los contenedores de contenido no bloqueen el fondo */
    .main .block-container {
        background-color: transparent !important; /* Hacer el contenedor principal transparente */
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }

    /* Estilo específico para el contenedor de contenido cuando el usuario NO está logueado */
    /* Esto intenta hacer el fondo transparente para que se vea la imagen principal */
    .stApp:not([data-st-loggedin="true"]) .main .block-container {
        background-color: transparent !important;
        box-shadow: none !important; /* Eliminar cualquier sombra que pueda estar creando el efecto de cuadro */
    }

    /* Opcional: Asegurar que otros elementos comunes dentro del main sean transparentes si es necesario */
     .stTabs [data-testid="stVerticalBlock"],
     .stTextInput > div > div,
     .stTextArea > div > div,
     div[data-testid="stVerticalBlock"],
     div[data-testid="stHorizontalBlock"] {
         background-color: transparent !important;
     }

    

    /* Contenedor principal para las pestañas */
    .auth-tabs-container {
        display: flex;
        flex-direction: row; /* Pestañas en fila */
        justify-content: space-around; /* Espacio equitativo entre pestañas */
        margin-bottom: 15px;
    }

    /* Estilo base para cada pestaña */
    .auth-tab {
        padding: 10px 15px; /* Ajustar padding para que parezcan botones */
        cursor: pointer; /* Cursor de mano */
        color: #ffffff; /* Color de texto inactivo (blanco por defecto) */
        font-weight: bold; /* Texto en negrita */
        transition: all 0.3s ease-in-out; /* Transición suave */
        text-decoration: none; /* Remover subrayado del enlace */
        background-color: rgba(255, 255, 255, 0.1); /* Fondo ligeramente visible para inactivo */
        border-radius: 5px 5px 0 0; /* Bordes redondeados solo arriba */
        flex-grow: 1; /* Asegura que las pestañas compartan el espacio horizontal */
        text-align: center; /* Centrar texto */
    }

    .auth-tab:hover {
         color: #ffffff; /* Color de texto blanco al pasar el mouse */
         background-color: rgba(255, 255, 255, 0.2); /* Fondo un poco más visible al pasar el mouse */
    }

    /* Estilo para la pestaña activa */
    .auth-tab.active {
        border-bottom: none; /* Eliminar borde inferior para la pestaña activa */
        color: white; /* Color de texto blanco para la pestaña activa */
        background-color: #007bff; /* Fondo azul sólido para la pestaña activa */
    }

     /* Asegurar que la pestaña inactiva tenga un fondo claro si la activa tiene fondo oscuro y viceversa */
    .auth-tab:not(.active) {
         background-color: #f0f2f6; /* Un color gris claro/blanco para la pestaña inactiva */
         color: #4a4a4a; /* Color de texto oscuro para la pestaña inactiva */
    }

     .auth-tab:not(.active):hover {
         background-color: #e0e0e0; /* Un color gris un poco más oscuro al pasar el mouse */
         color: #4a4a4a; /* Mantener color de texto oscuro */
    }

     /* Estilos para los formularios y elementos dentro de la sidebar */
    div[data-testid="stSidebar"] div.stForm {
         margin: 0; 
         padding: 15px; 
         box-shadow: none;
         background-color: transparent;
    }

    div[data-testid="stSidebar"] input[type="text"], 
    div[data-testid="stSidebar"] input[type="password"],
    div[data-testid="stSidebar"] .stButton button {
         width: 100%; 
         margin-bottom: 10px; 
    }

    div[data-testid="stSidebar"] .stButton button {
        background-color: #007bff; 
        color: white;
        padding: 10px;
        border-radius: 5px;
        border: none;
    }

     div[data-testid="stSidebar"] .stCheckbox div:first-child {
        margin-right: 5px; 
     }
     div[data-testid="stSidebar"] .stMarkdown div:first-child {
        font-size: smaller; 
     }

    </style>
    """, unsafe_allow_html=True)

# Estilos para el fondo de la aplicación principal y las tarjetas de hoteles
st.markdown("""
    <style>
    /* Aplicar fondo al contenedor principal del contenido */
    .main {
        background-image: url('https://images.unsplash.com/photo-1560769629-975ec148e202?q=80&w=2850&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'); /* Nueva Imagen de Unsplash */
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    /* Intentar aplicar fondo al cuerpo de la página como respaldo */
    body {
        background-image: url('https://images.unsplash.com/photo-1560769629-975ec148e202?q=80&w=2850&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'); /* Nueva Imagen de Unsplash */
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    /* Asegurar que los contenedores de contenido no bloqueen el fondo */
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.1); /* Fondo blanco semi-transparente para el contenido general */
        padding: 20px; /* Espacio interno */
        border-radius: 10px; /* Bordes redondeados */
        margin-top: 20px; /* Margen superior */
        box-sizing: border-box; /* Incluir padding y borde en el tamaño total */
    }

    /* Estilo para los contenedores de los hoteles dentro de las columnas (tarjetas) */
    .main [data-testid="stVerticalBlock"] {
        background-color: rgba(30, 30, 30, 0.8); /* Fondo oscuro semi-transparente */
        border: 1px solid rgba(200, 200, 200, 0.3); /* Borde sutil más visible */
        border-radius: 10px; /* Bordes redondeados */
        padding: 10px; /* Espacio interno, reducido un poco */
        margin-bottom: 20px; /* Espacio entre tarjetas en diferentes filas */
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2); /* Sombra suave */
        color: #ffffff; /* Color de texto por defecto para elementos dentro de la tarjeta */
        box-sizing: border-box; /* Incluir padding y borde en el tamaño total */
    }

    /* Asegurar que la imagen tenga medidas uniformes y use todo el ancho de la tarjeta */
    .main [data-testid="stVerticalBlock"] img {
        width: 100%; /* Asegurar que la imagen ocupe el ancho del contenedor */
        height: 140px; /* Altura fija para uniformidad, reducida un poco */
        object-fit: cover; /* Cubrir el área manteniendo la proporción, recortando si es necesario */
        border-radius: 8px; /* Bordes redondeados para la imagen */
        margin-bottom: 10px; /* Espacio debajo de la imagen */
    }

    /* Ajustar estilos de texto para legibilidad */
    .main [data-testid="stVerticalBlock"] h3 {
        color: #ffffff; /* Color de texto blanco para títulos */
        margin-top: 0; /* Eliminar margen superior extra del título */
        margin-bottom: 10px; /* Espacio debajo del título */
    }

    .main [data-testid="stVerticalBlock"] p {
         color: #f0f0f0; /* Color de texto blanco ligeramente más claro para párrafos */
         margin-bottom: 8px; /* Espacio debajo de los párrafos */
    }

    /* Ajustar el botón para que se vea bien en la tarjeta y sea más pequeño */
    .main [data-testid="stVerticalBlock"] .stButton button {
        width: 50%; /* Botón que ocupe todo el ancho de la tarjeta */
        background-color: #007bff; /* Color de fondo del botón */
        color: white; /* Color de texto del botón */
        padding: 8px 8px; /* Espacio interno del botón (reducido) */
        border-radius: 7px; /* Bordes redondeados del botón */
        border: none; /* Sin borde en el botón */
        margin-top: 8px; /* Espacio encima del botón (reducido) */
        font-size: 14px; /* Tamaño de fuente más pequeño */
        transition: background-color 0.3s ease; /* Transición suave para el hover */
    }

    .main [data-testid="stVerticalBlock"] .stButton button:hover {
        background-color: #0056b3; /* Color más oscuro al pasar el ratón */
    }

     /* Eliminar fondos blancos por defecto de elementos específicos dentro de las tarjetas */
     .main [data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"],
     .main [data-testid="stVerticalBlock"] [data-testid="stHorizontalBlock"],
     .main [data-testid="stVerticalBlock"] .stMarkdown,
     .main [data-testid="stVerticalBlock"] p,
     .main [data-testid="stVerticalBlock"] h3 {
         background-color: transparent !important; /* Forzar transparencia para que se vea el fondo de la tarjeta */
         color: inherit; /* Heredar el color de texto de la tarjeta */
     }

    /* Asegurar que la capa por defecto de Streamlit no oscurezca la imagen de fondo */
    .stApp > header,
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* Ajustar la barra lateral para que tenga un fondo */
    [data-testid="stSidebar"] {
        background-color: rgba(49, 51, 63, 0.95); /* Fondo oscuro semi-transparente para la sidebar */
        padding: 20px; /* Añadir padding a la sidebar */
    }

    /* Asegurar que el contenido de la sidebar sea legible */
     [data-testid="stSidebar"] .stSidebarContent {
         background-color: transparent !important;
         color: #ffffff; /* Color de texto claro en la sidebar */
     }
     [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
         color: #ffffff; /* Color de texto claro para títulos en la sidebar */
     }

    /* Estilos para el menú de navegación (cuando se usa st.radio en la sidebar) */
    [data-testid="stSidebar"] .stRadio > label {
        padding: 10px; /* Espacio interno */
        margin-bottom: 0px; /* Eliminar espacio entre elementos */
        border-radius: 0px; /* Eliminar bordes redondeados */
        cursor: pointer; /* Cursor de mano */
        transition: background-color 0.3s ease;
        display: block; /* Hacer que ocupe todo el ancho */
        border-bottom: 1px solid rgba(255, 255, 255, 0.1); /* Añadir separador inferior */
    }

    [data-testid="stSidebar"] .stRadio > label:hover {
        background-color: rgba(255, 255, 255, 0.1); /* Fondo suave al pasar el ratón */
    }

    /* Estilo para la opción de menú seleccionada */
    [data-testid="stSidebar"] .stRadio > label.st-label-inline.css-1x8cdl9,
    [data-testid="stSidebar"] .stRadio > label[data-baseweb="radio"] input[checked] + div {
        background-color: #007bff; /* Fondo azul para la opción seleccionada */
        color: white; /* Texto blanco para la opción seleccionada */
    }

     /* Ocultar el círculo del radio button */
     [data-testid="stSidebar"] .stRadio [data-baseweb="radio"] label span:first-child {
        display: none !important;
     }

    /* Ajustar el padding de la sidebar para que el menú llegue a los bordes */
    [data-testid="stSidebar"] .stSidebarContent {
        padding-top: 0;
        padding-bottom: 0;
        padding-left: 15px; /* Ajustar según necesidad */
        padding-right: 15px; /* Ajustar según necesidad */
        background-color: transparent !important;
        color: #ffffff; /* Color de texto claro en la sidebar */
    }

    /* Asegurar que el título del menú tenga padding superior e inferior */
    [data-testid="stSidebar"] .stRadio > label:first-child {
        border-top: none; /* Asegurar que el primer elemento no tenga borde superior si no lo deseas */
    }

    </style>
    """, unsafe_allow_html=True)

# Inicializar estado de sesión para login y usuario
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'id_usuario' not in st.session_state:
    st.session_state['user_id'] = None
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = None
# Inicializar estado de sesión para la vista de detalles del hotel
if 'viewing_hotel_details' not in st.session_state:
    st.session_state['viewing_hotel_details'] = None

# Inicializar estado de sesión para la selección del menú no logueado
# Aseguramos que siempre tenga un valor por defecto al inicio
if 'auth_menu_selection' not in st.session_state or st.session_state['auth_menu_selection'] not in ["Iniciar Sesión", "Registrarse"]:
    st.session_state['auth_menu_selection'] = "Iniciar Sesión"

# Capturar la selección de la URL (o mantener el estado de sesión si no hay query param)
query_params = st.experimental_get_query_params()
if "auth_menu_selection" in query_params:
    # Actualizar el estado de sesión con la selección de la URL
    st.session_state['auth_menu_selection'] = query_params['auth_menu_selection'][0]
    # Opcional: limpiar query params después de usar si no quieres que persistan en la URL
    # st.experimental_set_query_params(auth_menu_selection=[]) # Descomentar si se desea limpiar la URL

# Inicializar el sistema de recomendación (solo se inicializa una vez por sesión con st.cache_resource)
@st.cache_resource
def inicializar_sistema():
    print("Iniciando sistema...") # Mensaje para depuración
    sistema = SistemaRecomendacion()
    sistema.cargar_datos()
    return sistema

sistema = None # Inicializar sistema como None por defecto

# --- SIDEBAR: Título de la Aplicación ---
if st.session_state.get('logged_in') and st.session_state.get('user_name'):
    st.sidebar.title(f"Hola, {st.session_state['user_name']}")
else:
    st.sidebar.title("🏨 Sistema Recomendador")

# Lógica condicional para mostrar contenido según el estado de login
if not st.session_state['logged_in']:
    # --- SIDEBAR: Menú de Autenticación (estilo pestañas con HTML/CSS) ---
    st.sidebar.markdown("---") # Separador visual
   
    # HTML para las pestañas con manejo de clics
    login_class = "auth-tab active" if st.session_state['auth_menu_selection'] == "Iniciar Sesión" else "auth-tab"
    register_class = "auth-tab active" if st.session_state['auth_menu_selection'] == "Registrarse" else "auth-tab"

    st.sidebar.markdown(f"""
    <div class="auth-tabs-container">
        <a href="?auth_menu_selection=Iniciar Sesión" class="{login_class}" target="_self">Iniciar Sesión</a>
        <a href="?auth_menu_selection=Registrarse" class="{register_class}" target="_self">Registrarse</a>
    </div>
    """, unsafe_allow_html=True)

    # --- SIDEBAR: Contenido de Autenticación (formularios en la sidebar) ---
    # Mostrar el contenido en la sidebar basado en la selección del estado de sesión

    # Mostrar el formulario de login si la opción 'Iniciar Sesión' está seleccionada y no está logueado
    if not st.session_state['logged_in'] and st.session_state.get('auth_menu_selection') == "Iniciar Sesión":
     
     
        # --- Formulario de Login (en la sidebar) ---
        with st.sidebar.form("login_form_sidebar"):
            st.subheader("Incia Sesión")
            user_email = st.text_input("Correo electrónico", key='login_email_sidebar')
            user_password = st.text_input("Contraseña", type="password", key='login_password_sidebar')

            col_remember, col_forgot = st.columns(2)
            with col_remember:
                st.checkbox("Recordar")
            with col_forgot:
                st.markdown("<div style='text-align: right;'><a href='#'>Olvidé contraseña</a></div>", unsafe_allow_html=True)

            st.write("")

            login_button = st.form_submit_button("Iniciar sesión")

            # Placeholder para mostrar mensajes de error de login dentro del form
            login_error_placeholder = st.empty()

            if login_button:
                # Limpiar cualquier mensaje de error previo al intentar loguear de nuevo
                login_error_placeholder.empty()

                try:
                    conn = mysql.connector.connect(**DB_CONFIG)
                    cursor = conn.cursor()
                    cursor.execute("SELECT id_usuario, nombre FROM usuario WHERE email = %s AND password = %s", 
                                 (user_email, user_password))
                    usuario = cursor.fetchone()
                    cursor.close()
                    conn.close()

                    if usuario:
                        # Si el login es exitoso, actualizamos el estado y forzamos una reejecución
                        st.session_state['logged_in'] = True
                        st.session_state['id_usuario'] = usuario[0] # Usar 'id_usuario' según la base de datos
                        st.session_state['user_name'] = usuario[1]
                        st.experimental_rerun() # Forzar reejecución para mostrar el contenido logueado (compatible con versiones anteriores)
                    else:
                        # Si el login falla, mostramos el error en el placeholder
                        login_error_placeholder.error("Correo electrónico o contraseña incorrectos.")

                except Exception as e:
                    # Este error se mostrará si hay un problema de conexión a la BD, por ejemplo
                 
                    print(f"Error técnico al intentar iniciar sesión: {e}") # Imprimir error técnico en consola

    # Mostrar el formulario de registro si la opción 'Registrarse' está seleccionada y no está logueado
    elif not st.session_state['logged_in'] and st.session_state.get('auth_menu_selection') == "Registrarse":

        # --- Formulario de Registro (en la sidebar) ---
        with st.sidebar.form("registro_usuario_sidebar"):
            st.subheader("📝 Registro de Usuario")
            nombre = st.text_input("Nombre completo", key='register_nombre_sidebar')
            email = st.text_input("Email", key='register_email_sidebar')
            password = st.text_input("Contraseña", type="password", key='register_password_sidebar')
            edad = st.number_input("Edad", min_value=1, max_value=120, step=1, key='register_edad_sidebar')
            genero = st.selectbox("Género", ("F", "M", "Otro"), key='register_genero_sidebar')
            submit = st.form_submit_button("Registrar")
            if submit:
                if nombre.strip() == "" or email.strip() == "" or password.strip() == "":
                    st.warning("Por favor, completa todos los campos obligatorios.")
                else:
                    try:
                        conn = mysql.connector.connect(**DB_CONFIG)
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO usuario (nombre, email, password, edad, genero) VALUES (%s, %s, %s, %s, %s)",
                            (nombre, email, password, edad, genero)
                        )
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success("¡Usuario registrado exitosamente! Ahora puedes iniciar sesión.")
                        # Cambiar a la opción de Iniciar Sesión en la sidebar después del registro exitoso
                        st.session_state['auth_menu_selection'] = "Iniciar Sesión"
                        st.experimental_rerun() # Usar experimental_rerun con query_params
                    except Exception as e:
                        st.error(f"Error al registrar usuario: {e}")

    # --- CONTENIDO PRINCIPAL (si no está logueado) ---
    # Mostrar contenido principal basado en la selección de la sidebar no logueada
    # Solo mostramos el contenido principal si no está logueado Y la selección NO es Iniciar Sesión o Registrarse
    # Esto asegura que al inicio, con 'Iniciar Sesión' seleccionado por defecto, solo se vea la barra lateral de login/registro
    if not st.session_state['logged_in']:
        # CSS para el fondo del contenido principal cuando no está logueado y no muestra formularios auth
        

        # --- Mensaje de bienvenida en el contenido principal (cuando no está logueado) ---
        st.title("🏨 ¡Bienvenido al Sistema Recomendador de Hoteles de Cartagena!  Aqui encontraras el hotel de tu prefenrencia y tus gustos ")
        st.markdown("Por favor, inicia sesión en la barra lateral izquierda.")

        # Contenido adicional para usuarios no logueados (si es necesario, actualmente solo la visualización de usuarios registrados si se selecciona esa opción)
        if st.session_state.get('auth_menu_selection') == "Usuarios registrados": # Aunque ya quitamos esta opción del menú inicial
             
         

            # --- Visualización de usuarios (en el contenido principal) ---
            st.subheader("👥 Usuarios Registrados")
            # Inicializar sistema solo si se necesita para esta sección (acceso a BD)
            if sistema is None:
                 sistema = inicializar_sistema()
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                usuarios_df = pd.read_sql("SELECT id_usuario, nombre, email, edad, genero FROM usuario", conn)
                conn.close()
                st.dataframe(usuarios_df)
            except Exception as e:
                st.error(f"Error al cargar usuarios: {e}")
        # El bloque else anterior que mostraba el mensaje de bienvenida ya no es necesario aquí

elif st.session_state['logged_in']:
    # --- CONTENIDO: Sistema Recomendador (si está logueado) ---
    # Inicializar sistema solo si es necesario para las funcionalidades principales (acceso a BD)
    if sistema is None:
        sistema = inicializar_sistema()

    # --- SIDEBAR: Menú desplegable (si está logueado) ---
    # Definir opciones de menú para usuarios logueados con íconos
    all_menu_options = [
        "🏠 Inicio",
        "🏨 Reservar",
        "⭐ Favoritos",
        "🌟 Mis Valoraciones",
        "📊 Mis Interacciones",
        "👤 Mi Cuenta",
        "📝 Registro de usuario",
        "👥 Usuarios registrados"
    ]

    # Filtrar opciones basadas en si el usuario es admin
    if st.session_state.get('user_name') == 'admin':
        menu_options_logged_in = [opt for opt in all_menu_options if opt not in ["📝 Registro de usuario", "👤 Mi Cuenta"]]
    else:
        menu_options_logged_in = [opt for opt in all_menu_options if opt not in ["📝 Registro de usuario", "👥 Usuarios registrados"]]

    # Usar un radio button en lugar de selectbox para un menú más estático
    menu = st.sidebar.radio(
        "Menú",
        menu_options_logged_in,
        key='main_menu_radio_logged_in'
    )

    # --- SIDEBAR: Favoritos (por sesión - se mantiene en la sidebar si está logueado) ---
    if 'favoritos' not in st.session_state:
        st.session_state['favoritos'] = []

    if menu == "⭐ Favoritos":
        st.sidebar.title("⭐ Tus Favoritos")
        hoteles_df = sistema.hoteles_df if sistema is not None else None
        if st.session_state['favoritos']:
            st.write("Aquí están tus hoteles favoritos:")
            num_columnas = 2
            columnas = st.columns(num_columnas)

            if hoteles_df is not None and not hoteles_df.empty:
                for i, fav_nombre in enumerate(st.session_state['favoritos']):
                    hotel_info = hoteles_df[hoteles_df['nombre'] == fav_nombre]
                    if not hotel_info.empty:
                        hotel = hotel_info.iloc[0]
                        with columnas[i % num_columnas]:
                            st.subheader(hotel['nombre'])
                            ruta_imagen = obtener_imagen_hotel(hotel['id_hotel'])
                            if ruta_imagen:
                                st.image(ruta_imagen, use_column_width=True)
                            st.write(f"**Categoría:** {hotel['categoria']}")
                            st.write(f"**Precio promedio:** ${hotel['precio_promedio']:,.2f}")
                            st.write(f"**Ubicación:** {hotel['ubicacion']}")
                            st.write(f"**Descripción:** {hotel['descripcion'][:150]}...")
                            if st.button(f"Quitar de favoritos", key=f"del_fav_main_{hotel['id_hotel']}"):
                                try:
                                    hotel_id = int(hotel['id_hotel'])
                                    conn = mysql.connector.connect(**DB_CONFIG)
                                    cursor = conn.cursor()
                                    cursor.execute(
                                        "INSERT INTO interacciones_usuario (id_usuario, id_hotel, accion, valor) VALUES (%s, %s, %s, %s)",
                                        (st.session_state['id_usuario'], hotel_id, 'favorito', 0.0)
                                    )
                                    conn.commit()
                                    cursor.close()
                                    conn.close()
                                    st.session_state['favoritos'].remove(fav_nombre)
                                    st.experimental_rerun()
                                except Exception as e:
                                    st.error(f"Error al quitar favorito: {e}")
                    else:
                        st.warning(f"Información no encontrada para el hotel favorito: {fav_nombre}")
            else:
                st.error("No se pudieron cargar los datos de los hoteles.")
        else:
            st.info("Aún no tienes favoritos. Agrega desde la sección de Inicio o Explorar.")

    # --- Contenido principal basado en el menú ---
    if menu == "🏠 Inicio":
        st.markdown("""
        # 🏨 Sistema Recomendador de Hoteles
        
        Bienvenido al sistema que te ayuda a descubrir los mejores hoteles de Cartagena según tus gustos y los de otros usuarios.
        """)

        if 'hotel_to_reserve' not in st.session_state or st.session_state['hotel_to_reserve'] is None:
            pestanas = st.tabs(["🔍 Buscar por características", "👤 Recomendaciones personalizadas", "🏨 Explorar hoteles"])
            
            with pestanas[0]:
                st.subheader("Buscar hoteles según tus preferencias")
                descripcion = st.text_area(
                    "Describe lo que buscas en un hotel (servicios, ubicación, etc.):",
                    height=100,
                    placeholder="Ejemplo: piscina, spa, restaurante gourmet, centro histórico..."
                )
                if st.button("Buscar hoteles similares", key="buscar_caracteristicas"):
                    if descripcion.strip():
                        sistema = inicializar_sistema() if sistema is None else sistema

                        if sistema and not sistema.hoteles_df.empty:
                            recomendaciones = sistema.recomendar_por_caracteristicas(descripcion)
                            if recomendaciones:
                                st.success("Resultados encontrados:")
                                num_columnas = 2
                                columnas = st.columns(num_columnas)
                                for i, (id_hotel, similitud) in enumerate(recomendaciones):
                                    with columnas[i % num_columnas]:
                                        hotel = sistema.hoteles_df[sistema.hoteles_df['id_hotel'] == id_hotel].iloc[0]
                                        st.subheader(hotel['nombre'])
                                        ruta_imagen = obtener_imagen_hotel(hotel['id_hotel'])
                                        if ruta_imagen:
                                            st.image(ruta_imagen, use_column_width=True)
                                        st.write(f"**Categoría:** {hotel['categoria']}")
                                        st.write(f"**Precio promedio:** ${hotel['precio_promedio']:,.2f}")
                                        st.write(f"**Ubicación:** {hotel['ubicacion']}")
                                        st.write(f"**Descripción:** {hotel['descripcion'][:150]}...")
                                        st.progress(min(similitud, 1.0))
                                        if st.button(f"Agregar a favoritos", key=f"fav_carac_{id_hotel}"):
                                            if hotel['nombre'] not in st.session_state['favoritos']:
                                                st.session_state['favoritos'].append(hotel['nombre'])
                                                st.success(f"Agregado a favoritos: {hotel['nombre']}")
                                        if st.button("Ver Detalles", key=f"details_carac_{id_hotel}"):
                                            st.session_state['viewing_hotel_details'] = hotel['id_hotel']
                                            st.experimental_rerun()
                            else:
                                st.info("No se encontraron hoteles similares con esa descripción.")
                        elif sistema is None:
                            st.warning("El sistema de recomendación no está inicializado. No se pueden buscar hoteles.")
                        else:
                            st.warning("No se encontraron hoteles disponibles para la búsqueda.")
                    else:
                        st.warning("Por favor, ingresa una descripción para buscar hoteles.")

            with pestanas[1]:
                st.subheader("Recomendaciones según tu historial")
                user_id_input_value = st.session_state['id_usuario'] if st.session_state['logged_in'] and st.session_state['id_usuario'] else 1
                id_usuario = st.number_input("Ingresa tu ID de usuario:", min_value=1, step=1, value=user_id_input_value, key="user_id_reco_input")

                if st.button("Obtener recomendaciones", key="recomendar_usuario"):
                    if id_usuario:
                        sistema = inicializar_sistema() if sistema is None else sistema
                        if sistema and sistema.matriz_ratings is not None and not sistema.matriz_ratings.empty:
                            recomendaciones = sistema.recomendar_por_usuario(id_usuario)
                            if recomendaciones:
                                st.success("Tus recomendaciones:")
                                num_columnas = 2
                                columnas = st.columns(num_columnas)
                                for i, (hotel_id, puntuacion) in enumerate(recomendaciones):
                                    with columnas[i % num_columnas]:
                                        hotel = sistema.hoteles_df[sistema.hoteles_df['id_hotel'] == hotel_id].iloc[0]
                                        st.subheader(hotel['nombre'])
                                        ruta_imagen = obtener_imagen_hotel(hotel['id_hotel'])
                                        if ruta_imagen:
                                            st.image(ruta_imagen, use_column_width=True)
                                        st.write(f"**Puntuación estimada:** {puntuacion:.2f}")
                                        st.write(f"**Categoría:** {hotel['categoria']}")
                                        st.write(f"**Precio promedio:** ${hotel['precio_promedio']:,.2f}")
                                        st.write(f"**Ubicación:** {hotel['ubicacion']}")
                                        st.write(f"**Descripción:** {hotel['descripcion'][:150]}...")
                                        st.progress(min(puntuacion if pd.notna(puntuacion) else 0.0, 1.0))
                                        if st.button(f"Agregar a favoritos", key=f"fav_recom_{hotel_id}"):
                                            if hotel['nombre'] not in st.session_state['favoritos']:
                                                st.session_state['favoritos'].append(hotel['nombre'])
                                                st.success(f"Agregado a favoritos: {hotel['nombre']}")
                                        if st.button("Ver Detalles ", key=f"details_recom_{hotel_id}"):
                                             st.session_state['viewing_hotel_details'] = hotel_id
                                             st.experimental_rerun()
                            else:
                                st.info("No hay suficientes datos para generar recomendaciones personalizadas. ¡Interactúa con algunos hoteles!")
                        elif sistema is None:
                            st.warning("El sistema de recomendación no está inicializado. No se pueden generar recomendaciones.")
                        else:
                            st.info("No hay suficientes datos (valoraciones) para generar recomendaciones personalizadas.")
                    else:
                        st.warning("Por favor, ingresa tu ID de usuario para recibir recomendaciones.")

            with pestanas[2]:
                st.subheader("Explora todos los hoteles disponibles")
                with st.container():
                    col1, col2 = st.columns(2)
                    with col1:
                        categoria = st.selectbox("Categoría:", ["Todas", "5 estrellas", "4 estrellas", "3 estrellas"])
                    with col2:
                        precio_max = st.slider("Precio máximo por noche:", 300000, 1000000, 1000000, step=50000)

                sistema = inicializar_sistema() if sistema is None else sistema

                if sistema and not sistema.hoteles_df.empty:
                    hoteles_filtrados = sistema.hoteles_df
                    if categoria != "Todas":
                        hoteles_filtrados = hoteles_filtrados[hoteles_filtrados['categoria'] == categoria]
                    hoteles_filtrados = hoteles_filtrados[hoteles_filtrados['precio_promedio'] <= precio_max]
                    if len(hoteles_filtrados) == 0:
                        st.warning("No hay hoteles que cumplan con los filtros seleccionados.")
                    else:
                        num_columnas = 2
                        columnas = st.columns(num_columnas)
                        for i, (_, hotel) in enumerate(hoteles_filtrados.iterrows()):
                            with columnas[i % num_columnas]:
                                st.subheader(hotel['nombre'])
                                ruta_imagen = obtener_imagen_hotel(hotel['id_hotel'])
                                if ruta_imagen:
                                    st.image(ruta_imagen, use_column_width=True)
                                st.write(f"**Categoría:** {hotel['categoria']}")
                                st.write(f"**Precio promedio:** ${hotel['precio_promedio']:,.2f}")
                                st.write(f"**Ubicación:** {hotel['ubicacion']}")
                                st.write(f"**Descripción:** {hotel['descripcion'][:150]}...")
                                if st.button(f"Agregar a favoritos", key=f"fav_expl_{hotel['id_hotel']}"):
                                    if hotel['nombre'] not in st.session_state['favoritos']:
                                        st.session_state['favoritos'].append(hotel['nombre'])
                                        st.success(f"Agregado a favoritos: {hotel['nombre']}")
                                if st.button("Ver Detalles", key=f"details_expl_{hotel['id_hotel']}"):
                                    st.session_state['viewing_hotel_details'] = hotel['id_hotel']
                                    st.experimental_rerun()
                elif sistema is None:
                    st.warning("El sistema de recomendación no está inicializado. No se pueden explorar hoteles.")
                else:
                    st.warning("No se encontraron hoteles disponibles para explorar.")

    elif menu == "🏨 Reservar":
        st.subheader("🏨 Realizar y ver Reservas")
        
        # Crear dos columnas para la sección de reservas
        col_reserva, col_historial = st.columns([2, 1])
        
        with col_reserva:
            st.markdown("### 📅 Realizar nueva reserva")
            st.markdown("---")
            
            # Sección para seleccionar hotel
            sistema = inicializar_sistema() if sistema is None else sistema
            
            if sistema is not None and not sistema.hoteles_df.empty:
                # Mostrar información del hotel seleccionado
                hotel_names = sistema.hoteles_df['nombre'].tolist()
                selected_hotel_name = st.selectbox("Selecciona un hotel:", hotel_names, key='select_hotel_to_reserve')
                
                if selected_hotel_name:
                    hotel_info = sistema.hoteles_df[sistema.hoteles_df['nombre'] == selected_hotel_name].iloc[0]
                    
                    # Mostrar detalles del hotel en una tarjeta
                    with st.container():
                        st.markdown(f"""
                        <div style='background-color: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 10px; margin: 10px 0;'>
                            <h3 style='color: #ffffff;'>{hotel_info['nombre']}</h3>
                            <p style='color: #f0f0f0;'>📍 {hotel_info['ubicacion']}</p>
                            <p style='color: #f0f0f0;'>⭐ {hotel_info['categoria']}</p>
                            <p style='color: #f0f0f0;'>💰 Precio promedio: ${hotel_info['precio_promedio']:,.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Mostrar imagen del hotel
                        ruta_imagen = obtener_imagen_hotel(hotel_info['id_hotel'])
                        if ruta_imagen:
                            st.image(ruta_imagen, use_column_width=True)
                    
                    # Formulario de reserva
                    st.markdown("### 📝 Detalles de la reserva")
                    with st.form("formulario_reserva"):
                        # Fechas de entrada y salida
                        col_fechas = st.columns(2)
                        with col_fechas[0]:
                            fecha_entrada = st.date_input("Fecha de entrada", min_value=datetime.now().date())
                        with col_fechas[1]:
                            fecha_salida = st.date_input("Fecha de salida", min_value=fecha_entrada)
                        
                        # Número de huéspedes y tipo de habitación
                        col_habitacion = st.columns(2)
                        with col_habitacion[0]:
                            num_huespedes = st.number_input("Número de huéspedes", min_value=1, max_value=10, value=2)
                        with col_habitacion[1]:
                            tipo_habitacion = st.selectbox("Tipo de habitación", 
                                ["Habitación Estándar", "Habitación Deluxe", "Suite", "Suite Presidencial"])
                        
                        # Servicios adicionales
                        st.markdown("### 🛎️ Servicios adicionales")
                        col_servicios = st.columns(3)
                        with col_servicios[0]:
                            desayuno = st.checkbox("Desayuno incluido")
                        with col_servicios[1]:
                            traslado = st.checkbox("Servicio de traslado")
                        with col_servicios[2]:
                            spa = st.checkbox("Acceso al spa")
                        
                        # Solicitudes especiales
                        solicitudes = st.text_area("Solicitudes especiales", 
                            placeholder="Ej: Cama king size, vista al mar, habitación para no fumadores...")
                        
                        # Resumen de la reserva
                        st.markdown("### 📊 Resumen de la reserva")
                        noches = (fecha_salida - fecha_entrada).days
                        precio_base = hotel_info['precio_promedio'] * noches
                        servicios_adicionales = sum([
                            50000 if desayuno else 0,
                            30000 if traslado else 0,
                            100000 if spa else 0
                        ])
                        total = precio_base + servicios_adicionales
                        
                        st.markdown(f"""
                        <div style='background-color: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 10px; margin: 10px 0;'>
                            <p style='color: #f0f0f0;'>🏨 Hotel: {hotel_info['nombre']}</p>
                            <p style='color: #f0f0f0;'>📅 Noches: {noches}</p>
                            <p style='color: #f0f0f0;'>👥 Huéspedes: {num_huespedes}</p>
                            <p style='color: #f0f0f0;'>🛏️ Habitación: {tipo_habitacion}</p>
                            <p style='color: #f0f0f0;'>💰 Precio base: ${precio_base:,.2f}</p>
                            <p style='color: #f0f0f0;'>➕ Servicios adicionales: ${servicios_adicionales:,.2f}</p>
                            <h4 style='color: #ffffff;'>Total: ${total:,.2f}</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Botón de confirmación
                        if st.form_submit_button("Confirmar Reserva", use_container_width=True):
                            try:
                                conn = mysql.connector.connect(**DB_CONFIG)
                                cursor = conn.cursor()
                                
                                # Registrar la reserva en la base de datos
                                sql_insert_reserva = """
                                INSERT INTO interacciones_usuario 
                                (id_usuario, id_hotel, accion, valor, fecha) 
                                VALUES (%s, %s, %s, %s, %s)
                                """
                                cursor.execute(sql_insert_reserva, (
                                    st.session_state['id_usuario'],
                                    hotel_info['id_hotel'],
                                    'reserva',
                                    float(total),
                                    datetime.now()
                                ))
                                
                                conn.commit()
                                st.success("¡Reserva confirmada con éxito! Recibirás un correo con los detalles.")
                                st.balloons()
                                
                            except Exception as e:
                                st.error(f"Error al procesar la reserva: {e}")
                            finally:
                                if cursor: cursor.close()
                                if conn: conn.close()
            else:
                st.warning("No se encontraron hoteles disponibles.")
        
        with col_historial:
            st.markdown("### 📋 Historial de Reservas")
            st.markdown("---")
            
            try:
                conn_history = mysql.connector.connect(**DB_CONFIG)
                cursor_history = conn_history.cursor(dictionary=True)
                sql_select_reservas = """
                SELECT
                    h.nombre AS Nombre_Hotel,
                    i.fecha AS Fecha_Reserva,
                    i.valor AS Monto_Total
                FROM interacciones_usuario i
                JOIN hoteles h ON i.id_hotel = h.id_hotel
                WHERE i.id_usuario = %s AND i.accion = 'reserva'
                ORDER BY i.fecha DESC
                """
                cursor_history.execute(sql_select_reservas, (st.session_state['id_usuario'],))
                historial_reservas = cursor_history.fetchall()
                
                if historial_reservas:
                    for reserva in historial_reservas:
                        with st.container():
                            st.markdown(f"""
                            <div style='background-color: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 10px; margin: 10px 0;'>
                                <h4 style='color: #ffffff;'>{reserva['Nombre_Hotel']}</h4>
                                <p style='color: #f0f0f0;'>📅 {reserva['Fecha_Reserva'].strftime('%d/%m/%Y %H:%M')}</p>
                                <p style='color: #f0f0f0;'>💰 ${float(reserva['Monto_Total']):,.2f}</p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("Aún no tienes reservas registradas.")
            except Exception as e:
                st.error(f"Error al cargar el historial de reservas: {e}")
            finally:
                if cursor_history: cursor_history.close()
                if conn_history: conn_history.close()

    elif menu == "🌟 Mis Valoraciones":
        st.subheader("🌟 Tus Valoraciones")

        # Sección para enviar una nueva valoración
        st.markdown("### Enviar nueva valoración")
        sistema = inicializar_sistema() if sistema is None else sistema

        if sistema is not None and not sistema.hoteles_df.empty:
            hotel_names = sistema.hoteles_df['nombre'].tolist()
            selected_hotel_name_rating = st.selectbox("Selecciona un hotel para valorar:", hotel_names, key='select_hotel_rating')
            rating_value = st.slider("Tu valoración (1=Malo, 5=Excelente):", 1, 5, 3, key='rating_slider')

            if st.button("Enviar Valoración", key='submit_rating_button'):
                try:
                    conn = mysql.connector.connect(**DB_CONFIG)
                    cursor = conn.cursor()
                    hotel_id_to_rate = sistema.hoteles_df[sistema.hoteles_df['nombre'] == selected_hotel_name_rating]['id_hotel'].iloc[0]
                    sql_check_rating = "SELECT id_valoracion FROM valoraciones WHERE id_usuario = %s AND id_hotel = %s"
                    cursor.execute(sql_check_rating, (st.session_state['id_usuario'], hotel_id_to_rate))
                    existing_rating = cursor.fetchone()

                    if existing_rating:
                        sql_update_rating = "UPDATE valoraciones SET puntuacion = %s, fecha_valoracion = CURRENT_TIMESTAMP WHERE id_valoracion = %s"
                        cursor.execute(sql_update_rating, (rating_value, existing_rating[0]))
                        st.success(f"Valoración actualizada para {selected_hotel_name_rating}.")
                    else:
                        sql_insert_rating = "INSERT INTO valoraciones (id_usuario, id_hotel, puntuacion) VALUES (%s, %s, %s)"
                        cursor.execute(sql_insert_rating, (st.session_state['id_usuario'], hotel_id_to_rate, rating_value))
                        st.success(f"Valoración registrada para {selected_hotel_name_rating}.")

                    sql_insert_interaccion_rating = "INSERT INTO interacciones_usuario (id_usuario, id_hotel, accion, valor) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql_insert_interaccion_rating, (st.session_state['id_usuario'], hotel_id_to_rate, 'valoracion', float(rating_value)))
                    conn.commit()
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error al enviar la valoración: {e}")
                finally:
                    if cursor: cursor.close()
                    if conn: conn.close()
        else:
            st.warning("No se encontraron hoteles disponibles para valorar.")

        st.markdown("---")

        # Sección para ver historial de valoraciones
        st.markdown("### Tu Historial de Valoraciones")
        try:
            conn_history = mysql.connector.connect(**DB_CONFIG)
            cursor_history = conn_history.cursor(dictionary=True)
            sql_select_valoraciones = """
            SELECT
                h.nombre AS Nombre_Hotel,
                v.puntuacion AS Tu_Valoracion,
                v.fecha_valoracion AS Fecha_Valoracion
            FROM valoraciones v
            JOIN hoteles h ON v.id_hotel = h.id_hotel
            WHERE v.id_usuario = %s
            ORDER BY v.fecha_valoracion DESC
            """
            cursor_history.execute(sql_select_valoraciones, (st.session_state['id_usuario'],))
            historial_valoraciones = cursor_history.fetchall()
            if historial_valoraciones:
                valoraciones_df = pd.DataFrame(historial_valoraciones)
                valoraciones_df['Fecha_Valoracion'] = pd.to_datetime(valoraciones_df['Fecha_Valoracion']).dt.strftime('%d/%m/%Y %H:%M')
                st.dataframe(valoraciones_df, use_container_width=True, hide_index=True)
            else:
                st.info("Aún no tienes valoraciones registradas.")
        except Exception as e:
            st.error(f"Error al cargar el historial de valoraciones: {e}")
        finally:
            if cursor_history: cursor_history.close()
            if conn_history: conn_history.close()

    elif menu == "📊 Mis Interacciones":
        st.subheader("📊 Tu Historial Completo de Interacciones")
        st.markdown("Aquí puedes ver todas las acciones que has realizado en el sistema (vistas, favoritos, reservas, valoraciones).")

        try:
            conn_history = mysql.connector.connect(**DB_CONFIG)
            cursor_history = conn_history.cursor(dictionary=True)
            sql_select_user_interacciones = """
            SELECT
                h.nombre AS Nombre_Hotel,
                i.accion AS Tipo_Interaccion,
                i.valor AS Valor_Asociado,
                i.fecha AS Fecha_Interaccion
            FROM interacciones_usuario i
            JOIN hoteles h ON i.id_hotel = h.id_hotel
            WHERE i.id_usuario = %s
            ORDER BY i.fecha DESC
            """
            cursor_history.execute(sql_select_user_interacciones, (st.session_state['id_usuario'],))
            user_interacciones = cursor_history.fetchall()

            if user_interacciones:
                interacciones_df = pd.DataFrame(user_interacciones)
                interacciones_df['Tipo_Interaccion'] = interacciones_df['Tipo_Interaccion'].map({
                    'valoracion': '⭐ Valoración',
                    'favorito': '❤️ Favorito',
                    'reserva': '📅 Reserva',
                    'vista': '👁️ Vista'
                })
                interacciones_df['Fecha_Interaccion'] = pd.to_datetime(interacciones_df['Fecha_Interaccion']).dt.strftime('%d/%m/%Y %H:%M')
                st.dataframe(interacciones_df, use_container_width=True, hide_index=True)
            else:
                st.info("Aún no tienes interacciones registradas.")
        except Exception as e:
            st.error(f"Error al cargar el historial de interacciones: {e}")
        finally:
            if cursor_history: cursor_history.close()
            if conn_history: conn_history.close()

    elif menu == "👤 Mi Cuenta":
        st.subheader("👤 Mi Cuenta")
        st.markdown("Aquí puedes ver y gestionar la información de tu cuenta.")
        
        user_id = st.session_state.get('id_usuario')
        
        if user_id:
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor(dictionary=True)
                sql_select_user = "SELECT nombre, email, edad, genero FROM usuario WHERE id_usuario = %s"
                cursor.execute(sql_select_user, (user_id,))
                user_data = cursor.fetchone()
                
                if user_data:
                    # Mostrar datos del usuario
                    st.markdown("### Tus Datos")
                    st.write(f"**Nombre:** {user_data['nombre']}")
                    st.write(f"**Email:** {user_data['email']}")
                    st.write(f"**Edad:** {user_data['edad']}")
                    st.write(f"**Género:** {user_data['genero']}")
                    
                    st.markdown("### Foto de Perfil")
                    uploaded_file = st.file_uploader("Sube una foto de perfil", type=["png", "jpg", "jpeg"])
                    if uploaded_file is not None:
                        st.image(uploaded_file, caption="Foto de Perfil", use_column_width=True)
                        st.info("La foto se muestra temporalmente. Para guardarla permanentemente, necesitaríamos implementar el almacenamiento.")
                        
                    st.markdown("### Gestionar Cuenta")
                    st.warning("⚠️ Esta acción eliminará tu cuenta y todos los datos asociados (interacciones, valoraciones, reservas).")
                    if st.button("Eliminar Cuenta", key='delete_account_button'):
                        # Confirmación opcional (se podría usar st.confirm si estuviera disponible o simular con estado)
                        st.session_state['confirm_delete_account'] = True
                        
                    if st.session_state.get('confirm_delete_account'):
                        st.info("¿Estás seguro de que quieres eliminar tu cuenta? Esta acción es irreversible.")
                        col_confirm_delete, col_cancel_delete = st.columns(2)
                        with col_confirm_delete:
                            if st.button("Sí, Eliminar Definitivamente", key='confirm_delete_final'):
                                try:
                                    # Eliminar interacciones, valoraciones, reservas asociadas al usuario
                                    delete_interacciones_sql = "DELETE FROM interacciones_usuario WHERE id_usuario = %s"
                                    cursor.execute(delete_interacciones_sql, (user_id,))
                                    delete_valoraciones_sql = "DELETE FROM valoraciones WHERE id_usuario = %s"
                                    cursor.execute(delete_valoraciones_sql, (user_id,))
                                    # Asumiendo que hay una tabla 'reservas' directa o que las reservas están en interacciones
                                    # Si 'reservas' es una tabla separada y tiene id_usuario:
                                    # delete_reservas_sql = "DELETE FROM reservas WHERE id_usuario = %s"
                                    # cursor.execute(delete_reservas_sql, (user_id,))
                                    
                                    # Eliminar el usuario
                                    delete_user_sql = "DELETE FROM usuario WHERE id_usuario = %s"
                                    cursor.execute(delete_user_sql, (user_id,))
                                    
                                    conn.commit()
                                    st.success("Tu cuenta ha sido eliminada con éxito.")
                                    # Limpiar estado de sesión y redirigir a la página de inicio de sesión
                                    st.session_state['logged_in'] = False
                                    st.session_state['id_usuario'] = None
                                    st.session_state['user_name'] = None
                                    st.session_state['favoritos'] = []
                                    st.session_state['viewing_hotel_details'] = None
                                    st.session_state['selected_user_for_history'] = None
                                    st.session_state['confirm_delete_account'] = False # Reset confirmation state
                                    st.experimental_rerun()
                                except Exception as e:
                                    conn.rollback()
                                    st.error(f"Error al eliminar la cuenta: {e}")
                                    st.session_state['confirm_delete_account'] = False # Reset confirmation state on error
                                finally:
                                    if cursor: cursor.close()
                                    if conn: conn.close()
                        with col_cancel_delete:
                            if st.button("Cancelar", key='cancel_delete'):
                                st.session_state['confirm_delete_account'] = False # Reset confirmation state
                                st.experimental_rerun()
                else:
                    st.error("No se pudieron cargar los datos de tu cuenta.")
                    
            except Exception as e:
                st.error(f"Error al cargar la información de la cuenta: {e}")
                
            finally:
                if cursor: cursor.close()
                if conn: conn.close()
        else:
            st.warning("Debes iniciar sesión para ver la información de tu cuenta.")

    elif menu == "👥 Usuarios registrados":
        st.subheader("👥 Gestión de Usuarios Registrados")

        if st.session_state.get('user_name') == 'admin':
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor(dictionary=True)
                sql_select_users = "SELECT id_usuario, nombre, email, edad, genero FROM usuario WHERE nombre != 'admin'"
                cursor.execute(sql_select_users)
                usuarios_registrados = cursor.fetchall()

                if usuarios_registrados:
                    st.write("Aquí puedes gestionar los usuarios registrados:")
                    col_users, col_history_display = st.columns([1, 1])
                    with col_users:
                        st.subheader("Lista de Usuarios")
                        usuarios_df = pd.DataFrame(usuarios_registrados)
                        for index, row in usuarios_df.iterrows():
                            user_id_to_delete = row['id_usuario']
                            user_name_to_delete = row['nombre']
                            with st.container():
                                st.write(f"**Nombre:** {row['nombre']}")
                                st.write(f"**Email:** {row['email']}")
                                st.write(f"**Edad:** {row['edad']}")
                                st.write(f"**Género:** {row['genero']}")
                                col_history, col_delete = st.columns([1, 1])
                                with col_history:
                                    history_button_key = f"view_history_{user_id_to_delete}"
                                    if st.button("Ver Historial", key=history_button_key):
                                        st.session_state['selected_user_for_history'] = user_id_to_delete
                                        st.experimental_rerun()
                                with col_delete:
                                    delete_button_key = f"delete_user_{user_id_to_delete}"
                                    if st.button("Eliminar", key=delete_button_key):
                                        try:
                                            conn_delete = mysql.connector.connect(**DB_CONFIG)
                                            cursor_delete = conn_delete.cursor()
                                            delete_interacciones_sql = "DELETE FROM interacciones_usuario WHERE id_usuario = %s"
                                            cursor_delete.execute(delete_interacciones_sql, (user_id_to_delete,))
                                            delete_valoraciones_sql = "DELETE FROM valoraciones WHERE id_usuario = %s"
                                            cursor_delete.execute(delete_valoraciones_sql, (user_id_to_delete,))
                                            delete_reservas_sql = "DELETE FROM reservas WHERE id_usuario = %s"
                                            cursor_delete.execute(delete_reservas_sql, (user_id_to_delete,))
                                            delete_user_sql = "DELETE FROM usuario WHERE id_usuario = %s"
                                            cursor_delete.execute(delete_user_sql, (user_id_to_delete,))
                                            conn_delete.commit()
                                            st.success(f"Usuario {user_name_to_delete} eliminado con éxito.")
                                            if st.session_state.get('selected_user_for_history') == user_id_to_delete:
                                                st.session_state['selected_user_for_history'] = None
                                            st.experimental_rerun()
                                        except Exception as e:
                                            conn_delete.rollback()
                                            st.error(f"Error al eliminar usuario {user_name_to_delete}: {e}")
                                        finally:
                                            cursor_delete.close()
                                            conn_delete.close()
                                st.markdown("---")
                    with col_history_display:
                        st.subheader("Historial de Interacciones")
                        if st.session_state.get('selected_user_for_history'):
                            user_id_to_show_history = st.session_state['selected_user_for_history']
                            selected_user_info = usuarios_df[usuarios_df['id_usuario'] == user_id_to_show_history]
                            selected_user_name = selected_user_info['nombre'].iloc[0] if not selected_user_info.empty else "Usuario Desconocido"
                            st.write(f"Mostrando historial para: **{selected_user_name}**")
                            try:
                                conn_history = mysql.connector.connect(**DB_CONFIG)
                                cursor_history = conn_history.cursor(dictionary=True)
                                sql_select_user_interacciones = """
                                SELECT
                                    h.nombre AS Nombre_Hotel,
                                    i.accion AS Tipo_Interaccion,
                                    i.valor AS Valor_Asociado,
                                    i.fecha AS Fecha_Interaccion
                                FROM interacciones_usuario i
                                JOIN hoteles h ON i.id_hotel = h.id_hotel
                                WHERE i.id_usuario = %s
                                ORDER BY i.fecha DESC
                                """
                                cursor_history.execute(sql_select_user_interacciones, (user_id_to_show_history,))
                                user_interacciones = cursor_history.fetchall()
                                if user_interacciones:
                                    interacciones_df = pd.DataFrame(user_interacciones)
                                    interacciones_df['Tipo_Interaccion'] = interacciones_df['Tipo_Interaccion'].map({
                                        'valoracion': '⭐ Valoración',
                                        'favorito': '❤️ Favorito',
                                        'reserva': '📅 Reserva',
                                        'vista': '👁️ Vista'
                                    })
                                    interacciones_df['Fecha_Interaccion'] = pd.to_datetime(interacciones_df['Fecha_Interaccion']).dt.strftime('%d/%m/%Y %H:%M')
                                    st.dataframe(interacciones_df, use_container_width=True, hide_index=True)
                                else:
                                    st.info("Este usuario no tiene interacciones registradas.")
                            except Exception as e:
                                st.error(f"Error al cargar el historial de interacciones: {e}")
                            finally:
                                cursor_history.close()
                                conn_history.close()
                        else:
                            st.info("Selecciona un usuario para ver su historial de interacciones.")
                else:
                    st.info("No hay usuarios registrados.")
            except Exception as e:
                st.error(f"Error general en la sección de gestión de usuarios: {e}")
        else:
            st.warning("No tienes permisos para ver esta sección.")

    # Botón de Logout (en la sidebar cuando está logueado)
    st.sidebar.markdown("---") # Separador
    if st.sidebar.button("Cerrar Sesión", key='logout_button'):
        st.session_state['logged_in'] = False
        st.session_state['user_id'] = None
        st.session_state['user_name'] = None
        st.session_state['favoritos'] = []
        st.session_state['viewing_hotel_details'] = None
        st.session_state['selected_user_for_history'] = None
        st.experimental_rerun()

# Cerrar conexión al finalizar (esto puede ser problemático con st.cache_resource, mejor manejar conexiones dentro de las funciones que la usan)
# sistema.cerrar_conexion() 