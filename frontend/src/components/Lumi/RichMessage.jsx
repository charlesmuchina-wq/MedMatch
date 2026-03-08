import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check } from 'lucide-react';
import { useState } from 'react';

const CopyButton = ({ text }) => {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };
  return (
    <button onClick={handleCopy} className="absolute top-2 right-2 p-1 rounded bg-white/10 hover:bg-white/20 transition-colors opacity-0 group-hover:opacity-100">
      {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3 text-slate-400" />}
    </button>
  );
};

const RichMessage = ({ content }) => {
  if (!content) return null;

  return (
    <div className="rich-message">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            const code = String(children).replace(/\n$/, '');
            if (!inline && (match || code.includes('\n'))) {
              return (
                <div className="relative group my-2 rounded-lg overflow-hidden">
                  {match && <div className="text-[9px] text-slate-500 bg-[#1e1e2e] px-3 py-1 border-b border-white/5 font-mono">{match[1]}</div>}
                  <SyntaxHighlighter
                    style={oneDark}
                    language={match ? match[1] : 'text'}
                    PreTag="div"
                    customStyle={{ margin: 0, padding: '12px', fontSize: '12px', background: '#1e1e2e', borderRadius: match ? '0 0 8px 8px' : '8px' }}
                    {...props}
                  >
                    {code}
                  </SyntaxHighlighter>
                  <CopyButton text={code} />
                </div>
              );
            }
            return <code className="px-1.5 py-0.5 rounded bg-white/10 text-[#e06c75] text-[12px] font-mono" {...props}>{children}</code>;
          },
          blockquote({ children }) {
            return <blockquote className="border-l-2 border-[#00CEC9]/50 pl-3 my-1.5 text-white/60 italic">{children}</blockquote>;
          },
          table({ children }) {
            return <div className="overflow-x-auto my-2"><table className="min-w-full text-xs border border-white/10 rounded-lg overflow-hidden">{children}</table></div>;
          },
          thead({ children }) { return <thead className="bg-white/5">{children}</thead>; },
          th({ children }) { return <th className="px-3 py-1.5 text-left text-white/70 font-semibold border-b border-white/10">{children}</th>; },
          td({ children }) { return <td className="px-3 py-1.5 border-b border-white/5 text-white/80">{children}</td>; },
          a({ href, children }) { return <a href={href} target="_blank" rel="noopener noreferrer" className="text-[#00CEC9] hover:underline">{children}</a>; },
          ul({ children }) { return <ul className="list-disc list-inside my-1 space-y-0.5">{children}</ul>; },
          ol({ children }) { return <ol className="list-decimal list-inside my-1 space-y-0.5">{children}</ol>; },
          li({ children }) { return <li className="text-white/80">{children}</li>; },
          p({ children }) { return <p className="my-0.5">{children}</p>; },
          strong({ children }) { return <strong className="font-bold text-white">{children}</strong>; },
          em({ children }) { return <em className="italic text-white/90">{children}</em>; },
          del({ children }) { return <del className="line-through text-white/50">{children}</del>; },
          hr() { return <hr className="border-white/10 my-2" />; },
          h1({ children }) { return <h1 className="text-lg font-bold text-white mt-2 mb-1">{children}</h1>; },
          h2({ children }) { return <h2 className="text-base font-bold text-white mt-2 mb-1">{children}</h2>; },
          h3({ children }) { return <h3 className="text-sm font-bold text-white mt-1.5 mb-0.5">{children}</h3>; },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default RichMessage;
