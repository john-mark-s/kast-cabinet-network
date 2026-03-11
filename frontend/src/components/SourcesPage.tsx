import { ExternalLink, Scale, Users, Building } from 'lucide-react';

const LEGAL_BASIS = [
  {
    law: "Ley 20.285 (2008)",
    desc: "Ley de Transparencia y Acceso a la Información Pública. Obliga al Estado a publicar datos de forma activa (transparencia activa) y a responder solicitudes ciudadanas.",
    url: "https://www.bcn.cl/leychile/navegar?idNorma=276363",
    icon: Scale,
  },
  {
    law: "Ley 20.730 (2014)",
    desc: "Ley del Lobby. Obliga a registrar todas las audiencias, viajes y donativos de autoridades sujetas al lobby. Los registros son públicos en leylobby.gob.cl.",
    url: "https://www.bcn.cl/leychile/navegar?idNorma=1060115",
    icon: Users,
  },
  {
    law: "Ley 20.880 (2016)",
    desc: "Ley sobre Probidad en la Función Pública. Ministros y altos funcionarios deben declarar todo su patrimonio e intereses al asumir, durante el cargo y al salir.",
    url: "https://www.bcn.cl/leychile/navegar?idNorma=1086062",
    icon: Building,
  },
];

const DATA_SOURCES = [
  {
    id: "infoprobidad",
    name: "InfoProbidad",
    url: "https://www.infoprobidad.cl/Home/Listado",
    desc: "Portal oficial de declaraciones de patrimonio e intereses. Datos abiertos disponibles en formato estructurado.",
    format: "Portal web + API REST",
    frequency: "Al asumir, anualmente y al salir del cargo",
    license: "Datos públicos (Ley 20.880)",
    limitations: "Algunas declaraciones pueden estar desactualizadas o incompletas.",
  },
  {
    id: "chilecompra",
    name: "Mercado Público (ChileCompra)",
    url: "https://www.mercadopublico.cl/",
    desc: "Portal de compras públicas del Estado. API REST permite consultar órdenes de compra por RUT de proveedor.",
    format: "API REST (JSON)",
    frequency: "Tiempo real",
    license: "CC0 (datos abiertos)",
    limitations: "API pública tiene límite de velocidad. Algunas licitaciones antiguas no están disponibles.",
  },
  {
    id: "infolobby",
    name: "InfoLobby (leylobby.gob.cl)",
    url: "https://www.leylobby.gob.cl/",
    desc: "Registro de audiencias, viajes y donativos. API REST sin autenticación.",
    format: "API REST (JSON)",
    frequency: "Tiempo real (registro obligatorio en 48-72h)",
    license: "Datos públicos (Ley 20.730)",
    limitations: "Solo registra desde 2014. No incluye reuniones informales.",
  },
  {
    id: "sii",
    name: "SII — Nómina de Personas Jurídicas",
    url: "https://www.sii.cl/sobre_el_sii/nominapersonasjuridicas.html",
    desc: "Descarga masiva de la nómina de empresas chilenas. Permite verificar actividad, tamaño y dirección de cualquier empresa por RUT.",
    format: "CSV/Excel (descarga masiva)",
    frequency: "Actualización mensual",
    license: "Datos públicos",
    limitations: "No incluye información financiera ni nombres de dueños.",
  },
];

const VERIFY_STEPS = [
  {
    title: "Declaraciones de patrimonio (InfoProbidad)",
    steps: [
      "Ve a infoprobidad.cl → Listado",
      "Busca por nombre del ministro/a",
      "Descarga la declaración más reciente",
      "Revisa: participaciones en empresas, bienes raíces, vehículos, deudas",
    ],
    url: "https://www.infoprobidad.cl/Home/Listado",
  },
  {
    title: "Contratos públicos (Mercado Público)",
    steps: [
      "Ve a mercadopublico.cl → Búsqueda Avanzada",
      "En el campo 'Proveedor', ingresa el RUT de la empresa (ej: 96.953.120-8)",
      "Filtra por tipo: Orden de Compra",
      "Revisa montos, compradores y fechas",
    ],
    url: "https://www.mercadopublico.cl/Portal/Modules/Site/Busquedas/BuscadorAvanzado.aspx",
  },
  {
    title: "Reuniones de lobby (InfoLobby)",
    steps: [
      "Ve a leylobby.gob.cl",
      "Selecciona el ministerio correspondiente",
      "Selecciona al ministro/a como sujeto pasivo",
      "Revisa audiencias, viajes con financiamiento externo y donativos",
    ],
    url: "https://www.leylobby.gob.cl/",
  },
  {
    title: "Empresas (SII)",
    steps: [
      "Ve a sii.cl → Nómina de Personas Jurídicas",
      "Descarga el archivo CSV",
      "Busca por RUT para verificar: nombre, actividad económica, tamaño, dirección",
    ],
    url: "https://www.sii.cl/sobre_el_sii/nominapersonasjuridicas.html",
  },
];

export function SourcesPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      {/* Legal basis */}
      <section>
        <h2 className="text-lg font-semibold text-slate-100 mb-4">Base Legal</h2>
        <div className="grid gap-4 sm:grid-cols-3">
          {LEGAL_BASIS.map(({ law, desc, url, icon: Icon }) => (
            <div key={law} className="bg-slate-800 border border-slate-700 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Icon className="w-4 h-4 text-blue-400" />
                <a
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm font-semibold text-blue-400 hover:text-blue-300"
                >
                  {law}
                </a>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Verification guide */}
      <section>
        <h2 className="text-lg font-semibold text-slate-100 mb-4">Guía de Verificación</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {VERIFY_STEPS.map(({ title, steps, url }) => (
            <div key={title} className="bg-slate-800 border border-slate-700 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-slate-200 mb-3">{title}</h3>
              <ol className="space-y-1.5">
                {steps.map((step, i) => (
                  <li key={i} className="flex gap-2 text-xs text-slate-400">
                    <span className="flex-shrink-0 w-4 h-4 rounded-full bg-slate-700 text-slate-300 flex items-center justify-center text-xs">
                      {i + 1}
                    </span>
                    <span className="leading-relaxed">{step}</span>
                  </li>
                ))}
              </ol>
              <a
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-3 flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300"
              >
                <ExternalLink className="w-3 h-3" />
                Ir al portal
              </a>
            </div>
          ))}
        </div>
      </section>

      {/* Data sources */}
      <section>
        <h2 className="text-lg font-semibold text-slate-100 mb-4">Fuentes de Datos</h2>
        <div className="space-y-3">
          {DATA_SOURCES.map(source => (
            <div key={source.id} className="bg-slate-800 border border-slate-700 rounded-lg p-4">
              <div className="flex items-start justify-between gap-2 mb-2">
                <a
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 text-sm font-semibold text-blue-400 hover:text-blue-300"
                >
                  {source.name}
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
              <p className="text-xs text-slate-400 mb-2">{source.desc}</p>
              <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
                <div>
                  <span className="text-slate-500">Formato: </span>
                  <span className="text-slate-300">{source.format}</span>
                </div>
                <div>
                  <span className="text-slate-500">Licencia: </span>
                  <span className="text-slate-300">{source.license}</span>
                </div>
                <div className="col-span-2">
                  <span className="text-slate-500">Frecuencia: </span>
                  <span className="text-slate-300">{source.frequency}</span>
                </div>
                <div className="col-span-2">
                  <span className="text-slate-500">Limitaciones: </span>
                  <span className="text-slate-400">{source.limitations}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Disclaimer */}
      <section className="bg-slate-800/50 border border-slate-700 rounded-lg p-5">
        <h2 className="text-sm font-semibold text-slate-300 mb-2">Aviso metodológico</h2>
        <p className="text-sm text-slate-400 leading-relaxed">
          Este proyecto presenta conexiones documentadas en fuentes públicas. Los patrones identificados
          son <strong className="text-slate-300">señales para la investigación periodística, no prueba de irregularidades</strong>.
          Cada dato incluye enlaces de verificación para que cualquier persona pueda comprobar la información de forma independiente.
        </p>
        <p className="text-sm text-slate-400 leading-relaxed mt-2">
          Errores y omisiones pueden reportarse abriendo un issue en{' '}
          <a
            href="https://github.com/johnmarkshorack/kast-cabinet-network"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-400 hover:text-blue-300"
          >
            GitHub
          </a>
          . Todos los datos provienen de fuentes gubernamentales públicas bajo las leyes 20.285, 20.730 y 20.880.
        </p>
      </section>
    </div>
  );
}
