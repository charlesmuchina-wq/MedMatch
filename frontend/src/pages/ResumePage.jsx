import { useState, useCallback } from "react";
import { toast } from "sonner";
import { Upload, Cloud, FileText, User, Briefcase, GraduationCap, Award, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useDropzone } from "react-dropzone";
import { useTranslation } from "@/utils/i18n";
import CloudStorageUpload from "@/components/CloudStorageUpload";
import ResumeAutoFill from "@/components/ResumeAutoFill";
import LinkedInSync from "@/components/LinkedInSync";
import api from "@/utils/apiClient";

const ResumePage = ({ resume, setResume }) => {
  const { t } = useTranslation();
  const [uploading, setUploading] = useState(false);
  const [activeTab, setActiveTab] = useState("resume");

  const handleFileUpload = useCallback(async (file) => {
    if (!file) return;
    
    const fileName = file.name.toLowerCase();
    const validExtensions = ['.pdf', '.doc', '.docx'];
    const isValid = validExtensions.some(ext => fileName.endsWith(ext));
    
    if (!isValid) {
      toast.error(t("resume.invalidFormat") || "Please upload a PDF, DOC, or DOCX file");
      return;
    }
    
    // For non-PDF files from cloud storage, show conversion notice
    if (!fileName.endsWith('.pdf')) {
      toast.info(t("resume.conversionNote") || "Note: DOC/DOCX files will be processed. For best results, use PDF format.");
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/resume/upload`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error(await response.text());
      }
      
      const data = await response.json();
      setResume(data);
      toast.success(t("resume.parsed") || "Resume uploaded and parsed successfully!");
    } catch (e) {
      const errorMsg = e.message || t("resume.uploadFailed") || "Failed to upload resume";
      // If backend doesn't support DOC/DOCX yet, show helpful message
      if (errorMsg.includes("PDF") && !fileName.endsWith('.pdf')) {
        toast.error(t("resume.convertToPdf") || "Please convert your document to PDF format and try again");
      } else {
        toast.error(errorMsg);
      }
    }
    setUploading(false);
  }, [setResume, t]);

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    handleFileUpload(file);
  }, [handleFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1
  });

  const handleLinkedInSync = (syncedData) => {
    // Update resume with LinkedIn data
    if (syncedData) {
      setResume(prev => ({
        ...prev,
        full_name: syncedData.name || prev?.full_name,
        email: syncedData.email || prev?.email,
        profile_picture: syncedData.picture || prev?.profile_picture,
        linkedin_synced: true
      }));
      toast.success(t("linkedin.synced") || "LinkedIn profile synced!");
    }
  };

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-4xl mx-auto animate-fade-in" data-testid="resume-page">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-semibold text-slate-900 dark:text-slate-100 tracking-tight" style={{ fontFamily: 'IBM Plex Sans' }}>
          {t("resume.myResume")}
        </h1>
        <CloudStorageUpload onFileSelected={handleFileUpload} isLoading={uploading} />
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-8">
        <TabsList className="mb-6">
          <TabsTrigger value="resume" data-testid="resume-tab">
            <FileText className="w-4 h-4 mr-2" />
            {t("resume.myResume") || "My Resume"}
          </TabsTrigger>
          <TabsTrigger value="autofill" data-testid="autofill-tab">
            <Award className="w-4 h-4 mr-2" />
            {t("autofill.title") || "Auto-Fill"}
          </TabsTrigger>
          <TabsTrigger value="linkedin" data-testid="linkedin-tab">
            <User className="w-4 h-4 mr-2" />
            {t("linkedin.title") || "LinkedIn"}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="resume">
          <Card className="mb-8">
            <CardContent className="p-6">
              <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`} data-testid="resume-dropzone">
                <input {...getInputProps()} />
                <div className="text-center py-12">
                  {uploading ? (
                    <>
                      <Loader2 className="w-12 h-12 mx-auto text-turquoise animate-spin mb-4" />
                      <p className="text-slate-600 dark:text-slate-400">{t("resume.parsing")}</p>
                    </>
                  ) : (
                    <>
                      <Upload className="w-12 h-12 mx-auto text-slate-300 mb-4" />
                      <p className="text-lg font-medium text-slate-700 dark:text-slate-300 mb-2">
                        {isDragActive ? (t("resume.dropHere") || "Drop your resume here...") : t("resume.dragDrop")}
                      </p>
                      <p className="text-slate-500 mb-4">{t("resume.or")}</p>
                      <Badge variant="outline" className="cursor-pointer hover:bg-turquoise/10">
                        {t("resume.browse")}
                      </Badge>
                      <p className="text-xs text-slate-400 mt-4">{t("resume.supportedFormats")}</p>
                    </>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

      {/* Resume Content Display */}
      {resume && (
        <div className="space-y-6">
          {/* Personal Info */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="w-5 h-5 text-turquoise" />
                {t("resume.personalInfo")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                {resume.name && (
                  <div>
                    <p className="text-sm text-slate-500">{t("resume.name") || "Name"}</p>
                    <p className="font-medium text-slate-900 dark:text-slate-100">{resume.name}</p>
                  </div>
                )}
                {resume.email && (
                  <div>
                    <p className="text-sm text-slate-500">{t("auth.email")}</p>
                    <p className="font-medium text-slate-900 dark:text-slate-100">{resume.email}</p>
                  </div>
                )}
                {resume.phone && (
                  <div>
                    <p className="text-sm text-slate-500">{t("auth.phone")}</p>
                    <p className="font-medium text-slate-900 dark:text-slate-100">{resume.phone}</p>
                  </div>
                )}
                {resume.location && (
                  <div>
                    <p className="text-sm text-slate-500">{t("jobs.location")}</p>
                    <p className="font-medium text-slate-900 dark:text-slate-100">{resume.location}</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Summary */}
          {resume.summary && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5 text-turquoise" />
                  {t("resume.summary")}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-slate-700 dark:text-slate-300 whitespace-pre-wrap">{resume.summary}</p>
              </CardContent>
            </Card>
          )}

          {/* Experience */}
          {resume.experience?.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Briefcase className="w-5 h-5 text-turquoise" />
                  {t("resume.workExperience")}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {resume.experience.map((exp, idx) => (
                  <div key={idx} className="border-l-2 border-turquoise/30 pl-4">
                    <p className="font-semibold text-slate-900 dark:text-slate-100">{exp.title}</p>
                    <p className="text-turquoise">{exp.company}</p>
                    <p className="text-sm text-slate-500">{exp.dates}</p>
                    {exp.description && (
                      <p className="text-slate-600 dark:text-slate-400 mt-2 text-sm">{exp.description}</p>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Education */}
          {resume.education?.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <GraduationCap className="w-5 h-5 text-turquoise" />
                  {t("resume.education")}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {resume.education.map((edu, idx) => (
                  <div key={idx} className="border-l-2 border-turquoise/30 pl-4">
                    <p className="font-semibold text-slate-900 dark:text-slate-100">{edu.degree}</p>
                    <p className="text-turquoise">{edu.school}</p>
                    <p className="text-sm text-slate-500">{edu.dates}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Skills */}
          {resume.skills?.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Award className="w-5 h-5 text-turquoise" />
                  {t("resume.skills")}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {resume.skills.map((skill, idx) => (
                    <Badge key={idx} variant="secondary" className="bg-turquoise/10 text-turquoise">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
        </TabsContent>

        <TabsContent value="autofill">
          <ResumeAutoFill resume={resume} />
        </TabsContent>

        <TabsContent value="linkedin">
          <LinkedInSync onSync={handleLinkedInSync} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ResumePage;
