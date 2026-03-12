/**
 * MobileBottomNav — Bottom navigation for mobile ENZI experience
 * Shows on screens < 768px
 */
import { MessageCircle, Hash, Search, Sparkles, User } from 'lucide-react';

const MobileBottomNav = ({ activeTab, onTabChange, unreadCount = 0, user }) => {
  const tabs = [
    { id: 'channels', icon: Hash, label: 'Channels' },
    { id: 'dms', icon: MessageCircle, label: 'DMs', badge: unreadCount },
    { id: 'search', icon: Search, label: 'Search' },
    { id: 'ai', icon: Sparkles, label: 'AI' },
    { id: 'profile', icon: User, label: 'Me' },
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-xl border-t border-slate-200 px-2 pb-safe" data-testid="mobile-bottom-nav">
      <div className="flex items-center justify-around h-14">
        {tabs.map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button key={tab.id} onClick={() => onTabChange(tab.id)}
              className={`flex flex-col items-center gap-0.5 px-3 py-1.5 rounded-xl transition-colors relative ${isActive ? 'text-[#008080]' : 'text-slate-400'}`}
              data-testid={`mobile-nav-${tab.id}`}>
              <Icon className={`w-5 h-5 ${isActive ? 'stroke-[2.5]' : ''}`} />
              <span className={`text-[9px] font-medium ${isActive ? 'text-[#008080]' : 'text-slate-500'}`}>{tab.label}</span>
              {tab.badge > 0 && (
                <span className="absolute -top-0.5 right-0.5 w-4 h-4 bg-red-500 rounded-full text-[8px] text-white font-bold flex items-center justify-center">
                  {tab.badge > 9 ? '9+' : tab.badge}
                </span>
              )}
              {isActive && <div className="absolute -bottom-1.5 w-6 h-0.5 rounded-full bg-[#008080]" />}
            </button>
          );
        })}
      </div>
    </nav>
  );
};

export default MobileBottomNav;
