// Standalone ESLint flat config for security-only scan (DAST evidence pack)
// Run: npx eslint --config eslint.security.config.mjs "src/**/*.{js,jsx,ts,tsx}" -f json -o ../docs/security/eslint_security_report.json
import securityPlugin from "eslint-plugin-security";

export default [
  {
    files: ["src/**/*.{js,jsx,ts,tsx}"],
    plugins: { security: securityPlugin },
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
    rules: {
      "security/detect-bidi-characters": "error",
      "security/detect-buffer-noassert": "error",
      "security/detect-child-process": "error",
      "security/detect-disable-mustache-escape": "error",
      "security/detect-eval-with-expression": "error",
      "security/detect-new-buffer": "error",
      "security/detect-no-csrf-before-method-override": "error",
      "security/detect-non-literal-fs-filename": "warn",
      "security/detect-non-literal-regexp": "warn",
      "security/detect-non-literal-require": "warn",
      "security/detect-object-injection": "warn",
      "security/detect-possible-timing-attacks": "warn",
      "security/detect-pseudoRandomBytes": "error",
      "security/detect-unsafe-regex": "error",
    },
  },
  {
    ignores: [
      "build/**",
      "node_modules/**",
      "src/**/*.test.{js,jsx,ts,tsx}",
      "src/**/__tests__/**",
    ],
  },
];
