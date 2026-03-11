import type { NodeType, RedFlag } from '../types/graph';

const NODE_TYPES: { value: NodeType; label: string; color: string }[] = [
  { value: 'person', label: 'Personas', color: 'bg-blue-500' },
  { value: 'company', label: 'Empresas', color: 'bg-slate-400' },
  { value: 'institution', label: 'Instituciones', color: 'bg-green-500' },
  { value: 'corporate_client', label: 'Clientes', color: 'bg-purple-500' },
];

const FLAG_TYPES: { value: RedFlag; label: string }[] = [
  { value: 'SELF_DEALING', label: 'Autocontratación' },
  { value: 'REVOLVING_DOOR', label: 'Puerta giratoria' },
  { value: 'COLLUSION_LINK', label: 'Colusión' },
  { value: 'CORPORATE_RESTRUCTURING', label: 'Reestructuración' },
  { value: 'GOV_CONTRACTOR', label: 'Contratista' },
  { value: 'ACTIVE_CONTRACT', label: 'Contrato activo' },
];

interface Props {
  activeTypes: Set<NodeType>;
  activeFlags: Set<RedFlag>;
  onTypeToggle: (type: NodeType) => void;
  onFlagToggle: (flag: RedFlag) => void;
}

export function FilterPanel({ activeTypes, activeFlags, onTypeToggle, onFlagToggle }: Props) {
  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
          Tipo de nodo
        </h3>
        <div className="space-y-1">
          {NODE_TYPES.map(({ value, label, color }) => (
            <button
              key={value}
              onClick={() => onTypeToggle(value)}
              className={`flex items-center gap-2 w-full text-left px-2 py-1 rounded text-sm transition-colors ${
                activeTypes.has(value)
                  ? 'text-slate-100'
                  : 'text-slate-500'
              }`}
            >
              <span className={`w-3 h-3 rounded-sm flex-shrink-0 ${activeTypes.has(value) ? color : 'bg-slate-700'}`} />
              {label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
          Alertas
        </h3>
        <div className="space-y-1">
          {FLAG_TYPES.map(({ value, label }) => (
            <button
              key={value}
              onClick={() => onFlagToggle(value)}
              className={`flex items-center gap-2 w-full text-left px-2 py-1 rounded text-sm transition-colors ${
                activeFlags.has(value)
                  ? 'text-red-300'
                  : 'text-slate-500'
              }`}
            >
              <span className={`w-3 h-3 rounded flex-shrink-0 border ${
                activeFlags.has(value) ? 'bg-red-900 border-red-600' : 'bg-slate-700 border-slate-600'
              }`} />
              {label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
