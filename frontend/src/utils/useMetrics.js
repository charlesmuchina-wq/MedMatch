/**
 * MedMatch Production Metrics Hook
 * Tracks user engagement, feature usage, and conversions.
 */
import { useCallback, useEffect, useRef } from 'react';
import { apiClient } from './apiClient';

// Generate unique session ID
const generateSessionId = () => {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

// Get or create session ID from sessionStorage
const getSessionId = () => {
  let sessionId = sessionStorage.getItem('medmatch_session_id');
  if (!sessionId) {
    sessionId = generateSessionId();
    sessionStorage.setItem('medmatch_session_id', sessionId);
  }
  return sessionId;
};

// Detect device type
const getDeviceType = () => {
  const ua = navigator.userAgent;
  if (/mobile/i.test(ua)) return 'mobile';
  if (/tablet/i.test(ua)) return 'tablet';
  if (window.electronAPI?.isDesktop) return 'desktop_app';
  return 'web';
};

/**
 * Hook for tracking production metrics
 */
export const useMetrics = () => {
  const sessionId = useRef(getSessionId());
  const pageStartTime = useRef(Date.now());

  // Track session start on mount
  useEffect(() => {
    const trackSessionStart = async () => {
      try {
        await apiClient.post('/api/metrics/session/start', {
          session_id: sessionId.current,
          device_type: getDeviceType(),
          referrer: document.referrer || null,
        });
      } catch (error) {
        console.debug('Session tracking failed:', error);
      }
    };

    trackSessionStart();

    // Track session end on unload
    const handleUnload = () => {
      navigator.sendBeacon(
        `${process.env.REACT_APP_BACKEND_URL}/api/metrics/session/end?session_id=${sessionId.current}`
      );
    };

    window.addEventListener('beforeunload', handleUnload);
    return () => window.removeEventListener('beforeunload', handleUnload);
  }, []);

  // Track page view
  const trackPageView = useCallback(async (pagePath, pageTitle) => {
    const timeOnPage = Date.now() - pageStartTime.current;
    pageStartTime.current = Date.now();

    try {
      await apiClient.post('/api/metrics/page-view', {
        session_id: sessionId.current,
        page_path: pagePath,
        page_title: pageTitle,
        time_on_page_ms: timeOnPage > 1000 ? timeOnPage : null,
      });
    } catch (error) {
      console.debug('Page view tracking failed:', error);
    }
  }, []);

  // Track feature usage
  const trackFeature = useCallback(async (featureName, category, options = {}) => {
    try {
      await apiClient.post('/api/metrics/feature-usage', {
        feature_name: featureName,
        feature_category: category,
        duration_ms: options.duration,
        success: options.success !== false,
        metadata: options.metadata,
      });
    } catch (error) {
      console.debug('Feature tracking failed:', error);
    }
  }, []);

  // Track job application
  const trackJobApplication = useCallback(async (jobData) => {
    try {
      await apiClient.post('/api/metrics/job-application', {
        job_id: jobData.jobId,
        job_title: jobData.title,
        company: jobData.company,
        source: jobData.source || 'search',
        application_method: jobData.method || 'direct',
        used_ai_cover_letter: jobData.usedAI || false,
      });
    } catch (error) {
      console.debug('Application tracking failed:', error);
    }
  }, []);

  // Track AI tool usage
  const trackAIUsage = useCallback(async (toolName, inputType, options = {}) => {
    try {
      await apiClient.post('/api/metrics/ai-tool-usage', {
        tool_name: toolName,
        input_type: inputType,
        output_quality_score: options.qualityScore,
        tokens_used: options.tokensUsed || 0,
        response_time_ms: options.responseTime || 0,
        user_feedback: options.feedback, // 'positive', 'negative', 'neutral'
      });
    } catch (error) {
      console.debug('AI usage tracking failed:', error);
    }
  }, []);

  // Track conversion
  const trackConversion = useCallback(async (conversionType, source, options = {}) => {
    try {
      await apiClient.post('/api/metrics/conversion', {
        conversion_type: conversionType,
        source: source,
        campaign: options.campaign,
        value: options.value,
      });
    } catch (error) {
      console.debug('Conversion tracking failed:', error);
    }
  }, []);

  return {
    sessionId: sessionId.current,
    trackPageView,
    trackFeature,
    trackJobApplication,
    trackAIUsage,
    trackConversion,
  };
};

/**
 * Higher-order component for automatic page view tracking
 */
export const withPageTracking = (WrappedComponent, pageName) => {
  return function TrackedComponent(props) {
    const { trackPageView } = useMetrics();

    useEffect(() => {
      trackPageView(window.location.pathname, pageName);
    }, [trackPageView]);

    return <WrappedComponent {...props} />;
  };
};

export default useMetrics;
