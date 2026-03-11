import type { RedFlag } from '../types/graph';

interface FlagConfig {
  label: string;
  bg: string;
  text: string;
  border: string;
}

const FLAG_CONFIG: Record<string, FlagConfig> = {
  SELF_DEALING: { label: 'Autocontratación', bg: 'bg-red-900', text: 'text-red-200', border: 'border-red-600' },
  REVOLVING_DOOR: { label: 'Puerta giratoria', bg: 'bg-orange-900', text: 'text-orange-200', border: 'border-orange-600' },
  DIRECT_AWARD_CLUSTER: { label: 'Trato directo', bg: 'bg-red-900', text: 'text-red-200', border: 'border-red-600' },
  LOBBY_TO_CONTRACT: { label: 'Lobby→Contrato', bg: 'bg-orange-900', text: 'text-orange-200', border: 'border-orange-600' },
  CONCENTRATION: { label: 'Concentración', bg: 'bg-yellow-900', text: 'text-yellow-200', border: 'border-yellow-600' },
  CORPORATE_RESTRUCTURING: { label: 'Reestructuración', bg: 'bg-yellow-900', text: 'text-yellow-200', border: 'border-yellow-600' },
  GOV_CONTRACTOR: { label: 'Contratista', bg: 'bg-blue-900', text: 'text-blue-200', border: 'border-blue-600' },
  COLLUSION_LINK: { label: 'Colusión', bg: 'bg-red-900', text: 'text-red-200', border: 'border-red-600' },
  ACTIVE_CONTRACT: { label: 'Contrato activo', bg: 'bg-blue-900', text: 'text-blue-200', border: 'border-blue-600' },
};

interface Props {
  flag: RedFlag | string;
  size?: 'sm' | 'md';
}

export function RedFlagBadge({ flag, size = 'sm' }: Props) {
  const config = FLAG_CONFIG[flag] ?? {
    label: flag,
    bg: 'bg-slate-700',
    text: 'text-slate-200',
    border: 'border-slate-500',
  };

  const sizeClass = size === 'sm' ? 'text-xs px-1.5 py-0.5' : 'text-sm px-2 py-1';

  return (
    <span
      className={`inline-flex items-center rounded border ${config.bg} ${config.text} ${config.border} ${sizeClass} font-mono font-medium`}
      title={flag}
    >
      {config.label}
    </span>
  );
}
