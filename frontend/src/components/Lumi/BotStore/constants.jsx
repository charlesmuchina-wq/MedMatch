import { Star } from 'lucide-react';

export const ICON_MAP_KEYS = {
  'user-search': 'Users', 'file-text': 'FileText', 'mic': 'Mic', 'zap': 'Zap',
  'dollar-sign': 'DollarSign', 'edit': 'Edit', 'calendar': 'Calendar',
  'search': 'Search', 'users': 'Users', 'brain': 'Brain', 'book-open': 'BookOpen',
  'globe': 'Globe', 'message-circle': 'MessageCircle', 'shield': 'Shield',
  'monitor': 'MonitorSmartphone', 'scale': 'Scale', 'alert-triangle': 'AlertTriangle',
  'check-circle': 'CheckCircle',
};

export const CAT_STYLES = {
  'Job Toolkit':    { bg: '#00B894', accent: '#00B894' },
  'AI Meeting':     { bg: '#6C5CE7', accent: '#6C5CE7' },
  'AI Messenger':   { bg: '#00CEC9', accent: '#00CEC9' },
  'Security & QA':  { bg: '#E17055', accent: '#E17055' },
};

export const RatingStars = ({ rating, size = 'sm' }) => {
  const s = size === 'sm' ? 'w-3 h-3' : 'w-4 h-4';
  return (
    <div className="flex items-center gap-0.5">
      {[1,2,3,4,5].map(i => (
        <Star key={i} className={`${s} ${i <= Math.round(rating) ? 'text-amber-400 fill-amber-400' : 'text-slate-600'}`} />
      ))}
      <span className={`ml-1 font-medium ${size === 'sm' ? 'text-[10px]' : 'text-xs'} text-slate-400`}>{rating}</span>
    </div>
  );
};

export const getCat = (cat) => CAT_STYLES[cat] || { bg: '#64748b', accent: '#64748b' };
