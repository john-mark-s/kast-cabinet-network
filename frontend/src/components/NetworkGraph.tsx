import { useRef, useCallback, useEffect } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import type Cytoscape from 'cytoscape';
import type { GraphNode, GraphEdge, NodeType } from '../types/graph';

interface Props {
  nodes: GraphNode[];
  edges: GraphEdge[];
  selectedNodeId: string | null;
  focusNodeId: string | null;
  onNodeClick: (id: string) => void;
}

const NODE_COLORS: Record<NodeType, string> = {
  person: '#3B82F6',
  company: '#94A3B8',
  institution: '#22C55E',
  corporate_client: '#A855F7',
};

const EDGE_COLORS: Record<string, string> = {
  owned: '#94A3B8',
  heads: '#22C55E',
  family: '#EC4899',
  works_at: '#F59E0B',
  contract: '#EF4444',
  advisory: '#F97316',
  met_with: '#06B6D4',
  received_gift: '#8B5CF6',
  board: '#10B981',
  govt_role: '#64748B',
  rumored: '#475569',
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function buildStylesheet(selectedId: string | null): any[] {
  return [
    {
      selector: 'node',
      style: {
        'background-color': 'data(color)',
        'label': 'data(shortLabel)',
        'color': '#E2E8F0',
        'font-size': '11px',
        'font-weight': '500',
        'text-valign': 'bottom',
        'text-halign': 'center',
        'text-margin-y': 6,
        'text-wrap': 'wrap',
        'text-max-width': '90px',
        'text-background-color': '#0F172A',
        'text-background-opacity': 0.8,
        'text-background-padding': '2px',
        'text-background-shape': 'roundrectangle',
        'width': 36,
        'height': 36,
      },
    },
    {
      selector: 'node[?flagged]',
      style: {
        'border-width': 3,
        'border-color': '#CE1126',
        'border-style': 'dashed',
      },
    },
    {
      selector: 'node[status = "seed"]',
      style: {
        'opacity': 0.6,
      },
    },
    ...(selectedId ? [{
      selector: `node[id = "${selectedId}"]`,
      style: {
        'border-width': 3,
        'border-color': '#60A5FA',
        'border-style': 'solid',
        'width': 36,
        'height': 36,
      },
    }] : []),
    {
      selector: 'edge',
      style: {
        'width': 1.5,
        'line-color': 'data(edgeColor)',
        'target-arrow-color': 'data(edgeColor)',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        'opacity': 0.7,
      },
    },
    {
      selector: 'edge[?flagged]',
      style: {
        'line-style': 'dashed',
        'line-color': '#CE1126',
        'target-arrow-color': '#CE1126',
        'width': 2,
        'opacity': 1,
      },
    },
    {
      selector: 'edge[type = "rumored"]',
      style: {
        'line-style': 'dotted',
        'opacity': 0.4,
      },
    },
  ];
}

function buildElements(nodes: GraphNode[], edges: GraphEdge[]) {
  const cyNodes = nodes.map(node => ({
    data: {
      id: node.id,
      shortLabel: node.type === 'person'
        ? node.label.split(' ').slice(0, 2).join('\n')   // "Jorge\nQuiroz"
        : node.label.length > 20
          ? node.label.slice(0, 18) + '…'
          : node.label,
      color: NODE_COLORS[node.type] ?? '#64748B',
      flagged: node.flags.length > 0,
      status: node.status,
      type: node.type,
    },
  }));

  const nodeIds = new Set(nodes.map(n => n.id));
  const cyEdges = edges
    .filter(e => nodeIds.has(e.source) && nodeIds.has(e.target))
    .map(edge => ({
      data: {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        edgeColor: EDGE_COLORS[edge.type] ?? '#64748B',
        flagged: edge.flags.length > 0,
        type: edge.type,
      },
    }));

  return [...cyNodes, ...cyEdges];
}

const LAYOUT = {
  name: 'cose',
  animate: false,
  nodeRepulsion: () => 120000,
  nodeOverlap: 60,
  idealEdgeLength: () => 160,
  gravity: 0.05,
  numIter: 2000,
  initialTemp: 1000,
  coolingFactor: 0.99,
  minTemp: 1.0,
  fit: true,
  padding: 60,
};

const EDGE_LEGEND = [
  { type: 'owned',         label: 'Propiedad',       color: '#94A3B8' },
  { type: 'heads',         label: 'Dirige',           color: '#22C55E' },
  { type: 'family',        label: 'Familia',          color: '#EC4899' },
  { type: 'contract',      label: 'Contrato',         color: '#EF4444' },
  { type: 'advisory',      label: 'Asesoría',         color: '#F97316' },
  { type: 'board',         label: 'Directorio',       color: '#10B981' },
  { type: 'met_with',      label: 'Audiencia lobby',  color: '#06B6D4' },
  { type: 'received_gift', label: 'Donativo',         color: '#8B5CF6' },
  { type: 'govt_role',     label: 'Cargo público',    color: '#64748B' },
  { type: 'works_at',      label: 'Trabaja en',       color: '#F59E0B' },
  { type: 'rumored',       label: 'No confirmado',    color: '#475569' },
];

export function NetworkGraph({ nodes, edges, selectedNodeId, focusNodeId, onNodeClick }: Props) {
  const cyRef = useRef<Cytoscape.Core | null>(null);

  const elements = buildElements(nodes, edges);
  const stylesheet = buildStylesheet(selectedNodeId);

  const handleCy = useCallback((cy: Cytoscape.Core) => {
    cyRef.current = cy;
    cy.removeAllListeners();
    cy.on('tap', 'node', (evt: Cytoscape.EventObject) => {
      const nodeId = evt.target.id() as string;
      onNodeClick(nodeId);
    });
  }, [onNodeClick]);

  // After layout settles, pan+zoom to the focused node
  useEffect(() => {
    if (!focusNodeId || !cyRef.current) return;
    const timer = setTimeout(() => {
      const cy = cyRef.current;
      if (!cy) return;
      const target = cy.getElementById(focusNodeId);
      if (target && target.length > 0) {
        cy.animate({
          center: { eles: target },
          zoom: Math.min(cy.zoom() * 1.5, 2.5),
        }, { duration: 400 });
      }
    }, 300); // wait for cose layout to finish
    return () => clearTimeout(timer);
  }, [focusNodeId, nodes]);

  if (nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-slate-400">
        <p className="text-sm">No hay nodos para mostrar con los filtros actuales.</p>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full">
      <CytoscapeComponent
        elements={elements}
        stylesheet={stylesheet}
        layout={LAYOUT}
        style={{ width: '100%', height: '100%', background: '#0F172A' }}
        cy={handleCy}
      />

      {/* Edge legend */}
      <div className="absolute bottom-3 left-3 bg-[#1E293B]/90 border border-slate-700 rounded-lg p-3 text-xs backdrop-blur-sm">
        <p className="text-slate-400 font-medium mb-2 uppercase tracking-wide text-[10px]">Tipo de conexión</p>
        <div className="grid grid-cols-2 gap-x-4 gap-y-1">
          {EDGE_LEGEND.map(({ label, color }) => (
            <div key={label} className="flex items-center gap-1.5">
              <div className="w-4 h-0.5 flex-shrink-0" style={{ backgroundColor: color }} />
              <span className="text-slate-300">{label}</span>
            </div>
          ))}
        </div>
        <div className="mt-2 pt-2 border-t border-slate-700 flex items-center gap-1.5">
          <div className="w-4 h-0.5 flex-shrink-0 border-t-2 border-dashed border-[#CE1126]" />
          <span className="text-slate-300">Alerta activa</span>
        </div>
      </div>
    </div>
  );
}
