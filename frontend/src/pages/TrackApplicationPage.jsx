/**
import { useTranslation } from "@/utils/i18n";
 * Track Application Page
 * Allows candidates to track their application status via tracking link
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  CheckCircle, Clock, Calendar, AlertCircle, Briefcase, Building2,
  ArrowLeft, Loader2, Mail, RefreshCw
} from 'lucide-react';
import { Card, CardContent, CardHeader } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

// Status configurations with icons and colors
const STATUS_CONFIG = {
  received: {
    icon: Mail,
    color: 'bg-blue-500',
    bgColor: 'bg-blue-50 dark:bg-blue-950',
    textColor: 'text-blue-700 dark:text-blue-300'
  },
  under_review: {
    icon: Clock,
    color: 'bg-purple-500',
    bgColor: 'bg-purple-50 dark:bg-purple-950',
    textColor: 'text-purple-700 dark:text-purple-300'
  },
  shortlisted: {
    icon: CheckCircle,
    color: 'bg-emerald-500',
    bgColor: 'bg-emerald-50 dark:bg-emerald-950',
    textColor: 'text-emerald-700 dark:text-emerald-300'
  },
  interview_scheduled: {
    icon: Calendar,
    color: 'bg-amber-500',
    bgColor: 'bg-amber-50 dark:bg-amber-950',
    textColor: 'text-amber-700 dark:text-amber-300'
  },
  interview_completed: {
    icon: CheckCircle,
    color: 'bg-indigo-500',
    bgColor: 'bg-indigo-50 dark:bg-indigo-950',
    textColor: 'text-indigo-700 dark:text-indigo-300'
  },
  offer_extended: {
    icon: CheckCircle,
    color: 'bg-green-600',
    bgColor: 'bg-green-50 dark:bg-green-950',
    textColor: 'text-green-700 dark:text-green-300'
  },
  hired: {
    icon: CheckCircle,
    color: 'bg-teal-500',
    bgColor: 'bg-teal-50 dark:bg-teal-950',
    textColor: 'text-teal-700 dark:text-teal-300'
  },
  application_deferred: {
    icon: Clock,
    color: 'bg-orange-500',
    bgColor: 'bg-orange-50 dark:bg-orange-950',
    textColor: 'text-orange-700 dark:text-orange-300'
  },
  not_selected: {
    icon: AlertCircle,
    color: 'bg-slate-500',
    bgColor: 'bg-slate-50 dark:bg-slate-800',
    textColor: 'text-slate-700 dark:text-slate-300'
  },
  position_closed: {
    icon: AlertCircle,
    color: 'bg-slate-400',
    bgColor: 'bg-slate-50 dark:bg-slate-800',
    textColor: 'text-slate-600 dark:text-slate-400'
  },
  withdrawn: {
    icon: AlertCircle,
    color: 'bg-gray-500',
    bgColor: 'bg-gray-50 dark:bg-gray-800',
    textColor: 'text-gray-700 dark:text-gray-300'
  }
};

export default function TrackApplicationPage() {
  const { applicationId } = useParams();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [application, setApplication] = useState(null);

  const loadApplication = useCallback(async (showRefresh = false) => {
    if (showRefresh) setRefreshing(true);
    else setLoading(true);
    
    try {
      const params = token ? `?token=${token}` : '';
      const response = await axios.get(`${API}/api/ats/track/${applicationId}${params}`);
      setApplication(response.data);
      setError(null);
      if (showRefresh) toast.success('Application status refreshed');
    } catch (err) {
      if (err.response?.status === 404) {
        setError('Application not found. Please check your tracking link.');
      } else {
        setError('Unable to load application status. Please try again later.');
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [applicationId, token]);

  useEffect(() => {
    loadApplication();
  }, [loadApplication]);

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-turquoise mx-auto" />
          <p className="mt-4 text-muted-foreground">Loading application status...</p>
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
            <h2 className="text-xl font-bold mb-2">Unable to Track Application</h2>
            <p className="text-muted-foreground mb-6">{error}</p>
            <Button onClick={() => navigate('/')} variant="outline">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Go to MedMatch
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const statusConfig = STATUS_CONFIG[application?.status] || STATUS_CONFIG.received;
  const StatusIcon = statusConfig.icon;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-turquoise mb-2">MedMatch</h1>
          <p className="text-muted-foreground">Application Tracker</p>
        </div>

        {/* Status Card */}
        <Card className="mb-6 overflow-hidden">
          <div className={`${statusConfig.color} h-2`} />
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <Badge className={`${statusConfig.bgColor} ${statusConfig.textColor} border-0`}>
                {application?.status_emoji} {application?.status_label}
              </Badge>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => loadApplication(true)}
                disabled={refreshing}
              >
                <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className={`${statusConfig.bgColor} rounded-lg p-6 text-center mb-6`}>
              <div className={`w-16 h-16 rounded-full ${statusConfig.color} flex items-center justify-center mx-auto mb-4`}>
                <StatusIcon className="h-8 w-8 text-white" />
              </div>
              <h2 className={`text-xl font-bold ${statusConfig.textColor}`}>
                {application?.status_label}
              </h2>
              <p className="text-muted-foreground mt-2">
                {application?.status_description}
              </p>
            </div>

            {/* Job Info */}
            <div className="border rounded-lg p-4 mb-6">
              <div className="flex items-start gap-3">
                <div className="p-2 rounded-lg bg-turquoise/10">
                  <Briefcase className="h-5 w-5 text-turquoise" />
                </div>
                <div>
                  <h3 className="font-semibold">{application?.job_title || 'Position'}</h3>
                  <p className="text-sm text-muted-foreground flex items-center gap-1">
                    <Building2 className="h-3 w-3" />
                    {application?.company || 'Company'}
                  </p>
                </div>
              </div>
            </div>

            {/* Timeline */}
            <div className="mb-6">
              <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wider mb-4">
                Application Timeline
              </h3>
              <div className="space-y-4">
                {application?.status_history?.map((event, idx) => {
                  const eventConfig = STATUS_CONFIG[event.status] || STATUS_CONFIG.received;
                  const EventIcon = eventConfig.icon;
                  const isLatest = idx === application.status_history.length - 1;
                  
                  return (
                    <div key={idx} className="flex gap-3">
                      <div className="flex flex-col items-center">
                        <div className={`w-8 h-8 rounded-full ${isLatest ? eventConfig.color : 'bg-slate-200 dark:bg-slate-700'} flex items-center justify-center`}>
                          <EventIcon className={`h-4 w-4 ${isLatest ? 'text-white' : 'text-slate-500'}`} />
                        </div>
                        {idx < application.status_history.length - 1 && (
                          <div className="w-0.5 h-8 bg-slate-200 dark:bg-slate-700" />
                        )}
                      </div>
                      <div className="flex-1 pb-2">
                        <p className={`font-medium ${isLatest ? eventConfig.textColor : 'text-slate-500'}`}>
                          {STATUS_CONFIG[event.status]?.icon ? event.status.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ') : event.status}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {formatDate(event.timestamp)}
                        </p>
                        {event.message && (
                          <p className="text-sm text-muted-foreground mt-1 italic">
                            &ldquo;{event.message}&rdquo;
                          </p>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Key Dates */}
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-3">
                <p className="text-muted-foreground">Applied On</p>
                <p className="font-medium">{formatDate(application?.applied_at)}</p>
              </div>
              <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-3">
                <p className="text-muted-foreground">Last Updated</p>
                <p className="font-medium">{formatDate(application?.last_updated)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button onClick={() => navigate('/search')} variant="outline">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Browse More Jobs
          </Button>
          <Button onClick={() => navigate('/')}>
            Go to Dashboard
          </Button>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-sm text-muted-foreground">
          <p>Application ID: <span className="font-mono text-xs">{application?.application_id}</span></p>
          <p className="mt-2">Powered by <span className="text-turquoise font-semibold">MedMatch</span></p>
        </div>
      </div>
    </div>
  );
}
