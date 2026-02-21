/**
 * Public Application Form Page
 * Allows external candidates to apply via shareable link
 */
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  Briefcase, MapPin, DollarSign, Building2, Clock, Upload,
  Send, CheckCircle, FileText, Link2, User, Mail, Phone,
  Linkedin, Globe, ArrowLeft, Loader2, AlertCircle
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { useTranslation } from "@/utils/i18n";
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

export default function PublicApplicationPage() {
  const { token } = useParams();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);
  const [jobDetails, setJobDetails] = useState(null);
  const [trackingInfo, setTrackingInfo] = useState(null);
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    linkedin_url: '',
    portfolio_url: '',
    cover_letter: '',
    resume_url: ''
  });

  useEffect(() => {
    loadApplicationForm();
  }, [token]);

  const loadApplicationForm = async () => {
    try {
      const response = await axios.get(`${API}/api/ats/apply/${token}`);
      setJobDetails(response.data);
      setError(null);
    } catch (err) {
      if (err.response?.status === 404) {
        setError('This application link is invalid or has been deactivated.');
      } else if (err.response?.status === 410) {
        setError(err.response.data.detail || 'This application link has expired.');
      } else {
        setError('Unable to load application form. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name || !formData.email) {
      toast.error('Please fill in your name and email');
      return;
    }
    
    setSubmitting(true);
    
    try {
      const response = await axios.post(`${API}/api/ats/apply/${token}`, formData);
      setSubmitted(true);
      setTrackingInfo(response.data);
      toast.success('Application submitted successfully!');
    } catch (err) {
      if (err.response?.status === 409) {
        toast.error('You have already applied for this position');
      } else {
        toast.error(err.response?.data?.detail || 'Failed to submit application');
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-turquoise mx-auto" />
          <p className="mt-4 text-muted-foreground">Loading application form...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardContent className="pt-8 pb-8 text-center">
            <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-bold mb-2">Application Unavailable</h2>
            <p className="text-muted-foreground mb-6">{error}</p>
            <Button onClick={() => navigate('/')} variant="outline">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Go to MedMatch-AI KARAU
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (submitted && trackingInfo) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center p-4">
        <Card className="max-w-lg w-full">
          <CardContent className="pt-8 pb-8 text-center">
            <div className="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="h-10 w-10 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold mb-2">Application Submitted!</h2>
            <p className="text-muted-foreground mb-6">
              Your application for <strong>{jobDetails?.job?.title}</strong> at{' '}
              <strong>{jobDetails?.job?.company}</strong> has been received.
            </p>
            
            <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4 mb-6">
              <p className="text-sm text-muted-foreground mb-2">Track your application:</p>
              <code className="text-xs break-all text-turquoise">
                {trackingInfo.tracking_url}
              </code>
              <Button
                variant="outline"
                size="sm"
                className="mt-3 w-full"
                onClick={() => {
                  navigator.clipboard.writeText(trackingInfo.tracking_url);
                  toast.success('Tracking link copied!');
                }}
              >
                Copy Tracking Link
              </Button>
            </div>
            
            <p className="text-sm text-muted-foreground">
              A confirmation email has been sent to <strong>{formData.email}</strong>
            </p>
            
            <div className="mt-8 flex gap-3 justify-center">
              <Button onClick={() => navigate('/')}>
                Browse More Jobs
              </Button>
              <Button variant="outline" onClick={() => window.open(trackingInfo.tracking_url, '_blank')}>
                Track Application
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const job = jobDetails?.job;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 py-8 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-turquoise mb-2">MedMatch-AI KARAU</h1>
          <p className="text-muted-foreground">Life Sciences & Engineering Talent Ecosystem</p>
        </div>

        {/* Job Card */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-start gap-4">
              <div className="p-3 rounded-xl bg-turquoise/10">
                <Briefcase className="h-8 w-8 text-turquoise" />
              </div>
              <div className="flex-1">
                <CardTitle className="text-2xl">{job?.title}</CardTitle>
                <div className="flex items-center gap-2 mt-2 text-muted-foreground">
                  <Building2 className="h-4 w-4" />
                  <span className="font-medium">{job?.company}</span>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3 mb-4">
              {job?.location && (
                <Badge variant="outline" className="gap-1">
                  <MapPin className="h-3 w-3" />
                  {job.location}
                </Badge>
              )}
              {job?.salary && (
                <Badge variant="outline" className="gap-1">
                  <DollarSign className="h-3 w-3" />
                  {job.salary}
                </Badge>
              )}
            </div>
            
            {job?.tags?.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-4">
                {job.tags.map((tag, idx) => (
                  <Badge key={idx} className="bg-turquoise/10 text-turquoise">
                    {tag}
                  </Badge>
                ))}
              </div>
            )}
            
            {job?.description && (
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <p className="text-muted-foreground whitespace-pre-wrap">
                  {job.description.slice(0, 500)}
                  {job.description.length > 500 && '...'}
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Application Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-turquoise" />
              Apply for this Position
            </CardTitle>
            <CardDescription>
              Fill out the form below to submit your application
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Basic Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="name" className="flex items-center gap-1">
                    <User className="h-4 w-4" />
                    Full Name *
                  </Label>
                  <Input
                    id="name"
                    placeholder="John Doe"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="email" className="flex items-center gap-1">
                    <Mail className="h-4 w-4" />
                    Email *
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="john@example.com"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="phone" className="flex items-center gap-1">
                    <Phone className="h-4 w-4" />
                    Phone Number
                  </Label>
                  <Input
                    id="phone"
                    type="tel"
                    placeholder="+1 (555) 123-4567"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  />
                </div>
                <div>
                  <Label htmlFor="linkedin" className="flex items-center gap-1">
                    <Linkedin className="h-4 w-4" />
                    LinkedIn Profile
                  </Label>
                  <Input
                    id="linkedin"
                    type="url"
                    placeholder="https://linkedin.com/in/yourprofile"
                    value={formData.linkedin_url}
                    onChange={(e) => setFormData({ ...formData, linkedin_url: e.target.value })}
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="portfolio" className="flex items-center gap-1">
                  <Globe className="h-4 w-4" />
                  Portfolio / Website
                </Label>
                <Input
                  id="portfolio"
                  type="url"
                  placeholder="https://yourportfolio.com"
                  value={formData.portfolio_url}
                  onChange={(e) => setFormData({ ...formData, portfolio_url: e.target.value })}
                />
              </div>

              {jobDetails?.require_resume && (
                <div>
                  <Label htmlFor="resume" className="flex items-center gap-1">
                    <Upload className="h-4 w-4" />
                    Resume Link
                  </Label>
                  <Input
                    id="resume"
                    type="url"
                    placeholder="Link to your resume (Google Drive, Dropbox, etc.)"
                    value={formData.resume_url}
                    onChange={(e) => setFormData({ ...formData, resume_url: e.target.value })}
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Paste a link to your resume hosted on Google Drive, Dropbox, or similar service
                  </p>
                </div>
              )}

              <div>
                <Label htmlFor="cover_letter" className="flex items-center gap-1">
                  <FileText className="h-4 w-4" />
                  Cover Letter / Message
                </Label>
                <Textarea
                  id="cover_letter"
                  placeholder="Tell us why you're a great fit for this role..."
                  rows={5}
                  value={formData.cover_letter}
                  onChange={(e) => setFormData({ ...formData, cover_letter: e.target.value })}
                />
              </div>

              {/* Custom Questions */}
              {jobDetails?.custom_questions?.map((question, idx) => (
                <div key={idx}>
                  <Label>{question.question}</Label>
                  {question.type === 'textarea' ? (
                    <Textarea
                      placeholder={question.placeholder || 'Your answer...'}
                      onChange={(e) => setFormData({
                        ...formData,
                        custom_answers: {
                          ...formData.custom_answers,
                          [question.id || idx]: e.target.value
                        }
                      })}
                    />
                  ) : (
                    <Input
                      placeholder={question.placeholder || 'Your answer...'}
                      onChange={(e) => setFormData({
                        ...formData,
                        custom_answers: {
                          ...formData.custom_answers,
                          [question.id || idx]: e.target.value
                        }
                      })}
                    />
                  )}
                </div>
              ))}

              <Button
                type="submit"
                className="w-full gap-2"
                size="lg"
                disabled={submitting}
              >
                {submitting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4" />
                    Submit Application
                  </>
                )}
              </Button>

              <p className="text-xs text-center text-muted-foreground">
                By submitting, you agree to MedMatch-AI KARAU's Terms of Service and Privacy Policy
              </p>
            </form>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-8 text-sm text-muted-foreground">
          <p>Powered by <span className="text-turquoise font-semibold">MedMatch-AI KARAU</span></p>
          <p className="mt-1">Life Sciences & Engineering Talent Ecosystem</p>
        </div>
      </div>
    </div>
  );
}
