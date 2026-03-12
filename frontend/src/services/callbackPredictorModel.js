/**
 * MedMatch - Lightweight Callback Probability Predictor
 * Uses weighted scoring (no TensorFlow dependency)
 */

const FEATURE_NAMES = [
  'skills_match_ratio', 'experience_years', 'education_match', 'location_match',
  'salary_match', 'industry_experience', 'job_title_similarity', 'keywords_match',
  'recency_score', 'company_size_fit', 'resume_completeness', 'certifications_match',
];

const NUM_FEATURES = FEATURE_NAMES.length;
const MODEL_VERSION = '3.0.0';

const WEIGHTS = {
  skills_match_ratio: 0.25, experience_years: 0.15, education_match: 0.08,
  location_match: 0.10, salary_match: 0.08, industry_experience: 0.08,
  job_title_similarity: 0.12, keywords_match: 0.06, recency_score: 0.02,
  company_size_fit: 0.02, resume_completeness: 0.02, certifications_match: 0.02,
};

class CallbackPredictorModel {
  constructor() { this.isReady = false; }

  async initialize() { this.isReady = true; return true; }

  normalizeFeatures(raw) {
    return {
      skills_match_ratio: Math.min(1, Math.max(0, raw.skills_match_ratio || 0)),
      experience_years: Math.min(1, (raw.experience_years || 0) / 20),
      education_match: Math.min(1, Math.max(0, raw.education_match || 0)),
      location_match: raw.location_match ? 1 : 0,
      salary_match: Math.min(1, Math.max(0, raw.salary_match || 0.5)),
      industry_experience: raw.industry_experience ? 1 : 0,
      job_title_similarity: Math.min(1, Math.max(0, raw.job_title_similarity || 0)),
      keywords_match: Math.min(1, Math.max(0, raw.keywords_match || 0)),
      recency_score: Math.min(1, Math.max(0, raw.recency_score || 1)),
      company_size_fit: Math.min(1, Math.max(0, raw.company_size_fit || 0.5)),
      resume_completeness: Math.min(1, Math.max(0, raw.resume_completeness || 0)),
      certifications_match: Math.min(1, Math.max(0, raw.certifications_match || 0)),
    };
  }

  async predict(features) {
    if (!this.isReady) await this.initialize();
    const norm = this.normalizeFeatures(features);
    let score = 0;
    for (const [key, weight] of Object.entries(WEIGHTS)) {
      score += (norm[key] || 0) * weight;
    }
    const probability = 1 / (1 + Math.exp(-8 * (score - 0.45)));
    const completeness = Object.values(norm).filter(v => v > 0).length / NUM_FEATURES;
    const confidence = 0.5 + completeness * 0.5;
    return {
      probability: Math.round(probability * 100),
      confidence: Math.round(confidence * 100),
      category: probability >= 0.7 ? 'high' : probability >= 0.4 ? 'medium' : 'low',
      features: norm,
      modelVersion: MODEL_VERSION,
    };
  }

  async getFeatureImportance() {
    const total = Object.values(WEIGHTS).reduce((a, b) => a + b, 0);
    const imp = {};
    for (const [k, v] of Object.entries(WEIGHTS)) imp[k] = Math.round((v / total) * 100);
    return imp;
  }

  extractMatchFeatures(resume, job) {
    const rSkills = (resume.skills || []).map(s => s.toLowerCase());
    const jSkills = (job.required_skills || job.skills || []).map(s => s.toLowerCase());
    const matched = rSkills.filter(s => jSkills.includes(s));
    const skills_match_ratio = jSkills.length > 0 ? matched.length / jSkills.length : 0.5;
    const rExp = resume.experience_years || resume.years_experience || 0;
    const jExp = job.min_experience || job.experience_required || 0;
    const rTitle = (resume.current_title || resume.job_title || '').toLowerCase().split(/\s+/);
    const jTitle = (job.title || '').toLowerCase().split(/\s+/);
    const titleOverlap = rTitle.filter(w => jTitle.includes(w)).length;
    const rLoc = (resume.location || resume.preferred_location || '').toLowerCase();
    const jLoc = (job.location || '').toLowerCase();
    const fields = ['skills', 'experience', 'education', 'summary', 'contact'];
    const filled = fields.filter(f => resume[f] && (Array.isArray(resume[f]) ? resume[f].length > 0 : true));
    return {
      skills_match_ratio, experience_years: Math.min(rExp / Math.max(jExp, 1), 1),
      education_match: resume.education ? 0.7 : 0.3,
      location_match: jLoc.includes('remote') || rLoc.includes(jLoc) || jLoc.includes(rLoc) ? 1 : 0.5,
      salary_match: 0.7, industry_experience: 0.6,
      job_title_similarity: jTitle.length > 0 ? titleOverlap / jTitle.length : 0.5,
      keywords_match: skills_match_ratio * 0.8, recency_score: 1.0,
      company_size_fit: 0.6, resume_completeness: filled.length / fields.length,
      certifications_match: (resume.certifications?.length || 0) > 0 ? 0.7 : 0.3,
    };
  }

  async analyzeMatch(resume, job) {
    const features = this.extractMatchFeatures(resume, job);
    const prediction = await this.predict(features);
    const importance = await this.getFeatureImportance();
    return { ...prediction, featureImportance: importance, recommendations: this.generateRecommendations(features, prediction), matchBreakdown: features };
  }

  generateRecommendations(features, prediction) {
    const recs = [];
    if (features.skills_match_ratio < 0.5) recs.push({ type: 'skills', priority: 'high', message: 'Your skills match is below average. Highlight relevant skills.' });
    if (features.resume_completeness < 0.7) recs.push({ type: 'profile', priority: 'medium', message: 'Complete your profile to increase visibility.' });
    if (features.job_title_similarity < 0.3) recs.push({ type: 'title', priority: 'medium', message: 'Consider tailoring your resume title to match the role.' });
    if (features.experience_years < 0.5) recs.push({ type: 'experience', priority: 'low', message: 'Highlight relevant projects or transferable skills.' });
    if (prediction.probability < 40) recs.push({ type: 'general', priority: 'high', message: 'Consider looking for roles that better align with your profile.' });
    return recs;
  }

  getModelInfo() {
    return { version: MODEL_VERSION, features: FEATURE_NAMES, numFeatures: NUM_FEATURES, architecture: ['Weighted Scoring Model (no ML dependency)'], isReady: this.isReady };
  }

  dispose() { this.isReady = false; }
}

export const callbackPredictor = new CallbackPredictorModel();
export { CallbackPredictorModel, FEATURE_NAMES, NUM_FEATURES, MODEL_VERSION };
