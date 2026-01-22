import { useState, useEffect } from "react";
import { toast } from "sonner";
import { 
  CreditCard, Calendar, Clock, AlertCircle, CheckCircle, 
  XCircle, RefreshCw, ExternalLink, Download, Loader2,
  ChevronDown, ChevronUp, Shield
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import api from "@/utils/apiClient";

const API = process.env.REACT_APP_BACKEND_URL;

const SubscriptionManager = ({ user }) => {
  const [subscription, setSubscription] = useState(null);
  const [billingHistory, setBillingHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    fetchSubscription();
    fetchBillingHistory();
  }, []);

  const fetchSubscription = async () => {
    try {
      const response = await api.client.get(`${API}/api/payments/subscription`);
      setSubscription(response.data);
    } catch (e) {
      console.error("Failed to fetch subscription:", e);
    }
    setLoading(false);
  };

  const fetchBillingHistory = async () => {
    try {
      const response = await api.client.get(`${API}/api/payments/billing-history`);
      setBillingHistory(response.data.stripe_invoices || []);
    } catch (e) {
      console.error("Failed to fetch billing history:", e);
    }
  };

  const handleCancelSubscription = async () => {
    setActionLoading(true);
    try {
      const response = await api.client.post(`${API}/api/payments/subscription/cancel`);
      toast.success(response.data.message);
      fetchSubscription();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Failed to cancel subscription");
    }
    setActionLoading(false);
  };

  const handleReactivateSubscription = async () => {
    setActionLoading(true);
    try {
      const response = await api.client.post(`${API}/api/payments/subscription/reactivate`);
      toast.success(response.data.message);
      fetchSubscription();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Failed to reactivate subscription");
    }
    setActionLoading(false);
  };

  const handleUpdatePaymentMethod = async () => {
    setActionLoading(true);
    try {
      const response = await api.client.post(`${API}/api/payments/update-payment-method`);
      if (response.data.url) {
        window.location.href = response.data.url;
      }
    } catch (e) {
      toast.error(e.response?.data?.detail || "Failed to open payment settings");
    }
    setActionLoading(false);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      active: { color: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400", icon: CheckCircle },
      trialing: { color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400", icon: Clock },
      past_due: { color: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400", icon: AlertCircle },
      canceled: { color: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400", icon: XCircle },
      canceling: { color: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400", icon: Clock },
    };
    
    const config = statusConfig[status] || statusConfig.active;
    const Icon = config.icon;
    
    return (
      <Badge className={`${config.color} flex items-center gap-1`}>
        <Icon className="w-3 h-3" />
        {status?.toUpperCase()}
      </Badge>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="w-6 h-6 animate-spin text-violet-500" />
      </div>
    );
  }

  if (!subscription?.has_subscription) {
    return null; // Don't show if no subscription
  }

  return (
    <Card className="border-violet-200 dark:border-violet-800" data-testid="subscription-manager">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Shield className="w-5 h-5 text-violet-500" />
              Subscription Management
            </CardTitle>
            <CardDescription>Manage your Recruiter Pro subscription</CardDescription>
          </div>
          {getStatusBadge(subscription.status)}
        </div>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Current Plan Info */}
        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 bg-violet-50 dark:bg-violet-900/20 rounded-lg">
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-1">Current Plan</p>
            <p className="font-semibold text-slate-900 dark:text-slate-100">
              {subscription.plan} - ${subscription.price}/month
            </p>
          </div>
          
          <div className="p-4 bg-violet-50 dark:bg-violet-900/20 rounded-lg">
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-1">
              {subscription.trial_end && new Date(subscription.trial_end) > new Date() 
                ? "Trial Ends" 
                : "Next Billing Date"}
            </p>
            <p className="font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-violet-500" />
              {subscription.trial_end && new Date(subscription.trial_end) > new Date()
                ? formatDate(subscription.trial_end)
                : formatDate(subscription.current_period_end)}
            </p>
          </div>
        </div>

        {/* Payment Method */}
        {subscription.payment_method && (
          <div className="p-4 border border-slate-200 dark:border-slate-700 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-slate-100 dark:bg-slate-800 rounded-lg flex items-center justify-center">
                  <CreditCard className="w-5 h-5 text-slate-600 dark:text-slate-400" />
                </div>
                <div>
                  <p className="font-medium text-slate-900 dark:text-slate-100 capitalize">
                    {subscription.payment_method.brand} •••• {subscription.payment_method.last4}
                  </p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    Expires {subscription.payment_method.exp_month}/{subscription.payment_method.exp_year}
                  </p>
                </div>
              </div>
              <Button 
                variant="outline" 
                size="sm"
                onClick={handleUpdatePaymentMethod}
                disabled={actionLoading}
              >
                {actionLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Update"}
              </Button>
            </div>
          </div>
        )}

        {/* Cancel Warning */}
        {subscription.cancel_at_period_end && (
          <div className="p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-amber-800 dark:text-amber-200">
                  Subscription ending
                </p>
                <p className="text-sm text-amber-700 dark:text-amber-300">
                  Your subscription will end on {formatDate(subscription.current_period_end)}. 
                  You'll lose access to premium features after this date.
                </p>
                <Button 
                  size="sm" 
                  className="mt-3 bg-amber-600 hover:bg-amber-700"
                  onClick={handleReactivateSubscription}
                  disabled={actionLoading}
                >
                  {actionLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  ) : (
                    <RefreshCw className="w-4 h-4 mr-2" />
                  )}
                  Keep Subscription
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Billing History */}
        <div>
          <button 
            onClick={() => setShowHistory(!showHistory)}
            className="flex items-center justify-between w-full p-3 text-left hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg transition-colors"
          >
            <span className="font-medium text-slate-900 dark:text-slate-100">Billing History</span>
            {showHistory ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
          </button>
          
          {showHistory && (
            <div className="mt-2 space-y-2">
              {billingHistory.length === 0 ? (
                <p className="text-sm text-slate-500 dark:text-slate-400 p-3">
                  No billing history yet
                </p>
              ) : (
                billingHistory.map((invoice, idx) => (
                  <div 
                    key={invoice.invoice_id || idx}
                    className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-lg"
                  >
                    <div>
                      <p className="font-medium text-slate-900 dark:text-slate-100">
                        ${invoice.amount?.toFixed(2)} {invoice.currency?.toUpperCase()}
                      </p>
                      <p className="text-sm text-slate-500 dark:text-slate-400">
                        {formatDate(invoice.paid_at || invoice.period_start)}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={
                        invoice.status === 'paid' 
                          ? 'bg-emerald-100 text-emerald-700' 
                          : 'bg-slate-100 text-slate-700'
                      }>
                        {invoice.status}
                      </Badge>
                      {invoice.invoice_pdf && (
                        <a 
                          href={invoice.invoice_pdf} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="p-1.5 hover:bg-slate-200 dark:hover:bg-slate-700 rounded"
                        >
                          <Download className="w-4 h-4 text-slate-500" />
                        </a>
                      )}
                      {invoice.hosted_invoice_url && (
                        <a 
                          href={invoice.hosted_invoice_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="p-1.5 hover:bg-slate-200 dark:hover:bg-slate-700 rounded"
                        >
                          <ExternalLink className="w-4 h-4 text-slate-500" />
                        </a>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        {/* Actions */}
        {!subscription.cancel_at_period_end && subscription.status !== 'canceled' && (
          <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="outline" className="text-red-600 border-red-200 hover:bg-red-50">
                  Cancel Subscription
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Cancel your subscription?</AlertDialogTitle>
                  <AlertDialogDescription>
                    Your subscription will remain active until the end of your current billing period 
                    ({formatDate(subscription.current_period_end)}). After that, you'll lose access to:
                    <ul className="list-disc list-inside mt-2 space-y-1">
                      <li>Unlimited job postings</li>
                      <li>Advanced candidate search</li>
                      <li>ATS and analytics</li>
                      <li>In-app messaging</li>
                    </ul>
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Keep Subscription</AlertDialogCancel>
                  <AlertDialogAction 
                    onClick={handleCancelSubscription}
                    className="bg-red-600 hover:bg-red-700"
                  >
                    {actionLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Cancel Subscription"}
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default SubscriptionManager;
