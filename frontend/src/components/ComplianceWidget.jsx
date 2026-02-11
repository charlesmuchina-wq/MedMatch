/**
 * ComplianceWidget - Shows compliance alerts and pending reviews
 * Displays on Recruiter Dashboard for real-time compliance monitoring
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Shield, AlertTriangle, CheckCircle, Clock, 
  ChevronRight, RefreshCw, Eye, Globe, Scale
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const SeverityBadge = ({ severity }) => {
  const styles = {
    CRITICAL: 'bg-red-500 text-white',
    HIGH: 'bg-orange-500 text-white',
    MEDIUM: 'bg-yellow-500 text-white',
    LOW: 'bg-blue-500 text-white'
  };
  return <Badge className={styles[severity] || 'bg-gray-500 text-white'}>{severity}</Badge>;
};

export default function ComplianceWidget({ compact = false }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [complianceData, setComplianceData] = useState(null);
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    loadComplianceData();
  }, []);

  const loadComplianceData = async () => {
    setLoading(true);
    try {
      const [summaryRes, alertsRes] = await Promise.all([
        fetch(`${API_URL}/api/compliance-alerts/summary`, { credentials: 'include' }),
        fetch(`${API_URL}/api/compliance-alerts/active`, { credentials: 'include' })
      ]);

      if (summaryRes.ok) {
        const summary = await summaryRes.json();
        setComplianceData(summary);
      }

      if (alertsRes.ok) {
        const alertData = await alertsRes.json();
        setAlerts(alertData.alerts || []);
      }
    } catch (error) {
      console.error('Error loading compliance data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'COMPLIANT': return 'text-green-500';
      case 'ACTION_REQUIRED': return 'text-red-500';
      default: return 'text-yellow-500';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'COMPLIANT': return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'ACTION_REQUIRED': return <AlertTriangle className="h-5 w-5 text-red-500" />;
      default: return <Clock className="h-5 w-5 text-yellow-500" />;
    }
  };

  if (loading) {
    return (
      <Card className="animate-pulse">
        <CardContent className="p-6">
          <div className="h-24 bg-slate-200 dark:bg-slate-700 rounded" />
        </CardContent>
      </Card>
    );
  }

  // Compact version for sidebar or small spaces
  if (compact) {
    return (
      <Card 
        className="cursor-pointer hover:border-turquoise/50 transition-all"
        onClick={() => navigate('/admin/global-compliance')}
        data-testid="compliance-widget-compact"
      >
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${
                complianceData?.compliance_status === 'COMPLIANT' 
                  ? 'bg-green-100 dark:bg-green-900/30' 
                  : 'bg-red-100 dark:bg-red-900/30'
              }`}>
                {getStatusIcon(complianceData?.compliance_status)}
              </div>
              <div>
                <p className="font-medium text-sm">AI Compliance</p>
                <p className={`text-xs ${getStatusColor(complianceData?.compliance_status)}`}>
                  {complianceData?.compliance_status || 'Unknown'}
                </p>
              </div>
            </div>
            {complianceData?.alerts?.total_active > 0 && (
              <Badge variant="destructive" className="text-xs">
                {complianceData.alerts.total_active}
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  // Full widget version
  return (
    <Card data-testid="compliance-widget">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Shield className="h-5 w-5 text-turquoise" />
              AI Compliance Status
            </CardTitle>
            <CardDescription>Real-time compliance monitoring & GUAL</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={loadComplianceData}>
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => navigate('/admin/global-compliance')}
            >
              View All
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Status Banner */}
        <div className={`p-3 rounded-lg flex items-center justify-between ${
          complianceData?.compliance_status === 'COMPLIANT'
            ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
            : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
        }`}>
          <div className="flex items-center gap-3">
            {getStatusIcon(complianceData?.compliance_status)}
            <div>
              <p className={`font-semibold ${getStatusColor(complianceData?.compliance_status)}`}>
                {complianceData?.compliance_status === 'COMPLIANT' 
                  ? 'All Systems Compliant' 
                  : 'Action Required'}
              </p>
              <p className="text-xs text-muted-foreground">
                {complianceData?.gual?.total_entries || 0} GUAL entries logged
              </p>
            </div>
          </div>
          {complianceData?.gual?.pending_reviews > 0 && (
            <Badge variant="outline" className="bg-amber-50 text-amber-700 border-amber-200">
              <Eye className="h-3 w-3 mr-1" />
              {complianceData.gual.pending_reviews} pending review
            </Badge>
          )}
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-3 gap-3">
          <div className="p-3 bg-muted/50 rounded-lg text-center">
            <Globe className="h-5 w-5 mx-auto mb-1 text-turquoise" />
            <p className="text-lg font-bold">15</p>
            <p className="text-xs text-muted-foreground">Regions</p>
          </div>
          <div className="p-3 bg-muted/50 rounded-lg text-center">
            <Scale className="h-5 w-5 mx-auto mb-1 text-blue-500" />
            <p className="text-lg font-bold">28</p>
            <p className="text-xs text-muted-foreground">Laws</p>
          </div>
          <div className="p-3 bg-muted/50 rounded-lg text-center">
            <Shield className="h-5 w-5 mx-auto mb-1 text-green-500" />
            <p className="text-lg font-bold">GUAL</p>
            <p className="text-xs text-muted-foreground">Active</p>
          </div>
        </div>

        {/* Active Alerts */}
        {alerts.length > 0 ? (
          <div className="space-y-2">
            <p className="text-sm font-medium flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-500" />
              Active Alerts ({alerts.length})
            </p>
            <div className="space-y-2 max-h-[150px] overflow-y-auto">
              {alerts.slice(0, 3).map((alert, idx) => (
                <div 
                  key={alert.id || idx}
                  className="p-2 border rounded-lg flex items-center justify-between text-sm hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <SeverityBadge severity={alert.severity} />
                    <span className="truncate text-muted-foreground">
                      {alert.message}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            {alerts.length > 3 && (
              <Button 
                variant="link" 
                size="sm" 
                className="w-full"
                onClick={() => navigate('/admin/global-compliance')}
              >
                View all {alerts.length} alerts
              </Button>
            )}
          </div>
        ) : (
          <div className="text-center py-3 text-sm text-muted-foreground">
            <CheckCircle className="h-8 w-8 mx-auto mb-2 text-green-500/50" />
            <p>No active compliance alerts</p>
          </div>
        )}

        {/* Location Status */}
        {!complianceData?.user_status?.location_set && (
          <div className="p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
            <p className="text-sm text-amber-700 dark:text-amber-400 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" />
              Location not set - required for cross-border compliance
            </p>
            <Button 
              variant="outline" 
              size="sm" 
              className="mt-2 w-full"
              onClick={() => navigate('/location-settings')}
            >
              Set Location
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
