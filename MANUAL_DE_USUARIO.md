# Manual de Usuario

## 1. Introducción

### Descripción General del Sistema

**HealthAnalytics IPS** es una plataforma web integral para la gestión y análisis de datos clínicos en instituciones prestadoras de salud (IPS). El sistema permite cargar, transformar y analizar conjuntos de datos de pacientes, visualizar indicadores clave de rendimiento (KPIs) en un panel interactivo, ejecutar modelos de Machine Learning para predicción de riesgos, y generar reportes exportables en múltiples formatos.

### Objetivo del Sistema

Proporcionar a profesionales de la salud, analistas y administradores una herramienta unificada que facilite la toma de decisiones basada en datos, mediante la automatización de procesos ETL (Extract, Transform, Load), visualización de métricas clínicas, y predicción del nivel de riesgo de enfermedades cardiovasculares utilizando inteligencia artificial.

### Público Objetivo

- **Administradores** de instituciones de salud
- **Médicos** y personal clínico
- **Analistas de datos** en el ámbito sanitario
- Personal técnico encargado de la operación del sistema

---

## 2. Requisitos de Acceso

### 2.1 Credenciales

El acceso al sistema se realiza mediante credenciales proporcionadas por el administrador del sistema. No existe un registro público; los usuarios son creados exclusivamente a través del panel de administración de Django (`/admin/`).

| Elemento | Descripción |
|----------|-------------|
| **Usuario** | Nombre de usuario único asignado por el administrador |
| **Contraseña** | Contraseña segura proporcionada por el administrador |
| **Roles disponibles** | Administrador, Médico, Analista |

#### Roles Disponibles

| Rol | Descripción |
|-----|-------------|
| **Administrador** | Acceso completo a todas las funcionalidades del sistema, incluyendo gestión de pacientes, ejecución ETL, entrenamiento de modelos ML y exportación de reportes |
| **Médico** | Acceso al panel de control, visualización y gestión de pacientes (crear, editar), predicciones de riesgo clínico y exportación de reportes |
| **Analista** | Acceso al panel de control, ejecución de procesos ETL, entrenamiento de modelos ML, visualización de versiones de modelos y exportación de reportes |

### 2.2 Requisitos Técnicos

| Requisito | Especificación |
|-----------|----------------|
| **Navegador recomendado** | Google Chrome 90+, Mozilla Firefox 88+, Microsoft Edge 90+ |
| **Conexión a internet** | Requerida (mínimo 2 Mbps) |
| **Resolución de pantalla** | Mínimo 1024 × 768 píxeles |
| **JavaScript** | Debe estar habilitado |
| **Sistema operativo** | Windows 10+, macOS 11+, Ubuntu 20.04+ |

---

## 3. Inicio de Sesión

### Pasos para Acceder al Sistema

1. Abra su navegador web y diríjase a la URL del sistema:
   **https://healthcare-etl-analytics-platform.onrender.com/**

2. En la pantalla de inicio de sesión, ingrese su **nombre de usuario** en el campo "Usuario".

3. Ingrese su **contraseña** en el campo "Contraseña".

4. Haga clic en el botón **"Entrar"**.

5. Si las credenciales son correctas, será redirigido al **Panel Principal (Dashboard)**.

    > **Nota:** La sesión expira después de 1 hora de inactividad por motivos de seguridad.

### Captura de Pantalla

```
[Placeholder: Pantalla de inicio de sesión de HealthAnalytics IPS]
```

---

## 4. Panel Principal (Dashboard)

### 4.1 Descripción General

El Dashboard es la pantalla principal del sistema, accesible inmediatamente después del inicio de sesión. Proporciona una vista general del estado de los pacientes registrados en la plataforma, mostrando indicadores clave, gráficos interactivos y tendencias. Todos los roles tienen acceso a esta sección.

### 4.2 Indicadores y Métricas

En la parte superior del Dashboard se presentan **tarjetas de KPIs** con los siguientes indicadores:

| Indicador | Descripción |
|-----------|-------------|
| **Total Pacientes** | Número total de pacientes registrados en el sistema |
| **Pacientes Críticos** | Cantidad de pacientes clasificados en riesgo crítico |
| **Hipertensos** | Pacientes diagnosticados con hipertensión |
| **Diabéticos** | Pacientes diagnosticados con diabetes |
| **Fumadores** | Pacientes registrados como fumadores |
| **Riesgo Promedio** | Puntaje de riesgo promedio de todos los pacientes |
| **Predicciones ML** | Cantidad de predicciones realizadas por el modelo de Machine Learning |

### 4.3 Gráficos Disponibles

El Dashboard incluye los siguientes gráficos interactivos generados con Chart.js:

| Gráfico | Tipo | Descripción |
|---------|------|-------------|
| **Distribución de Riesgo** | Doughnut (anillo) | Proporción de pacientes en cada nivel de riesgo: Crítico, Alto, Medio, Bajo |
| **Distribución por Sexo** | Doughnut (anillo) | Distribución de pacientes por género (Masculino, Femenino, Desconocido) |
| **Buckets de Edad** | Barras | Cantidad de pacientes por rango etario: <18, 18–34, 35–49, 50–64, 65+ |
| **Buckets de IMC** | Barras | Clasificación por Índice de Masa Corporal: Bajo peso, Normal, Sobrepeso, Obeso |
| **Diagnósticos Principales** | Pastel (pie) | Los diagnósticos más frecuentes entre los pacientes |
| **Tendencia de Pacientes** | Líneas | Evolución del registro de pacientes a lo largo del tiempo |
| **Mapa de Calor Clínico** | Matriz de datos | Relación entre presión sistólica y niveles de glucosa |

### 4.4 Interpretación de Resultados

- **Distribución de Riesgo**: Un alto porcentaje de pacientes en nivel "Crítico" o "Alto" puede indicar una población con necesidades de intervención urgente.
- **Buckets de Edad**: Permite identificar qué grupos etarios son los más prevalentes en la base de pacientes.
- **Buckets de IMC**: Útil para detectar tendencias de obesidad o desnutrición en la población atendida.
- **Tendencia de Pacientes**: Muestra el crecimiento de la base de datos a lo largo del tiempo; útil para evaluar la adopción del sistema.

Para actualizar los datos del Dashboard en tiempo real, haga clic en el botón **"Actualizar"** disponible en la interfaz.

---

## 5. Proceso ETL

### 5.1 Carga de Archivos

El módulo ETL permite la carga de archivos con datos clínicos en formato **CSV** o **Excel (.xlsx / .xls)**. Está disponible para los roles **Administrador** y **Analista**.

**Pasos para cargar un archivo:**

1. Navegue a la sección **ETL** desde el menú principal.
2. Seleccione una de las siguientes opciones:
   - **Cargar archivo**: Haga clic en el botón "Seleccionar archivo" y elija un archivo CSV o Excel desde su computadora.
   - **Usar dataset predeterminado**: Seleccione esta opción para utilizar el conjunto de datos clínico de demostración (1800 registros incluido en el sistema).
3. Haga clic en **"Ejecutar ETL"** para iniciar el proceso.

### 5.2 Validación de Datos

El sistema realiza las siguientes validaciones durante el proceso ETL:

1. **Detección de duplicados Nivel 1 (archivo)**: Se calcula un hash SHA256 del archivo cargado. Si el archivo ya fue procesado anteriormente, se rechaza y se notifica al usuario.
2. **Detección de duplicados Nivel 2 (paciente)**: Se verifica si el `id_paciente` ya existe en la base de datos. Los registros duplicados se omiten y se registran en el historial.
3. **Limpieza de datos**: Se normalizan los encabezados (eliminación de acentos, conversión a snake_case), se convierten tipos de datos numéricos y se eliminan unidades de medida (mmHg, %, mm).

### 5.3 Transformación

Durante la transformación, el sistema aplica las siguientes operaciones:

1. **Imputación de valores faltantes**: Los valores ausentes se completan con valores predeterminados clínicamente razonables (edad = 35, peso = 72, altura = 1.70).
2. **Cálculo automático del IMC**: Se recalcula el Índice de Masa Corporal a partir del peso y la altura.
3. **Normalización de booleanos**: Los campos binarios se convierten a valores estandarizados.
4. **Redistribución clínica**: Se aplica una redistribución estadística que asigna aproximadamente un 20% de pacientes a nivel crítico, 25% a nivel alto y el resto a niveles medio y bajo.
5. **Asignación de puntaje de riesgo**: Se calcula un puntaje basado en una suma ponderada de presión sistólica, presión diastólica, glucosa, SpO2, colesterol, IMC, edad y tabaquismo.
6. **Asignación de diagnóstico preliminar**: Se genera un diagnóstico preliminar basado en el perfil clínico del paciente.

### 5.4 Almacenamiento

Una vez transformados, los datos se almacenan en la base de datos:

1. Los registros nuevos se insertan en la tabla de pacientes.
2. Se registra un resumen del procesamiento en el historial ETL, incluyendo:
   - Archivo procesado
   - Número de registros procesados
   - Número de registros insertados
   - Número de registros duplicados
   - Duración del proceso
   - Estado (éxito/error)

### 5.5 Historial de Procesamientos

El sistema mantiene un registro histórico de todas las ejecuciones ETL. Para consultarlo:

1. Navegue a la sección **ETL**.
2. Desplácese hacia abajo para ver la tabla de **Historial de Procesamientos**.
3. La tabla muestra: fecha de inicio, fecha de finalización, archivo, registros procesados, duración y estado.

#### Posibles Errores y Soluciones Recomendadas

| Error | Causa Posible | Solución Recomendada |
|-------|---------------|----------------------|
| "El archivo ya fue procesado" | El archivo tiene un hash SHA256 que ya existe en el sistema | Cargue un archivo diferente o verifique si ya fue procesado anteriormente |
| "Formato de archivo no soportado" | El archivo no es CSV, XLSX ni XLS | Convierta el archivo a uno de los formatos soportados |
| "No se pudieron leer los datos" | El archivo está corrupto o tiene un formato incorrecto | Verifique la integridad del archivo y que contenga las columnas requeridas |
| "Error de conexión a la base de datos" | Problema temporal de conectividad | Intente nuevamente en unos minutos. Si persiste, contacte al soporte técnico |

---

## 6. Módulo de Analítica

### 6.1 KPIs

El módulo de analítica proporciona indicadores clave de salud poblacional, accesibles desde el panel de control y desde la API de analítica:

| KPI | Descripción |
|-----|-------------|
| **Total de pacientes** | Conteo absoluto de pacientes registrados |
| **Pacientes críticos** | Número de pacientes en nivel de riesgo crítico |
| **Pacientes de alto riesgo** | Número de pacientes en nivel de riesgo alto |
| **Pacientes de riesgo medio** | Número de pacientes en nivel de riesgo medio |
| **Pacientes de bajo riesgo** | Número de pacientes en nivel de riesgo bajo |
| **Hipertensos** | Pacientes con diagnóstico de hipertensión |
| **Diabéticos** | Pacientes con diagnóstico de diabetes |
| **Fumadores** | Pacientes que son fumadores activos |
| **Riesgo promedio** | Puntaje de riesgo promedio calculado sobre todos los pacientes |

### 6.2 Estadísticas Descriptivas

Para las siguientes variables clínicas, el sistema calcula:

| Variable | Media | Mediana | Moda | Desviación Estándar |
|----------|-------|---------|------|---------------------|
| Edad | ✓ | ✓ | ✓ | ✓ |
| IMC | ✓ | ✓ | ✓ | ✓ |
| Presión Sistólica | ✓ | ✓ | ✓ | ✓ |
| Presión Diastólica | ✓ | ✓ | ✓ | ✓ |
| Glucosa | ✓ | ✓ | ✓ | ✓ |
| SpO2 (Saturación de Oxígeno) | ✓ | ✓ | ✓ | ✓ |
| Colesterol | ✓ | ✓ | ✓ | ✓ |

### 6.3 Segmentación de Datos

El sistema permite segmentar la población de pacientes según los siguientes criterios:

| Segmentación | Categorías |
|--------------|------------|
| **Por edad** | < 18 años, 18–34, 35–49, 50–64, 65+ |
| **Por sexo** | Masculino, Femenino, Desconocido |
| **Por IMC (OMS)** | Bajo peso, Normal, Sobrepeso, Obeso |
| **Por diagnóstico** | Lista de diagnósticos registrados |
| **Por nivel de riesgo** | Crítico, Alto, Medio, Bajo |

### 6.4 Interpretación de Resultados

- **Estadísticas descriptivas**: Permiten comprender la distribución y variabilidad de las variables clínicas en la población atendida.
- **Segmentaciones**: Facilitan la identificación de subgrupos poblacionales que requieren atención específica (por ejemplo, adultos mayores con obesidad).

---

## 7. Modelos de Machine Learning

### 7.1 Descripción General

HealthAnalytics IPS incorpora un modelo de **Random Forest Classifier** entrenado para predecir el nivel de riesgo de enfermedad cardiovascular en pacientes. El modelo clasifica a los pacientes en cuatro categorías: **Bajo**, **Medio**, **Alto** y **Crítico**.

**Características del modelo:**

- **Algoritmo**: Random Forest (150 árboles, profundidad máxima 15)
- **Características de entrada** (6 variables numéricas):
  - Edad (`edad`)
  - Índice de Masa Corporal (`imc`)
  - Presión Sistólica (`presion_sistolica`)
  - Presión Diastólica (`presion_diastolica`)
  - Glucosa (`glucosa`)
  - Colesterol (`colesterol`)
- **Balanceo de clases**: SMOTE (Synthetic Minority Over-sampling Technique)
- **Partición**: 80% entrenamiento / 20% prueba (estratificada)

### 7.2 Entrenamiento

El entrenamiento del modelo está disponible para los roles **Administrador** y **Analista**.

**Pasos para entrenar un nuevo modelo:**

1. Navegue a la sección **Machine Learning** desde el menú principal.
2. En el área de **Analista**, haga clic en el botón **"Entrenar Nuevo Modelo"**.
3. El sistema utilizará automáticamente todos los pacientes registrados en la base de datos para entrenar el modelo.
4. Espere a que el proceso complete (puede tomar varios segundos dependiendo del volumen de datos).
5. Una vez finalizado, el nuevo modelo se activa automáticamente y se registra una nueva versión en el historial.

**Versiones del modelo:** El sistema mantiene un historial de todas las versiones entrenadas, accesible desde la tabla de versiones en la misma sección. Cada versión incluye la fecha de entrenamiento y las métricas de rendimiento.

### 7.3 Predicciones

La predicción de riesgo está disponible para los roles **Administrador** y **Médico**.

**Pasos para realizar una predicción:**

1. Navegue a la sección **Machine Learning**.
2. En el área **Clínica**, complete los siguientes campos del formulario:
   - Edad
   - IMC
   - Presión Sistólica
   - Presión Diastólica
   - Glucosa
   - Colesterol
3. Opcionalmente, ingrese un **ID de paciente** para asociar la predicción a un registro existente.
4. Haga clic en **"Predecir Riesgo"**.
5. El sistema mostrará:
   - **Nivel de riesgo** predicho (Bajo / Medio / Alto / Crítico)
   - **Porcentaje de confianza** de la predicción
   - **Probabilidades** detalladas para cada categoría

> **Nota:** Si se ingresa un ID de paciente, la predicción se registra automáticamente en el historial de predicciones del paciente.

### 7.4 Métricas

El modelo se evalúa utilizando las siguientes métricas estándar de clasificación:

| Métrica | Descripción | Interpretación |
|---------|-------------|----------------|
| **Accuracy (Exactitud)** | Proporción de predicciones correctas sobre el total de predicciones | Una exactitud del 89% significa que 89 de cada 100 predicciones son correctas |
| **Precision (Precisión)** | Proporción de verdaderos positivos sobre el total de predicciones positivas | Indica qué tan confiable es cuando el modelo predice una clase específica |
| **Recall (Sensibilidad)** | Proporción de verdaderos positivos sobre el total de casos positivos reales | Mide la capacidad del modelo para identificar correctamente los casos positivos |
| **F1 Score** | Media armónica entre precisión y recall | Proporciona un balance entre precisión y sensibilidad; útil cuando hay clases desbalanceadas |

**Ejemplo de métricas del modelo activo (última versión):**

| Métrica | Entrenamiento | Prueba |
|---------|---------------|--------|
| Accuracy | 99.59% | 89.17% |
| Precision (ponderada) | 87.40% | 90.30% |
| Recall (ponderado) | 89.10% | 89.10% |
| F1-Score (ponderado) | 88.30% | 89.00% |

> **Nota:** Las métricas pueden variar entre versiones del modelo. Consulte la tabla de versiones en la interfaz para ver las métricas actualizadas.

---

## 8. Reportes

### 8.1 Generación de Reportes

El módulo de reportes permite exportar los datos de pacientes en múltiples formatos. Todos los roles autenticados tienen acceso a esta sección.

**Pasos para generar un reporte:**

1. Navegue a la sección **Reportes** desde el menú principal.
2. Opcionalmente, seleccione un filtro por **nivel de riesgo** en el menú desplegable (Bajo, Medio, Alto, Crítico) para limitar los datos exportados.
3. Seleccione el formato de exportación deseado.

### 8.2 Exportación CSV

- **Formato**: Archivo CSV (valores separados por comas)
- **Columnas incluidas**: ID, Nombres, Apellidos, Edad, Sexo, IMC, Riesgo, Fecha de registro
- **Cómo exportar**: Haga clic en el botón **"Exportar CSV"** en la sección de reportes
- **Compatibilidad**: Abre directamente en Microsoft Excel, Google Sheets o cualquier editor de texto

### 8.3 Exportación Excel

- **Formato**: Archivo Excel (.xlsx) con múltiples hojas
- **Hojas incluidas**:

| Hoja | Contenido |
|------|-----------|
| **Pacientes** | Todos los registros de pacientes (con filtro aplicado) |
| **KPIs** | Indicadores clave: distribución por nivel de riesgo |
| **Segmentaciones** | Distribución por rangos de edad |
| **Predicciones** | Últimas 50 predicciones de Machine Learning |
| **Historial ETL** | Últimas 50 ejecuciones del proceso ETL |
| **Meta** | Metadatos del reporte: fecha de generación, filtros aplicados |

- **Cómo exportar**: Haga clic en el botón **"Exportar Excel"**
- **Nombre del archivo**: `healthanalytics_report.xlsx`

### 8.4 Exportación PDF

- **Formato**: Documento PDF con paginación
- **Capacidad máxima**: Hasta 200 pacientes por reporte
- **Contenido**: Tabla formateada con datos de pacientes (ID, nombres, apellidos, edad, sexo, IMC, riesgo)
- **Cómo exportar**: Haga clic en el botón **"Exportar PDF"**
- **Compatibilidad**: Visualización en cualquier lector de PDF (Adobe Acrobat, navegadores web)

---

## 9. Gestión de Usuarios

### 9.1 Roles

El sistema cuenta con tres roles predefinidos. Los usuarios son creados exclusivamente por el administrador del sistema a través del panel de administración de Django (`/admin/`).

| Rol | Permisos |
|-----|----------|
| **Administrador** | Acceso total: dashboard, gestión completa de pacientes (CRUD), ejecución ETL, entrenamiento y predicción ML, exportación de reportes |
| **Médico** | Dashboard, creación y edición de pacientes, predicciones clínicas ML, exportación de reportes |
| **Analista** | Dashboard, ejecución ETL, entrenamiento de modelos ML y consulta de versiones, exportación de reportes |

### 9.2 Permisos

| Funcionalidad | Administrador | Médico | Analista |
|---------------|:-------------:|:------:|:--------:|
| Dashboard | ✓ | ✓ | ✓ |
| Listar pacientes | ✓ | ✓ | ✓ |
| Crear paciente | ✓ | ✓ | ✗ |
| Editar paciente | ✓ | ✓ | ✗ |
| Eliminar paciente | ✓ | ✗ | ✗ |
| Ejecutar ETL | ✓ | ✗ | ✓ |
| Predicción ML (Clínica) | ✓ | ✓ | ✗ |
| Entrenar modelo ML | ✓ | ✗ | ✓ |
| Ver versiones de modelos | ✓ | ✗ | ✓ |
| Exportar reportes | ✓ | ✓ | ✓ |

### 9.3 Buenas Prácticas

- **Asignación de roles**: Otorgue el rol de **Administrador** únicamente al personal de TI o supervisores del sistema.
- **Rol de Médico**: Asígnelo exclusivamente a personal clínico que necesita crear y editar registros de pacientes y realizar predicciones.
- **Rol de Analista**: Ideal para personal de datos que ejecuta procesos ETL y entrena modelos.
- **Rotación de contraseñas**: Cambie las contraseñas periódicamente según la política de seguridad de la institución.
- **Registro de accesos**: Todas las acciones quedan registradas en los historiales del sistema (ETL, predicciones, etc.).

---

## 10. Solución de Problemas Frecuentes

| Problema | Posible Causa | Solución |
|----------|---------------|----------|
| **No puedo iniciar sesión** | Credenciales incorrectas | Verifique que el usuario y la contraseña sean correctos. Contacte al administrador si olvidó su contraseña |
| **La sesión expiró** | Inactividad superior a 1 hora | Inicie sesión nuevamente |
| **No veo el botón de ETL** | Su rol no tiene permisos para ejecutar ETL | Solicite al administrador que le asigne el rol de Administrador o Analista |
| **No puedo eliminar un paciente** | Su rol es Médico o Analista | Solo el rol Administrador puede eliminar pacientes |
| **Error al cargar archivo ETL** | Formato incorrecto o archivo duplicado | Verifique que el archivo sea CSV o Excel (.xlsx/.xls) y que no haya sido procesado anteriormente |
| **El modelo ML no predice correctamente** | Modelo desactualizado o datos insuficientes | Entrene un nuevo modelo con más datos desde la sección ML (rol Administrador o Analista) |
| **Los gráficos del Dashboard no cargan** | Problema de conexión o JavaScript deshabilitado | Verifique su conexión a internet y que JavaScript esté habilitado en el navegador |
| **Error al exportar PDF** | Más de 200 pacientes en el reporte | Aplique un filtro por nivel de riesgo para reducir la cantidad de registros |
| **Página no encontrada (404)** | URL incorrecta o recurso no disponible | Verifique la URL o navegue desde el menú principal |

---

## 11. Preguntas Frecuentes (FAQ)

**¿Cómo puedo crear una cuenta de usuario?**

Las cuentas de usuario son creadas exclusivamente por el administrador del sistema a través del panel de administración de Django (`/admin/`). No existe registro público.

**¿Qué tipos de archivos puedo cargar en el proceso ETL?**

El sistema acepta archivos en formato CSV (.csv), Excel (.xlsx) y Excel legacy (.xls).

**¿Cuántos pacientes puedo tener en el sistema?**

No hay un límite predefinido. La capacidad depende del plan de alojamiento y la base de datos configurada.

**¿Con qué frecuencia debo entrenar el modelo de Machine Learning?**

Se recomienda reentrenar el modelo cada vez que se cargue un lote significativo de nuevos pacientes (por ejemplo, cada 500–1000 nuevos registros) para mantener la precisión de las predicciones.

**¿Los datos de los pacientes están seguros?**

Sí. El sistema implementa medidas de seguridad como expiración de sesión (1 hora), cookies HttpOnly, cifrado de contraseñas y control de acceso basado en roles (RBAC).

**¿Puedo exportar los reportes con filtros específicos?**

Sí. En la sección de Reportes puede aplicar un filtro por nivel de riesgo antes de exportar. La exportación a Excel incluye el filtro aplicado en la hoja de metadatos.

**¿Qué significan los colores en las etiquetas de riesgo de los pacientes?**

- **Rojo (danger)**: Riesgo Crítico
- **Amarillo/Naranja (warning)**: Riesgo Alto
- **Azul (info)**: Riesgo Medio
- **Verde (success)**: Riesgo Bajo

**¿Cómo puedo ver el historial de procesamientos ETL?**

El historial se muestra en la parte inferior de la página de ETL, en una tabla con fecha, archivo, registros procesados y estado.

---

## 12. Contacto y Soporte

Para obtener soporte técnico o resolver dudas adicionales sobre el sistema, utilice los siguientes canales:

| Canal | Detalle |
|-------|---------|
| **Repositorio del proyecto** | GitHub: [Healthcare-ETL-Analytics-Platform](https://github.com/santicova18/Healthcare-ETL-Analytics-Platform) |
| **Plataforma en vivo** | [healthcare-etl-analytics-platform.onrender.com](https://healthcare-etl-analytics-platform.onrender.com/) |
| **Reporte de incidencias** | Abra un issue en el repositorio del proyecto |
| **Documentación** | README.md, manual de usuario y documentación técnica de métricas del modelo |

---

*Documento generado para la plataforma **HealthAnalytics IPS** — Panel Clínico de Gestión y Analítica de Datos en Salud.*

*Versión del sistema: 1.0.0*
