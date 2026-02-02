/**
 * MedMatch - TensorFlow.js Neural Network for Callback Probability Prediction
 * 
 * A browser-based neural network that predicts the probability of getting
 * a callback for a job application based on resume-job matching features.
 */
import * as tf from '@tensorflow/tfjs';

// Feature configuration
const FEATURE_NAMES = [
  'skills_match_ratio',        // Ratio of matched skills (0-1)
  'experience_years',          // Years of experience (normalized)
  'education_match',           // Education level match (0-1)
  'location_match',            // Location preference match (0-1)
  'salary_match',              // Salary expectation match (0-1)
  'industry_experience',       // Same industry experience (0-1)
  'job_title_similarity',      // Title semantic similarity (0-1)
  'keywords_match',            // Keywords match ratio (0-1)
  'recency_score',             // How recent the application is (0-1)
  'company_size_fit',          // Company size preference match (0-1)
  'resume_completeness',       // Resume profile completeness (0-1)
  'certifications_match',      // Relevant certifications (0-1)
];

const NUM_FEATURES = FEATURE_NAMES.length;
const MODEL_VERSION = '2.0.0';
const MODEL_STORAGE_KEY = 'medmatch_callback_model';

class CallbackPredictorModel {
  constructor() {
    this.model = null;
    this.isReady = false;
    this.isBrowser = typeof window !== 'undefined';
  }

  /**
   * Build the neural network architecture
   * Input: 12 features
   * Hidden layers: 64 -> 32 -> 16 neurons with ReLU activation
   * Output: 1 neuron with sigmoid activation (probability)
   */
  buildModel() {
    const model = tf.sequential();
    
    // Input layer + first hidden layer
    model.add(tf.layers.dense({
      inputShape: [NUM_FEATURES],
      units: 64,
      activation: 'relu',
      kernelInitializer: 'glorotUniform',
      kernelRegularizer: tf.regularizers.l2({ l2: 0.001 }),
    }));
    
    // Batch normalization for training stability
    model.add(tf.layers.batchNormalization());
    
    // Dropout for regularization
    model.add(tf.layers.dropout({ rate: 0.3 }));
    
    // Second hidden layer
    model.add(tf.layers.dense({
      units: 32,
      activation: 'relu',
      kernelRegularizer: tf.regularizers.l2({ l2: 0.001 }),
    }));
    
    model.add(tf.layers.batchNormalization());
    model.add(tf.layers.dropout({ rate: 0.2 }));
    
    // Third hidden layer
    model.add(tf.layers.dense({
      units: 16,
      activation: 'relu',
    }));
    
    // Output layer - sigmoid for probability
    model.add(tf.layers.dense({
      units: 1,
      activation: 'sigmoid',
    }));
    
    // Compile with Adam optimizer
    model.compile({
      optimizer: tf.train.adam(0.001),
      loss: 'binaryCrossentropy',
      metrics: ['accuracy'],
    });
    
    return model;
  }

  /**
   * Initialize the model - either load from storage or create new
   */
  async initialize() {
    if (this.isReady) return true;
    
    try {
      // Try to load pre-trained model from IndexedDB
      if (this.isBrowser) {
        try {
          this.model = await tf.loadLayersModel(`indexeddb://${MODEL_STORAGE_KEY}`);
          console.log('[CallbackPredictor] Loaded pre-trained model from storage');
          this.isReady = true;
          return true;
        } catch (e) {
          console.log('[CallbackPredictor] No saved model found, creating new model');
        }
      }
      
      // Create and train a new model with synthetic data
      this.model = this.buildModel();
      await this.trainWithSyntheticData();
      
      // Save the trained model
      if (this.isBrowser) {
        await this.model.save(`indexeddb://${MODEL_STORAGE_KEY}`);
        console.log('[CallbackPredictor] Model saved to storage');
      }
      
      this.isReady = true;
      return true;
    } catch (error) {
      console.error('[CallbackPredictor] Initialization failed:', error);
      return false;
    }
  }

  /**
   * Generate synthetic training data for initial model training
   * This simulates realistic job application scenarios
   */
  generateSyntheticData(numSamples = 2000) {
    const features = [];
    const labels = [];
    
    for (let i = 0; i < numSamples; i++) {
      // Generate random feature values
      const sample = {
        skills_match_ratio: Math.random(),
        experience_years: Math.random(),
        education_match: Math.random(),
        location_match: Math.random(),
        salary_match: Math.random(),
        industry_experience: Math.random(),
        job_title_similarity: Math.random(),
        keywords_match: Math.random(),
        recency_score: Math.random(),
        company_size_fit: Math.random(),
        resume_completeness: Math.random(),
        certifications_match: Math.random(),
      };
      
      // Calculate realistic callback probability based on features
      // Higher weights for more important features
      const weights = {
        skills_match_ratio: 0.25,
        experience_years: 0.15,
        education_match: 0.08,
        location_match: 0.10,
        salary_match: 0.08,
        industry_experience: 0.08,
        job_title_similarity: 0.12,
        keywords_match: 0.06,
        recency_score: 0.02,
        company_size_fit: 0.02,
        resume_completeness: 0.02,
        certifications_match: 0.02,
      };
      
      // Calculate weighted score
      let score = 0;
      for (const [key, weight] of Object.entries(weights)) {
        score += sample[key] * weight;
      }
      
      // Add some noise
      score += (Math.random() - 0.5) * 0.15;
      
      // Apply sigmoid-like transformation
      const probability = 1 / (1 + Math.exp(-8 * (score - 0.5)));
      
      // Convert to binary label with some randomness
      const threshold = Math.random();
      const label = probability > threshold ? 1 : 0;
      
      features.push(Object.values(sample));
      labels.push(label);
    }
    
    return {
      features: tf.tensor2d(features),
      labels: tf.tensor2d(labels, [numSamples, 1]),
    };
  }

  /**
   * Train the model with synthetic data
   */
  async trainWithSyntheticData() {
    console.log('[CallbackPredictor] Training model with synthetic data...');
    
    const { features, labels } = this.generateSyntheticData(2000);
    
    const history = await this.model.fit(features, labels, {
      epochs: 50,
      batchSize: 32,
      validationSplit: 0.2,
      shuffle: true,
      callbacks: {
        onEpochEnd: (epoch, logs) => {
          if (epoch % 10 === 0) {
            console.log(`[CallbackPredictor] Epoch ${epoch}: loss=${logs.loss.toFixed(4)}, accuracy=${logs.acc.toFixed(4)}`);
          }
        },
      },
    });
    
    // Clean up tensors
    features.dispose();
    labels.dispose();
    
    console.log('[CallbackPredictor] Training complete');
    return history;
  }

  /**
   * Normalize feature values to 0-1 range
   */
  normalizeFeatures(rawFeatures) {
    return {
      skills_match_ratio: Math.min(1, Math.max(0, rawFeatures.skills_match_ratio || 0)),
      experience_years: Math.min(1, (rawFeatures.experience_years || 0) / 20), // Max 20 years
      education_match: Math.min(1, Math.max(0, rawFeatures.education_match || 0)),
      location_match: rawFeatures.location_match ? 1 : 0,
      salary_match: Math.min(1, Math.max(0, rawFeatures.salary_match || 0.5)),
      industry_experience: rawFeatures.industry_experience ? 1 : 0,
      job_title_similarity: Math.min(1, Math.max(0, rawFeatures.job_title_similarity || 0)),
      keywords_match: Math.min(1, Math.max(0, rawFeatures.keywords_match || 0)),
      recency_score: Math.min(1, Math.max(0, rawFeatures.recency_score || 1)),
      company_size_fit: Math.min(1, Math.max(0, rawFeatures.company_size_fit || 0.5)),
      resume_completeness: Math.min(1, Math.max(0, rawFeatures.resume_completeness || 0)),
      certifications_match: Math.min(1, Math.max(0, rawFeatures.certifications_match || 0)),
    };
  }

  /**
   * Predict callback probability for a job application
   * @param {Object} features - Raw feature values
   * @returns {Object} Prediction result with probability and confidence
   */
  async predict(features) {
    if (!this.isReady) {
      await this.initialize();
    }
    
    if (!this.model) {
      throw new Error('Model not initialized');
    }
    
    // Normalize features
    const normalized = this.normalizeFeatures(features);
    const featureVector = FEATURE_NAMES.map(name => normalized[name]);
    
    // Create tensor and predict
    const inputTensor = tf.tensor2d([featureVector]);
    const prediction = this.model.predict(inputTensor);
    const probability = (await prediction.data())[0];
    
    // Clean up tensors
    inputTensor.dispose();
    prediction.dispose();
    
    // Calculate confidence based on feature completeness
    const featureCompleteness = Object.values(normalized).filter(v => v > 0).length / NUM_FEATURES;
    const confidence = 0.5 + (featureCompleteness * 0.5);
    
    // Determine callback likelihood category
    let category;
    if (probability >= 0.7) {
      category = 'high';
    } else if (probability >= 0.4) {
      category = 'medium';
    } else {
      category = 'low';
    }
    
    return {
      probability: Math.round(probability * 100),
      confidence: Math.round(confidence * 100),
      category,
      features: normalized,
      modelVersion: MODEL_VERSION,
    };
  }

  /**
   * Get feature importance based on model weights
   */
  async getFeatureImportance() {
    if (!this.model) {
      await this.initialize();
    }
    
    // Get first layer weights
    const firstLayer = this.model.getLayer(undefined, 0);
    const weights = firstLayer.getWeights()[0];
    const weightData = await weights.data();
    
    // Calculate importance as sum of absolute weights for each feature
    const importance = {};
    for (let i = 0; i < NUM_FEATURES; i++) {
      let sum = 0;
      for (let j = 0; j < 64; j++) { // 64 is the number of neurons in first layer
        sum += Math.abs(weightData[i * 64 + j]);
      }
      importance[FEATURE_NAMES[i]] = sum;
    }
    
    // Normalize to percentages
    const total = Object.values(importance).reduce((a, b) => a + b, 0);
    const normalized = {};
    for (const [key, value] of Object.entries(importance)) {
      normalized[key] = Math.round((value / total) * 100);
    }
    
    return normalized;
  }

  /**
   * Analyze resume-job match and return detailed breakdown
   */
  async analyzeMatch(resume, job) {
    // Extract features from resume and job
    const features = this.extractMatchFeatures(resume, job);
    
    // Get prediction
    const prediction = await this.predict(features);
    
    // Get feature importance
    const importance = await this.getFeatureImportance();
    
    // Generate recommendations
    const recommendations = this.generateRecommendations(features, prediction);
    
    return {
      ...prediction,
      featureImportance: importance,
      recommendations,
      matchBreakdown: features,
    };
  }

  /**
   * Extract match features from resume and job data
   */
  extractMatchFeatures(resume, job) {
    const resumeSkills = (resume.skills || []).map(s => s.toLowerCase());
    const jobSkills = (job.required_skills || job.skills || []).map(s => s.toLowerCase());
    
    // Calculate skills match
    const matchedSkills = resumeSkills.filter(s => jobSkills.includes(s));
    const skills_match_ratio = jobSkills.length > 0 
      ? matchedSkills.length / jobSkills.length 
      : 0.5;
    
    // Calculate experience match
    const resumeExp = resume.experience_years || resume.years_experience || 0;
    const jobMinExp = job.min_experience || job.experience_required || 0;
    const experience_years = Math.min(resumeExp / Math.max(jobMinExp, 1), 1);
    
    // Calculate title similarity using word overlap
    const resumeTitle = (resume.current_title || resume.job_title || '').toLowerCase().split(/\s+/);
    const jobTitle = (job.title || '').toLowerCase().split(/\s+/);
    const titleOverlap = resumeTitle.filter(w => jobTitle.includes(w)).length;
    const job_title_similarity = jobTitle.length > 0 
      ? titleOverlap / jobTitle.length 
      : 0.5;
    
    // Location match
    const resumeLocation = (resume.location || resume.preferred_location || '').toLowerCase();
    const jobLocation = (job.location || '').toLowerCase();
    const location_match = 
      jobLocation.includes('remote') || 
      resumeLocation.includes(jobLocation) || 
      jobLocation.includes(resumeLocation) ? 1 : 0.5;
    
    // Resume completeness
    const profileFields = ['skills', 'experience', 'education', 'summary', 'contact'];
    const filledFields = profileFields.filter(f => resume[f] && 
      (Array.isArray(resume[f]) ? resume[f].length > 0 : true));
    const resume_completeness = filledFields.length / profileFields.length;
    
    return {
      skills_match_ratio,
      experience_years,
      education_match: resume.education ? 0.7 : 0.3,
      location_match,
      salary_match: 0.7, // Default assumption
      industry_experience: 0.6, // Default assumption
      job_title_similarity,
      keywords_match: skills_match_ratio * 0.8, // Similar to skills
      recency_score: 1.0, // New application
      company_size_fit: 0.6, // Default assumption
      resume_completeness,
      certifications_match: (resume.certifications?.length || 0) > 0 ? 0.7 : 0.3,
    };
  }

  /**
   * Generate recommendations to improve callback probability
   */
  generateRecommendations(features, prediction) {
    const recommendations = [];
    
    if (features.skills_match_ratio < 0.5) {
      recommendations.push({
        type: 'skills',
        priority: 'high',
        message: 'Your skills match is below average. Consider highlighting relevant skills or acquiring new ones.',
      });
    }
    
    if (features.resume_completeness < 0.7) {
      recommendations.push({
        type: 'profile',
        priority: 'medium',
        message: 'Complete your profile to increase visibility. Add missing sections like summary, skills, or education.',
      });
    }
    
    if (features.job_title_similarity < 0.3) {
      recommendations.push({
        type: 'title',
        priority: 'medium',
        message: 'Your current title differs significantly from the job. Consider tailoring your resume title.',
      });
    }
    
    if (features.experience_years < 0.5) {
      recommendations.push({
        type: 'experience',
        priority: 'low',
        message: 'You may have less experience than required. Highlight relevant projects or transferable skills.',
      });
    }
    
    if (prediction.probability < 40) {
      recommendations.push({
        type: 'general',
        priority: 'high',
        message: 'This may not be the best match. Consider looking for roles that better align with your profile.',
      });
    }
    
    return recommendations;
  }

  /**
   * Get model statistics and info
   */
  getModelInfo() {
    return {
      version: MODEL_VERSION,
      features: FEATURE_NAMES,
      numFeatures: NUM_FEATURES,
      architecture: ['Input(12)', 'Dense(64, ReLU)', 'BatchNorm', 'Dropout(0.3)', 
                     'Dense(32, ReLU)', 'BatchNorm', 'Dropout(0.2)', 
                     'Dense(16, ReLU)', 'Dense(1, Sigmoid)'],
      isReady: this.isReady,
    };
  }

  /**
   * Dispose of the model to free memory
   */
  dispose() {
    if (this.model) {
      this.model.dispose();
      this.model = null;
      this.isReady = false;
    }
  }
}

// Export singleton instance
export const callbackPredictor = new CallbackPredictorModel();

// Export class and feature names for flexibility
export { CallbackPredictorModel, FEATURE_NAMES, NUM_FEATURES, MODEL_VERSION };
