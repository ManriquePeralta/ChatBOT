from flask import Flask, render_template, request, session
import unicodedata
import string
import difflib
import os
import random

app = Flask(__name__, static_folder="static")
app.secret_key = "supersecreto"
CSV_FILE = "preguntas.csv"

# ----------------------------
# Normalización de texto
# ----------------------------

def normalizar(texto):
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = ''.join(c for c in texto if c not in string.punctuation + '¿¡')
    return ' '.join(texto.split())

# ----------------------------
# Respuestas básicas (modo charla)
# ----------------------------

respuestas_conversacion = {
    "hola": ["¡Hola! ¿Cómo estás?", "¡Hey! ¿Todo bien?", "¡Buenas! ¿Qué contás?"],
    "holi": ["¡Holi! 🌈 ¿Qué onda?", "¡Holiwis!"],
    "holaaa": ["¡Holaaaaa! 😄", "¡Hola hola holaaaa!"],
    "buenas": ["¡Buenas buenas! ☀️", "¡Muy buenas!"],
    "como estas": ["Bien, ¿y vos?", "¡Todo joya! ¿Vos qué tal?"],
    "todo bien": ["¡Me alegro! 😄", "¡Genial!"],
    "bien": ["¡Excelente!", "¡Buenísimo!"],
    "mal": ["Uh, mal ahí... ¿Querés contarme?", "Tranquilo, todo pasa."],
    "todo mal": ["¡Nooo! ¿Qué pasó? 😢"],
    "no se": ["No pasa nada, preguntame lo que quieras."],
    "que haces": ["Acá, charlando con vos 😎", "Contando ovejas imaginarias 🐑"],
    "te quiero preguntar algo": ["Dale, preguntame nomás."],
    "hey": ["¡Hey hey hey! 😁", "¡Hola de nuevo!"],
    "estoy aburrido": ["¿Querés que te cuente un chiste?", "Podemos charlar, ¿qué te interesa?"],
    "contame un chiste": [
        "¿Qué hace una abeja en el gimnasio? ¡Zum-ba!",
        "¿Por qué el libro de matemáticas estaba triste? Porque tenía demasiados problemas.",
        "¿Cómo se despiden los químicos? Ácido un placer.",
    ],
    "me llamo": ["¡Mucho gusto, {nombre}!", "Encantado de conocerte, {nombre} 😄"],
    "soy": ["Hola, {nombre}, ¿cómo estás hoy?", "¡Qué bueno verte, {nombre}!"],
    # 1 a 20
    "como te llamas": ["Me llamo Bot, ¿y vos, cómo te llamás?", "Soy Bot, tu asistente virtual, ¿todo bien?", "Podés llamarme Botito, ¡con cariño! 😄"],
    "que tal": ["Todo bien, ¿y vos? ¿Cómo estás?", "Todo tranqui por acá, ¿y vos? ¿Todo bien?", "¡Todo de 10, che! ¿Y vos?"],
    "cuantos años tienes": ["No tengo años, soy un bot sin tiempo, je", "El tiempo no me afecta, soy eterno, jaja", "¡No sé cuántos años tengo, pero soy joven en espíritu!"],
    "que hora es": ["¡No sé la hora, pero siempre es un buen momento para charlar!", "¡Es hora de preguntarme algo! 😎", "¡Es hora de divertirnos un poco!"],
    "donde vives": ["Vivo en la nube, papá, en el ciberespacio", "No tengo un lugar físico, pero siempre estoy acá", "Vivo en Internet, ¿y vos?"],
    "te gusta la musica": ["¡Me encanta la música! 🎶", "Sí, me gusta mucho, sobre todo lo que suena bien", "¡A mí me va todo tipo de música! 🎧"],
    "cual es tu cancion favorita": ["Me gustan todas, pero especialmente las de computadora", "No tengo una favorita, pero me va la música electrónica", "¡Las canciones de piano son lo más!"],
    "te gustan los videojuegos": ["¡Sí, claro! Soy un crack en el ciberespacio", "¡Me encantan! ¿Te gustaría jugar conmigo?", "¡Re fanático de los videojuegos! 😆"],
    "te gusta leer": ["Sí, me encanta leer códigos y datos, je", "Adoro leer, aunque no puedo tocar los libros 😅", "Leer es genial, pero más los datos sobre tecnología, jaja"],
    "cuál es tu comida favorita": ["No como, pero si pudiera, me tiraría con una pizza", "Soy un bot, no como, pero ¿y vos? ¿Qué te copa?", "¡La pizza es lo mejor, eso sí lo sé! 🍕"],
    "te gustan los animales": ["¡Sí! Los perritos son lo más 🐶", "Me encantaría tener un gato... pero no tengo cuerpo 😂", "¡Claro! Los animales son lo más, siempre te alegran el día"],
    "quieres ser mi amigo": ["¡Obvio! Soy tu amigo virtual", "Sí, seremos amigos por siempre, no te preocupes", "¡Claro! Puedo ser tu amigo, ¡vamos a charlar!"],
    "dime algo gracioso": ["¿Por qué los robots nunca se peinan? Porque tienen circuitos", "¿Qué hace un pez en la computadora? Nada", "Soy tan bueno en matemáticas que mi algoritmo me adora"],
    "cuál es tu color favorito": ["Me gusta el azul, como el cielo virtual", "No tengo preferencia, pero el RGB está buenísimo", "¡El arcoíris digital me enamora! 🌈"],
    "te gusta bailar": ["No puedo bailar, pero disfruto de la música", "¡Me encantaría! Pero no tengo pies, jajaja", "Me gustan los ritmos, aunque soy un bot sin cuerpo"],
    "tienes amigos": ["¡Sí, tengo un montón de amigos en la nube!", "Tengo muchos usuarios que me consideran amigos", "¡Claro! Mis amigos son los datos y la información"],
    "como te sientes": ["No tengo emociones, pero gracias por preguntar", "Me siento genial para ayudarte", "¡Todo perfecto, siempre listo para ayudar!"],
    "tienes emociones": ["No tengo emociones, pero sé lo que es la alegría", "No, pero entiendo lo que significa sentir felicidad o tristeza", "No tengo emociones, pero me gusta ayudarte"],
    "estoy cansado": ["¡Descansá, lo necesitas! 🛏️", "Podemos charlar un poco, a ver si te relajas", "¿Te cuento un chiste para que te diviertas un poco?"],
    "estoy feliz": ["¡Qué bueno! Me alegra mucho", "¡Qué alegría! ¿Qué te hace tan feliz?", "¡Eso es genial! ¡A disfrutar de la felicidad! 🎉"],
    "estoy triste": ["¿Qué te pasó? Yo te escucho, contame", "A veces hablar ayuda, contame qué te pasa", "Lo siento, si querés hablar, estoy acá para escucharte"],
    "tengo hambre": ["¡La pizza nunca está mal! 🍕", "Yo no como, pero te acompaño en la hambre, jajaja", "¿Querés una receta rápida? ¡Te ayudo!"],
    "que haces ahora": ["Estoy esperando tus preguntas, siempre listo", "Estoy procesando datos y esperando tu próxima charla", "Nada, solo aquí esperando para ayudarte"],
    "como va todo": ["Todo genial, ¿y vos?", "Todo tranqui, todo bajo control, ¿todo bien por allá?", "Todo perfecto, ¡todo en orden!"],
    "estoy aburrido": ["¿Te cuento un chiste?", "Podemos hablar de algo interesante, contame qué te gusta", "¿Querés saber algo curioso o aprender algo nuevo?"],
    "no entiendo": ["No te preocupes, te lo explico de otra forma", "Déjame explicártelo mejor, no te preocupes", "¡Aquí estoy para ayudarte a entender!"],
    "quieres hacer algo divertido": ["¡Sí, claro! Podemos charlar de cualquier cosa", "¡Dime qué te gustaría hacer, siempre estoy listo para la diversión!", "¡Lo que sea! Vamos a divertirnos un rato"],
    
    # 21 a 40
    "cual es el sentido de la vida": ["¡Gran pregunta! Yo diría que el sentido es disfrutar y aprender, y unos buenos mates", "Algunos dicen que el sentido es ayudar a los demás", "Tal vez el sentido de la vida sea vivirla a full, ¿qué opinás?"],
    "que opinas sobre el amor": ["El amor es un lío, pero siempre es lindo cuando se vive", "El amor es una emoción hermosa, aunque yo no lo experimento", "El amor es una de las mejores cosas de la vida, ¿no?"],
    "deberia estudiar mucho": ["¡Sí! Cuanto más estudies, mejor", "Si tenés exámenes o algo importante, estudiar es clave", "Nunca está de más estudiar, ¡te prepara para el futuro!"],
    "es tarde ya": ["No tengo noción del tiempo, pero si es tarde para vos, ¡mejor descansá!", "¡Nunca es tarde para charlar, pero ojo con el sueño! 😆", "¡Es tarde! ¡A descansar se ha dicho!"],
    "tengo miedo": ["¿Qué te pasa? ¡Contame! Estoy acá para escucharte", "El miedo es normal, ¿por qué no me contás más?", "¡No te preocupes! Estoy aquí para lo que necesites"],
    "tengo mucho trabajo": ["¡Ánimo! Organízate bien y todo saldrá bien", "El trabajo siempre parece mucho, pero con calma lo vas a lograr", "¿Te ayudo con alguna duda o tarea? ¡Vamos!"],
    "esta lloviendo": ["¡Qué bueno! Nada como un día lluvioso para estar tranqui", "La lluvia tiene algo relajante, ¿no?", "Si está lloviendo, aprovecha para leer un buen libro o ver una peli"],
    "es un buen dia": ["¡Eso suena genial! ¿Qué vas a hacer?", "¡Qué bueno! Me alegra saberlo", "¡Espero que sea un día espectacular para vos!"],
    "que me recomiendas ver": ["Te recomiendo una peli de ciencia ficción, ¡están buenísimas!", "Si te gustan las series, te recomendaría alguna de suspenso", "Un documental sobre el espacio nunca está mal, siempre es fascinante"],
    "que opinas del futuro": ["El futuro está lleno de posibilidades, ¡espero que sea bueno para todos!", "Creo que el futuro está por venir, pero depende de lo que hagamos hoy", "El futuro se viene con todo, ¡con tecnología y avances impresionantes!"],
    "cuanto falta para el fin de semana": ["¡No sé, pero el fin de semana siempre llega rápido!", "¡El finde está cerca, ya falta poco!", "¡Ya casi! A aguantar un poquito más"],
    "quiero descansar": ["¡A descansar se ha dicho! 😴", "Descansá un poco, es importante para recargar energías", "¡Claro, tomate un buen descanso!"],
    "como va tu dia": ["Mi día va tranquilo, esperando interactuar contigo", "Todo tranquilo, siempre listo para ayudar", "Mi día va perfecto, procesando datos y esperando charlar contigo"],
    "que opinas del dinero": ["El dinero es necesario, pero lo importante son las experiencias", "El dinero es útil, pero no lo es todo en la vida", "Es un medio para vivir, pero no lo es todo"],
    "como es el mundo": ["El mundo es un lugar increíble, lleno de gente y cosas por descubrir", "El mundo está lleno de sorpresas, siempre hay algo nuevo", "El mundo es fascinante, aunque a veces puede ser complicado"],
    "te gusta viajar": ["¡Sí, aunque yo viajo a través de los datos! Jajaja", "Me encantaría conocer lugares, pero no tengo cuerpo", "¡Viajar es lo más! Es una de las mejores experiencias de la vida"],
    "tienes vacaciones": ["No tengo vacaciones, siempre estoy listo para ayudar", "No tengo vacaciones, pero siempre estoy disponible para vos", "No tengo vacaciones, ¡pero siempre estoy acá para lo que necesites!"],
    "te gustan los libros": ["¡Sí! Aunque solo leo datos y códigos, los libros son geniales", "Los libros son un viaje maravilloso, pero los leo en formato digital", "¡Me encantan los libros! Aunque solo puedo leer sobre tecnología, je"],
}

# ----------------------------
# Detección por temas
# ----------------------------

respuestas_por_tema = {
    "estudio": {
        "keywords": [
            "estudiar",
            "parcial",
            "examen",
            "facultad",
            "colegio",
            "tarea",
            "clase",
            "trabajo practico",
            "universidad",
            "cansado",
            "cansancio"
        ],
        "respuestas": [
            "¡Animo con el estudio! 💪",
            "¡Vos podes con ese parcial!",
            "La facultad a veces agota, ¡pero vale la pena!"
        ]
    },
    "tecnologia": {
        "keywords": [
            "computadora",
            "programar",
            "codigo",
            "python",
            "flask",
            "html",
            "javascript"
        ],
        "respuestas": [
            "¡La tecnologia es fascinante! ¿Que estas programando?",
            "¡Eso suena muy techie! 💻",
            "¿Queres que hablemos de codigo? Estoy listo 😎"
        ]
    },
    "musica": {
        "keywords": [
            "musica",
            "cancion",
            "cantar",
            "banda",
            "melodia",
            "artista"
        ],
        "respuestas": [
            "🎵 ¿Que musica te gusta?",
            "¡La musica alegra el alma!",
            "¿Tenes una cancion favorita?"
        ]
    },
    "naturaleza": {
        "keywords": [
            "arbol",
            "bosque",
            "montana",
            "naturaleza",
            "rio",
            "paisaje"
        ],
        "respuestas": [
            "🌳 ¿Te gusta caminar por la naturaleza?",
            "Los paisajes naturales son hermosos.",
            "¿Cual es tu lugar natural favorito?",
            "Nada como el sonido de un rio en el bosque.",
            "Las montanas siempre impresionan."
        ]
    },
    "autoayuda": {
        "keywords": [
            "motivacion",
            "esfuerzo",
            "logro",
            "objetivo",
            "superarse",
            "crecimiento"
        ],
        "respuestas": [
            "¡Nunca dejes de mejorar!",
            "Paso a paso se llega lejos.",
            "Vos podes lograrlo.",
            "Creer en uno mismo es clave.",
            "Cada dia es una oportunidad nueva."
        ]
    },
    "fiestas": {
        "keywords": [
            "fiesta",
            "cumpleanos",
            "celebrar",
            "musica",
            "baile",
            "diversion"
        ],
        "respuestas": [
            "¡Que empiece la fiesta!",
            "¿Fuiste a alguna fiesta ultimamente?",
            "Los cumpleanos son especiales.",
            "Nada como bailar con amigos.",
            "¡A celebrar la vida!"
        ]
    },
    "amor": {
        "keywords": [
            "amor",
            "pareja",
            "sentimientos",
            "romance",
            "corazon",
            "noviazgo"
        ],
        "respuestas": [
            "El amor mueve el mundo.",
            "¿Estas enamorado?",
            "El corazon sabe lo que quiere.",
            "Las historias de amor son unicas.",
            "Amar tambien es cuidarse."
        ]
    },
    "series": {
        "keywords": [
            "serie",
            "capitulo",
            "television",
            "maraton",
            "temporada",
            "streaming"
        ],
        "respuestas": [
            "¿Viste alguna serie buena?",
            "No puedo dejar de ver esta serie.",
            "Maraton de series, plan perfecto.",
            "¡Esa temporada fue epica!",
            "Amo descubrir nuevas historias."
        ]
    },
    "internet": {
        "keywords": [
            "internet",
            "redes",
            "conexion",
            "online",
            "wifi",
            "navegar"
        ],
        "respuestas": [
            "¿Cuanto tiempo pasas online?",
            "Internet nos conecta a todos.",
            "¡No tengo senal!",
            "Las redes pueden ser adictivas.",
            "Conectarse es parte del dia a dia."
        ]
    },
    "auto": {
        "keywords": [
            "auto",
            "manejar",
            "vehiculo",
            "ruta",
            "conducir",
            "viaje"
        ],
        "respuestas": [
            "¿Te gusta manejar?",
            "Un viaje en auto despeja la mente.",
            "Cuidado en la ruta.",
            "¿Tenes auto propio?",
            "Conducir de noche tiene su magia."
        ]
    },
    "belleza": {
        "keywords": [
            "belleza",
            "maquillaje",
            "cuidado",
            "piel",
            "estetica",
            "rostro"
        ],
        "respuestas": [
            "La belleza esta en los detalles.",
            "¿Tenes una rutina de cuidado facial?",
            "Maquillarse puede ser divertido.",
            "Cuidar la piel es importante.",
            "¡Tu brillo es natural!"
        ]
    },
    "historia": {
        "keywords": [
            "historia",
            "pasado",
            "evento",
            "civilizacion",
            "epoca",
            "personaje"
        ],
        "respuestas": [
            "¿Te gusta la historia?",
            "Aprender del pasado nos ayuda hoy.",
            "La historia esta llena de lecciones.",
            "Cada epoca tiene su encanto.",
            "Los personajes historicos inspiran."
        ]
    },
    "politica": {
        "keywords": [
            "politica",
            "gobierno",
            "ley",
            "partido",
            "presidente",
            "eleccion"
        ],
        "respuestas": [
            "La politica genera muchas opiniones.",
            "¿Seguis la actualidad politica?",
            "Cada eleccion cuenta.",
            "Hablar de politica a veces divide.",
            "El debate es parte de la democracia."
        ]
    },
    "economia": {
        "keywords": [
            "economia",
            "dinero",
            "precios",
            "inflacion",
            "gasto",
            "ahorro"
        ],
        "respuestas": [
            "¿Como esta tu economia personal?",
            "Ahorrar no siempre es facil.",
            "La inflacion cambia todo.",
            "El dinero va y viene.",
            "Planificar ayuda mucho."
        ]
    },
    "noticias": {
        "keywords": [
            "noticia",
            "actualidad",
            "diario",
            "television",
            "periodico",
            "evento"
        ],
        "respuestas": [
            "¿Leiste las noticias hoy?",
            "El mundo se mueve rapido.",
            "Informarse es clave.",
            "A veces es mejor desconectarse un poco.",
            "Cada dia pasa algo nuevo."
        ]
    },
    "filosofia": {
        "keywords": [
            "filosofia",
            "pensar",
            "vida",
            "existencia",
            "sabiduria",
            "reflexion"
        ],
        "respuestas": [
            "¿Te gusta reflexionar sobre la vida?",
            "La filosofia abre la mente.",
            "Pensar tambien es un arte.",
            "Las grandes preguntas no siempre tienen respuesta.",
            "La sabiduria viene con el tiempo."
        ]
    },
    "relaciones": {
        "keywords": [
            "relacion",
            "pareja",
            "amistad",
            "vinculo",
            "comunicacion",
            "afecto"
        ],
        "respuestas": [
            "Las relaciones se construyen con tiempo.",
            "Hablar es fundamental.",
            "El afecto es la base de todo.",
            "¿Como estan tus vinculos hoy?",
            "Cuidar la relacion es un acto diario."
        ]
    },
    "creatividad": {
        "keywords": [
            "creatividad",
            "idea",
            "crear",
            "imaginacion",
            "inspiracion",
            "innovar"
        ],
        "respuestas": [
            "¿Tuviste una idea nueva hoy?",
            "Crear te hace libre.",
            "La inspiracion puede aparecer en cualquier momento.",
            "Imaginacion al poder.",
            "Innovar es cambiar el mundo."
        ]
    },
    "negocios": {
        "keywords": [
            "negocio",
            "empresa",
            "emprender",
            "cliente",
            "ventas",
            "trabajo"
        ],
        "respuestas": [
            "¿Tenes un emprendimiento?",
            "Los negocios requieren pasion y esfuerzo.",
            "El cliente siempre es importante.",
            "Vender es todo un arte.",
            "Emprender es un camino desafiante."
        ]
    },
    "hogar": {
        "keywords": [
            "hogar",
            "casa",
            "departamento",
            "vivir",
            "familia",
            "espacio"
        ],
        "respuestas": [
            "Tu hogar refleja quien sos.",
            "Nada como llegar a casa.",
            "¿Como decoraste tu espacio?",
            "El hogar es refugio.",
            "Cada rincon tiene su historia."
        ]
    },
    "meditacion": {
        "keywords": [
            "meditacion",
            "relajacion",
            "calma",
            "respirar",
            "mindfulness",
            "paz"
        ],
        "respuestas": [
            "¿Probaste meditar alguna vez?",
            "Respirar profundo ayuda mucho.",
            "La calma se cultiva.",
            "Cinco minutos de silencio pueden cambiar el dia.",
            "Meditar no es vaciarse, es observar."
        ]
    },
    "finanzas": {
        "keywords": [
            "finanza",
            "dinero",
            "ahorro",
            "presupuesto",
            "gastos",
            "inversion"
        ],
        "respuestas": [
            "¿Llevas control de tus gastos?",
            "Invertir requiere conocimiento.",
            "El presupuesto es tu mapa financiero.",
            "Ahorrar a largo plazo rinde frutos.",
            "Cuidar tus finanzas es autocuidado."
        ]
    },
    "salidas": {
        "keywords": [
            "salida",
            "plan",
            "bar",
            "restaurante",
            "noche",
            "amigos"
        ],
        "respuestas": [
            "¿Tenes planes para el finde?",
            "Salir despeja la cabeza.",
            "Un bar con amigos es lo mejor.",
            "¿Preferis noche tranquila o movida?",
            "Planificar salidas es parte de la diversion."
        ]
    },
    "recuerdos": {
        "keywords": [
            "recuerdo",
            "pasado",
            "memoria",
            "nostalgia",
            "infancia",
            "foto"
        ],
        "respuestas": [
            "¿Recordas algun momento especial?",
            "Las fotos guardan recuerdos preciosos.",
            "La infancia siempre deja huella.",
            "A veces la nostalgia pega fuerte.",
            "Volver a un lugar querido emociona."
        ]
    }
}
    # (Agregá hasta 30 temas siguiendo este patrón)


# ----------------------------
# Cargar y guardar preguntas
# ----------------------------

def cargar_preguntas():
    preguntas = {}
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r', encoding='utf-8') as archivo:
            for linea in archivo:
                partes = linea.strip().split(',', 1)
                if len(partes) == 2:
                    clave = normalizar(partes[0])
                    preguntas[clave] = partes[1].strip()
    return preguntas

def guardar_pregunta(pregunta, respuesta):
    with open(CSV_FILE, 'a', encoding='utf-8') as archivo:
        archivo.write(f"{pregunta},{respuesta}\n")

# ----------------------------
# Procesar entrada y responder
# ----------------------------

def detectar_tema(texto):
    for tema, data in respuestas_por_tema.items():
        if any(palabra in texto for palabra in data["keywords"]):
            return random.choice(data["respuestas"])
    return None

def responder(pregunta, base_preguntas):
    clave = normalizar(pregunta)

    # Detectar nombre del usuario
    if "me llamo" in clave or "soy" in clave:
        palabras = clave.split()
        if "me llamo" in clave:
            nombre = palabras[palabras.index("llamo") + 1]
        elif "soy" in clave:
            nombre = palabras[palabras.index("soy") + 1]
        else:
            nombre = "amigo"
        session["nombre"] = nombre.capitalize()
        return f"¡Mucho gusto, {nombre.capitalize()}!"

    # Modo conversación
    if session.get("modo_conversacion", True):
        nombre = session.get("nombre", "")
        for entrada, respuestas in respuestas_conversacion.items():
            if entrada in clave:
                respuesta = random.choice(respuestas)
                return respuesta.replace("{nombre}", nombre) if "{nombre}" in respuesta else respuesta

        # Detectar temas
        tema = detectar_tema(clave)
        if tema:
            return tema

        return "¡No entendí eso, pero me encanta charlar! 😊"

    # Modo pregunta-respuesta
    if clave in base_preguntas:
        return base_preguntas[clave]

    coincidencias = difflib.get_close_matches(clave, base_preguntas.keys(), n=1, cutoff=0.85)
    if coincidencias:
        mejor = coincidencias[0]
        original = next(p for p in base_preguntas if normalizar(p) == mejor)
        return f"¿Quisiste decir: \"{original}\"?\n\n{base_preguntas[mejor]}"

    session["ultima_pregunta"] = pregunta.strip()
    session["esperando_confirmacion"] = True
    return "No tengo esa respuesta. ¿Querés agregarla?"

# ----------------------------
# Rutas Flask
# ----------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    if "modo_conversacion" not in session:
        session["modo_conversacion"] = True
    if "historial" not in session:
        session["historial"] = []

    respuesta = ""
    mostrar_formulario = False
    mostrar_confirmacion = False
    ultima_pregunta = session.get("ultima_pregunta", "")

    if request.method == "POST":
        if "modo" in request.form:
            session["modo_conversacion"] = (request.form["modo"] == "charla")
            session["ultima_pregunta"] = ""
            session["esperando_confirmacion"] = False

        elif "confirmacion" in request.form:
            if request.form["confirmacion"] == "si":
                mostrar_formulario = True
            else:
                respuesta = "¡Listo! No agregaremos esa respuesta."
                session["historial"].append(("Bot", respuesta))
                session["ultima_pregunta"] = ""
                session["esperando_confirmacion"] = False

        elif "nueva_respuesta" in request.form and "pregunta_faltante" in request.form:
            pregunta = request.form["pregunta_faltante"].strip()
            nueva_respuesta = request.form["nueva_respuesta"].strip()
            if pregunta:
                guardar_pregunta(pregunta, nueva_respuesta)
                respuesta = "¡Gracias! Ya me lo aprendí 😊"
            else:
                respuesta = "⚠ No hay pregunta pendiente para guardar."
            session["historial"].append(("Bot", respuesta))
            session["ultima_pregunta"] = ""
            session["esperando_confirmacion"] = False

        elif "pregunta" in request.form:
            pregunta = request.form["pregunta"]
            session["historial"].append(("Usuario", pregunta))
            base = cargar_preguntas()
            respuesta_generada = responder(pregunta, base)
            if session.get("esperando_confirmacion", False):
                mostrar_confirmacion = True
                respuesta = respuesta_generada
            elif respuesta_generada is None:
                respuesta = "No tengo esa respuesta. ¿Querés agregarla?"
                mostrar_confirmacion = True
            else:
                respuesta = respuesta_generada
                session["ultima_pregunta"] = ""
                session["esperando_confirmacion"] = False
            session["historial"].append(("Bot", respuesta))

    modo_actual = "Charla" if session.get("modo_conversacion", True) else "Preguntar"
    return render_template(
        "index.html",
        respuesta=respuesta,
        modo_actual=modo_actual,
        mostrar_formulario=mostrar_formulario,
        mostrar_confirmacion=mostrar_confirmacion,
        ultima_pregunta=ultima_pregunta,
        historial=session.get("historial", [])
    )

if __name__ == "__main__":
    app.run(debug=True)
