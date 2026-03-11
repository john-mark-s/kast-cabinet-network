import type { GraphNode } from '../types/graph';

interface Props {
  ministers: GraphNode[];
  selectedId: string | null;
  onSelect: (id: string | null) => void;
}

export function MinisterSelector({ ministers, selectedId, onSelect }: Props) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-track-slate-800 scrollbar-thumb-slate-600">
      <button
        onClick={() => onSelect(null)}
        className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
          selectedId === null
            ? 'bg-blue-600 border-blue-500 text-white'
            : 'bg-slate-800 border-slate-600 text-slate-300 hover:border-slate-400'
        }`}
      >
        Todos
      </button>
      {ministers.map(minister => {
        const isMapped = minister.status === 'mapped';
        const isSelected = selectedId === minister.id;
        const hasFlags = minister.flags.length > 0;

        return (
          <button
            key={minister.id}
            onClick={() => onSelect(isSelected ? null : minister.id)}
            title={`${minister.label} — ${minister.role ?? ''}`}
            className={`flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
              isSelected
                ? 'bg-blue-600 border-blue-500 text-white'
                : 'bg-slate-800 border-slate-600 text-slate-300 hover:border-slate-400'
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full flex-shrink-0 ${
                hasFlags ? 'bg-red-500' : isMapped ? 'bg-green-500' : 'bg-slate-500'
              }`}
            />
            <span className="max-w-[120px] truncate">
              {minister.label.split(' ').slice(0, 2).join(' ')}
            </span>
          </button>
        );
      })}
    </div>
  );
}
