import { useState, useRef, useEffect } from 'react';
import { Smile, Search, X, Clock } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';

const CATEGORIES = [
  { id: 'recent', label: 'Recent', icon: '🕐' },
  { id: 'smileys', label: 'Smileys', icon: '😀' },
  { id: 'people', label: 'People', icon: '👋' },
  { id: 'nature', label: 'Nature', icon: '🌿' },
  { id: 'food', label: 'Food', icon: '🍕' },
  { id: 'activities', label: 'Activities', icon: '⚽' },
  { id: 'travel', label: 'Travel', icon: '✈️' },
  { id: 'objects', label: 'Objects', icon: '💡' },
  { id: 'symbols', label: 'Symbols', icon: '❤️' },
  { id: 'flags', label: 'Flags', icon: '🏁' },
];

const EMOJI_DATA = {
  smileys: ['😀','😃','😄','😁','😆','😅','🤣','😂','🙂','😊','😇','🥰','😍','🤩','😘','😗','😋','😛','😜','🤪','😝','🤑','🤗','🤭','🤫','🤔','🤐','🤨','😐','😑','😶','😏','😒','🙄','😬','😮‍💨','🤥','😌','😔','😪','🤤','😴','😷','🤒','🤕','🤢','🤮','🥵','🥶','🥴','😵','🤯','🤠','🥳','🥸','😎','🤓','🧐','😕','😟','🙁','😮','😯','😲','😳','🥺','😦','😧','😨','😰','😥','😢','😭','😱','😖','😣','😞','😓','😩','😫','🥱','😤','😡','😠','🤬','😈','👿','💀','☠️','💩','🤡','👹','👺','👻','👽','👾','🤖'],
  people: ['👋','🤚','🖐️','✋','🖖','👌','🤌','🤏','✌️','🤞','🤟','🤘','🤙','👈','👉','👆','🖕','👇','☝️','👍','👎','✊','👊','🤛','🤜','👏','🙌','👐','🤲','🤝','🙏','💪','🦾','🦿','🦵','🦶','👂','🦻','👃','🧠','🫀','🫁','🦷','🦴','👀','👁️','👅','👄','💋','🩸','👶','🧒','👦','👧','🧑','👱','👨','🧔','👩','🧓','👴','👵','🙍','🙎','🙅','🙆','💁','🙋','🧏','🙇','🤦','🤷','💂','🏃','💃','🕺','🧗','🧘','🛀','🛌'],
  nature: ['🌿','🌱','🌲','🌳','🌴','🌵','🌾','🌷','🌹','🥀','🌺','🌸','🌼','🌻','🌞','🌝','🌛','🌜','🌚','🌕','🌖','🌗','🌘','🌑','🌒','🌓','🌔','🌙','🌎','🌍','🌏','💫','⭐','🌟','✨','⚡','☄️','💥','🔥','🌪️','🌈','☀️','🌤️','⛅','🌥️','☁️','🌦️','🌧️','⛈️','🌩️','🌨️','❄️','☃️','⛄','🌬️','💨','💧','💦','🌊','🐶','🐱','🐭','🐹','🐰','🦊','🐻','🐼','🐨','🐯','🦁','🐮','🐷','🐸','🐵','🐔','🐧','🐦','🐤','🦆','🦅','🦉','🦇','🐺','🐗','🐴','🦄','🐝','🪱','🐛','🦋','🐌','🐞','🐜','🪰','🪲','🪳','🦟','🦗','🕷️'],
  food: ['🍕','🍔','🍟','🌭','🥪','🌮','🌯','🫔','🥙','🧆','🥚','🍳','🥘','🍲','🫕','🥣','🥗','🍿','🧈','🧂','🥫','🍱','🍘','🍙','🍚','🍛','🍜','🍝','🍠','🍢','🍣','🍤','🍥','🥮','🍡','🥟','🥠','🥡','🦀','🦞','🦐','🦑','🦪','🍦','🍧','🍨','🍩','🍪','🎂','🍰','🧁','🥧','🍫','🍬','🍭','🍮','🍯','🍼','🥛','☕','🫖','🍵','🍶','🍾','🍷','🍸','🍹','🍺','🍻','🥂','🥃','🫗','🥤','🧋','🧃','🧉','🧊','🥝','🍇','🍈','🍉','🍊','🍋','🍌','🍍','🥭','🍎','🍏','🍐','🍑','🍒','🍓','🫐','🥝'],
  activities: ['⚽','🏀','🏈','⚾','🥎','🎾','🏐','🏉','🥏','🎱','🪀','🏓','🏸','🏒','🏑','🥍','🏏','🪃','🥅','⛳','🪁','🏹','🎣','🤿','🥊','🥋','🎽','🛹','🛼','🛷','⛸️','🥌','🎿','⛷️','🏂','🪂','🏋️','🤼','🤸','⛹️','🤺','🤾','🏌️','🏇','🧘','🏄','🏊','🤽','🚣','🧗','🚵','🚴','🏆','🥇','🥈','🥉','🏅','🎖️','🏵️','🎗️','🎪','🤹','🎭','🩰','🎨','🎬','🎤','🎧','🎼','🎹','🥁','🪘','🎷','🎺','🪗','🎸','🪕','🎻','🎲','♟️','🎯','🎳','🎮','🕹️','🧩'],
  travel: ['✈️','🛫','🛬','💺','🚁','🛸','🚀','🛰️','🛩️','🚂','🚃','🚄','🚅','🚆','🚇','🚈','🚉','🚊','🚝','🚞','🚋','🚌','🚍','🚎','🚐','🚑','🚒','🚓','🚔','🚕','🚖','🚗','🚘','🚙','🛻','🚚','🚛','🚜','🏎️','🏍️','🛵','🦽','🦼','🛺','🚲','🛴','🛹','🛼','🚏','🛣️','🛤️','🛞','⛽','🛟','🚨','🚥','🚦','🛑','🚧','⚓','🗺️','🗿','🗽','🗼','🏰','🏯','🏟️','🎡','🎢','🎠','⛲','⛱️','🏖️','🏝️','🏜️','🌋','⛰️','🏔️','🗻','🏕️','🛖','🏠','🏡','🏘️','🏚️','🏗️','🏭','🏢','🏬','🏣','🏤','🏥','🏦','🏨','🏪','🏫','🏩','💒','🏛️','⛪','🕌','🕍','🛕'],
  objects: ['💡','🔦','🕯️','🪔','📱','💻','🖥️','🖨️','⌨️','🖱️','🖲️','💾','💿','📀','📼','📷','📸','📹','🎥','📽️','🎞️','📞','☎️','📟','📠','📺','📻','🎙️','🎚️','🎛️','🧭','⏱️','⏲️','⏰','🕰️','⌛','⏳','📡','🔋','🔌','💵','💴','💶','💷','🪙','💰','💳','💎','⚖️','🪜','🧰','🪛','🔧','🔩','⚙️','🪤','🧱','⛓️','🧲','🔫','💣','🧨','🪓','🔪','🗡️','⚔️','🛡️','🚬','⚰️','🪦','⚱️','🏺','🔮','📿','🧿','💈','⚗️','🔭','🔬','🕳️','🩹','🩺','💊','💉','🩸','🧬','🦠','🧫','🧪','🌡️','🧹','🧺','🧻','🪣','🧼','🫧','🪥','🧽','🧯','🛒','🚬','🪝'],
  symbols: ['❤️','🧡','💛','💚','💙','💜','🖤','🤍','🤎','💔','❣️','💕','💞','💓','💗','💖','💘','💝','💟','☮️','✝️','☪️','🕉️','☸️','✡️','🔯','🕎','☯️','☦️','🛐','⛎','♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓','🆔','⚛️','🉑','☢️','☣️','📴','📳','🈶','🈚','🈸','🈺','🈷️','✴️','🆚','💮','🉐','㊙️','㊗️','🈴','🈵','🈹','🈲','🅰️','🅱️','🆎','🆑','🅾️','🆘','❌','⭕','🛑','⛔','📛','🚫','💯','💢','♨️','🚷','🚯','🚳','🚱','🔞','📵','🚭','❗','❕','❓','❔','‼️','⁉️','🔅','🔆','〽️','⚠️','🚸','🔱','⚜️','🔰','♻️','✅','🈯','💹','❇️','✳️','❎','🌐','💠','Ⓜ️','🌀','💤','🏧','🚾','♿','🅿️','🛗','🈳','🈂️','🛂','🛃','🛄','🛅','🚹','🚺','🚼','⚧','🚻','🚮','🎦','📶','🈁','🔣','ℹ️','🔤','🔡','🔠','🆖','🆗','🆙','🆒','🆕','🆓','0️⃣','1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟','🔢','#️⃣','*️⃣','⏏️','▶️','⏸️','⏯️','⏹️','⏺️','⏭️','⏮️','⏩','⏪','⏫','⏬','◀️','🔼','🔽','➡️','⬅️','⬆️','⬇️','↗️','↘️','↙️','↖️','↕️','↔️','↩️','↪️','⤴️','⤵️','🔀','🔁','🔂','🔄','🔃','🎵','🎶','➕','➖','➗','✖️','🟰','♾️','💲','💱','™️','©️','®️','〰️','➰','➿','🔚','🔙','🔛','🔝','🔜','✔️','☑️','🔘','🔴','🟠','🟡','🟢','🔵','🟣','⚫','⚪','🟤','🔺','🔻','🔸','🔹','🔶','🔷','🔳','🔲','▪️','▫️','◾','◽','◼️','◻️','🟥','🟧','🟨','🟩','🟦','🟪','⬛','⬜','🟫','🔈','🔇','🔉','🔊','🔔','🔕','📣','📢'],
  flags: ['🏁','🚩','🎌','🏴','🏳️','🏳️‍🌈','🏳️‍⚧️','🏴‍☠️','🇺🇸','🇬🇧','🇫🇷','🇩🇪','🇮🇹','🇪🇸','🇯🇵','🇰🇷','🇨🇳','🇮🇳','🇧🇷','🇲🇽','🇨🇦','🇦🇺','🇷🇺','🇿🇦','🇳🇬','🇰🇪','🇪🇬','🇸🇦','🇦🇪','🇮🇱','🇹🇷','🇬🇷','🇵🇱','🇳🇱','🇧🇪','🇨🇭','🇦🇹','🇸🇪','🇳🇴','🇩🇰','🇫🇮','🇮🇪','🇵🇹','🇦🇷','🇨🇱','🇨🇴','🇵🇪','🇻🇪','🇹🇭','🇻🇳','🇮🇩','🇲🇾','🇵🇭','🇸🇬','🇳🇿','🇵🇰','🇧🇩','🇱🇰','🇳🇵','🇪🇹','🇬🇭','🇹🇿','🇺🇬','🇲🇦','🇹🇳','🇩🇿'],
};

const RECENT_KEY = 'lumi_recent_emojis';

export const EmojiPicker = ({ isOpen, onClose, onSelect, position = 'above' }) => {
  const [search, setSearch] = useState('');
  const [activeCategory, setActiveCategory] = useState('smileys');
  const [recentEmojis, setRecentEmojis] = useState([]);
  const searchRef = useRef(null);
  const pickerRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      setSearch('');
      setActiveCategory('smileys');
      const stored = localStorage.getItem(RECENT_KEY);
      if (stored) setRecentEmojis(JSON.parse(stored));
      setTimeout(() => searchRef.current?.focus(), 100);
    }
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) return;
    const handleClickOutside = (e) => {
      if (pickerRef.current && !pickerRef.current.contains(e.target)) onClose();
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen, onClose]);

  const handleSelect = (emoji) => {
    onSelect(emoji);
    const updated = [emoji, ...recentEmojis.filter(e => e !== emoji)].slice(0, 24);
    setRecentEmojis(updated);
    localStorage.setItem(RECENT_KEY, JSON.stringify(updated));
  };

  const allEmojis = Object.values(EMOJI_DATA).flat();
  const filtered = search
    ? allEmojis.filter(() => true).slice(0, 60)
    : activeCategory === 'recent'
      ? recentEmojis
      : EMOJI_DATA[activeCategory] || [];

  if (!isOpen) return null;

  return (
    <div ref={pickerRef}
      className={`absolute ${position === 'above' ? 'bottom-full mb-2' : 'top-full mt-2'} left-0 w-[340px] bg-white rounded-xl shadow-2xl border border-slate-200 z-50 overflow-hidden`}
      data-testid="emoji-picker">

      {/* Search */}
      <div className="px-3 pt-3 pb-2">
        <div className="flex items-center gap-2 bg-slate-50 rounded-lg px-3 py-2 border border-slate-200">
          <Search className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
          <input ref={searchRef} value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Search emojis..."
            className="flex-1 text-xs bg-transparent outline-none text-slate-700 placeholder:text-slate-400"
            data-testid="emoji-search-input" />
          {search && <button onClick={() => setSearch('')}><X className="w-3 h-3 text-slate-400" /></button>}
        </div>
      </div>

      {/* Category tabs */}
      {!search && (
        <div className="flex items-center gap-0.5 px-2 pb-1 overflow-x-auto scrollbar-none">
          {CATEGORIES.map(cat => (
            <button key={cat.id} onClick={() => setActiveCategory(cat.id)}
              className={`flex-shrink-0 p-1.5 rounded-lg text-sm transition-all ${activeCategory === cat.id ? 'bg-slate-100 scale-110' : 'hover:bg-slate-50 opacity-60 hover:opacity-100'}`}
              title={cat.label} data-testid={`emoji-cat-${cat.id}`}>
              {cat.icon}
            </button>
          ))}
        </div>
      )}

      {/* Category label */}
      <div className="px-3 py-1">
        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
          {search ? 'Search Results' : CATEGORIES.find(c => c.id === activeCategory)?.label}
        </span>
      </div>

      {/* Emoji grid */}
      <ScrollArea className="h-[220px]">
        <div className="px-2 pb-2">
          {filtered.length === 0 ? (
            <div className="text-center py-6">
              <p className="text-xs text-slate-400">{activeCategory === 'recent' ? 'No recent emojis yet' : 'No emojis found'}</p>
            </div>
          ) : (
            <div className="grid grid-cols-8 gap-0.5">
              {filtered.map((emoji, i) => (
                <button key={`${emoji}-${i}`} onClick={() => handleSelect(emoji)}
                  className="w-9 h-9 flex items-center justify-center text-xl rounded-lg hover:bg-slate-100 transition-colors active:scale-90"
                  data-testid={`emoji-${i}`}>
                  {emoji}
                </button>
              ))}
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="px-3 py-2 border-t border-slate-100 bg-slate-50/50 flex items-center justify-between">
        <span className="text-[10px] text-slate-400 font-medium">
          {activeCategory === 'recent' ? `${recentEmojis.length} recent` : `${filtered.length} emojis`}
        </span>
        <div className="flex items-center gap-1 text-[10px] text-slate-400">
          <kbd className="px-1 py-0.5 bg-white rounded border border-slate-200 font-mono text-[9px]">Ctrl</kbd>
          <span>+</span>
          <kbd className="px-1 py-0.5 bg-white rounded border border-slate-200 font-mono text-[9px]">E</kbd>
          <span className="ml-1">toggle</span>
        </div>
      </div>
    </div>
  );
};
