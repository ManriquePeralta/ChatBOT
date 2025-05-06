from flask import Flask, render_template, request, session
import unicodedata
import string
import difflib
import os

app = Flask(__name__, static_folder="static")
app.secret_key = "supersecreto"
CSV_FILE = "preguntas.csv"

respuestas_conversacion = {
    "hola": "¡Hola! ¿Cómo estás?",
    "holi": "¡Holi! 🌈 ¿Qué onda?",
    "holaaa": "¡Holaaaaa! 😄",
    "todo bien?": "¡Todo bien! ¿Y vos?",
    "todo bien": "¡Me alegro! 😄 ¿Querés charlar o preguntarme algo?",
    "como estas": "Todo bien, gracias. ¿Y vos?",
    "que onda": "Todo tranqui por acá. ¿Y vos?",
    "todo ok": "¡Todo ok! ¿Y vos?",
    "bien": "¡Genial!",
    "bien vos": "¡Todo tranqui por acá!",
    "mal": "Uh mal ahi... ¿Qué pasó?",
    "todo mal": "¡No! ¿Qué pasó?",
    "no se": "No te preocupes, ¡preguntame lo que quieras!",
    "que haces": "Acá, charlando con vos... como siempre 😎",
    "que haces?": "Viendo memes en mi cabeza 🧠✨",
    "te quiero preguntar algo": "Dale, preguntame nomás.",
    "hey": "¡Hey! 😁 ¿Qué contás?",
    "buenas": "¡Buenas buenas! ☀️",
    "buen dia": "¡Buen día! 🌞 ¿Cómo va?",
    "hello": "¡Hello! 😄 ¿Cómo estás?",
    "hi": "¡Hi! 😁 ¿Qué tal?",
    "quien sos": "Soy un bot creado para ayudarte. ¿En qué puedo asistirte?",
    "quien eres": "Soy un bot creado para ayudarte. ¿En qué puedo asistirte?",
    "soy agustina": "¡Hola Agustina! 😊 ¿Cómo estás?",
}

def normalizar(texto):
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = ''.join(c for c in texto if c not in string.punctuation + '¿¡')
    return ' '.join(texto.split())

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

def responder(pregunta, base_preguntas):
    clave = normalizar(pregunta)

    if session.get("modo_conversacion", True):
        for frase in respuestas_conversacion:
            if frase in clave:
                if frase == "te quiero preguntar algo":
                    session["modo_conversacion"] = False
                return respuestas_conversacion[frase]
        return "¡No entendí eso, pero me encanta charlar! 😊"

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
