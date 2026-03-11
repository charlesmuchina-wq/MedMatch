/**
 * DomainContext — React context providing domain-resolved portal config
 * Available throughout the app via useDomain() hook
 */
import { createContext, useContext, useMemo } from 'react';
import { resolveDomainConfig } from '@/config/DomainConfig';

const DomainContext = createContext(null);

export const useDomain = () => {
  const ctx = useContext(DomainContext);
  if (!ctx) {
    // Fallback for components rendered outside provider
    return resolveDomainConfig(window.location.hostname, new URLSearchParams(window.location.search));
  }
  return ctx;
};

export const DomainProvider = ({ children }) => {
  const config = useMemo(() => {
    const hostname = window.location.hostname;
    const params = new URLSearchParams(window.location.search);
    const resolved = resolveDomainConfig(hostname, params);

    // Set document title based on domain
    if (resolved.title) {
      document.title = resolved.title;
    }

    return resolved;
  }, []);

  return (
    <DomainContext.Provider value={config}>
      {children}
    </DomainContext.Provider>
  );
};

export default DomainContext;
