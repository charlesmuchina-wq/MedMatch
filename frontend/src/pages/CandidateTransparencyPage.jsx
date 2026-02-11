/**
 * Job Seeker AI Transparency Page
 * Shows candidate rights, AI notice, and allows opt-out/explanation requests
 * Compliant with EU AI Act, NYC LL 144, California AEDT
 */
import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';
import {
  Shield,
  Eye,
  FileText,
  AlertCircle,
  CheckCircle,
  Info,
  Scale,
  UserCheck,
  MessageSquare,
  Download,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Lock,
  Globe,
  HelpCircle
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '../components/ui/dialog';
import { Textarea } from '../components/ui/textarea';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

export default function CandidateTransparencyPage() {
  const [loading, setLoading] = useState(true);
  const [notice, setNotice] = useState(null);
  const [candidateView, setCandidateView] = useState(null);
  const [expandedSections, setExpandedSections] = useState({});
  const [showOptOutDialog, setShowOptOutDialog] = useState(false);
  const [showExplanationDialog, setShowExplanationDialog] = useState(false);
  const [optOutReason, setOptOutReason] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [noticeRes, viewRes] = await Promise.all([
        fetch(`${API_URL}/api/ai-compliance/candidate/transparency-notice`).then(r => r.json()),
        fetch(`${API_URL}/api/ai-compliance/candidate/dashboard?candidate_id=current`).then(r => r.json()),
      ]);
      setNotice(noticeRes);
      setCandidateView(viewRes);
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Failed to load transparency information');
    } finally {
      setLoading(false);
    }
  };

  const toggleSection = (idx) => {
    setExpandedSections(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  const handleOptOut = async () => {
    setSubmitting(true);
    try {
      const response = await fetch(`${API_URL}/api/ai-compliance/candidate/opt-out`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ candidate_id: 'current', reason: optOutReason })
      });
      const result = await response.json();
      toast.success('Opt-out request submitted successfully');
      setShowOptOutDialog(false);
      setOptOutReason('');
    } catch (error) {
      toast.error('Failed to submit opt-out request');
    } finally {
      setSubmitting(false);
    }
  };

  const handleExplanationRequest = async () => {
    setSubmitting(true);
    try {
      const response = await fetch(`${API_URL}/api/ai-compliance/candidate/request-explanation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ candidate_id: 'current', assessment_id: 'latest' })
      });
      const result = await response.json();
      toast.success('Explanation request submitted');
      setShowExplanationDialog(false);
    } catch (error) {
      toast.error('Failed to submit request');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin h-8 w-8 border-4 border-turquoise border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6 max-w-4xl mx-auto" data-testid="candidate-transparency-page">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="flex justify-center mb-4">
          <div className="p-4 rounded-full bg-turquoise/10">
            <Shield className="h-12 w-12 text-turquoise" />
          </div>
        </div>
        <h1 className="text-2xl font-bold">AI Transparency & Your Rights</h1>
        <p className="text-muted-foreground mt-2">
          Understanding how AI is used in your job application process
        </p>
      </div>

      {/* Compliance Badges */}
      <div className="flex flex-wrap justify-center gap-2 mb-6">
        {notice?.compliance_standards?.map((standard) => (
          <Badge key={standard} variant="outline" className="text-xs">
            {standard}
          </Badge>
        ))}
      </div>

      {/* Your Rights Card */}
      <Card className="border-2 border-turquoise/30">
        <CardHeader className="bg-turquoise/5">
          <CardTitle className="flex items-center gap-2">
            <Scale className="h-5 w-5 text-turquoise" />
            Your Rights
          </CardTitle>
          <CardDescription>
            As a job seeker, you have the following rights regarding AI-assisted evaluation
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="grid gap-4">
            {candidateView?.your_rights?.map((right, idx) => (
              <div key={idx} className="flex items-start gap-4 p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                <div className="p-2 rounded-lg bg-turquoise/10">
                  <CheckCircle className="h-5 w-5 text-turquoise" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium">{right.right}</h3>
                  <p className="text-sm text-muted-foreground mt-1">{right.description}</p>
                </div>
                {right.action_url && (
                  <Button variant="outline" size="sm" onClick={() => {
                    if (right.right.includes('Opt-Out')) setShowOptOutDialog(true);
                    else if (right.right.includes('Explanation')) setShowExplanationDialog(true);
                  }}>
                    Request
                  </Button>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* AI Transparency Notice */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-turquoise" />
            {notice?.template?.title}
          </CardTitle>
          <CardDescription>
            Version {notice?.version} • Effective {notice?.effective_date}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {notice?.template?.sections?.map((section, idx) => (
              <div key={idx} className="border rounded-lg overflow-hidden">
                <button
                  onClick={() => toggleSection(idx)}
                  className="w-full p-4 flex items-center justify-between hover:bg-muted/50 transition-colors text-left"
                >
                  <span className="font-medium">{section.heading}</span>
                  {expandedSections[idx] ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                </button>
                {expandedSections[idx] && (
                  <div className="px-4 pb-4 bg-muted/30">
                    <p className="text-sm text-muted-foreground mb-3">{section.content}</p>
                    {section.items && (
                      <ul className="list-disc list-inside space-y-1 text-sm">
                        {section.items.map((item, iidx) => (
                          <li key={iidx} className="text-muted-foreground">{item}</li>
                        ))}
                      </ul>
                    )}
                    {section.audit_info && (
                      <div className="mt-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <p className="text-sm"><strong>Most Recent Audit:</strong> {section.audit_info.most_recent_audit_date}</p>
                        <p className="text-sm"><strong>Auditor:</strong> {section.audit_info.auditor}</p>
                        <Button variant="link" size="sm" className="p-0 h-auto mt-1">
                          View Audit Summary <ExternalLink className="h-3 w-3 ml-1" />
                        </Button>
                      </div>
                    )}
                    {section.actions && (
                      <div className="mt-3 flex flex-wrap gap-2">
                        <Button variant="outline" size="sm" onClick={() => setShowOptOutDialog(true)}>
                          Request Opt-Out
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => setShowExplanationDialog(true)}>
                          Request Explanation
                        </Button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Your AI Assessments */}
      {candidateView?.ai_assessments?.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="h-5 w-5 text-turquoise" />
              Your AI Assessments
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {candidateView.ai_assessments.map((assessment, idx) => (
                <div key={idx} className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <p className="font-medium">{assessment.job_title}</p>
                    <p className="text-sm text-muted-foreground">{assessment.company} • {assessment.assessment_date}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge variant="outline">{assessment.status}</Badge>
                    {assessment.explanation_available && (
                      <Button variant="outline" size="sm" onClick={() => setShowExplanationDialog(true)}>
                        View Explanation
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Human Review Guarantee */}
      <Card className="bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <UserCheck className="h-12 w-12 text-green-600" />
            <div>
              <h3 className="font-semibold text-green-800 dark:text-green-400">Human Review Guarantee</h3>
              <p className="text-sm text-green-700 dark:text-green-500">
                All AI recommendations are reviewed by a human recruiter before any employment decision is made.
                You will never be rejected solely based on an AI assessment.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Contact Information */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <HelpCircle className="h-8 w-8 text-muted-foreground" />
            <div>
              <h3 className="font-medium">Questions?</h3>
              <p className="text-sm text-muted-foreground">
                Contact our Data Protection Officer at{' '}
                <a href="mailto:privacy@medmatch.com" className="text-turquoise hover:underline">
                  privacy@medmatch.com
                </a>
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Opt-Out Dialog */}
      <Dialog open={showOptOutDialog} onOpenChange={setShowOptOutDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Request Alternative Evaluation Process</DialogTitle>
            <DialogDescription>
              You have the right to opt out of AI-assisted evaluation. A member of our team will contact you
              to arrange an alternative selection process.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <label className="text-sm font-medium">Reason (optional)</label>
            <Textarea
              value={optOutReason}
              onChange={(e) => setOptOutReason(e.target.value)}
              placeholder="Please share why you'd prefer an alternative process..."
              className="mt-2"
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowOptOutDialog(false)}>Cancel</Button>
            <Button onClick={handleOptOut} disabled={submitting}>
              {submitting ? 'Submitting...' : 'Submit Request'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Explanation Request Dialog */}
      <Dialog open={showExplanationDialog} onOpenChange={setShowExplanationDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Request Decision Explanation</DialogTitle>
            <DialogDescription>
              Under the EU AI Act and California law, you have the right to understand how AI influenced
              decisions about your application.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-4">
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <h4 className="font-medium mb-2">What you'll receive:</h4>
              <ul className="list-disc list-inside text-sm space-y-1 text-muted-foreground">
                <li>Key factors that influenced the AI assessment</li>
                <li>How your skills and experience were weighted</li>
                <li>The confidence level of the AI recommendation</li>
                <li>Information about human review status</li>
              </ul>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowExplanationDialog(false)}>Cancel</Button>
            <Button onClick={handleExplanationRequest} disabled={submitting}>
              {submitting ? 'Submitting...' : 'Request Explanation'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
