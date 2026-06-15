# 🔋 Smart Battery & Electricity Price Predictor (End-to-End MLOps Pipeline)

Este proyecto despliega un sistema industrializado e inteligente de ingeniería de datos e Inteligencia Artificial para optimizar los ciclos de carga y descarga de una batería comercial conectada a la red eléctrica española (OMIE). El sistema predice las fluctuaciones del precio de la energía basándose en variables meteorológicas e históricos del mercado, sentando las bases para tomar decisiones automatizadas de arbitraje energético.

---

## 🏗️ Arquitectura del Sistema

El proyecto está diseñado bajo principios de software limpio, desacoplamiento de procesos e idempotencia, dividiéndose en tres capas clave:

1. **Ingesta & Orquestación (Data Engineering)**
   * **Orquestación:** Automatizada con **Dagster** mediante *Software-Defined Assets*. Configurada con un demonio de ejecución y *Schedules* para actualizaciones incrementales diarias en la madrugada (03:00 AM).
   * **Procesamiento de Alta Resolución:** Ingesta desde APIs públicas (ESIOS/Red Eléctrica para precios del pool y Open-Meteo para radiación solar). Unión y modelado de datos a resolución de 15 minutos utilizando **Polars** (con técnicas de *Forward Fill* para sincronizar el clima horario con la granularidad comercial cuarto-horaria).
   * **Almacenamiento:** Base de datos analítica local con **DuckDB**, garantizando persistencia veloz, concurrencia segura y cargas de datos idempotentes mediante sentencias `INSERT OR IGNORE`.

2. **Inteligencia Artificial (Machine Learning / MLOps)**
   * **Algoritmo:** Regresor avanzado basado en **XGBoost**, entrenado con un histórico robusto de datos reales.
   * **Ingeniería de Características Robustas:** Generación de variables con memoria temporal (Lags de 24h y 48h, Ventanas Móviles de clima y características de calendario) utilizando *Temporal Joins* por fecha exacta en Polars, blindando al modelo contra el desorden de filas o pérdidas de datos aleatorias en las APIs de producción.

3. **Algoritmo de Arbitraje (Próximamente)**
   * Lógica de optimización para la carga de la batería en horas de precio suelo (efecto de la curva pato solar a mediodía) y descarga en picos de demanda nocturna.

---

## 📁 Estructura del Proyecto

```text
PROYECTO/
├── data/
│   └── database/          # Almacenamiento analítico local de DuckDB (ignorado en Git)
├── src/
│   ├── ingestion/         # Clases base y clientes HTTP para APIs externas (REE/Open-Meteo)
│   ├── transformation/    # Scripts de limpieza, normalización y transformación con Polars
│   ├── orchestration/     # Torre de control, Assets, Definitions y Schedules de Dagster
│   ├── models/            # Factoría de IA: Alineamiento temporal exacto y entrenamiento de XGBoost
│   └── config.py          # Configuración centralizada de variables globales y rutas del sistema
├── .gitignore             # Filtro de seguridad (oculta entornos virtuales, DBs locales y claves)
├── .env.example           # Plantilla pública con las variables de entorno requeridas
└── pyproject.toml         # Gestión de dependencias moderna y determinista con UV (Astral)