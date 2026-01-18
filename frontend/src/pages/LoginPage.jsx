import { useState, useEffect, useCallback } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import { useTheme } from "@/App";
import { 
  Mail, Phone, Lock, User, Loader2, ArrowRight, Eye, EyeOff,
  Smartphone, Fingerprint
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Label } from "@/components/ui/label";
import { BiometricLogin, BiometricRegistration } from "@/components/BiometricAuth";

const API = process.env.REACT_APP_BACKEND_URL;

const LoginPage = ({ onAuthSuccess }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isDark } = useTheme();
  
  const [activeTab, setActiveTab] = useState("email");
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isRegister, setIsRegister] = useState(false);
  const [selectedRole, setSelectedRole] = useState("job_seeker"); // job_seeker or recruiter
  
  // Email form
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  
  // Phone form
  const [phoneNumber, setPhoneNumber] = useState("");
  const [otpCode, setOtpCode] = useState("");
  const [otpSent, setOtpSent] = useState(false);

  // Callback handlers defined with useCallback
  const handleGoogleCallback = useCallback(async (sessionId) => {
    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/api/auth/google/session`, 
        { session_id: sessionId },
        { withCredentials: true }
      );
      
      toast.success("Logged in with Google!");
      onAuthSuccess(response.data.user);
      navigate('/');
    } catch (e) {
      toast.error("Google login failed");
    }
    setIsLoading(false);
    // Clear the hash
    window.history.replaceState(null, '', window.location.pathname);
  }, [onAuthSuccess, navigate]);

  const handleAppleCallback = useCallback(async (idToken, code) => {
    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/api/auth/apple/callback`,
        { id_token: idToken, code: code },
        { withCredentials: true }
      );
      
      toast.success("Logged in with Apple!");
      onAuthSuccess(response.data.user);
      navigate('/');
    } catch (e) {
      toast.error(e.response?.data?.detail || "Apple login failed");
    }
    setIsLoading(false);
    // Clear the hash
    window.history.replaceState(null, '', window.location.pathname);
  }, [onAuthSuccess, navigate]);

  // Check for Google OAuth callback (session_id in URL hash)
  // Also check for Apple Sign In callback (id_token in URL hash)
  useEffect(() => {
    const hash = location.hash;
    if (hash) {
      // Google callback
      if (hash.includes('session_id=')) {
        const sessionId = hash.split('session_id=')[1]?.split('&')[0];
        if (sessionId) {
          handleGoogleCallback(sessionId);
        }
      }
      // Apple callback (fragment response mode)
      else if (hash.includes('id_token=')) {
        const params = new URLSearchParams(hash.substring(1));
        const idToken = params.get('id_token');
        const code = params.get('code');
        if (idToken) {
          handleAppleCallback(idToken, code);
        }
      }
    }
  }, [location, handleGoogleCallback, handleAppleCallback]);

  // Check if already authenticated
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await axios.get(`${API}/api/auth/me`, {
          withCredentials: true
        });
        if (response.data?.user_id) {
          onAuthSuccess(response.data);
          navigate('/');
        }
      } catch (e) {
        // Not authenticated, stay on login page
      }
    };
    checkAuth();
  }, [onAuthSuccess, navigate]);

  // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
  const handleGoogleLogin = () => {
    const redirectUrl = window.location.origin + '/login';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  const handleAppleLogin = async () => {
    try {
      // Load Apple Sign In configuration
      const configResponse = await axios.get(`${API}/api/auth/apple/config`);
      const config = configResponse.data;
      
      // For form_post mode, redirect to backend endpoint that will handle the POST
      const redirectUri = `${API}/api/auth/apple/redirect`;
      
      // Build Apple authorization URL
      const params = new URLSearchParams({
        client_id: config.client_id,
        redirect_uri: redirectUri,
        response_type: config.response_type,
        response_mode: config.response_mode,
        scope: config.scope,
        state: Math.random().toString(36).substring(7)
      });
      
      // Redirect to Apple Sign In
      const appleAuthUrl = `https://appleid.apple.com/auth/authorize?${params.toString()}`;
      window.location.href = appleAuthUrl;
      
    } catch (e) {
      if (e.response?.status === 500) {
        toast.error("Apple Sign-In not configured. Contact admin.");
      } else {
        toast.error("Failed to start Apple Sign-In");
      }
    }
  };

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      const endpoint = isRegister ? `${API}/api/auth/register` : `${API}/api/auth/login`;
      const payload = isRegister 
        ? { email, password, name, role: selectedRole }
        : { email, password };
      
      const response = await axios.post(endpoint, payload, { withCredentials: true });
      
      const roleMessage = response.data.user?.role === 'recruiter' 
        ? "Welcome, Recruiter!" 
        : isRegister ? "Account created! 15-day free trial started." : "Logged in!";
      toast.success(roleMessage);
      onAuthSuccess(response.data.user);
      navigate('/');
    } catch (e) {
      toast.error(e.response?.data?.detail || "Authentication failed");
    }
    setIsLoading(false);
  };

  const handleSendOtp = async () => {
    if (!phoneNumber || phoneNumber.length < 10) {
      toast.error("Please enter a valid phone number");
      return;
    }
    
    setIsLoading(true);
    try {
      // Format phone number with country code if not present
      const formattedPhone = phoneNumber.startsWith('+') ? phoneNumber : `+1${phoneNumber}`;
      await axios.post(`${API}/api/auth/phone/send-otp`, { phone_number: formattedPhone });
      setOtpSent(true);
      toast.success("OTP sent to your phone!");
    } catch (e) {
      toast.error(e.response?.data?.detail || "Failed to send OTP");
    }
    setIsLoading(false);
  };

  const handleVerifyOtp = async () => {
    if (!otpCode || otpCode.length < 4) {
      toast.error("Please enter the OTP code");
      return;
    }
    
    setIsLoading(true);
    try {
      const formattedPhone = phoneNumber.startsWith('+') ? phoneNumber : `+1${phoneNumber}`;
      const response = await axios.post(`${API}/api/auth/phone/verify-otp`, 
        { phone_number: formattedPhone, code: otpCode },
        { withCredentials: true }
      );
      
      toast.success("Phone verified!");
      onAuthSuccess(response.data.user);
      navigate('/');
    } catch (e) {
      toast.error(e.response?.data?.detail || "Invalid OTP");
    }
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800" data-testid="login-page">
      {/* Batik pattern background */}
      <div className="absolute inset-0 opacity-5 pointer-events-none"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%2320b2aa' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }}
      />
      
      <Card className="w-full max-w-md relative z-10 shadow-xl">
        <CardHeader className="text-center pb-2">
          <div className="w-16 h-16 bg-gradient-to-br from-turquoise to-teal-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl font-bold text-white">M</span>
          </div>
          <CardTitle className="text-2xl font-bold text-slate-900 dark:text-slate-100" style={{ fontFamily: 'IBM Plex Sans' }}>
            Welcome to MedMatch
          </CardTitle>
          <CardDescription>
            AI-powered job search for remote positions
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Social Login Buttons */}
          <div className="space-y-3">
            <Button 
              variant="outline" 
              className="w-full h-12 font-medium"
              onClick={handleGoogleLogin}
              disabled={isLoading}
              data-testid="google-login-btn"
            >
              <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Continue with Google
            </Button>
            
            {/* Apple Sign In Button - Following Apple HIG */}
            <button 
              onClick={handleAppleLogin}
              disabled={isLoading}
              className={`w-full h-12 flex items-center justify-center gap-3 rounded-lg font-medium transition-colors ${
                isDark 
                  ? 'bg-white text-black hover:bg-gray-100' 
                  : 'bg-black text-white hover:bg-gray-900'
              }`}
              style={{ minWidth: '140px', minHeight: '30px' }}
              data-testid="apple-login-btn"
            >
              {/* Official Apple Logo SVG */}
              <svg 
                className="w-5 h-5" 
                viewBox="0 0 24 24" 
                fill="currentColor"
              >
                <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
              </svg>
              <span style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif' }}>
                Sign in with Apple
              </span>
            </button>
          </div>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-slate-200 dark:border-slate-700" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white dark:bg-slate-900 px-2 text-slate-500">Or continue with</span>
            </div>
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-4">
              <TabsTrigger value="email" className="flex items-center gap-2">
                <Mail className="w-4 h-4" /> Email
              </TabsTrigger>
              <TabsTrigger value="phone" className="flex items-center gap-2">
                <Smartphone className="w-4 h-4" /> Phone
              </TabsTrigger>
            </TabsList>

            {/* Email Login */}
            <TabsContent value="email">
              <form onSubmit={handleEmailSubmit} className="space-y-4">
                {isRegister && (
                  <>
                    {/* Role Selection */}
                    <div className="space-y-2">
                      <Label>I am a</Label>
                      <div className="grid grid-cols-2 gap-3">
                        <button
                          type="button"
                          onClick={() => setSelectedRole("job_seeker")}
                          className={`p-3 rounded-lg border-2 transition-all text-left ${
                            selectedRole === "job_seeker"
                              ? "border-turquoise bg-turquoise/10"
                              : "border-slate-200 dark:border-slate-700 hover:border-slate-300"
                          }`}
                        >
                          <div className="font-medium text-slate-900 dark:text-slate-100 text-sm">Job Seeker</div>
                          <div className="text-xs text-slate-500 dark:text-slate-400">$1 lifetime • 15-day trial</div>
                        </button>
                        <button
                          type="button"
                          onClick={() => setSelectedRole("recruiter")}
                          className={`p-3 rounded-lg border-2 transition-all text-left ${
                            selectedRole === "recruiter"
                              ? "border-turquoise bg-turquoise/10"
                              : "border-slate-200 dark:border-slate-700 hover:border-slate-300"
                          }`}
                        >
                          <div className="font-medium text-slate-900 dark:text-slate-100 text-sm">Recruiter</div>
                          <div className="text-xs text-slate-500 dark:text-slate-400">Free forever</div>
                        </button>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="name">Name</Label>
                      <div className="relative">
                        <User className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                        <Input
                          id="name"
                          type="text"
                          placeholder="Your name"
                          value={name}
                          onChange={(e) => setName(e.target.value)}
                          className="pl-10"
                          data-testid="name-input"
                        />
                      </div>
                    </div>
                  </>
                )}
                
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                    <Input
                      id="email"
                      type="email"
                      placeholder="you@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="pl-10"
                      required
                      data-testid="email-input"
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="pl-10 pr-10"
                      required
                      data-testid="password-input"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-3 text-slate-400 hover:text-slate-600"
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
                
                <Button 
                  type="submit" 
                  className="w-full h-11 bg-gradient-to-r from-turquoise to-teal-600 hover:from-teal-600 hover:to-turquoise"
                  disabled={isLoading}
                  data-testid="email-submit-btn"
                >
                  {isLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <>
                      {isRegister ? "Create Account" : "Sign In"}
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </>
                  )}
                </Button>

                <p className="text-center text-sm text-slate-500">
                  {isRegister ? "Already have an account?" : "Don't have an account?"}{" "}
                  <button
                    type="button"
                    onClick={() => setIsRegister(!isRegister)}
                    className="text-turquoise hover:underline font-medium"
                  >
                    {isRegister ? "Sign in" : "Create one"}
                  </button>
                </p>
              </form>
            </TabsContent>

            {/* Phone Login */}
            <TabsContent value="phone">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number</Label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                    <Input
                      id="phone"
                      type="tel"
                      placeholder="+1 (555) 123-4567"
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value)}
                      className="pl-10"
                      disabled={otpSent}
                      data-testid="phone-input"
                    />
                  </div>
                </div>

                {!otpSent ? (
                  <Button 
                    onClick={handleSendOtp}
                    className="w-full h-11 bg-gradient-to-r from-turquoise to-teal-600"
                    disabled={isLoading || !phoneNumber}
                    data-testid="send-otp-btn"
                  >
                    {isLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <>Send OTP <ArrowRight className="w-4 h-4 ml-2" /></>
                    )}
                  </Button>
                ) : (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor="otp">Verification Code</Label>
                      <Input
                        id="otp"
                        type="text"
                        placeholder="Enter 6-digit code"
                        value={otpCode}
                        onChange={(e) => setOtpCode(e.target.value)}
                        maxLength={6}
                        className="text-center text-2xl tracking-widest"
                        data-testid="otp-input"
                      />
                    </div>
                    
                    <Button 
                      onClick={handleVerifyOtp}
                      className="w-full h-11 bg-gradient-to-r from-turquoise to-teal-600"
                      disabled={isLoading || otpCode.length < 4}
                      data-testid="verify-otp-btn"
                    >
                      {isLoading ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <>Verify & Sign In <ArrowRight className="w-4 h-4 ml-2" /></>
                      )}
                    </Button>

                    <button
                      type="button"
                      onClick={() => { setOtpSent(false); setOtpCode(""); }}
                      className="w-full text-center text-sm text-slate-500 hover:text-turquoise"
                    >
                      Change phone number
                    </button>
                  </>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default LoginPage;
