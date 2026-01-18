import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { toast } from "sonner";
import { useTheme } from "@/App";
import { 
  Crown, Check, Sparkles, Shield, Clock, Zap, CreditCard,
  Loader2, Globe, Users, Briefcase, Star, ArrowRight
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useTranslation } from "@/utils/i18n";
import api from "@/utils/apiClient";

const API = process.env.REACT_APP_BACKEND_URL;

const MembershipPage = ({ user }) => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { isDark } = useTheme();
  const { t } = useTranslation();
  const [membership, setMembership] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);

  // Check for payment success
  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    if (sessionId) {
      checkPaymentStatus(sessionId);
    }
  }, [searchParams]);

  useEffect(() => {
    fetchMembershipStatus();
  }, []);

  const fetchMembershipStatus = async () => {
    try {
      const response = await api.client.get(`${API}/api/membership/status`, {
        withCredentials: true
      });
      setMembership(response.data);
    } catch (e) {
      console.error("Failed to fetch membership status");
    }
    setLoading(false);
  };

  const checkPaymentStatus = async (sessionId) => {
    setProcessing(true);
    try {
      // Poll for payment status
      for (let i = 0; i < 5; i++) {
        const response = await axios.get(`${API}/api/payments/status/${sessionId}`, {
          withCredentials: true
        });
        
        if (response.data.payment_status === 'paid') {
          toast.success("🎉 Payment successful! Welcome to MedMatch Premium!");
          fetchMembershipStatus();
          navigate('/membership', { replace: true });
          break;
        } else if (response.data.status === 'expired') {
          toast.error("Payment session expired");
          break;
        }
        
        // Wait 2 seconds before next poll
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    } catch (e) {
      toast.error("Failed to verify payment");
    }
    setProcessing(false);
  };

  const handleUpgrade = async (provider = 'stripe') => {
    setProcessing(true);
    try {
      const endpoint = provider === 'paypal' 
        ? `${API}/api/payments/paypal/create`
        : `${API}/api/payments/create-checkout`;
      
      const response = await axios.post(endpoint, {
        origin_url: window.location.origin
      }, { withCredentials: true });
      
      if (provider === 'paypal' && response.data.approval_url) {
        window.location.href = response.data.approval_url;
      } else if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      } else if (response.data.membership_status === 'active') {
        toast.success("You already have lifetime membership!");
        fetchMembershipStatus();
      }
    } catch (e) {
      toast.error(e.response?.data?.detail || "Failed to start checkout");
    }
    setProcessing(false);
  };

  // Handle PayPal return
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const paymentId = urlParams.get('paymentId');
    const payerId = urlParams.get('PayerID');
    const provider = urlParams.get('provider');
    
    if (provider === 'paypal' && paymentId && payerId) {
      executePayPalPayment(paymentId, payerId);
    }
  }, []);

  const executePayPalPayment = async (paymentId, payerId) => {
    setProcessing(true);
    try {
      const response = await axios.post(`${API}/api/payments/paypal/execute`, {
        paymentId,
        PayerID: payerId
      }, { withCredentials: true });
      
      if (response.data.status === 'success') {
        toast.success("🎉 Payment successful! Welcome to MedMatch Premium!");
        fetchMembershipStatus();
        navigate('/membership', { replace: true });
      }
    } catch (e) {
      toast.error("Payment failed. Please try again.");
    }
    setProcessing(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-turquoise" />
      </div>
    );
  }

  const isRecruiter = membership?.role === 'recruiter';
  const isActive = membership?.membership_status === 'active';
  const isTrial = membership?.membership_status === 'trial';
  const isExpired = membership?.membership_status === 'expired';

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-5xl mx-auto animate-fade-in" data-testid="membership-page">
      {/* Header */}
      <div className="text-center mb-10">
        <div className="w-20 h-20 bg-gradient-to-br from-amber-400 to-orange-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
          <Crown className="w-10 h-10 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100" style={{ fontFamily: 'IBM Plex Sans' }}>
          {isRecruiter ? "Recruiter Account" : "MedMatch Membership"}
        </h1>
        <p className="text-slate-500 dark:text-slate-400 mt-2 max-w-xl mx-auto">
          {isRecruiter 
            ? "Post jobs and find qualified candidates worldwide"
            : "Your gateway to landing your dream remote job"}
        </p>
      </div>

      {/* Current Status Card */}
      <Card className="mb-8 border-2 border-turquoise/30">
        <CardContent className="p-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-4">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                isActive ? 'bg-emerald-100 dark:bg-emerald-900/30' :
                isTrial ? 'bg-amber-100 dark:bg-amber-900/30' :
                'bg-red-100 dark:bg-red-900/30'
              }`}>
                {isActive ? <Check className="w-6 h-6 text-emerald-600" /> :
                 isTrial ? <Clock className="w-6 h-6 text-amber-600" /> :
                 <Shield className="w-6 h-6 text-red-600" />}
              </div>
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-slate-100">
                  {isRecruiter ? "Recruiter (Free Forever)" :
                   isActive ? "Lifetime Member" :
                   isTrial ? "Free Trial" : "Trial Expired"}
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {isRecruiter ? "Post unlimited jobs" :
                   isActive ? "Full access to all features" :
                   isTrial ? `${membership?.days_remaining} days remaining` :
                   "Upgrade to continue"}
                </p>
              </div>
            </div>
            
            <Badge className={`text-sm px-4 py-2 ${
              isActive ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' :
              isTrial ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400' :
              'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
            }`}>
              {isRecruiter ? "FREE" : isActive ? "ACTIVE" : isTrial ? "TRIAL" : "EXPIRED"}
            </Badge>
          </div>

          {isTrial && membership?.days_remaining !== null && (
            <div className="mt-6">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-slate-500 dark:text-slate-400">Trial Progress</span>
                <span className="text-slate-700 dark:text-slate-300">{15 - membership.days_remaining}/15 days used</span>
              </div>
              <Progress value={((15 - membership.days_remaining) / 15) * 100} className="h-2" />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pricing Section - Show only for job seekers who aren't active */}
      {!isRecruiter && !isActive && (
        <div className="grid md:grid-cols-2 gap-6 mb-10">
          {/* Free Trial */}
          <Card className={`${isTrial ? 'border-2 border-amber-400' : ''}`}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-amber-500" />
                Free Trial
              </CardTitle>
              <CardDescription>Try MedMatch for 15 days</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-4">
                $0 <span className="text-sm font-normal text-slate-500">/ 15 days</span>
              </div>
              <ul className="space-y-3">
                {[
                  "Resume upload & parsing",
                  "Job search (limited)",
                  "Save up to 10 jobs",
                  "Basic AI features"
                ].map((feature, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                    <Check className="w-4 h-4 text-emerald-500" /> {feature}
                  </li>
                ))}
              </ul>
              {isTrial && (
                <Button variant="outline" className="w-full mt-6" disabled>
                  Current Plan
                </Button>
              )}
            </CardContent>
          </Card>

          {/* Lifetime Membership */}
          <Card className="border-2 border-turquoise relative overflow-hidden">
            <div className="absolute top-0 right-0 bg-turquoise text-white text-xs px-3 py-1 rounded-bl-lg font-medium">
              BEST VALUE
            </div>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Crown className="w-5 h-5 text-turquoise" />
                Lifetime Membership
              </CardTitle>
              <CardDescription>One payment, forever access</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-4">
                $1 <span className="text-sm font-normal text-slate-500">/ forever</span>
              </div>
              <ul className="space-y-3">
                {[
                  "Unlimited job searches",
                  "All AI features (Cover Letters, Interview Prep)",
                  "Voice & Video Interview Coach",
                  "Application Analytics",
                  "Email Alerts & Daily Digest",
                  "Multiple Resume Profiles",
                  "Priority Support"
                ].map((feature, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                    <Check className="w-4 h-4 text-turquoise" /> {feature}
                  </li>
                ))}
              </ul>
              
              {/* Payment Options */}
              <div className="mt-6 space-y-3">
                <Button 
                  onClick={() => handleUpgrade('stripe')}
                  disabled={processing}
                  className="w-full bg-gradient-to-r from-turquoise to-teal-600 hover:from-teal-600 hover:to-turquoise"
                  data-testid="upgrade-stripe-btn"
                >
                  {processing ? (
                    <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Processing...</>
                  ) : (
                    <><CreditCard className="w-4 h-4 mr-2" /> Pay $1 with Card</>
                  )}
                </Button>
                
                <Button 
                  onClick={() => handleUpgrade('paypal')}
                  disabled={processing}
                  variant="outline"
                  className="w-full border-[#0070ba] text-[#0070ba] hover:bg-[#0070ba]/10"
                  data-testid="upgrade-paypal-btn"
                >
                  {processing ? (
                    <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Processing...</>
                  ) : (
                    <>
                      <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M7.076 21.337H2.47a.641.641 0 0 1-.633-.74L4.944 3.72a.77.77 0 0 1 .757-.629h6.153c2.046 0 3.667.468 4.736 1.371 1.006.85 1.468 2.076 1.338 3.548-.33 3.692-2.898 5.447-6.246 5.447h-1.83a.77.77 0 0 0-.758.628l-.87 5.507a.64.64 0 0 1-.632.54h-.516v1.205zm12.234-14.446c-.395 4.268-3.133 6.38-7.07 6.38h-1.315l-1.026 6.491h2.45l.714-4.515h1.315c3.936 0 6.673-2.112 7.07-6.38.096-1.04-.052-1.89-.427-2.578.34.327.597.738.758 1.238.156.485.234 1.057.234 1.713 0 .257-.012.521-.038.79-.233 2.55-1.553 4.41-3.615 5.346.826-.773 1.397-1.79 1.687-3.036.058-.248.102-.508.133-.779.026-.232.039-.455.039-.667 0-.555-.063-1.044-.187-1.47a3.283 3.283 0 0 0-.722-1.333z"/>
                      </svg>
                      Pay $1 with PayPal
                    </>
                  )}
                </Button>
              </div>
              
              <p className="text-xs text-slate-500 text-center mt-3">
                Secure payment • All currencies accepted worldwide
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Features Grid */}
      <div className="mb-10">
        <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-6 text-center" style={{ fontFamily: 'IBM Plex Sans' }}>
          {isRecruiter ? "Recruiter Features" : "What's Included"}
        </h2>
        <div className="grid md:grid-cols-3 gap-4">
          {(isRecruiter ? [
            { icon: Briefcase, title: "Post Jobs", desc: "Unlimited job postings" },
            { icon: Users, title: "Reach Talent", desc: "Connect with job seekers" },
            { icon: Globe, title: "Worldwide", desc: "Global candidate reach" }
          ] : [
            { icon: Sparkles, title: "AI-Powered", desc: "Smart job matching" },
            { icon: Globe, title: "Worldwide Jobs", desc: "Remote positions globally" },
            { icon: Zap, title: "Quick Apply", desc: "One-click applications" },
            { icon: Shield, title: "Privacy First", desc: "Your data stays yours" },
            { icon: Star, title: "Interview Prep", desc: "AI coaching tools" },
            { icon: CreditCard, title: "One-Time Fee", desc: "No subscriptions" }
          ]).map(({ icon: Icon, title, desc }) => (
            <div key={title} className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg text-center">
              <Icon className="w-8 h-8 text-turquoise mx-auto mb-2" />
              <h4 className="font-medium text-slate-900 dark:text-slate-100">{title}</h4>
              <p className="text-xs text-slate-500 dark:text-slate-400">{desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recruiter Job Posting CTA */}
      {isRecruiter && (
        <Card className="bg-gradient-to-r from-violet-500 to-purple-600 text-white">
          <CardContent className="p-6 flex items-center justify-between flex-wrap gap-4">
            <div>
              <h3 className="text-xl font-semibold mb-1">Ready to find talent?</h3>
              <p className="text-violet-100">Post your first job and reach qualified candidates</p>
            </div>
            <Button 
              variant="secondary"
              onClick={() => navigate('/recruiter/post-job')}
              className="bg-white text-violet-600 hover:bg-violet-50"
            >
              Post a Job <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default MembershipPage;
