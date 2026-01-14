import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import { useTheme } from "@/App";
import { 
  Mail, Phone, Lock, User, Loader2, ArrowRight, Eye, EyeOff,
  Chrome, Apple, Smartphone
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Label } from "@/components/ui/label";

const API = process.env.REACT_APP_BACKEND_URL;

const LoginPage = ({ onAuthSuccess }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isDark } = useTheme();
  
  const [activeTab, setActiveTab] = useState("email");
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isRegister, setIsRegister] = useState(false);
  
  // Email form
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  
  // Phone form
  const [phoneNumber, setPhoneNumber] = useState("");
  const [otpCode, setOtpCode] = useState("");
  const [otpSent, setOtpSent] = useState(false);

  // Check for Google OAuth callback (session_id in URL hash)
  useEffect(() => {
    const hash = location.hash;
    if (hash && hash.includes('session_id=')) {
      const sessionId = hash.split('session_id=')[1]?.split('&')[0];
      if (sessionId) {
        handleGoogleCallback(sessionId);
      }
    }
  }, [location]);

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
  }, []);

  const handleGoogleCallback = async (sessionId) => {
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
  };

  // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
  const handleGoogleLogin = () => {
    const redirectUrl = window.location.origin + '/login';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  const handleAppleLogin = () => {
    toast.info("Apple Sign-In requires additional setup. Contact support for Apple Developer credentials.");
  };

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      const endpoint = isRegister ? `${API}/api/auth/register` : `${API}/api/auth/login`;
      const payload = isRegister 
        ? { email, password, name }
        : { email, password };
      
      const response = await axios.post(endpoint, payload, { withCredentials: true });
      
      toast.success(isRegister ? "Account created!" : "Logged in!");
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
              <Chrome className="w-5 h-5 mr-3 text-red-500" />
              Continue with Google
            </Button>
            
            <Button 
              variant="outline" 
              className="w-full h-12 font-medium"
              onClick={handleAppleLogin}
              disabled={isLoading}
              data-testid="apple-login-btn"
            >
              <Apple className="w-5 h-5 mr-3" />
              Continue with Apple
            </Button>
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
