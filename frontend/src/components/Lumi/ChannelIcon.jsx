import { Hash, Megaphone, Shield } from 'lucide-react';

export const ChannelIcon = ({ type }) => {
  if (type === 'announcement') return <Megaphone className="w-4 h-4" />;
  if (type === 'domain') return <Shield className="w-4 h-4" />;
  return <Hash className="w-4 h-4" />;
};
