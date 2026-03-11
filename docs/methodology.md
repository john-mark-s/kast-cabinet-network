# Metodología

## Principio fundamental

> Los patrones identificados son **señales para la investigación periodística**, no prueba de irregularidades. Toda conexión incluye enlaces directos a las fuentes públicas para verificación independiente.

---

## Definiciones de alertas (Red Flags)

### SELF_DEALING — Autocontratación
**Criterio:** El ministro/a encabeza un ministerio que ha otorgado contratos a una empresa donde tiene participación patrimonial declarada.

**Severidad:** Crítica

**Por qué importa:** La ley de probidad y el Estatuto Administrativo prohíben ejercer jurisdicción sobre asuntos donde uno tiene interés personal. Requiere investigación periodística y potencialmente denuncia ante la Contraloría.

**Cómo verificar:** Declaración de intereses en InfoProbidad + contratos del ministerio en ChileCompra.

---

### REVOLVING_DOOR — Puerta giratoria
**Criterio:** Una persona transitó entre el sector privado (empresa vinculada a un ministro) y un cargo público, o viceversa, dentro de un período de 24 meses.

**Severidad:** Alta

**Por qué importa:** Las personas con conocimiento privilegiado del Estado pueden usar ese conocimiento en beneficio privado, o viceversa.

**Cómo verificar:** Declaraciones en InfoProbidad (sección "actividades ejercidas"), portales de transparencia ministeriales.

---

### COLLUSION_LINK — Vínculo con caso de colusión
**Criterio:** Una entidad ha sido nombrada en resoluciones del TDLC (Tribunal de Defensa de la Libre Competencia) o investigaciones de la FNE (Fiscalía Nacional Económica) como parte de un cartel o práctica anticompetitiva.

**Severidad:** Alta

**Por qué importa:** Indica que la entidad ha participado en conductas que dañan a consumidores y al mercado. Si esa entidad ahora tiene acceso privilegiado al Estado, puede reproducir esas prácticas en compras públicas.

**Cómo verificar:** Resoluciones del TDLC en tdlc.cl. Investigaciones FNE en fne.gob.cl.

---

### DIRECT_AWARD_CLUSTER — Trato directo repetido
**Criterio:** El mismo proveedor recibió 3 o más contratos por trato directo (sin licitación) del mismo organismo comprador en un período de 12 meses.

**Severidad:** Alta

**Por qué importa:** El trato directo debería ser la excepción. Su uso repetido con el mismo proveedor puede indicar favoritismo o evasión de controles.

**Cómo verificar:** ChileCompra → filtrar por tipo "Trato Directo" + RUT proveedor.

---

### LOBBY_TO_CONTRACT — Lobby seguido de contrato
**Criterio:** Una entidad que registró audiencias con un ministerio (ley de lobby) luego recibió un contrato de ese mismo ministerio dentro de 18 meses.

**Severidad:** Alta

**Por qué importa:** No es necesariamente irregular, pero es una señal que merece investigación. Las audiencias y contratos son públicos.

**Cómo verificar:** InfoLobby (audiencias) + ChileCompra (contratos) + comparar fechas y entidades.

---

### CONCENTRATION — Concentración de contratos
**Criterio:** Un único proveedor representa más del 40% del gasto de un ministerio en una categoría de compra en un año.

**Severidad:** Media

**Por qué importa:** Puede indicar falta de competencia en el proceso de compra o dependencia excesiva de un proveedor.

**Cómo verificar:** ChileCompra datos abiertos → análisis por ministerio y categoría.

---

### CORPORATE_RESTRUCTURING — Reestructuración corporativa
**Criterio:** Una empresa fue renombrada, fusionada o restructurada dentro de 12 meses de un evento de escrutinio público (investigación, nombramiento a cargo público, etc.).

**Severidad:** Media

**Por qué importa:** Puede ser legítimo, pero también puede ser un intento de disociar al titular de sus intereses corporativos para efectos de declaración.

**Cómo verificar:** Registro de Comercio, nómina SII (buscar historial de cambio de nombre), prensa.

---

### GOV_CONTRACTOR — Contratista del Estado
**Criterio:** La entidad tiene o ha tenido contratos con organismos del Estado.

**Severidad:** Informativa

**Por qué importa:** No es negativo en sí mismo. Es un indicador de que la entidad tiene relación económica con el Estado.

**Cómo verificar:** ChileCompra por RUT.

---

### ACTIVE_CONTRACT — Contrato activo
**Criterio:** La entidad tiene un contrato activo (sin fecha de término, o fecha de término en el futuro).

**Severidad:** Informativa

**Por qué importa:** Un contrato activo durante el ejercicio del cargo del ministro vinculado es más relevante que contratos históricos.

**Cómo verificar:** ChileCompra → verificar estado del contrato.

---

## Niveles de severidad

| Nivel | Significado |
|-------|-------------|
| Crítico | Posible conflicto de interés directo; requiere atención inmediata |
| Alto | Señal significativa que merece investigación periodística |
| Medio | Patrón a seguir; contexto es clave |
| Info | Dato de contexto; no implica irregularidad |

---

## El RUT como llave de enlace

Chile asigna un RUT único a toda persona y empresa. Este proyecto usa el RUT para vincular:

1. **InfoProbidad** → ministro declara RUT de empresas donde tiene participación
2. **SII** → confirma nombre, actividad y dirección de esas empresas
3. **ChileCompra** → busca contratos donde esas empresas son proveedoras
4. **InfoLobby** → busca audiencias de esas empresas con organismos públicos

Este sistema de cruce de RUTs permite construir el grafo de conexiones automáticamente a medida que llegan nuevas declaraciones.

---

## Limitaciones

1. **Datos de InfoProbidad**: Los declarantes pueden omitir bienes o intereses. Las declaraciones son juradas pero no auditadas de forma rutinaria.

2. **ChileCompra**: Las compras directas menores (bajo UTM 3) no siempre se publican. Algunos contratos tienen datos incompletos.

3. **InfoLobby**: Solo registra desde 2014. No captura reuniones informales (almuerzo, golf, evento social).

4. **SII**: No identifica propietarios. Solo actividad y dirección de la empresa.

5. **Alcance Phase 1**: En la fase inicial, solo Jorge Quiroz está completamente mapeado. Los demás ministros son nodos semilla.

---

## Cómo reportar errores

Abre un issue en GitHub con:
- El dato incorrecto
- La fuente que contradice el dato
- Un enlace directo a la fuente
