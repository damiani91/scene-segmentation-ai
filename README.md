# Scene Segmentation

## ¿Cómo Funciona? Flujo Técnico Detallado

El proceso se puede dividir en tres grandes pasos:

### 1. Interfaz de Usuario y Carga del Video (Frontend - React):

*   **Carga de archivo**: El usuario ve una interfaz limpia y moderna (diseñada con TailwindCSS) con un área para arrastrar y soltar o seleccionar un archivo de video desde su dispositivo.
*   **Previsualización**: Una vez que se selecciona un video válido, la aplicación lo muestra en un reproductor de video. Esto le permite al usuario confirmar que ha subido el archivo correcto antes de comenzar el costoso (en tiempo y procesamiento) análisis.
*   **Botón de Análisis**: Hay un botón principal, "Analyze Video", que inicia todo el proceso. Este botón se desactiva mientras el análisis está en curso para evitar acciones duplicadas.

### 2. Procesamiento del Video en el Navegador (Frontend - JavaScript):

Cuando el usuario hace clic en "Analyze Video", la aplicación no envía el archivo de video completo a Gemini. En su lugar, realiza un ingenioso pre-procesamiento directamente en el navegador del usuario.

*   **Extracción de Fotogramas (extractFramesFromVideo)**: La aplicación carga el video en un elemento `<video>` de HTML que no es visible. Luego, utiliza un elemento `<canvas>` para "dibujar" fotogramas (imágenes estáticas) del video a intervalos regulares (actualmente, extrae 2 fotogramas por cada segundo de video).
*   **Conversión a Base64**: Cada fotograma capturado se convierte en una cadena de texto en formato Base64 con el tipo de imagen image/jpeg. El resultado es un arreglo (una lista) de muchas imágenes que representan la secuencia del video.

### 3. Análisis con la API de Gemini (Backend Lógico):

*   **Llamada a la API (analyzeVideoFrames)**: Ahora, la aplicación toma la lista de fotogramas en formato Base64 y la envía al modelo gemini-2.5-pro a través de la API de @google/genai.
*   **Prompt Multimodal**: La solicitud a la API es "multimodal", lo que significa que combina texto e imágenes. Se envía:
    *   Un prompt de texto que instruye al modelo para que actúe como un "experto analista de cine". Se le pide que identifique escenas distintas (definiendo una escena como una acción continua en un mismo lugar) y que genere metadatos para cada una.
    *   La secuencia de imágenes (los fotogramas) que el modelo analizará visualmente.
*   **Respuesta Estructurada (JSON Schema)**: La solicitud se configura para que Gemini devuelva la respuesta obligatoriamente en formato JSON, siguiendo un esquema (responseSchema) muy específico. Este esquema define qué campos debe tener cada objeto de escena:
    *   `scene_number`: Número de la escena.
    *   `start_time` y `end_time`: Marcas de tiempo de inicio y fin.
    *   `name`: Un título corto para la escena.
    *   `genre`: El género (Drama, Acción, etc.).
    *   `description`: Un resumen de lo que ocurre.
    *   `characters`, `setting`, `mood`: Campos opcionales para personajes, lugar y ambiente.

### Visualización del Resultado

*   **Estado de Carga**: Mientras todo este proceso ocurre, la interfaz muestra indicadores de carga claros, informando al usuario en qué etapa se encuentra ("Extrayendo fotogramas...", "Analizando con Gemini...").
*   **Manejo de Errores**: Si algo sale mal (el video está corrupto, la API falla, etc.), se muestra un mensaje de error descriptivo.
*   **Visor de JSON**: Cuando el análisis es exitoso, el JSON resultante se muestra en un visor de código bien formateado en la columna derecha de la aplicación. Este componente incluye un práctico botón para copiar todo el JSON al portapapeles con un solo clic.

### Casos de Uso Potenciales

Esta herramienta es increíblemente útil para:

*   **Editores de video y cineastas**: Para generar rápidamente un desglose de escenas o un guion de post-producción.
*   **Archivistas y bibliotecas de medios**: Para catalogar y etiquetar grandes volúmenes de contenido de video de forma automática, haciéndolo más fácil de buscar.
*   **Creadores de contenido**: Para obtener resúmenes y metadatos de sus videos para plataformas como YouTube.
*   **Empresas de marketing**: Para analizar contenido de video y entender mejor su estructura y mensaje.
