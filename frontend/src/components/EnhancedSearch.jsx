/**
 * Enhanced Search Components
 * 
 * Features:
 * - Autocomplete with debouncing
 * - Spell correction suggestions
 * - Search history
 * - Popular searches
 * - Fuzzy matching
 * - Performance optimized (< 3.8s Time to First Result)
 */

import React, { useState, useEffect, useCallback, useRef, memo } from 'react';
import { Search, Clock, TrendingUp, X, Loader2, Sparkles, History } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { apiClient } from '@/utils/apiClient';

const API = process.env.REACT_APP_BACKEND_URL;

// Debounce hook for search input
const useDebounce = (value, delay) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
};

// ============== Autocomplete Suggestion Item ==============
const SuggestionItem = memo(({ suggestion, onClick, isHighlighted }) => {
  const getIcon = () => {
    switch (suggestion.type) {
      case 'history':
        return <History className="w-4 h-4 text-gray-400" />;
      case 'popular':
        return <TrendingUp className="w-4 h-4 text-orange-400" />;
      case 'suggested':
        return <Sparkles className="w-4 h-4 text-purple-400" />;
      default:
        return <Search className="w-4 h-4 text-gray-400" />;
    }
  };

  return (
    <button
      onClick={() => onClick(suggestion.text)}
      className={`w-full flex items-center gap-3 px-4 py-2.5 text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
        isHighlighted ? 'bg-gray-50 dark:bg-gray-700' : ''
      }`}
    >
      {getIcon()}
      <span className="flex-1 text-sm text-gray-700 dark:text-gray-200">{suggestion.text}</span>
      {suggestion.type === 'popular' && (
        <span className="text-xs text-orange-500 bg-orange-50 px-2 py-0.5 rounded">Trending</span>
      )}
    </button>
  );
});

// ============== Spell Correction Banner ==============
const SpellCorrectionBanner = memo(({ original, corrected, onAccept, onDismiss }) => {
  if (!corrected) return null;

  return (
    <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 dark:bg-blue-900/30 border-b border-blue-100 dark:border-blue-800">
      <Sparkles className="w-4 h-4 text-blue-500" />
      <span className="text-sm text-blue-700 dark:text-blue-300">
        Did you mean: <button onClick={onAccept} className="font-semibold underline">{corrected}</button>?
      </span>
      <button onClick={onDismiss} className="ml-auto text-blue-400 hover:text-blue-600">
        <X className="w-4 h-4" />
      </button>
    </div>
  );
});

// ============== Enhanced Search Input ==============
export const EnhancedSearchInput = memo(({
  value,
  onChange,
  onSearch,
  placeholder = "Search jobs, skills, companies...",
  className = "",
  autoFocus = false,
  showSuggestions = true,
  "data-testid": testId
}) => {
  const [inputValue, setInputValue] = useState(value || '');
  const [suggestions, setSuggestions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const [spellCorrection, setSpellCorrection] = useState(null);
  const inputRef = useRef(null);
  const dropdownRef = useRef(null);

  const debouncedValue = useDebounce(inputValue, 200);

  // Fetch autocomplete suggestions
  useEffect(() => {
    if (!showSuggestions || debouncedValue.length < 2) {
      setSuggestions([]);
      return;
    }

    const fetchSuggestions = async () => {
      setIsLoading(true);
      try {
        const response = await apiClient.get(`/api/search/autocomplete?q=${encodeURIComponent(debouncedValue)}&limit=8`);
        setSuggestions(response.suggestions || []);
        setShowDropdown(true);
      } catch (error) {
        console.error('Autocomplete error:', error);
        setSuggestions([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSuggestions();
  }, [debouncedValue, showSuggestions]);

  // Check spelling when user stops typing
  useEffect(() => {
    if (debouncedValue.length < 3) {
      setSpellCorrection(null);
      return;
    }

    const checkSpelling = async () => {
      try {
        const response = await apiClient.get(`/api/search/spell-check?q=${encodeURIComponent(debouncedValue)}`);
        if (response.was_corrected) {
          setSpellCorrection(response.corrected);
        } else {
          setSpellCorrection(null);
        }
      } catch (error) {
        console.error('Spell check error:', error);
      }
    };

    checkSpelling();
  }, [debouncedValue]);

  // Handle keyboard navigation
  const handleKeyDown = useCallback((e) => {
    if (!showDropdown || suggestions.length === 0) {
      if (e.key === 'Enter') {
        handleSearch(inputValue);
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex(prev => 
          prev > 0 ? prev - 1 : suggestions.length - 1
        );
        break;
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0) {
          handleSuggestionClick(suggestions[highlightedIndex].text);
        } else {
          handleSearch(inputValue);
        }
        break;
      case 'Escape':
        setShowDropdown(false);
        setHighlightedIndex(-1);
        break;
      default:
        break;
    }
  }, [showDropdown, suggestions, highlightedIndex, inputValue]);

  const handleInputChange = useCallback((e) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    setHighlightedIndex(-1);
    onChange?.(newValue);
  }, [onChange]);

  const handleSuggestionClick = useCallback((text) => {
    setInputValue(text);
    setShowDropdown(false);
    setHighlightedIndex(-1);
    onChange?.(text);
    handleSearch(text);
  }, [onChange]);

  const handleSearch = useCallback((query) => {
    setShowDropdown(false);
    onSearch?.(query);
  }, [onSearch]);

  const handleAcceptCorrection = useCallback(() => {
    if (spellCorrection) {
      setInputValue(spellCorrection);
      onChange?.(spellCorrection);
      setSpellCorrection(null);
      handleSearch(spellCorrection);
    }
  }, [spellCorrection, onChange]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (
        dropdownRef.current && 
        !dropdownRef.current.contains(e.target) &&
        !inputRef.current?.contains(e.target)
      ) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className={`relative ${className}`}>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <Input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => suggestions.length > 0 && setShowDropdown(true)}
          placeholder={placeholder}
          className="pl-10 pr-10"
          autoFocus={autoFocus}
          data-testid={testId}
        />
        {isLoading && (
          <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 animate-spin" />
        )}
        {!isLoading && inputValue && (
          <button
            onClick={() => {
              setInputValue('');
              onChange?.('');
              setSuggestions([]);
            }}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Spell Correction */}
      {spellCorrection && !showDropdown && (
        <SpellCorrectionBanner
          original={inputValue}
          corrected={spellCorrection}
          onAccept={handleAcceptCorrection}
          onDismiss={() => setSpellCorrection(null)}
        />
      )}

      {/* Autocomplete Dropdown */}
      {showDropdown && suggestions.length > 0 && (
        <div
          ref={dropdownRef}
          className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50 overflow-hidden"
        >
          {suggestions.map((suggestion, index) => (
            <SuggestionItem
              key={`${suggestion.text}-${index}`}
              suggestion={suggestion}
              onClick={handleSuggestionClick}
              isHighlighted={index === highlightedIndex}
            />
          ))}
        </div>
      )}
    </div>
  );
});

// ============== Search History Component ==============
export const SearchHistory = memo(({ onSelect, limit = 5 }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await apiClient.get(`/api/search/history?limit=${limit}`);
        setHistory(response.searches || []);
      } catch (error) {
        console.error('Failed to fetch search history:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [limit]);

  if (loading || history.length === 0) return null;

  return (
    <div className="mb-4">
      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2 flex items-center gap-2">
        <Clock className="w-4 h-4" />
        Recent Searches
      </h3>
      <div className="flex flex-wrap gap-2">
        {history.map((search, index) => (
          <button
            key={index}
            onClick={() => onSelect(search)}
            className="px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
          >
            {search}
          </button>
        ))}
      </div>
    </div>
  );
});

// ============== Popular Searches Component ==============
export const PopularSearches = memo(({ onSelect, limit = 8 }) => {
  const [popular, setPopular] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPopular = async () => {
      try {
        const response = await apiClient.get(`/api/search/popular?limit=${limit}`);
        setPopular(response.searches || []);
      } catch (error) {
        console.error('Failed to fetch popular searches:', error);
        // Fallback popular searches
        setPopular([
          'Software Engineer',
          'Quality Engineer', 
          'Data Scientist',
          'Product Manager',
          'Supplier Quality Manager',
          'Research Scientist',
          'Manufacturing Engineer',
          'Clinical Research'
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchPopular();
  }, [limit]);

  if (loading) return null;

  return (
    <div className="mb-4">
      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2 flex items-center gap-2">
        <TrendingUp className="w-4 h-4 text-orange-500" />
        Trending Searches
      </h3>
      <div className="flex flex-wrap gap-2">
        {popular.map((search, index) => (
          <button
            key={index}
            onClick={() => onSelect(search)}
            className="px-3 py-1.5 text-sm bg-orange-50 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 rounded-full hover:bg-orange-100 dark:hover:bg-orange-900/50 transition-colors"
          >
            {search}
          </button>
        ))}
      </div>
    </div>
  );
});

// Display names
EnhancedSearchInput.displayName = 'EnhancedSearchInput';
SearchHistory.displayName = 'SearchHistory';
PopularSearches.displayName = 'PopularSearches';
SuggestionItem.displayName = 'SuggestionItem';
SpellCorrectionBanner.displayName = 'SpellCorrectionBanner';

export default EnhancedSearchInput;
