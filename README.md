<div align="center">

# Endorphin Rush

**Plataforma web para la gestión de rutinas de entrenamiento, seguimiento de progreso y comunidad fitness.**

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.0-092E20?logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/status-en%20desarrollo-yellow)

</div>

---

## Tabla de contenidos

- [Descripción](#descripción)
- [Arquitectura](#arquitectura)
- [Stack tecnológico](#stack-tecnológico)
- [Requisitos previos](#requisitos-previos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Estructura del proyecto](#estructura-del-proyecto)

---

## Descripción

Endorphin Rush es una aplicación web desarrollada en **Django** que permite a los usuarios crear y personalizar rutinas de entrenamiento, registrar su progreso, y leer consejos en un foro comunitario.

## Stack tecnológico

- **Backend:** Django 6.0.6
- **Base de datos:** SQLite
- **Frontend:** Django Templates + Bootstrap 5
- **Gestión de dependencias:** `pip` + `venv`
- **Configuración:** variables de entorno vía `python-dotenv`

## Requisitos previos

- [Python 3.11+](https://www.python.org/downloads/)
- `pip` (incluido con Python)
- Git

## Instalación

```bash
# 1. Clonar el repositorio
git clone <URL_DEL_REPOSITORIO>
cd Endorphin-Rush

# 2. Crear y activar entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Instalar dependencias
pip install -r src/requirements.txt

# 4. Configurar variables de entorno
# Crear un archivo .env dentro de /src con al menos:
#   SECRET_KEY=tu_clave_secreta
cd src

# 5. Aplicar migraciones
python manage.py migrate

# 6. Crear superusuario (acceso al panel de administración)
python manage.py createsuperuser

# 7. Levantar el servidor de desarrollo
python manage.py runserver
```

La aplicación quedará disponible en **http://127.0.0.1:8000/**.


## Estructura del proyecto

```
Endorphin-Rush/
├── src/
│   ├── EndorphinRush/     # Configuración del proyecto (settings, urls)
│   ├── authentication/    # App de usuarios y perfiles
│   ├── core/               # Sesiones, historial y términos
│   ├── exercise_types/     # Catálogo de tipos de ejercicio
│   ├── exercises/          # Catálogo de ejercicios
│   ├── exercise_plans/     # Rutinas
│   ├── forum/               # Foro
│   ├── templates/          # Templates globales
│   ├── manage.py
│   └── requirements.txt
└── README.md
```

---

<div align="center">

Proyecto desarrollado por el equipo **A(lexis) A(lbani) A(strid)**
Taller de Programación Web - Universidad de Talca

</div>
