import React from "react";
import ReactDOM from "react-dom/client";
import axios from "axios";
import * as Sentry from "@sentry/react";
import "@/index.css";
import "@/styles/animations.css";
import App from "@/App";

// Sentry APM — no-op unless REACT_APP_SENTRY_DSN is set
const SENTRY_DSN = process.env.REACT_APP_SENTRY_DSN;
const SENTRY_ENV = process.env.REACT_APP_ENV || "development";
if (SENTRY_DSN) {
  Sentry.init({
    dsn: SENTRY_DSN,
    environment: SENTRY_ENV,
    integrations: [Sentry.browserTracingIntegration(), Sentry.replayIntegration()],
    tracesSampleRate: SENTRY_ENV === "production" ? 0.1 : 1.0,
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,
  });
}

// Configure axios to always send credentials (cookies) with requests
axios.defaults.withCredentials = true;

// Register service worker for PWA
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js')
      .then((registration) => {
        console.log('ServiceWorker registered:', registration.scope);
      })
      .catch((error) => {
        console.log('ServiceWorker registration failed:', error);
      });
  });
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <Sentry.ErrorBoundary fallback={<p style={{padding: 24}}>An unexpected error occurred. Our team has been notified.</p>}>
      <App />
    </Sentry.ErrorBoundary>
  </React.StrictMode>,
);
