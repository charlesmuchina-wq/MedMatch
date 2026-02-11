/**
 * LocationPromptModal - Prompts users to provide location for compliance
 * Required for cross-border jurisdiction detection in GUAL
 */
import React, { useState, useEffect } from 'react';
import { MapPin, Globe, AlertTriangle, Check } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from './ui/dialog';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

// Location options with regulatory significance
const LOCATIONS = [
  { code: 'US-CA', name: 'California, USA', flag: '🇺🇸', laws: ['California AEDT'] },
  { code: 'US-NY', name: 'New York, USA', flag: '🇺🇸', laws: ['NYC LL 144'] },
  { code: 'US-CO', name: 'Colorado, USA', flag: '🇺🇸', laws: ['Colorado AI Act'] },
  { code: 'US', name: 'Other US State', flag: '🇺🇸', laws: [] },
  { code: 'CA-ON', name: 'Ontario, Canada', flag: '🇨🇦', laws: ['Ontario ESA', 'AIDA'] },
  { code: 'CA', name: 'Other Canada', flag: '🇨🇦', laws: ['AIDA'] },
  { code: 'GB', name: 'United Kingdom', flag: '🇬🇧', laws: ['UK GDPR'] },
  { code: 'DE', name: 'Germany', flag: '🇩🇪', laws: ['EU AI Act', 'GDPR'] },
  { code: 'FR', name: 'France', flag: '🇫🇷', laws: ['EU AI Act', 'GDPR'] },
  { code: 'NL', name: 'Netherlands', flag: '🇳🇱', laws: ['EU AI Act', 'GDPR'] },
  { code: 'ES', name: 'Spain', flag: '🇪🇸', laws: ['EU AI Act', 'GDPR'] },
  { code: 'IT', name: 'Italy', flag: '🇮🇹', laws: ['EU AI Act', 'GDPR'] },
  { code: 'EU', name: 'Other EU Country', flag: '🇪🇺', laws: ['EU AI Act', 'GDPR'] },
  { code: 'SG', name: 'Singapore', flag: '🇸🇬', laws: ['WFA', 'PDPA', 'AI Verify'] },
  { code: 'CN', name: 'China', flag: '🇨🇳', laws: ['PIPL', 'Algorithm Filing'] },
  { code: 'KR', name: 'South Korea', flag: '🇰🇷', laws: ['AI Basic Act', 'PIPA'] },
  { code: 'JP', name: 'Japan', flag: '🇯🇵', laws: ['APPI', 'AI Guidelines'] },
  { code: 'BR', name: 'Brazil', flag: '🇧🇷', laws: ['LGPD', 'Bill 2338'] },
  { code: 'AU', name: 'Australia', flag: '🇦🇺', laws: ['Privacy Act'] },
  { code: 'IN', name: 'India', flag: '🇮🇳', laws: ['DPDP Act'] },
  { code: 'ZA', name: 'South Africa', flag: '🇿🇦', laws: ['POPIA'] },
  { code: 'OTHER', name: 'Other Country', flag: '🌍', laws: ['OECD AI Principles'] },
];

export default function LocationPromptModal({ isOpen, onClose, onLocationSet }) {
  const [selectedLocation, setSelectedLocation] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showLaws, setShowLaws] = useState(false);

  const selectedLocationData = LOCATIONS.find(l => l.code === selectedLocation);

  const handleSubmit = async () => {
    if (!selectedLocation) {
      toast.error('Please select your location');
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await fetch(`${API_URL}/api/compliance-alerts/location/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ location_code: selectedLocation })
      });

      if (!response.ok) throw new Error('Failed to update location');

      toast.success('Location saved successfully');
      onLocationSet?.(selectedLocation);
      onClose();
    } catch (error) {
      console.error('Error updating location:', error);
      toast.error('Failed to save location');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Globe className="h-5 w-5 text-turquoise" />
            Set Your Location
          </DialogTitle>
          <DialogDescription>
            Your location helps us ensure compliance with regional AI regulations and provide better transparency about how your data is processed.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Location Selector */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Where are you located?</label>
            <Select value={selectedLocation} onValueChange={setSelectedLocation}>
              <SelectTrigger className="w-full" data-testid="location-select">
                <SelectValue placeholder="Select your location..." />
              </SelectTrigger>
              <SelectContent className="max-h-[300px]">
                {LOCATIONS.map((loc) => (
                  <SelectItem key={loc.code} value={loc.code}>
                    <span className="flex items-center gap-2">
                      <span>{loc.flag}</span>
                      <span>{loc.name}</span>
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Applicable Laws Display */}
          {selectedLocationData && selectedLocationData.laws.length > 0 && (
            <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <button 
                onClick={() => setShowLaws(!showLaws)}
                className="flex items-center justify-between w-full text-sm"
              >
                <span className="flex items-center gap-2 text-blue-700 dark:text-blue-300">
                  <AlertTriangle className="h-4 w-4" />
                  <span>{selectedLocationData.laws.length} regulation(s) may apply</span>
                </span>
                <span className="text-blue-500">{showLaws ? '−' : '+'}</span>
              </button>
              
              {showLaws && (
                <div className="mt-2 pt-2 border-t border-blue-200 dark:border-blue-700">
                  <p className="text-xs text-blue-600 dark:text-blue-400 mb-2">
                    Based on your location, these AI regulations may affect how your data is processed:
                  </p>
                  <ul className="space-y-1">
                    {selectedLocationData.laws.map((law, idx) => (
                      <li key={idx} className="flex items-center gap-2 text-xs text-blue-700 dark:text-blue-300">
                        <Check className="h-3 w-3 text-green-500" />
                        {law}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Privacy Note */}
          <div className="p-3 bg-muted/50 rounded-lg text-xs text-muted-foreground">
            <MapPin className="h-4 w-4 inline mr-1" />
            Your location is used solely for compliance purposes and will not be shared with employers without your consent.
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={isSubmitting}>
            Skip for Now
          </Button>
          <Button 
            onClick={handleSubmit} 
            disabled={!selectedLocation || isSubmitting}
            data-testid="save-location-btn"
          >
            {isSubmitting ? 'Saving...' : 'Save Location'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// Hook to check if location prompt is needed
export function useLocationPrompt() {
  const [showPrompt, setShowPrompt] = useState(false);
  const [locationStatus, setLocationStatus] = useState(null);

  useEffect(() => {
    checkLocationStatus();
  }, []);

  const checkLocationStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/api/compliance-alerts/location/pending-prompts`, {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setLocationStatus(data);
        
        // Show prompt if location is not set and there are pending prompts
        if (data.prompt_required) {
          setShowPrompt(true);
        }
      }
    } catch (error) {
      console.error('Error checking location status:', error);
    }
  };

  const triggerPrompt = () => setShowPrompt(true);
  const closePrompt = () => setShowPrompt(false);

  return {
    showPrompt,
    locationStatus,
    triggerPrompt,
    closePrompt,
    refreshStatus: checkLocationStatus
  };
}
