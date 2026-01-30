/**
 * MedMatch ML Predictor - TensorFlow.js Client
 * Browser-based machine learning for real-time issue prediction.
 * Works alongside the backend scikit-learn model.
 */

// Simple rule-based predictor that can run in the browser
// This complements the backend ML model with instant predictions

export class BrowserMLPredictor {
  constructor() {
    this.thresholds = {
      errorRateWarning: 5,
      errorRateCritical: 15,
      latencyWarning: 500,
      latencyCritical: 2000,
      cpuWarning: 70,
      cpuCritical: 90,
      memoryWarning: 75,
      memoryCritical: 90,
    };
    
    this.weights = {
      errorRate: 0.3,
      latency: 0.25,
      cpu: 0.2,
      memory: 0.15,
      errorCount: 0.1,
    };
  }

  /**
   * Predict system health based on current metrics
   * @param {Object} metrics - Current system metrics
   * @returns {Object} Prediction result
   */
  predict(metrics) {
    const {
      errorRate = 0,
      avgLatency = 0,
      cpuUsage = 0,
      memoryUsage = 0,
      errorCount = 0,
      totalRequests = 0,
    } = metrics;

    // Calculate component scores (0-100, higher is healthier)
    const scores = {
      errorRate: this.calculateErrorRateScore(errorRate),
      latency: this.calculateLatencyScore(avgLatency),
      cpu: this.calculateResourceScore(cpuUsage, this.thresholds.cpuWarning, this.thresholds.cpuCritical),
      memory: this.calculateResourceScore(memoryUsage, this.thresholds.memoryWarning, this.thresholds.memoryCritical),
      errorCount: Math.max(0, 100 - errorCount * 2),
    };

    // Weighted overall score
    const overallScore = Object.entries(this.weights).reduce((sum, [key, weight]) => {
      return sum + (scores[key] || 0) * weight;
    }, 0);

    // Determine prediction
    let prediction = 'healthy';
    let severity = 'none';
    const issues = [];

    if (overallScore < 40) {
      prediction = 'critical';
      severity = 'critical';
    } else if (overallScore < 70) {
      prediction = 'degraded';
      severity = 'warning';
    }

    // Identify specific issues
    if (errorRate >= this.thresholds.errorRateCritical) {
      issues.push({
        type: 'error_rate',
        severity: 'critical',
        message: `Critical error rate: ${errorRate.toFixed(1)}%`,
        value: errorRate,
        threshold: this.thresholds.errorRateCritical,
      });
    } else if (errorRate >= this.thresholds.errorRateWarning) {
      issues.push({
        type: 'error_rate',
        severity: 'warning',
        message: `Elevated error rate: ${errorRate.toFixed(1)}%`,
        value: errorRate,
        threshold: this.thresholds.errorRateWarning,
      });
    }

    if (avgLatency >= this.thresholds.latencyCritical) {
      issues.push({
        type: 'latency',
        severity: 'critical',
        message: `Critical latency: ${avgLatency.toFixed(0)}ms`,
        value: avgLatency,
        threshold: this.thresholds.latencyCritical,
      });
    } else if (avgLatency >= this.thresholds.latencyWarning) {
      issues.push({
        type: 'latency',
        severity: 'warning',
        message: `High latency: ${avgLatency.toFixed(0)}ms`,
        value: avgLatency,
        threshold: this.thresholds.latencyWarning,
      });
    }

    if (cpuUsage >= this.thresholds.cpuCritical) {
      issues.push({
        type: 'cpu',
        severity: 'critical',
        message: `Critical CPU usage: ${cpuUsage.toFixed(0)}%`,
        value: cpuUsage,
        threshold: this.thresholds.cpuCritical,
      });
    }

    if (memoryUsage >= this.thresholds.memoryCritical) {
      issues.push({
        type: 'memory',
        severity: 'critical',
        message: `Critical memory usage: ${memoryUsage.toFixed(0)}%`,
        value: memoryUsage,
        threshold: this.thresholds.memoryCritical,
      });
    }

    return {
      prediction,
      severity,
      confidence: this.calculateConfidence(overallScore, totalRequests),
      healthScore: Math.round(overallScore),
      componentScores: scores,
      issues,
      recommendations: this.generateRecommendations(issues),
      timestamp: new Date().toISOString(),
    };
  }

  calculateErrorRateScore(errorRate) {
    if (errorRate <= 1) return 100;
    if (errorRate <= this.thresholds.errorRateWarning) {
      return 100 - (errorRate - 1) * (30 / (this.thresholds.errorRateWarning - 1));
    }
    if (errorRate <= this.thresholds.errorRateCritical) {
      return 70 - (errorRate - this.thresholds.errorRateWarning) * 
             (50 / (this.thresholds.errorRateCritical - this.thresholds.errorRateWarning));
    }
    return Math.max(0, 20 - (errorRate - this.thresholds.errorRateCritical));
  }

  calculateLatencyScore(latency) {
    if (latency <= 100) return 100;
    if (latency <= this.thresholds.latencyWarning) {
      return 100 - (latency - 100) * (30 / (this.thresholds.latencyWarning - 100));
    }
    if (latency <= this.thresholds.latencyCritical) {
      return 70 - (latency - this.thresholds.latencyWarning) * 
             (50 / (this.thresholds.latencyCritical - this.thresholds.latencyWarning));
    }
    return Math.max(0, 20 - (latency - this.thresholds.latencyCritical) / 100);
  }

  calculateResourceScore(usage, warningThreshold, criticalThreshold) {
    if (usage <= 50) return 100;
    if (usage <= warningThreshold) {
      return 100 - (usage - 50) * (30 / (warningThreshold - 50));
    }
    if (usage <= criticalThreshold) {
      return 70 - (usage - warningThreshold) * (50 / (criticalThreshold - warningThreshold));
    }
    return Math.max(0, 20 - (usage - criticalThreshold) * 2);
  }

  calculateConfidence(overallScore, totalRequests) {
    // Higher confidence with more data and extreme scores
    let confidence = 0.5;
    
    // More data = higher confidence
    if (totalRequests > 100) confidence += 0.2;
    else if (totalRequests > 50) confidence += 0.1;
    
    // Extreme scores are more certain
    if (overallScore > 90 || overallScore < 30) confidence += 0.2;
    else if (overallScore > 80 || overallScore < 40) confidence += 0.1;
    
    return Math.min(0.95, confidence);
  }

  generateRecommendations(issues) {
    const recommendations = [];
    
    for (const issue of issues) {
      switch (issue.type) {
        case 'error_rate':
          recommendations.push({
            priority: issue.severity === 'critical' ? 'high' : 'medium',
            action: 'Investigate error logs',
            details: 'Review recent error patterns and check for deployment issues',
          });
          break;
        case 'latency':
          recommendations.push({
            priority: issue.severity === 'critical' ? 'high' : 'medium',
            action: 'Optimize performance',
            details: 'Check database queries, enable caching, review slow endpoints',
          });
          break;
        case 'cpu':
          recommendations.push({
            priority: 'high',
            action: 'Scale resources',
            details: 'Consider scaling up CPU or optimizing resource-intensive operations',
          });
          break;
        case 'memory':
          recommendations.push({
            priority: 'high',
            action: 'Check for memory leaks',
            details: 'Review memory usage patterns and restart services if needed',
          });
          break;
      }
    }
    
    if (recommendations.length === 0) {
      recommendations.push({
        priority: 'low',
        action: 'Continue monitoring',
        details: 'System is healthy. Keep monitoring for changes.',
      });
    }
    
    return recommendations;
  }

  /**
   * Update thresholds for customization
   * @param {Object} newThresholds - New threshold values
   */
  updateThresholds(newThresholds) {
    this.thresholds = { ...this.thresholds, ...newThresholds };
  }

  /**
   * Update weights for score calculation
   * @param {Object} newWeights - New weight values
   */
  updateWeights(newWeights) {
    this.weights = { ...this.weights, ...newWeights };
  }
}

// Create singleton instance
export const browserPredictor = new BrowserMLPredictor();

export default browserPredictor;
