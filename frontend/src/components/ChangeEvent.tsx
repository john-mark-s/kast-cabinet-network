import { format, parseISO } from 'date-fns';
import { es } from 'date-fns/locale';
import type { ChangeEvent as ChangeEventType } from '../types/graph';

interface Props {
  event: ChangeEventType;
  onNodeClick?: (id: string) => void;
}

const SEVERITY_STYLES: Record<string, string> = {
  high: 'border-l-red-500 bg-red-950/20',
  medium: 'border-l-yellow-500 bg-yellow-950/20',
  low: 'border-l-blue-500 bg-blue-950/20',
  info: 'border-l-slate-500 bg-slate-800/50',
};

const SEVERITY_BADGE: Record<string, string> = {
  high: 'bg-red-900 text-red-200',
  medium: 'bg-yellow-900 text-yellow-200',
  low: 'bg-blue-900 text-blue-200',
  info: 'bg-slate-700 text-slate-300',
};

export function ChangeEvent({ event, onNodeClick }: Props) {
  const style = SEVERITY_STYLES[event.severity] ?? SEVERITY_STYLES.info;
  const badge = SEVERITY_BADGE[event.severity] ?? SEVERITY_BADGE.info;

  let dateStr = event.date;
  try {
    dateStr = format(parseISO(event.date), "d MMM yyyy", { locale: es });
  } catch {
    // keep original
  }

  return (
    <div className={`border-l-2 pl-4 py-3 pr-3 rounded-r ${style}`}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2 min-w-0">
          <span className="text-lg leading-none flex-shrink-0">{event.icon}</span>
          <div className="min-w-0">
            <p className="text-sm font-medium text-slate-100">{event.title}</p>
            <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">{event.desc}</p>
            {event.source && (
              <p className="text-xs text-slate-600 mt-1">Fuente: {event.source}</p>
            )}
            {event.nodeRefs.length > 0 && onNodeClick && (
              <div className="flex flex-wrap gap-1 mt-1.5">
                {event.nodeRefs.slice(0, 3).map(ref => (
                  <button
                    key={ref}
                    onClick={() => onNodeClick(ref)}
                    className="text-xs text-blue-400 hover:text-blue-300 bg-blue-950/50 px-1.5 py-0.5 rounded transition-colors"
                  >
                    {ref}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
        <div className="flex flex-col items-end gap-1 flex-shrink-0">
          <span className={`text-xs px-1.5 py-0.5 rounded ${badge}`}>
            {event.severity}
          </span>
          <span className="text-xs text-slate-500">{dateStr}</span>
        </div>
      </div>
    </div>
  );
}
