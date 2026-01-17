import { useState, useCallback } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Upload, Cloud } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useDropzone } from "react-dropzone";
import CloudStorageUpload from "@/components/CloudStorageUpload";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const ResumePage = ({ resume, setResume }) => {
  const [uploading, setUploading] = useState(false);

  const handleFileUpload = useCallback(async (file) => {
    if (!file) return;
    
    const fileName = file.name.toLowerCase();
    const validExtensions = ['.pdf', '.doc', '.docx'];
    const isValid = validExtensions.some(ext => fileName.endsWith(ext));
    
    if (!isValid) {
      toast.error("Please upload a PDF, DOC, or DOCX file");
      return;
    }
    
    // For non-PDF files from cloud storage, show conversion notice
    if (!fileName.endsWith('.pdf')) {
      toast.info("Note: DOC/DOCX files will be processed. For best results, use PDF format.");
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API}/resume/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResume(response.data);
      toast.success("Resume uploaded and parsed successfully!");
    } catch (e) {
      const errorMsg = e.response?.data?.detail || "Failed to upload resume";
      // If backend doesn't support DOC/DOCX yet, show helpful message
      if (errorMsg.includes("PDF") && !fileName.endsWith('.pdf')) {
        toast.error("Please convert your document to PDF format and try again");
      } else {
        toast.error(errorMsg);
      }
    }
    setUploading(false);
  }, [setResume]);

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

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-4xl mx-auto animate-fade-in" data-testid="resume-page">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-semibold text-slate-900 dark:text-slate-100 tracking-tight" style={{ fontFamily: 'IBM Plex Sans' }}>
          My Resume
        </h1>
        <CloudStorageUpload onFileSelected={handleFileUpload} isLoading={uploading} />
      </div>

      <Card className="mb-8">
        <CardContent className="p-6">
          <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`} data-testid="resume-dropzone">
            <input {...getInputProps()} data-testid="resume-input" />
            <Upload className="w-10 h-10 text-slate-400 mx-auto mb-3" />
            {uploading ? (
              <p className="text-slate-600 dark:text-slate-300">Processing your resume...</p>
            ) : (
              <>
                <p className="text-slate-700 dark:text-slate-200 font-medium">
                  {isDragActive ? "Drop your resume here" : "Drag & drop your resume"}
                </p>
                <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">or click to browse (PDF only)</p>
                <p className="text-slate-400 dark:text-slate-500 text-xs mt-3 flex items-center justify-center gap-1">
                  <Cloud className="w-3 h-3" /> Or import from Google Drive, Dropbox, OneDrive
                </p>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {resume && (
        <div className="space-y-6">
          <Card>
            <CardHeader><CardTitle style={{ fontFamily: 'IBM Plex Sans' }}>Profile</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-slate-500">Full Name</label>
                  <p className="font-medium text-slate-900 dark:text-slate-100">{resume.full_name || '-'}</p>
                </div>
                <div>
                  <label className="text-sm text-slate-500">Email</label>
                  <p className="font-medium text-slate-900 dark:text-slate-100">{resume.email || '-'}</p>
                </div>
              </div>
              {resume.summary && (
                <div>
                  <label className="text-sm text-slate-500">Summary</label>
                  <p className="text-slate-700 mt-1">{resume.summary}</p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle style={{ fontFamily: 'IBM Plex Sans' }}>Skills</CardTitle>
              <CardDescription>These skills will be used for job matching</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {resume.skills?.map((skill, i) => (
                  <Badge key={i} variant="secondary" className="bg-slate-100">{skill}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          {resume.experience?.length > 0 && (
            <Card>
              <CardHeader><CardTitle style={{ fontFamily: 'IBM Plex Sans' }}>Experience</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                {resume.experience.map((exp, i) => (
                  <div key={i} className="border-l-2 border-slate-200 pl-4">
                    <h4 className="font-medium text-slate-900 dark:text-slate-100">{exp.title}</h4>
                    <p className="text-sm text-slate-600">{exp.company} • {exp.duration}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};

export default ResumePage;
