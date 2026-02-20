/**
 * Pseudo-localization Utility for MedMatch
 * 
 * CAPA-002: Translation Coverage Investigation
 * 
 * This utility transforms text to pseudo-locale format to help identify
 * hardcoded strings that bypass the translation system.
 * 
 * Pseudo-locale format: [!!! Śéƭƭïñϱƨ !!!]
 * - Brackets indicate translatable text
 * - Accented characters test special character rendering
 * - Any text that remains in normal English is hardcoded
 */

// Character mapping for pseudo-localization
const PSEUDO_MAP = {
  'a': 'ä', 'A': 'Ä',
  'b': 'ƀ', 'B': 'Ɓ',
  'c': 'ç', 'C': 'Ç',
  'd': 'đ', 'D': 'Đ',
  'e': 'ë', 'E': 'Ë',
  'f': 'ƒ', 'F': 'Ƒ',
  'g': 'ğ', 'G': 'Ğ',
  'h': 'ħ', 'H': 'Ħ',
  'i': 'ï', 'I': 'Ï',
  'j': 'ĵ', 'J': 'Ĵ',
  'k': 'ķ', 'K': 'Ķ',
  'l': 'ĺ', 'L': 'Ĺ',
  'm': 'ɱ', 'M': 'Ɱ',
  'n': 'ñ', 'N': 'Ñ',
  'o': 'ö', 'O': 'Ö',
  'p': 'þ', 'P': 'Þ',
  'q': 'ɋ', 'Q': 'Ɋ',
  'r': 'ř', 'R': 'Ř',
  's': 'š', 'S': 'Š',
  't': 'ţ', 'T': 'Ţ',
  'u': 'ü', 'U': 'Ü',
  'v': 'ṽ', 'V': 'Ṽ',
  'w': 'ŵ', 'W': 'Ŵ',
  'x': 'χ', 'X': 'Χ',
  'y': 'ÿ', 'Y': 'Ÿ',
  'z': 'ž', 'Z': 'Ž'
};

/**
 * Transform a string to pseudo-locale format
 * @param {string} text - Original text
 * @returns {string} - Pseudo-localized text with brackets and accents
 */
export function pseudoLocalize(text) {
  if (!text || typeof text !== 'string') return text;
  
  // Skip if already pseudo-localized
  if (text.startsWith('[!!!') && text.endsWith('!!!]')) return text;
  
  // Transform characters
  let transformed = '';
  for (const char of text) {
    transformed += PSEUDO_MAP[char] || char;
  }
  
  // Wrap in brackets for visibility
  return `[!!! ${transformed} !!!]`;
}

/**
 * Transform all strings in a translation object to pseudo-locale
 * @param {object} translations - Translation object
 * @returns {object} - Pseudo-localized translations
 */
export function createPseudoLocale(translations) {
  const result = {};
  
  for (const [key, value] of Object.entries(translations)) {
    if (typeof value === 'string') {
      result[key] = pseudoLocalize(value);
    } else if (typeof value === 'object' && value !== null) {
      result[key] = createPseudoLocale(value);
    } else {
      result[key] = value;
    }
  }
  
  return result;
}

/**
 * Check if text appears to be hardcoded (not pseudo-localized)
 * @param {string} text - Text to check
 * @returns {boolean} - True if text appears hardcoded
 */
export function isHardcoded(text) {
  if (!text || typeof text !== 'string') return false;
  
  // Skip very short strings
  if (text.length < 3) return false;
  
  // Skip numbers, URLs, emails
  if (/^[\d\s.,]+$/.test(text)) return false;
  if (/^https?:\/\//.test(text)) return false;
  if (/\S+@\S+\.\S+/.test(text)) return false;
  
  // Check if it's regular English text (not pseudo-localized)
  const englishPattern = /^[A-Za-z\s.,!?'"()-]+$/;
  return englishPattern.test(text);
}

export default { pseudoLocalize, createPseudoLocale, isHardcoded };
