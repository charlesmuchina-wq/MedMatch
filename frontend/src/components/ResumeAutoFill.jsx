import { useState, useEffect } from "react";
import { 
  Copy, Check, FileText, User, Briefcase, GraduationCap, 
  Sparkles, Download, RefreshCw, Loader2, ClipboardCopy,
  Mail, Phone, MapPin, Linkedin as LinkedinIcon
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { useTranslation } from "@/utils/i18n";
import { apiClient } from "@/utils/apiClient";

/**
 * Resume Auto-Fill Component
 * Provides copy-ready data from resume for job application forms
 */
const ResumeAutoFill = ({ resume }) => {
  const { t } = useTranslation();
  const [autofillData, setAutofillData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copiedField, setCopiedField] = useState(null);
  const [activeTab, setActiveTab] = useState("personal");

  useEffect(() => {
    if (resume) {
      fetchAutofillData();
    } else {
      setLoading(false);
    }
  }, [resume]);

  const fetchAutofillData = async () => {
    try {
      const response = await apiClient.get("/autofill/data");
      setAutofillData(response.autofill_data);
    } catch (error) {
      console.error("Failed to fetch autofill data:", error);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (value, fieldName) => {
    try {
      await navigator.clipboard.writeText(value);
      setCopiedField(fieldName);
      toast.success(t("autofill.copied") || "Copied to clipboard!");
      setTimeout(() => setCopiedField(null), 2000);
    } catch (error) {
      toast.error(t("autofill.copyFailed") || "Failed to copy");
    }
  };

  const copyAllInCategory = async (category) => {
    if (!autofillData?.[category]) return;
    
    const text = autofillData[category]
      .map(field => `${field.field_label}: ${field.value}`)
      .join("\n");
    
    await copyToClipboard(text, `all_${category}`);
  };

  const getIconForCategory = (category) => {
    switch (category) {
      case "personal": return User;
      case "professional": return Briefcase;
      case "education": return GraduationCap;
      case "skills": return Sparkles;
      case "work_history": return FileText;
      default: return FileText;
    }
  };

  const getIconForField = (fieldName) => {
    if (fieldName.includes("email")) return Mail;
    if (fieldName.includes("phone")) return Phone;
    if (fieldName.includes("location") || fieldName.includes("address")) return MapPin;
    if (fieldName.includes("linkedin")) return LinkedinIcon;
    return ClipboardCopy;
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6 flex items-center justify-center">
          <Loader2 className="w-6 h-6 animate-spin text-turquoise" />
        </CardContent>
      </Card>
    );
  }

  if (!resume) {
    return (
      <Card>
        <CardContent className="p-6 text-center">
          <FileText className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h3 className="font-medium text-slate-900 dark:text-slate-100 mb-2">
            {t("autofill.noResume") || "No Resume Found"}
          </h3>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            {t("autofill.uploadFirst") || "Upload your resume to enable auto-fill"}
          </p>
        </CardContent>
      </Card>
    );
  }

  const categories = [
    { id: "personal", label: t("autofill.personal") || "Personal Info" },
    { id: "professional", label: t("autofill.professional") || "Professional" },
    { id: "education", label: t("autofill.education") || "Education" },
    { id: "skills", label: t("autofill.skills") || "Skills" },
    { id: "work_history", label: t("autofill.workHistory") || "Work History" }
  ];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <ClipboardCopy className="w-5 h-5 text-turquoise" />
              {t("autofill.title") || "Auto-Fill Data"}
            </CardTitle>
            <CardDescription>
              {t("autofill.description") || "Click any field to copy for job applications"}
            </CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={fetchAutofillData}>
            <RefreshCw className="w-4 h-4 mr-1" />
            {t("common.refresh") || "Refresh"}
          </Button>
        </div>
      </CardHeader>
      
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid grid-cols-5 mb-4">
            {categories.map(cat => {
              const Icon = getIconForCategory(cat.id);
              return (
                <TabsTrigger key={cat.id} value={cat.id} className="text-xs">
                  <Icon className="w-3 h-3 mr-1" />
                  <span className="hidden sm:inline">{cat.label}</span>
                </TabsTrigger>
              );
            })}
          </TabsList>
          
          {categories.map(cat => (
            <TabsContent key={cat.id} value={cat.id}>
              <div className="space-y-2">
                {/* Copy All Button */}
                {autofillData?.[cat.id]?.length > 0 && (
                  <div className="flex justify-end mb-3">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => copyAllInCategory(cat.id)}
                    >
                      <Copy className="w-3 h-3 mr-1" />
                      {t("autofill.copyAll") || "Copy All"}
                    </Button>
                  </div>
                )}
                
                {/* Fields */}
                {autofillData?.[cat.id]?.length > 0 ? (
                  <div className="grid gap-2">
                    {autofillData[cat.id].map((field, idx) => {
                      const FieldIcon = getIconForField(field.field_name);
                      const isCopied = copiedField === field.field_name;
                      
                      return (
                        <button
                          key={idx}
                          onClick={() => copyToClipboard(field.value, field.field_name)}
                          className={`w-full p-3 rounded-lg border text-left transition-all ${
                            isCopied 
                              ? "border-green-500 bg-green-50 dark:bg-green-900/20" 
                              : "border-slate-200 dark:border-slate-700 hover:border-turquoise/50 hover:bg-slate-50 dark:hover:bg-slate-800/50"
                          }`}
                          data-testid={`autofill-${field.field_name}`}
                        >
                          <div className="flex items-start justify-between gap-2">
                            <div className="flex items-start gap-2 flex-1 min-w-0">
                              <FieldIcon className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                                isCopied ? "text-green-500" : "text-slate-400"
                              }`} />
                              <div className="min-w-0">
                                <p className="text-xs text-slate-500 dark:text-slate-400 mb-0.5">
                                  {field.field_label}
                                </p>
                                <p className={`text-sm font-medium truncate ${
                                  isCopied 
                                    ? "text-green-700 dark:text-green-300" 
                                    : "text-slate-900 dark:text-slate-100"
                                }`}>
                                  {field.value}
                                </p>
                              </div>
                            </div>
                            {isCopied ? (
                              <Check className="w-4 h-4 text-green-500 flex-shrink-0" />
                            ) : (
                              <Copy className="w-4 h-4 text-slate-300 flex-shrink-0" />
                            )}
                          </div>
                        </button>
                      );
                    })}
                  </div>
                ) : (
                  <div className="text-center py-8 text-slate-500 dark:text-slate-400">
                    <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">
                      {t("autofill.noDataInCategory") || "No data available in this category"}
                    </p>
                  </div>
                )}
              </div>
            </TabsContent>
          ))}
        </Tabs>
        
        {/* Quick tip */}
        <div className="mt-4 p-3 bg-turquoise/10 rounded-lg">
          <p className="text-xs text-turquoise-700 dark:text-turquoise-300">
            <Sparkles className="w-3 h-3 inline mr-1" />
            {t("autofill.tip") || "Tip: Click any field to instantly copy it for pasting into job application forms."}
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default ResumeAutoFill;
