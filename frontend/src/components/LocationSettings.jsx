import { useState, useEffect } from "react";
import { MapPin, Navigation, Bell, Car, Train, Bike, Home, Save, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import api from "@/utils/apiClient";
import { useTranslation } from "@/utils/i18n";

const LocationSettings = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [geocoding, setGeocoding] = useState(false);
  const [preferences, setPreferences] = useState({
    home_lat: null,
    home_lon: null,
    home_address: "",
    preferred_radius_miles: 25,
    commute_preference: "driving",
    location_alerts_enabled: true,
    preferred_work_types: ["remote", "hybrid", "onsite"],
  });
  const [nearestHub, setNearestHub] = useState(null);

  useEffect(() => {
    fetchPreferences();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchPreferences = async () => {
    try {
      const response = await api.client.get("/api/geolocation/preferences");
      if (response.data) {
        setPreferences({
          home_lat: response.data.home_coordinates?.lat || null,
          home_lon: response.data.home_coordinates?.lon || null,
          home_address: response.data.home_coordinates?.address || "",
          preferred_radius_miles: response.data.preferred_radius_miles || 25,
          commute_preference: response.data.commute_preference || "driving",
          location_alerts_enabled: response.data.location_alerts_enabled ?? true,
          preferred_work_types: response.data.preferred_work_types || ["remote", "hybrid", "onsite"],
        });
        
        // Fetch nearest hub if we have coordinates
        if (response.data.home_coordinates?.lat) {
          fetchNearestHub(response.data.home_coordinates.lat, response.data.home_coordinates.lon);
        }
      }
    } catch (error) {
      console.error("Failed to fetch location preferences:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchNearestHub = async (lat, lon) => {
    try {
      const response = await api.client.get(`/api/geolocation/nearest-hub?lat=${lat}&lon=${lon}`);
      setNearestHub(response.data);
    } catch (error) {
      console.error("Failed to fetch nearest hub:", error);
    }
  };

  const handleGeocodeAddress = async () => {
    if (!preferences.home_address) {
      toast.error("Please enter an address");
      return;
    }

    setGeocoding(true);
    try {
      const response = await api.client.post("/api/geolocation/geocode", {
        address: preferences.home_address,
      });

      if (response.data.found) {
        const coords = response.data.coordinates;
        setPreferences((prev) => ({
          ...prev,
          home_lat: coords.lat,
          home_lon: coords.lon,
        }));
        fetchNearestHub(coords.lat, coords.lon);
        toast.success("Location found!");
      } else {
        toast.error(response.data.message || "Could not find location");
      }
    } catch (error) {
      toast.error("Failed to geocode address");
    } finally {
      setGeocoding(false);
    }
  };

  const handleUseCurrentLocation = () => {
    if (!navigator.geolocation) {
      toast.error("Geolocation is not supported by your browser");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        setPreferences((prev) => ({
          ...prev,
          home_lat: latitude,
          home_lon: longitude,
          home_address: t('components.locationSettings.currentLocation') || "Current Location",
        }));
        fetchNearestHub(latitude, longitude);
        toast.success(t('components.locationSettings.locationDetected') || "Location updated!");
      },
      (error) => {
        toast.error(t('components.locationSettings.locationFailed') || "Failed to get your location. Please enter manually.");
      }
    );
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.client.put("/api/geolocation/preferences", preferences);
      toast.success(t('components.locationSettings.preferencesSaved') || "Location preferences saved!");
    } catch (error) {
      toast.error(t('components.locationSettings.saveFailed') || "Failed to save preferences");
    } finally {
      setSaving(false);
    }
  };

  const toggleWorkType = (type) => {
    setPreferences((prev) => {
      const types = prev.preferred_work_types;
      if (types.includes(type)) {
        return { ...prev, preferred_work_types: types.filter((t) => t !== type) };
      } else {
        return { ...prev, preferred_work_types: [...types, type] };
      }
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin text-turquoise" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="location-settings">
      {/* Home Location Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Home className="h-5 w-5 text-turquoise" />
            {t('components.locationSettings.homeLocation') || 'Home Location'}
          </CardTitle>
          <CardDescription>
            {t('components.locationSettings.homeLocationDesc') || 'Set your home address to get commute times and proximity-based job alerts'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <div className="flex-1">
              <Label htmlFor="address">{t('components.locationSettings.addressOrCity') || 'Address or City'}</Label>
              <Input
                id="address"
                placeholder={t('components.locationSettings.addressPlaceholder') || "e.g., San Francisco, Boston, Austin"}
                value={preferences.home_address}
                onChange={(e) =>
                  setPreferences((prev) => ({ ...prev, home_address: e.target.value }))
                }
                data-testid="home-address-input"
              />
            </div>
            <div className="flex items-end gap-2">
              <Button
                variant="outline"
                onClick={handleGeocodeAddress}
                disabled={geocoding}
              >
                {geocoding ? <Loader2 className="h-4 w-4 animate-spin" /> : <MapPin className="h-4 w-4" />}
              </Button>
              <Button
                variant="outline"
                onClick={handleUseCurrentLocation}
                title={t('components.locationSettings.useCurrentLocation') || "Use current location"}
                aria-label={t('components.locationSettings.useCurrentLocation') || "Use current location"}
              >
                <Navigation className="h-4 w-4" aria-hidden="true" />
              </Button>
            </div>
          </div>

          {preferences.home_lat && preferences.home_lon && (
            <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg" role="status" aria-live="polite">
              <div className="text-sm text-slate-600 dark:text-slate-300">
                <span className="font-medium">Coordinates:</span>{" "}
                {preferences.home_lat.toFixed(4)}, {preferences.home_lon.toFixed(4)}
              </div>
              {nearestHub && (
                <div className="mt-2 text-sm">
                  <span className="font-medium">Nearest Hub:</span>{" "}
                  <Badge variant="secondary">{nearestHub.name}</Badge>
                  <span className="text-slate-500 ml-2">
                    ({nearestHub.distance_miles} mi away)
                  </span>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Search Radius Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="h-5 w-5 text-turquoise" aria-hidden="true" />
            {t('components.locationSettings.searchRadius') || 'Job Search Radius'}
          </CardTitle>
          <CardDescription>
            {t('components.locationSettings.searchRadiusDesc') || 'Only show hybrid and onsite jobs within this distance'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <Label>{t('components.locationSettings.maxDistance') || 'Maximum Distance'}</Label>
              <Badge variant="outline" className="text-lg font-bold">
                {preferences.preferred_radius_miles} {t('components.locationSettings.miles') || 'miles'}
              </Badge>
            </div>
            <Slider
              value={[preferences.preferred_radius_miles]}
              onValueChange={([value]) =>
                setPreferences((prev) => ({ ...prev, preferred_radius_miles: value }))
              }
              min={5}
              max={100}
              step={5}
              className="w-full"
              data-testid="radius-slider"
            />
            <div className="flex justify-between text-xs text-slate-500">
              <span>5 mi (Urban)</span>
              <span>25 mi (Standard)</span>
              <span>100 mi (Rural)</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Commute Preferences Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Car className="h-5 w-5 text-turquoise" />
            Commute Preferences
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>Primary Commute Mode</Label>
            <Select
              value={preferences.commute_preference}
              onValueChange={(value) =>
                setPreferences((prev) => ({ ...prev, commute_preference: value }))
              }
            >
              <SelectTrigger className="mt-2" data-testid="commute-mode-select">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="driving">
                  <div className="flex items-center gap-2">
                    <Car className="h-4 w-4" /> Driving (City)
                  </div>
                </SelectItem>
                <SelectItem value="driving_highway">
                  <div className="flex items-center gap-2">
                    <Car className="h-4 w-4" /> Driving (Highway)
                  </div>
                </SelectItem>
                <SelectItem value="transit">
                  <div className="flex items-center gap-2">
                    <Train className="h-4 w-4" /> Public Transit
                  </div>
                </SelectItem>
                <SelectItem value="cycling">
                  <div className="flex items-center gap-2">
                    <Bike className="h-4 w-4" /> Cycling
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Work Type Preferences Card */}
      <Card>
        <CardHeader>
          <CardTitle>Preferred Work Types</CardTitle>
          <CardDescription>
            Select the work arrangements you are interested in
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {["remote", "hybrid", "onsite"].map((type) => (
              <Badge
                key={type}
                variant={preferences.preferred_work_types.includes(type) ? "default" : "outline"}
                className={`cursor-pointer capitalize px-4 py-2 ${
                  preferences.preferred_work_types.includes(type)
                    ? "bg-turquoise hover:bg-turquoise/80"
                    : ""
                }`}
                onClick={() => toggleWorkType(type)}
                data-testid={`work-type-${type}`}
              >
                {type}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Location Alerts Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5 text-turquoise" />
            Location-Based Alerts
          </CardTitle>
          <CardDescription>
            Get notified when new jobs are posted near you
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Enable Proximity Alerts</p>
              <p className="text-sm text-slate-500">
                Receive notifications for jobs within your search radius
              </p>
            </div>
            <Switch
              checked={preferences.location_alerts_enabled}
              onCheckedChange={(checked) =>
                setPreferences((prev) => ({ ...prev, location_alerts_enabled: checked }))
              }
              data-testid="location-alerts-toggle"
            />
          </div>
        </CardContent>
      </Card>

      {/* Save Button */}
      <Button
        className="w-full bg-turquoise hover:bg-turquoise/90"
        size="lg"
        onClick={handleSave}
        disabled={saving}
        data-testid="save-location-btn"
      >
        {saving ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Saving...
          </>
        ) : (
          <>
            <Save className="mr-2 h-4 w-4" />
            Save Location Preferences
          </>
        )}
      </Button>
    </div>
  );
};

export default LocationSettings;
