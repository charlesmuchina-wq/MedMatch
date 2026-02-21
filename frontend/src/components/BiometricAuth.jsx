import { useState, useCallback } from "react";
import { useTranslation } from "@/utils/i18n";
import axios from "axios";
import { toast } from "sonner";
import { Fingerprint, Loader2, ShieldCheck, Smartphone, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const API = process.env.REACT_APP_BACKEND_URL;

// Check if WebAuthn is supported
const isWebAuthnSupported = () => {
  return window.PublicKeyCredential !== undefined &&
    typeof window.PublicKeyCredential === "function";
};

// Base64URL encode/decode utilities
const base64urlEncode = (buffer) => {
  const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)));
  return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
};

const base64urlDecode = (str) => {
  str = str.replace(/-/g, '+').replace(/_/g, '/');
  while (str.length % 4) str += '=';
  return Uint8Array.from(atob(str), c => c.charCodeAt(0));
};

// Biometric Registration Component
export const BiometricRegistration = ({ onSuccess, email, username }) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [deviceName, setDeviceName] = useState("My Device");
  const supported = isWebAuthnSupported();

  const handleRegister = useCallback(async () => {
    if (!supported) {
      toast.error("Biometric authentication is not supported on this device");
      return;
    }

    setLoading(true);
    try {
      // Step 1: Get registration options from server
      const startResponse = await axios.post(`${API}/api/biometric/register/start`, {
        email,
        username,
        device_name: deviceName
      });

      const options = JSON.parse(startResponse.data.options);
      const userId = startResponse.data.user_id;

      // Convert challenge and user.id from base64url to ArrayBuffer
      options.challenge = base64urlDecode(options.challenge);
      options.user.id = base64urlDecode(options.user.id);

      // Step 2: Create credential with WebAuthn API
      const credential = await navigator.credentials.create({ publicKey: options });

      // Step 3: Send credential to server
      const completeResponse = await axios.post(`${API}/api/biometric/register/complete`, {
        user_id: userId,
        credential_id: base64urlEncode(credential.rawId),
        raw_id: base64urlEncode(credential.rawId),
        response: {
          clientDataJSON: base64urlEncode(credential.response.clientDataJSON),
          attestationObject: base64urlEncode(credential.response.attestationObject),
          transports: credential.response.getTransports ? credential.response.getTransports() : []
        },
        type: credential.type
      });

      if (completeResponse.data.verified) {
        toast.success("Biometric registration successful!");
        onSuccess?.(completeResponse.data);
      }
    } catch (error) {
      console.error("Biometric registration error:", error);
      if (error.name === "NotAllowedError") {
        toast.error("Biometric registration was cancelled or denied");
      } else {
        toast.error(error.response?.data?.detail || "Registration failed");
      }
    } finally {
      setLoading(false);
    }
  }, [email, username, deviceName, supported, onSuccess]);

  if (!supported) {
    return (
      <div className="flex items-center gap-2 p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg text-amber-700 dark:text-amber-300">
        <AlertCircle className="w-5 h-5" />
        <span className="text-sm">Biometric authentication is not supported on this browser</span>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 p-3 bg-turquoise/10 rounded-lg">
        <ShieldCheck className="w-5 h-5 text-turquoise" />
        <span className="text-sm text-slate-600 dark:text-slate-300">
          {t("biometric.secureLogin")}
        </span>
      </div>

      <Input
        placeholder={t("biometric.deviceName")}
        value={deviceName}
        onChange={(e) => setDeviceName(e.target.value)}
        className="dark:bg-slate-800"
      />

      <Button
        onClick={handleRegister}
        disabled={loading}
        className="w-full bg-turquoise hover:bg-turquoise/90"
        data-testid="biometric-register-btn"
      >
        {loading ? (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            {t("biometric.settingUp")}
          </>
        ) : (
          <>
            <Fingerprint className="w-4 h-4 mr-2" />
            {t("biometric.registerWith")}
          </>
        )}
      </Button>
    </div>
  );
};

// Biometric Login Component
export const BiometricLogin = ({ onSuccess }) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");
  const supported = isWebAuthnSupported();

  const handleLogin = useCallback(async () => {
    if (!supported) {
      toast.error(t("biometric.notSupported"));
      return;
    }

    if (!email) {
      toast.error(t("biometric.enterEmail"));
      return;
    }

    setLoading(true);
    try {
      // Step 1: Get authentication options from server
      const startResponse = await axios.post(`${API}/api/biometric/authenticate/start`, {
        email
      });

      const options = JSON.parse(startResponse.data.options);

      // Convert challenge and allowCredentials from base64url
      options.challenge = base64urlDecode(options.challenge);
      if (options.allowCredentials) {
        options.allowCredentials = options.allowCredentials.map(cred => ({
          ...cred,
          id: base64urlDecode(cred.id)
        }));
      }

      // Step 2: Get credential with WebAuthn API
      const credential = await navigator.credentials.get({ publicKey: options });

      // Step 3: Send assertion to server
      const completeResponse = await axios.post(`${API}/api/biometric/authenticate/complete`, {
        credential_id: base64urlEncode(credential.rawId),
        raw_id: base64urlEncode(credential.rawId),
        response: {
          clientDataJSON: base64urlEncode(credential.response.clientDataJSON),
          authenticatorData: base64urlEncode(credential.response.authenticatorData),
          signature: base64urlEncode(credential.response.signature),
          userHandle: credential.response.userHandle ? 
            base64urlEncode(credential.response.userHandle) : null
        },
        type: credential.type
      });

      if (completeResponse.data.verified) {
        toast.success("Login successful!");
        onSuccess?.(completeResponse.data);
      }
    } catch (error) {
      console.error("Biometric login error:", error);
      if (error.name === "NotAllowedError") {
        toast.error("Biometric login was cancelled or denied");
      } else {
        toast.error(error.response?.data?.detail || "Login failed");
      }
    } finally {
      setLoading(false);
    }
  }, [email, supported, onSuccess]);

  if (!supported) {
    return null;
  }

  return (
    <Card className="border-turquoise/30 dark:bg-slate-800">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Fingerprint className="w-5 h-5 text-turquoise" />
          {t("biometric.title")}
        </CardTitle>
        <CardDescription>
          {t("biometric.description")}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Input
          type="email"
          placeholder={t("biometric.emailPlaceholder")}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="dark:bg-slate-700"
          data-testid="biometric-email-input"
        />
        
        <Button
          onClick={handleLogin}
          disabled={loading || !email}
          className="w-full bg-turquoise hover:bg-turquoise/90"
          data-testid="biometric-login-btn"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Verifying...
            </>
          ) : (
            <>
              <Fingerprint className="w-4 h-4 mr-2" />
              Login with Biometrics
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
};

// Security Status Badge Component
export const SecurityBadge = ({ isVerified }) => {
  if (!isVerified) return null;
  
  return (
    <Badge className="bg-turquoise/20 text-turquoise border-turquoise/30">
      <ShieldCheck className="w-3 h-3 mr-1" />
      Biometric Verified
    </Badge>
  );
};

// Default export for backwards compatibility
const BiometricAuth = { BiometricRegistration, BiometricLogin, SecurityBadge };
export default BiometricAuth;
