# Fuentes de Datos

## 1. InfoProbidad

**URL:** https://www.infoprobidad.cl/Home/Listado
**API datos abiertos:** https://www.infoprobidad.cl/DatosAbiertos/DatosAbiertos
**SPARQL endpoint:** https://www.infoprobidad.cl/DatosAbiertos/SparqlQuery

### Descripción
Portal oficial del Consejo para la Transparencia (CPLT) para las declaraciones de patrimonio e intereses, regidas por la Ley 20.880.

### Formato
- Portal web para búsqueda manual
- API REST para descarga de datos estructurados
- Endpoint SPARQL para consultas complejas

### Frecuencia de actualización
Cuando los funcionarios presentan declaraciones (al asumir, anualmente, al cesar).

### Licencia
Datos públicos bajo Ley 20.880. Sin restricciones de uso para transparencia ciudadana.

### Limitaciones
- Algunas declaraciones pueden estar desactualizadas
- La calidad de los datos depende de lo que declara el funcionario
- No se audita el contenido de forma rutinaria

### Uso en este proyecto
Fuente primaria para identificar participaciones en empresas de los ministros. Los RUTs de empresas extraídos aquí se usan para buscar contratos en ChileCompra.

---

## 2. Mercado Público (ChileCompra)

**URL portal:** https://www.mercadopublico.cl/
**API REST:** https://api.mercadopublico.cl/servicios/v1/
**Datos abiertos OCDS:** https://datos-abiertos.chilecompra.cl

### Descripción
Sistema de compras públicas del Estado. Todas las licitaciones y órdenes de compra del sector público deben publicarse aquí.

### API
- `/publico/ordenesdecompra.json` — Órdenes de compra, filtrable por RUT proveedor
- `/publico/licitaciones.json` — Licitaciones activas y cerradas
- Requiere API key (gratuita en mercadopublico.cl; fallback de test: F8537A18-6766-4DEF-9E59-426B4FEE2844)

### Parámetros clave
```
rutProveedor: 12.345.678-9   (RUT con puntos y guión)
fechaInicio: 2020-01-01
fechaFin: 2024-12-31
pagina: 1
ticket: {API_KEY}
```

### Formato
JSON. Cada orden incluye: RUT comprador, RUT proveedor, monto, descripción, tipo (licitación/trato directo), fechas.

### Frecuencia de actualización
Tiempo real (cada compra se publica en el momento).

### Licencia
CC0 (dominio público). Los datos abiertos OCDS están disponibles para descarga masiva.

### Limitaciones
- API tiene rate limiting; usar tenacity para reintentos
- Compras menores a 3 UTM (~$250.000 CLP) pueden no publicarse
- Algunos registros históricos (antes de 2003) son incompletos

---

## 3. InfoLobby (leylobby.gob.cl)

**URL portal:** https://www.leylobby.gob.cl/
**API REST:** https://www.leylobby.gob.cl/api/v1/

### Descripción
Registro público de audiencias, viajes y donativos de autoridades sujetas a la Ley del Lobby (20.730).

### API — sin autenticación requerida
Endpoints principales:
- `GET /api/v1/audiencias?nombre={nombre}&per_page=100&page=1`
- `GET /api/v1/viajes?nombre={nombre}`
- `GET /api/v1/donativos?nombre={nombre}`

### Formato
JSON con paginación (100 registros por página por defecto).

Cada audiencia incluye:
- Fecha y hora
- Lugar
- Sujeto pasivo (funcionario que recibe)
- Solicitantes (quiénes piden la audiencia)
- Materias abordadas
- Documentos adjuntos

### Frecuencia de actualización
Los sujetos pasivos deben registrar audiencias dentro de 48-72 horas de realizadas.

### Licencia
Datos públicos (Ley 20.730). Sin restricciones de uso.

### Limitaciones
- Solo cubre desde entrada en vigor de la ley (2014 para niveles superiores)
- No registra reuniones informales o sociales
- La descripción de las materias puede ser vaga

---

## 4. SII — Nómina de Personas Jurídicas

**URL:** https://www.sii.cl/sobre_el_sii/nominapersonasjuridicas.html

### Descripción
El Servicio de Impuestos Internos publica periódicamente una nómina de todas las empresas y personas jurídicas de Chile.

### Formato
CSV o Excel (descarga masiva). Columnas principales:
- RUT
- Razón social
- Actividad económica (código CIIU)
- Tamaño de empresa (micro, pequeña, mediana, grande)
- Región y comuna
- Dirección

### Frecuencia de actualización
Mensual (aproximadamente).

### Licencia
Datos públicos.

### Limitaciones
- No identifica propietarios o directores
- Solo la empresa activa (no historial de cambios de nombre)
- Puede haber RUTs inactivos que no aparecen

### Uso en este proyecto
Verificar que un RUT corresponde a la empresa esperada. Detectar empresas en la misma dirección (señal de red corporativa).

---

## 5. Biblioteca del Congreso (BCN)

**URL datos abiertos:** https://opendata.camara.cl
**Reseñas parlamentarias:** https://www.bcn.cl/historiapolitica/resenas_parlamentarias/

### Descripción
Datos biográficos y parlamentarios de ex-parlamentarios. Algunos ministros tienen fichas BCN por su trayectoria legislativa.

### Uso en este proyecto
Verificar trayectoria política de ministros que fueron parlamentarios.

---

## 6. Portal de Transparencia

**URL:** https://www.portaltransparencia.cl/PortalPdT/

### Descripción
Portal de transparencia activa del Estado. Cada organismo publica su información de forma proactiva (personal, contratos, actos administrativos, etc.).

### Uso en este proyecto
Verificar contratos y gastos de ministerios específicos.

---

## 7. TDLC y FNE

**TDLC:** https://www.tdlc.cl/
**FNE:** https://www.fne.gob.cl/

### Descripción
El Tribunal de Defensa de la Libre Competencia (TDLC) y la Fiscalía Nacional Económica (FNE) son las autoridades de competencia de Chile.

### Uso en este proyecto
Verificar si una empresa o persona ha sido parte en casos de colusión o anticompetencia.

---

## 8. Fuentes periodísticas

Las siguientes fuentes periodísticas documentan aspectos de la red de Quiroz que aún no están en datos estructurados:

| Fuente | URL | Relevancia |
|--------|-----|-----------|
| CIPER Chile | https://ciperchile.cl | Investigación: 15 registros de Quiroz en casos de colusión |
| La Tercera / Pulso | https://latercera.com | Red corporativa y separación de socios |
| Contrapoder Chile | https://contrapoderchile.cl | Contratos QA con gobierno Piñera |
| Conadecus | https://conadecus.cl | Análisis rol Quiroz en Metrogas |

**Nota:** Las fuentes periodísticas se usan como referencia para hechos verificables. En el grafo, los datos provenientes solo de fuentes periodísticas (sin respaldo en datos oficiales) se marcan como `status: "seed"` pendiente de verificación.
