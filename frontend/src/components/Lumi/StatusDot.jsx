import { STATUS_COLORS } from './constants';

export const StatusDot = ({ status, size = 'sm', ringColor = 'ring-white' }) => {
  const s = size === 'sm' ? 'w-2.5 h-2.5' : 'w-3 h-3';
  return <span className={`inline-block ${s} rounded-full ${STATUS_COLORS[status] || STATUS_COLORS.offline} ring-2 ${ringColor}`} />;
};
