import React from "react";

/**
 * WCAG 2.4.1 Bypass Blocks - Skip-navigation link
 * Visible only when focused; jumps directly to <main id="main-content">.
 */
export const SkipNav = () => {
  return (
    <a
      href="#main-content"
      className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-[9999] focus:px-4 focus:py-2 focus:bg-blue-700 focus:text-white focus:rounded-md focus:outline-none focus:ring-2 focus:ring-white focus:shadow-lg"
      data-testid="skip-nav-link"
    >
      Skip to main content
    </a>
  );
};

export default SkipNav;
