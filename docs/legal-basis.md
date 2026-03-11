# Base Legal

Este proyecto se basa en tres leyes de transparencia que obligan al Estado chileno a publicar datos de sus funcionarios.

## Ley 20.285 — Transparencia y Acceso a la Información Pública (2008)

**Texto oficial:** https://www.bcn.cl/leychile/navegar?idNorma=276363

### ¿Qué obliga?
- **Transparencia activa:** Los organismos públicos deben publicar proactivamente información sobre sus actos, contratos, presupuestos y personal.
- **Transparencia pasiva:** Cualquier ciudadano puede solicitar información a órganos del Estado. El organismo tiene 20 días para responder.
- El Consejo para la Transparencia (CPLT) supervisa el cumplimiento.

### Relevancia para este proyecto
Todos los contratos en Mercado Público (ChileCompra) son públicos bajo esta ley. Los portales de transparencia activa de cada ministerio deben publicar sus contratos y gastos.

---

## Ley 20.730 — Regulación del Lobby (2014)

**Texto oficial:** https://www.bcn.cl/leychile/navegar?idNorma=1060115

### ¿Qué obliga?
- Los **sujetos pasivos** (ministros, subsecretarios, intendentes, alcaldes, altos funcionarios) deben registrar:
  - **Audiencias** con personas que buscan influir en decisiones públicas
  - **Viajes** financiados por terceros
  - **Donativos** recibidos
- Los registros se publican en **leylobby.gob.cl** dentro de 48-72 horas.
- La API REST de InfoLobby es pública y no requiere autenticación.

### Relevancia para este proyecto
Permite rastrear quién se reúne con qué ministro/a. Si una empresa se reúne con un ministerio y luego obtiene un contrato de ese ministerio, es una señal LOBBY_TO_CONTRACT.

---

## Ley 20.880 — Probidad en la Función Pública (2016)

**Texto oficial:** https://www.bcn.cl/leychile/navegar?idNorma=1086062

### ¿Qué obliga?
Los ministros, subsecretarios y otros altos funcionarios deben presentar **declaraciones de patrimonio e intereses** en tres momentos:
1. **Al asumir el cargo** (dentro de 30 días)
2. **Anualmente** (hasta el 31 de marzo de cada año)
3. **Al cesar en el cargo** (dentro de 30 días de salir)

Las declaraciones incluyen:
- Bienes raíces
- Vehículos
- Cuentas bancarias
- Inversiones y valores
- **Participaciones en sociedades y empresas**
- Deudas
- Actividades ejercidas en los 12 meses anteriores al cargo

### Relevancia para este proyecto
Las **participaciones en empresas** son la fuente primaria para construir el grafo de conexiones corporativas. Si un ministro declara tener acciones en una empresa que luego recibe contratos del Estado, es una señal SELF_DEALING.

---

## Portal de verificación

Todos los datos de InfoProbidad son accesibles en: https://www.infoprobidad.cl/Home/Listado

La API de datos abiertos de InfoProbidad está en: https://www.infoprobidad.cl/DatosAbiertos/DatosAbiertos
