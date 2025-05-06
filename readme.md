
# 🤖 Chatbot Web con Flask

Este es un chatbot web básico creado con Python y Flask. Tiene dos modos:  
- **Modo Charla**: interactúa de forma casual con frases amigables.  
- **Modo Preguntar**: responde preguntas desde una base de datos editable por el usuario.  

Además, el bot puede aprender nuevas respuestas si no conoce alguna.

---

## 🧠 Funcionalidades

- Interfaz web moderna y simple.
- Modo "charla" con respuestas relajadas y divertidas.
- Modo "preguntar" para consultas específicas.
- Aprende nuevas preguntas y respuestas desde la web.
- Historial de conversación en pantalla con scroll automático.
- Estilo visual personalizado con CSS (`styles.css`).

---

## 📦 Requisitos

- Python 3.7 o superior
- Flask

---

## 🚀 Instalación y uso

### 1. Cloná el repositorio

```bash
git clone https://github.com/ManriquePeralta/ChatBOT
cd TU_REPO
```

### 2. (Opcional) Crear entorno virtual

```bash
python -m venv venv
# Activar entorno
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate       # Windows
```

### 3. Instalar dependencias

```bash
pip install flask
```

### 4. Ejecutar la aplicación

```bash
python app.py
```

### 5. Abrir el navegador

Ir a: [http://localhost:5000](http://localhost:5000)

---

## 📁 Estructura del proyecto

```
chatbot/
├── app.py               # Código principal del servidor Flask
├── preguntas.csv        # Base de conocimiento dinámica
├── templates/
│   └── index.html       # Plantilla HTML principal
├── static/
│   └── styles.css       # Estilos visuales del sitio
├── README.md
└── .gitignore
```

---

## 🧠 ¿Cómo enseño algo nuevo al bot?

1. En modo "preguntar", escribí una pregunta.
2. Si no la conoce, el bot te pregunta si querés agregarla.
3. Si aceptás, podés escribir la respuesta.
4. El bot guarda esa info y podrá responder la próxima vez.

Todo queda guardado en el archivo `preguntas.csv`.

---

## 🛠 Mejoras posibles

- Guardar historial entre sesiones.
- Agregar respuestas contextuales o por tema.
- Usar una base de datos en vez de CSV.
- Desplegar la app en la nube (Render, Railway, PythonAnywhere).
- Agregar reconocimiento de voz o texto a voz.

---

## 📄 Licencia

MIT License

---

Hecho con 💻 y ☕ por [Tu Nombre o Usuario]
