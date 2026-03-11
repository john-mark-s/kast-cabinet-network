import { useState, useMemo, useEffect } from 'react';
import { Network, Radio, FileText, Github, AlertTriangle, X } from 'lucide-react';
import { useGraphData } from './hooks/useGraphData';
import { useChangelog } from './hooks/useChangelog';
import { NetworkGraph } from './components/NetworkGraph';
import { EntityProfile } from './components/EntityProfile';
import { MinisterSelector } from './components/MinisterSelector';
import { FilterPanel } from './components/FilterPanel';
import { SearchBar } from './components/SearchBar';
import { ChangesFeed } from './components/ChangesFeed';
import { SourcesPage } from './components/SourcesPage';
import type { NodeType, RedFlag } from './types/graph';

type Tab = 'graph' | 'changes' | 'sources';

export default function App() {
  const { graph, loading, error } = useGraphData();
  const { totalEvents } = useChangelog();

  const [activeTab, setActiveTab] = useState<Tab>('graph');
  const [showDisclaimer, setShowDisclaimer] = useState(
    () => localStorage.getItem('disclaimer-dismissed') !== '1'
  );

  useEffect(() => {
    if (!showDisclaimer) localStorage.setItem('disclaimer-dismissed', '1');
  }, [showDisclaimer]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedMinisterId, setSelectedMinisterId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTypes, setActiveTypes] = useState<Set<NodeType>>(
    new Set(['person', 'company', 'institution', 'corporate_client'])
  );
  const [activeFlags, setActiveFlags] = useState<Set<RedFlag>>(new Set());
  const [showFilters, setShowFilters] = useState(false);

  const ministers = useMemo(() => {
    if (!graph) return [];
    return graph.nodes.filter(n => n.type === 'person' && n.role?.toLowerCase().includes('minist'));
  }, [graph]);

  const filteredNodes = useMemo(() => {
    if (!graph) return [];
    let nodes = graph.nodes;

    // Filter by selected minister (show their network)
    if (selectedMinisterId) {
      const relatedIds = new Set<string>([selectedMinisterId]);
      graph.edges.forEach(e => {
        if (e.source === selectedMinisterId || e.target === selectedMinisterId) {
          relatedIds.add(e.source);
          relatedIds.add(e.target);
        }
      });
      nodes = nodes.filter(n => relatedIds.has(n.id));
    }

    // Filter by type
    nodes = nodes.filter(n => activeTypes.has(n.type));

    // Filter by flags
    if (activeFlags.size > 0) {
      nodes = nodes.filter(n => n.flags.some(f => activeFlags.has(f as RedFlag)));
    }

    // Search
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      nodes = nodes.filter(n =>
        n.label.toLowerCase().includes(q) ||
        n.role?.toLowerCase().includes(q) ||
        n.rut?.toLowerCase().includes(q)
      );
    }

    return nodes;
  }, [graph, selectedMinisterId, activeTypes, activeFlags, searchQuery]);

  const filteredEdges = useMemo(() => {
    if (!graph) return [];
    const nodeIds = new Set(filteredNodes.map(n => n.id));
    return graph.edges.filter(e => nodeIds.has(e.source) && nodeIds.has(e.target));
  }, [graph, filteredNodes]);

  const selectedNode = useMemo(() => {
    if (!graph || !selectedNodeId) return null;
    return graph.nodes.find(n => n.id === selectedNodeId) ?? null;
  }, [graph, selectedNodeId]);

  const handleTypeToggle = (type: NodeType) => {
    setActiveTypes(prev => {
      const next = new Set(prev);
      if (next.has(type)) next.delete(type);
      else next.add(type);
      return next;
    });
  };

  const handleFlagToggle = (flag: RedFlag) => {
    setActiveFlags(prev => {
      const next = new Set(prev);
      if (next.has(flag)) next.delete(flag);
      else next.add(flag);
      return next;
    });
  };

  const handleNodeClick = (id: string) => {
    setSelectedNodeId(id === selectedNodeId ? null : id);
  };

  const HIGH_SEVERITY_FLAGS = ['SELF_DEALING', 'REVOLVING_DOOR', 'COLLUSION_LINK', 'DIRECT_AWARD_CLUSTER', 'LOBBY_TO_CONTRACT'] as const;

  // High-severity flags count for badge
  const highFlagCount = useMemo(() => {
    if (!graph) return 0;
    return graph.nodes.filter(n =>
      n.flags.some(f => HIGH_SEVERITY_FLAGS.includes(f as typeof HIGH_SEVERITY_FLAGS[number]))
    ).length;
  }, [graph]);

  const handleShowAlerts = () => {
    setActiveTab('graph');
    setSelectedMinisterId(null);
    setActiveFlags(new Set(HIGH_SEVERITY_FLAGS as unknown as RedFlag[]));
    setShowFilters(true);
  };

  return (
    <div className="min-h-screen bg-[#0F172A] text-slate-100 flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-700 bg-[#1E293B] px-4 py-3">
        <div className="max-w-screen-xl mx-auto flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 min-w-0">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 rounded bg-[#CE1126] flex items-center justify-center">
                <Network className="w-4 h-4 text-white" />
              </div>
            </div>
            <div className="min-w-0">
              <h1 className="text-sm font-bold text-slate-100 leading-none truncate">
                Red Gabinete Kast
              </h1>
              <p className="text-xs text-slate-400 mt-0.5 truncate">
                Transparencia — Chile, marzo 2026
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {highFlagCount > 0 && (
              <button
                onClick={handleShowAlerts}
                title="Ver nodos con señales de conflicto de interés (colusión, puerta giratoria, contratos directos, etc.)"
                className="flex items-center gap-1.5 text-xs text-red-400 bg-red-950/50 border border-red-900 rounded px-2 py-1 hover:bg-red-900/50 hover:border-red-700 transition-colors cursor-pointer"
              >
                <AlertTriangle className="w-3 h-3" />
                <span>{highFlagCount} nodos con alertas — ver en red</span>
              </button>
            )}
            <a
              href="https://github.com/johnmarkshorack/kast-cabinet-network"
              target="_blank"
              rel="noopener noreferrer"
              className="text-slate-400 hover:text-slate-200 transition-colors"
              title="GitHub"
            >
              <Github className="w-5 h-5" />
            </a>
          </div>
        </div>
      </header>

      {/* Tab navigation */}
      <div className="border-b border-slate-700 bg-[#1E293B] px-4">
        <div className="max-w-screen-xl mx-auto flex gap-0">
          {(([
            { id: 'graph' as Tab, label: 'Red de conexiones', icon: Network, badge: undefined as number | undefined },
            { id: 'changes' as Tab, label: 'Cambios recientes', icon: Radio, badge: totalEvents as number | undefined },
            { id: 'sources' as Tab, label: 'Fuentes y verificación', icon: FileText, badge: undefined as number | undefined },
          ])).map(({ id, label, icon: Icon, badge }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`flex items-center gap-2 px-4 py-3 text-sm border-b-2 transition-colors ${
                activeTab === id
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span className="hidden sm:inline">{label}</span>
              {badge !== undefined && badge > 0 && (
                <span className="bg-blue-600 text-white text-xs rounded-full px-1.5 py-0.5 leading-none">
                  {badge}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* MVP disclaimer banner */}
      {showDisclaimer && (
        <div className="bg-amber-950/60 border-b border-amber-700/60 px-4 py-2.5">
          <div className="max-w-screen-xl mx-auto flex items-start gap-3">
            <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
            <p className="text-xs text-amber-200 flex-1">
              <span className="font-semibold">MVP — versión preliminar.</span>{' '}
              Esta herramienta puede contener errores o datos desactualizados. Los datos provienen de fuentes públicas pero no han sido verificados de forma exhaustiva.{' '}
              <span className="font-semibold">Si se usa en reportajes o investigaciones, cada dato debe verificarse independientemente en las fuentes originales</span>{' '}
              (InfoProbidad, Mercado Público, InfoLobby, SII). Los patrones identificados son señales investigativas, no prueba de irregularidades.
            </p>
            <button
              onClick={() => setShowDisclaimer(false)}
              className="flex-shrink-0 text-amber-400 hover:text-amber-200 transition-colors"
              title="Cerrar"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Main content */}
      <main className="flex-1 flex overflow-hidden">
        {activeTab === 'graph' && (
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Minister selector + search bar */}
            <div className="bg-[#1E293B] border-b border-slate-700 px-4 py-2 space-y-2">
              {graph && (
                <MinisterSelector
                  ministers={ministers}
                  selectedId={selectedMinisterId}
                  onSelect={setSelectedMinisterId}
                />
              )}
              <div className="flex gap-2">
                <div className="flex-1">
                  <SearchBar value={searchQuery} onChange={setSearchQuery} />
                </div>
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className={`px-3 py-2 rounded-lg text-sm border transition-colors flex-shrink-0 ${
                    showFilters || activeFlags.size > 0
                      ? 'bg-blue-900 border-blue-600 text-blue-200'
                      : 'bg-slate-800 border-slate-600 text-slate-400 hover:border-slate-400'
                  }`}
                >
                  Filtros {activeFlags.size > 0 && `(${activeFlags.size})`}
                </button>
              </div>
            </div>

            <div className="flex-1 flex overflow-hidden">
              {/* Filter sidebar */}
              {showFilters && (
                <div className="w-52 bg-[#1E293B] border-r border-slate-700 p-4 flex-shrink-0 overflow-y-auto">
                  <FilterPanel
                    activeTypes={activeTypes}
                    activeFlags={activeFlags}
                    onTypeToggle={handleTypeToggle}
                    onFlagToggle={handleFlagToggle}
                  />
                </div>
              )}

              {/* Graph area */}
              <div className="flex-1 relative overflow-hidden">
                {loading && (
                  <div className="absolute inset-0 flex items-center justify-center bg-[#0F172A] z-10">
                    <div className="text-center">
                      <div className="w-10 h-10 border-2 border-slate-600 border-t-blue-500 rounded-full animate-spin mx-auto mb-3" />
                      <p className="text-sm text-slate-400">Cargando red...</p>
                    </div>
                  </div>
                )}
                {error && (
                  <div className="absolute inset-0 flex items-center justify-center bg-[#0F172A] z-10">
                    <div className="text-center text-slate-400 max-w-sm p-4">
                      <AlertTriangle className="w-8 h-8 text-yellow-500 mx-auto mb-2" />
                      <p className="text-sm font-medium mb-1">Error cargando datos</p>
                      <p className="text-xs">{error}</p>
                    </div>
                  </div>
                )}
                {graph && !loading && (
                  <NetworkGraph
                    key={`${selectedMinisterId ?? 'all'}|${[...activeFlags].sort().join(',')}|${[...activeTypes].sort().join(',')}`}
                    nodes={filteredNodes}
                    edges={filteredEdges}
                    selectedNodeId={selectedNodeId}
                    focusNodeId={selectedMinisterId}
                    onNodeClick={handleNodeClick}
                  />
                )}
              </div>

              {/* Entity profile panel */}
              {selectedNode && graph && (
                <div className="w-80 bg-[#1E293B] border-l border-slate-700 flex-shrink-0 overflow-hidden flex flex-col">
                  <EntityProfile
                    node={selectedNode}
                    edges={graph.edges}
                    allNodes={graph.nodes}
                    onClose={() => setSelectedNodeId(null)}
                    onSelectNode={handleNodeClick}
                  />
                </div>
              )}
            </div>

            {/* Stats bar */}
            {graph && (
              <div className="bg-[#1E293B] border-t border-slate-700 px-4 py-1.5 flex items-center gap-4 text-xs text-slate-500">
                <span>{filteredNodes.length} nodos</span>
                <span>{filteredEdges.length} conexiones</span>
                <span>
                  {filteredNodes.filter(n => n.flags.length > 0).length} con alertas
                </span>
                <span className="ml-auto">
                  Actualizado: {graph.meta.generatedAt.split('T')[0]}
                </span>
              </div>
            )}
          </div>
        )}

        {activeTab === 'changes' && (
          <div className="flex-1 overflow-y-auto px-4 py-6 max-w-3xl mx-auto w-full">
            <h2 className="text-lg font-semibold text-slate-100 mb-6">Cambios recientes</h2>
            <ChangesFeed onNodeClick={(id) => {
              setActiveTab('graph');
              setSelectedNodeId(id);
            }} />
          </div>
        )}

        {activeTab === 'sources' && (
          <div className="flex-1 overflow-y-auto px-4 py-6">
            <SourcesPage />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-700 bg-[#1E293B] px-4 py-3">
        <div className="max-w-screen-xl mx-auto flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500">
          <div className="flex items-center gap-3">
            <span>Licencia: AGPL-3.0</span>
            <span>Datos: CC0 (fuentes gubernamentales)</span>
          </div>
          <p className="text-slate-600">
            Los patrones son señales investigativas, no prueba de irregularidades. Cada dato incluye fuente verificable.
          </p>
        </div>
      </footer>
    </div>
  );
}
