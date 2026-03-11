import { X, ExternalLink, Building2, User, Landmark, AlertTriangle } from 'lucide-react';
import type { GraphNode, GraphEdge } from '../types/graph';
import { RedFlagBadge } from './RedFlagBadge';
import { formatRutDisplay } from '../utils/rut';

interface Props {
  node: GraphNode;
  edges: GraphEdge[];
  allNodes: GraphNode[];
  onClose: () => void;
  onSelectNode: (id: string) => void;
}

const TYPE_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  person: User,
  company: Building2,
  institution: Landmark,
  corporate_client: AlertTriangle,
};

const TYPE_LABELS: Record<string, string> = {
  person: 'Persona',
  company: 'Empresa',
  institution: 'Institución',
  corporate_client: 'Cliente corporativo',
};

export function EntityProfile({ node, edges, allNodes, onClose, onSelectNode }: Props) {
  const TypeIcon = TYPE_ICONS[node.type] ?? User;
  const nodeMap = new Map(allNodes.map(n => [n.id, n]));

  // Find connected nodes
  const connectedEdges = edges.filter(e => e.source === node.id || e.target === node.id);
  const connectedNodes = connectedEdges
    .map(e => {
      const otherId = e.source === node.id ? e.target : e.source;
      return { edge: e, node: nodeMap.get(otherId) };
    })
    .filter(({ node: n }) => n !== undefined);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-start justify-between p-4 border-b border-slate-700">
        <div className="flex items-start gap-3 min-w-0">
          <div className={`p-2 rounded-lg flex-shrink-0 ${
            node.type === 'person' ? 'bg-blue-900' :
            node.type === 'company' ? 'bg-slate-700' :
            node.type === 'institution' ? 'bg-green-900' : 'bg-purple-900'
          }`}>
            <TypeIcon className="w-5 h-5 text-slate-100" />
          </div>
          <div className="min-w-0">
            <p className="text-xs text-slate-400">{TYPE_LABELS[node.type]}</p>
            <h2 className="text-base font-semibold text-slate-100 leading-tight">{node.label}</h2>
            {node.role && <p className="text-sm text-slate-400 mt-0.5">{node.role}</p>}
            {node.party && <p className="text-xs text-slate-500">{node.party}</p>}
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1 text-slate-400 hover:text-slate-200 flex-shrink-0 ml-2"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto">
        {/* RUT */}
        {node.rut && (
          <div className="px-4 pt-3">
            <p className="text-xs text-slate-400">RUT</p>
            <p className="text-sm font-mono text-slate-200">{formatRutDisplay(node.rut)}</p>
          </div>
        )}

        {/* Flags */}
        {node.flags.length > 0 && (
          <div className="px-4 pt-3">
            <p className="text-xs text-slate-400 mb-1.5">Alertas detectadas</p>
            <div className="flex flex-wrap gap-1">
              {node.flags.map(flag => (
                <RedFlagBadge key={flag} flag={flag} size="sm" />
              ))}
            </div>
          </div>
        )}

        {/* Notes */}
        {node.notes && (
          <div className="px-4 pt-3">
            <p className="text-xs text-slate-400 mb-1">Notas</p>
            <p className="text-sm text-slate-300 leading-relaxed">{node.notes}</p>
          </div>
        )}

        {/* Connections */}
        {connectedNodes.length > 0 && (
          <div className="px-4 pt-3">
            <p className="text-xs text-slate-400 mb-2">Conexiones ({connectedNodes.length})</p>
            <div className="space-y-1">
              {connectedNodes.map(({ edge, node: connNode }) => {
                if (!connNode) return null;
                const EdgeTypeIcon = TYPE_ICONS[connNode.type] ?? User;
                return (
                  <button
                    key={edge.id}
                    onClick={() => onSelectNode(connNode.id)}
                    className="w-full flex items-start gap-2 p-2 rounded bg-slate-800 hover:bg-slate-700 text-left transition-colors"
                  >
                    <EdgeTypeIcon className="w-3.5 h-3.5 text-slate-400 flex-shrink-0 mt-0.5" />
                    <div className="min-w-0">
                      <p className="text-xs font-medium text-slate-200 truncate">{connNode.label}</p>
                      <p className="text-xs text-slate-500 truncate">{edge.label}</p>
                      {edge.flags.length > 0 && (
                        <div className="flex gap-1 mt-0.5">
                          {edge.flags.slice(0, 2).map(f => (
                            <RedFlagBadge key={f} flag={f} size="sm" />
                          ))}
                        </div>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Verify section */}
        {node.verifyUrls.length > 0 && (
          <div className="px-4 pt-3 pb-4">
            <p className="text-xs text-slate-400 mb-2">Verificar estos datos</p>
            <div className="space-y-1">
              {node.verifyUrls.map((url, i) => (
                <a
                  key={i}
                  href={url.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-xs text-blue-400 hover:text-blue-300 transition-colors"
                >
                  <ExternalLink className="w-3 h-3 flex-shrink-0" />
                  {url.label}
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Sources */}
        {node.sources.length > 0 && (
          <div className="px-4 pt-2 pb-4 border-t border-slate-700">
            <p className="text-xs text-slate-500 mt-2">
              Fuentes: {node.sources.join(', ')}
            </p>
            {node.status === 'seed' && (
              <p className="text-xs text-slate-600 mt-1">
                Estado: nodo semilla — datos pendientes de mapeo
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
