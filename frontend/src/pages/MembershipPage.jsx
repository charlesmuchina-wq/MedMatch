import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { toast } from "sonner";
import { useTheme } from "@/App";
import { 
  Crown, Check, Sparkles, Shield, Clock, Zap, CreditCard,
  Loader2, Globe, Users, Briefcase, Star, ArrowRight, Building2
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useTranslation } from "@/utils/i18n";
import api from "@/utils/apiClient";
import SubscriptionManager from "@/components/SubscriptionManager";

const API = process.env.REACT_APP_BACKEND_URL;

const MembershipPage = ({ user }) => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { isDark } = useTheme();
  const { t } = useTranslation();
  const [membership, setMembership] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [isAnnual, setIsAnnual] = useState(false);

  // Check for payment success
  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    const success = searchParams.get('success');
    
    if (sessionId) {
      checkPaymentStatus(sessionId);
    } else if (success === 'true') {
      // If we have success but no session_id, just refresh membership status
      fetchMembershipStatus();
      toast.success("🎉 Payment successful! Welcome to MedMatch-AI KARAU Premium!");
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
        const response = await api.client.get(`${API}/api/payments/status/${sessionId}`);
        
        if (response.data.status === 'success' || response.data.payment_status === 'paid') {
          toast.success("🎉 Payment successful! Welcome to MedMatch-AI KARAU Premium!");
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

  const handleUpgrade = async (provider = 'stripe', plan = 'lifetime') => {
    setProcessing(true);
    try {
      const endpoint = provider === 'paypal' 
        ? `${API}/api/payments/paypal/create`
        : `${API}/api/payments/create-checkout`;
      
      const payload = {
        success_url: `${window.location.origin}/membership?success=true`,
        cancel_url: `${window.location.origin}/membership?canceled=true`,
        plan: plan
      };
      
      const response = await api.client.post(endpoint, payload);
      
      if (provider === 'paypal' && response.data.approval_url) {
        window.location.href = response.data.approval_url;
      } else if (response.data.url) {
        // Stripe returns 'url' for the checkout session
        window.location.href = response.data.url;
      } else if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      } else if (response.data.membership_status === 'active') {
        toast.success("You already have an active membership!");
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
      const response = await api.client.post(`${API}/api/payments/paypal/execute`, {
        payment_id: paymentId,
        payer_id: payerId
      });
      
      if (response.data.success) {
        toast.success("🎉 Payment successful! Welcome to MedMatch-AI KARAU Premium!");
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
  const isActive = membership?.status === 'active' || membership?.membership_status === 'active';
  const isTrial = membership?.status === 'trial' || membership?.membership_status === 'trial';
  const isExpired = membership?.status === 'expired' || membership?.membership_status === 'expired';
  const trialDays = isRecruiter ? 30 : 15;

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-5xl mx-auto animate-fade-in" data-testid="membership-page">
      {/* Header */}
      <div className="text-center mb-10">
        <div className={`w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6 ${
          isRecruiter 
            ? 'bg-gradient-to-br from-violet-500 to-purple-600' 
            : 'bg-gradient-to-br from-amber-400 to-orange-500'
        }`}>
          {isRecruiter ? <Briefcase className="w-10 h-10 text-white" /> : <Crown className="w-10 h-10 text-white" />}
        </div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100" style={{ fontFamily: 'IBM Plex Sans' }}>
          {isRecruiter ? "Recruiter Pro" : "MedMatch-AI KARAU Membership"}
        </h1>
        <p className="text-slate-500 dark:text-slate-400 mt-2 max-w-xl mx-auto">
          {isRecruiter 
            ? "Post jobs, access candidates, and build your dream team"
            : "Your gateway to landing your dream job in life sciences"}
        </p>
      </div>

      {/* Current Status Card */}
      <Card className={`mb-8 border-2 ${isRecruiter ? 'border-violet-500/30' : 'border-turquoise/30'}`}>
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
                  {isRecruiter 
                    ? (isActive ? "Recruiter Pro" : isTrial ? "Free Trial" : "Trial Expired")
                    : (isActive ? "Lifetime Member" : isTrial ? "Free Trial" : "Trial Expired")}
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {isActive 
                    ? (isRecruiter ? "Full access to all recruiter features" : "Full access to all features")
                    : isTrial 
                      ? `${membership?.days_remaining || trialDays} days remaining` 
                      : "Upgrade to continue"}
                </p>
              </div>
            </div>
            
            <Badge className={`text-sm px-4 py-2 ${
              isActive ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' :
              isTrial ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400' :
              'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
            }`}>
              {isActive ? "ACTIVE" : isTrial ? "TRIAL" : "EXPIRED"}
            </Badge>
          </div>

          {isTrial && membership?.days_remaining !== null && (
            <div className="mt-6">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-slate-500 dark:text-slate-400">Trial Progress</span>
                <span className="text-slate-700 dark:text-slate-300">{trialDays - (membership.days_remaining || 0)}/{trialDays} days used</span>
              </div>
              <Progress value={((trialDays - (membership.days_remaining || 0)) / trialDays) * 100} className="h-2" />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recruiter Pricing Section */}
      {isRecruiter && (
        <div className="mb-10">
          {/* 30-Day Trial Banner for Recruiters */}
          {isTrial && (
            <div className="mb-6 p-4 rounded-lg bg-gradient-to-r from-violet-50 to-purple-50 dark:from-violet-900/20 dark:to-purple-900/20 border border-violet-200 dark:border-violet-800">
              <div className="flex items-center gap-3">
                <Clock className="w-6 h-6 text-violet-600" />
                <div>
                  <p className="font-medium text-violet-800 dark:text-violet-200">
                    🎉 You're on a 30-day free trial!
                  </p>
                  <p className="text-sm text-violet-600 dark:text-violet-400">
                    {membership?.days_remaining || 30} days remaining • Full access to all recruiter features
                  </p>
                </div>
              </div>
            </div>
          )}

          <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-2 text-center">
            Choose Your Recruiter Plan
          </h2>
          <p className="text-center text-sm text-slate-500 mb-6">
            All plans include a <span className="font-medium text-violet-600">30-day free trial</span>
          </p>
          
          {/* Billing Toggle */}
          <div className="flex items-center justify-center gap-4 mb-8">
            <span className={`text-sm ${!isAnnual ? 'font-medium text-slate-900 dark:text-slate-100' : 'text-slate-500'}`}>Monthly</span>
            <button
              onClick={() => setIsAnnual(!isAnnual)}
              className={`relative w-14 h-7 rounded-full transition-colors ${isAnnual ? 'bg-turquoise' : 'bg-slate-300'}`}
            >
              <div className={`absolute top-1 w-5 h-5 rounded-full bg-white transition-transform ${isAnnual ? 'translate-x-8' : 'translate-x-1'}`} />
            </button>
            <span className={`text-sm ${isAnnual ? 'font-medium text-slate-900 dark:text-slate-100' : 'text-slate-500'}`}>
              Annual <Badge className="ml-1 bg-emerald-500 text-xs">Save 2 months</Badge>
            </span>
          </div>

          <div className="grid md:grid-cols-4 gap-4">
            {/* Starter Tier */}
            <Card className="border-slate-200">
              <CardHeader className="pb-4">
                <CardTitle className="text-lg">Starter</CardTitle>
                <CardDescription>For small practices</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-1">
                  ${isAnnual ? '2.50' : '2.99'}
                  <span className="text-sm font-normal text-slate-500">/mo</span>
                </div>
                {isAnnual && <p className="text-xs text-emerald-600 mb-4">$29.99 billed annually</p>}
                <div className="text-sm text-slate-600 dark:text-slate-400 mb-4 font-medium">
                  1-5 job postings
                </div>
                <ul className="space-y-2 text-sm">
                  {["5 active job posts", "Basic candidate search", "In-app messaging", "Email support"].map((f, i) => (
                    <li key={i} className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
                      <Check className="w-4 h-4 text-emerald-500" /> {f}
                    </li>
                  ))}
                </ul>
                <Button 
                  onClick={() => handleUpgrade('stripe', isAnnual ? 'recruiter_starter_annual' : 'recruiter_starter')}
                  disabled={processing}
                  variant="outline"
                  className="w-full mt-6"
                >
                  Get Started
                </Button>
              </CardContent>
            </Card>

            {/* Growth Tier */}
            <Card className="border-2 border-turquoise relative">
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <Badge className="bg-turquoise text-white">POPULAR</Badge>
              </div>
              <CardHeader className="pb-4">
                <CardTitle className="text-lg">Growth</CardTitle>
                <CardDescription>For growing teams</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-1">
                  ${isAnnual ? '6.66' : '7.99'}
                  <span className="text-sm font-normal text-slate-500">/mo</span>
                </div>
                {isAnnual && <p className="text-xs text-emerald-600 mb-4">$79.99 billed annually</p>}
                <div className="text-sm text-slate-600 dark:text-slate-400 mb-4 font-medium">
                  5-10 job postings
                </div>
                <ul className="space-y-2 text-sm">
                  {["10 active job posts", "Advanced candidate search", "Blind screening mode", "Analytics dashboard", "Priority support"].map((f, i) => (
                    <li key={i} className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
                      <Check className="w-4 h-4 text-turquoise" /> {f}
                    </li>
                  ))}
                </ul>
                <Button 
                  onClick={() => handleUpgrade('stripe', isAnnual ? 'recruiter_growth_annual' : 'recruiter_growth')}
                  disabled={processing}
                  className="w-full mt-6 bg-turquoise hover:bg-turquoise/90"
                >
                  Get Started
                </Button>
              </CardContent>
            </Card>

            {/* Premium Tier */}
            <Card className="border-violet-200 bg-violet-50/30 dark:bg-violet-900/10">
              <CardHeader className="pb-4">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Crown className="w-5 h-5 text-violet-500" />
                  Premium
                </CardTitle>
                <CardDescription>For large organizations</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-1">
                  ${isAnnual ? '12.50' : '14.99'}
                  <span className="text-sm font-normal text-slate-500">/mo</span>
                </div>
                {isAnnual && <p className="text-xs text-emerald-600 mb-4">$149.99 billed annually</p>}
                <div className="text-sm text-slate-600 dark:text-slate-400 mb-4 font-medium">
                  Unlimited job postings
                </div>
                <ul className="space-y-2 text-sm">
                  {["Unlimited job posts", "Full ATS integration", "Bulk candidate export", "Custom branding", "API access", "Dedicated support"].map((f, i) => (
                    <li key={i} className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
                      <Check className="w-4 h-4 text-violet-500" /> {f}
                    </li>
                  ))}
                </ul>
                <Button 
                  onClick={() => handleUpgrade('stripe', isAnnual ? 'recruiter_premium_annual' : 'recruiter_premium')}
                  disabled={processing}
                  className="w-full mt-6 bg-gradient-to-r from-violet-500 to-purple-600"
                >
                  Get Started
                </Button>
              </CardContent>
            </Card>

            {/* Enterprise Tier */}
            <Card className="border-slate-300 bg-slate-50 dark:bg-slate-800/50">
              <CardHeader className="pb-4">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Building2 className="w-5 h-5 text-slate-600" />
                  Enterprise
                </CardTitle>
                <CardDescription>For hospital networks</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-1">
                  Custom
                </div>
                <p className="text-xs text-slate-500 mb-4">Tailored for 50+ recruiters</p>
                <div className="text-sm text-slate-600 dark:text-slate-400 mb-4 font-medium">
                  Volume discounts
                </div>
                <ul className="space-y-2 text-sm">
                  {["Everything in Premium", "SSO/SAML integration", "Custom SLA", "Dedicated account manager", "On-site training", "HIPAA compliance"].map((f, i) => (
                    <li key={i} className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
                      <Check className="w-4 h-4 text-slate-500" /> {f}
                    </li>
                  ))}
                </ul>
                <Button 
                  variant="outline"
                  onClick={() => window.location.href = 'mailto:enterprise@medmatch.ai?subject=Enterprise%20Inquiry'}
                  className="w-full mt-6"
                >
                  Contact Sales
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Job Seeker Pricing Section */}
      {!isRecruiter && !isActive && (
        <div className="mb-10">
          {/* 30-Day Trial Banner */}
          {isTrial && (
            <div className="mb-6 p-4 rounded-lg bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 border border-amber-200 dark:border-amber-800">
              <div className="flex items-center gap-3">
                <Clock className="w-6 h-6 text-amber-600" />
                <div>
                  <p className="font-medium text-amber-800 dark:text-amber-200">
                    🎉 You're on a 30-day free trial!
                  </p>
                  <p className="text-sm text-amber-600 dark:text-amber-400">
                    {membership?.days_remaining || 30} days remaining • Enjoy full premium access
                  </p>
                </div>
              </div>
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-6">
            {/* Free Forever Tier */}
            <Card className={`${!membership?.tier || membership?.tier === 'free' ? 'border-2 border-slate-300' : ''}`}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-slate-500" />
                  Free Forever
                </CardTitle>
                <CardDescription>Basic job search features</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-4">
                  $0 <span className="text-sm font-normal text-slate-500">/ forever</span>
                </div>
                <ul className="space-y-3">
                  {[
                    "Unlimited job searches",
                    "View job listings",
                    "Save favorite jobs",
                    "Basic email alerts",
                    "Mobile app access"
                  ].map((feature, i) => (
                    <li key={i} className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                      <Check className="w-4 h-4 text-slate-400" /> {feature}
                    </li>
                  ))}
                </ul>
                <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
                  <p className="text-xs text-slate-500">Not included:</p>
                  <ul className="mt-2 space-y-1">
                    {["AI job matching", "Cover letter generator", "Interview prep", "Resume optimization"].map((f, i) => (
                      <li key={i} className="flex items-center gap-2 text-xs text-slate-400">
                        <span className="w-3 h-3 rounded-full border border-slate-300" /> {f}
                      </li>
                    ))}
                  </ul>
                </div>
              </CardContent>
            </Card>

            {/* Premium 3-Year Plan */}
            <Card className="border-2 border-turquoise relative overflow-hidden">
              <div className="absolute top-0 right-0 bg-turquoise text-white text-xs px-3 py-1 rounded-bl-lg font-medium">
                BEST VALUE
              </div>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Crown className="w-5 h-5 text-turquoise" />
                  Premium Membership
                </CardTitle>
                <CardDescription>Full access to all AI-powered features</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-1">
                  $3 <span className="text-sm font-normal text-slate-500">/ 3 years</span>
                </div>
                <p className="text-xs text-emerald-600 mb-4">Just $0.08/month • One-time payment</p>
                <ul className="space-y-3">
                  {[
                    "Everything in Free tier",
                    "AI-powered job matching",
                    "AI Resume Optimization",
                    "Unlimited cover letter generations",
                    "Interview Prep with AI feedback",
                    "Salary Negotiation Coaching",
                    "Priority visibility to recruiters",
                    "Career path recommendations",
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
                    onClick={() => handleUpgrade('stripe', 'job_seeker_3_year')}
                    disabled={processing}
                    className="w-full bg-gradient-to-r from-turquoise to-teal-600 hover:from-teal-600 hover:to-turquoise"
                    data-testid="upgrade-stripe-btn"
                  >
                    {processing ? (
                      <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Processing...</>
                    ) : (
                      <><CreditCard className="w-4 h-4 mr-2" /> Get Premium for $3</>
                    )}
                  </Button>
                  
                  <Button 
                    onClick={() => handleUpgrade('paypal', 'job_seeker_3_year')}
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
                        Pay with PayPal
                      </>
                    )}
                  </Button>
                </div>
                
                <p className="text-xs text-slate-500 text-center mt-3">
                  One-time payment • No recurring fees • 3 years of premium access
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Features Grid */}
      <div className="mb-10">
        <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-6 text-center" style={{ fontFamily: 'IBM Plex Sans' }}>
          {isRecruiter ? "Recruiter Pro Features" : "Premium Features"}
        </h2>
        <div className="grid md:grid-cols-3 gap-4">
          {(isRecruiter ? [
            { icon: Briefcase, title: "Unlimited Jobs", desc: "Post as many jobs as you need" },
            { icon: Users, title: "Candidate Database", desc: "Search qualified candidates" },
            { icon: Globe, title: "Global Reach", desc: "Hire from anywhere" },
            { icon: Star, title: "ATS System", desc: "Track all applicants" },
            { icon: Zap, title: "Quick Hire", desc: "Streamlined hiring process" },
            { icon: Shield, title: "Company Branding", desc: "Showcase your brand" }
          ] : [
            { icon: Sparkles, title: "AI-Powered", desc: "Smart job matching" },
            { icon: Globe, title: "All Locations", desc: "Remote, hybrid & on-site" },
            { icon: Zap, title: "Quick Apply", desc: "One-click applications" },
            { icon: Shield, title: "Privacy First", desc: "Your data stays yours" },
            { icon: Star, title: "Interview Prep", desc: "AI coaching tools" },
            { icon: CreditCard, title: "$3 for 3 Years", desc: "One-time payment" }
          ]).map(({ icon: Icon, title, desc }) => (
            <div key={title} className={`p-4 rounded-lg text-center ${
              isRecruiter ? 'bg-violet-50 dark:bg-violet-900/20' : 'bg-slate-50 dark:bg-slate-800'
            }`}>
              <Icon className={`w-8 h-8 mx-auto mb-2 ${isRecruiter ? 'text-violet-500' : 'text-turquoise'}`} />
              <h4 className="font-medium text-slate-900 dark:text-slate-100">{title}</h4>
              <p className="text-xs text-slate-500 dark:text-slate-400">{desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recruiter Job Posting CTA - Show for active recruiters */}
      {isRecruiter && isActive && (
        <Card className="bg-gradient-to-r from-violet-500 to-purple-600 text-white mb-8">
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

      {/* Subscription Management - Show for recruiters with active subscription */}
      {isRecruiter && isActive && (
        <SubscriptionManager user={user} />
      )}
    </div>
  );
};

export default MembershipPage;
