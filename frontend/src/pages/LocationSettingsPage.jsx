import { MapPin } from "lucide-react";
import LocationSettings from "@/components/LocationSettings";
import { useTranslation } from "@/utils/i18n";

const LocationSettingsPage = () => {
  const { t } = useTranslation();
  
  return (
    <div className="max-w-3xl mx-auto" data-testid="location-settings-page">
      <div className="mb-8">
        <h1 className="text-2xl font-bold flex items-center gap-3 text-slate-900 dark:text-white">
          <MapPin className="h-7 w-7 text-turquoise" />
          {t('pages.locationSettings.title')}
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mt-2">
          {t('pages.locationSettings.subtitle')}
        </p>
      </div>
      
      <LocationSettings />
    </div>
  );
};

export default LocationSettingsPage;
