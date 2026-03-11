import { useChangelog } from '../hooks/useChangelog';
import { ChangeEvent } from './ChangeEvent';

interface Props {
  onNodeClick?: (id: string) => void;
}

export function ChangesFeed({ onNodeClick }: Props) {
  const { changelog, loading, error } = useChangelog();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-48 text-slate-400">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-slate-600 border-t-blue-500 rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm">Cargando historial...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-center text-slate-400">
        <p className="text-sm">Error cargando el historial: {error}</p>
      </div>
    );
  }

  if (!changelog || changelog.weeks.length === 0) {
    return (
      <div className="p-4 text-center text-slate-400">
        <p className="text-sm">No hay eventos registrados aún.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {changelog.weeks.map(week => (
        <div key={week.week}>
          <div className="flex items-center gap-3 mb-3">
            <span className="text-xs font-mono text-slate-500 bg-slate-800 px-2 py-0.5 rounded">
              {week.week}
            </span>
            <div className="flex-1 h-px bg-slate-700" />
            <span className="text-xs text-slate-600">{week.events.length} evento{week.events.length !== 1 ? 's' : ''}</span>
          </div>
          <div className="space-y-2">
            {week.events.map((event, i) => (
              <ChangeEvent key={i} event={event} onNodeClick={onNodeClick} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
