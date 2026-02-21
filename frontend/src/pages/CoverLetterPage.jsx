import { useState, useEffect } from "react";
import { toast } from "sonner";
import { PenTool, Copy, Download, History, ChevronRight, Sparkles, Loader2, FileText, Languages } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import TranslationWidget from "@/components/TranslationWidget";
import { useTranslation } from "@/utils/i18n";
import api from "@/utils/apiClient";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const CoverLetterPage = ({ resume }) => {
  const { t } = useTranslation();
  const [jobTitle, setJobTitle] = useState("");
  const [company, setCompany] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [generating, setGenerating] = useState(false);
  const [coverLetter, setCoverLetter] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    // Load cover letter history
    api.client.get(`${API}/cover-letter/history`).then(res => {
      setHistory(res.data || []);
    }).catch(() => {});
  }, []);

  const generateCoverLetter = async () => {
    if (!jobTitle || !company || !jobDescription) {
      toast.error(t("coverLetter.fillAllFields") || "Please fill in all fields");
      return;
    }
    if (!resume) {
      toast.error(t("coverLetter.uploadResumeFirst") || "Please upload your resume first");
      return;
    }

    setGenerating(true);
    try {
      const response = await api.client.post(`${API}/cover-letter/generate`, {
        job_title: jobTitle,
        company: company,
        job_description: jobDescription
      });
      setCoverLetter(response.data);
      toast.success(t("coverLetter.generated") || "Cover letter generated!");
      // Refresh history
      const historyRes = await api.client.get(`${API}/cover-letter/history`);
      setHistory(historyRes.data || []);
    } catch (e) {
      toast.error(e.response?.data?.detail || t("coverLetter.generationFailed") || "Failed to generate cover letter");
    }
    setGenerating(false);
  };

  const copyToClipboard = () => {
    if (coverLetter?.cover_letter) {
      navigator.clipboard.writeText(coverLetter.cover_letter);
      toast.success(t("coverLetter.copied") || "Cover letter copied to clipboard!");
    }
  };

  const downloadAsTxt = () => {
    if (coverLetter?.cover_letter) {
      const blob = new Blob([coverLetter.cover_letter], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Cover_Letter_${company.replace(/\s+/g, '_')}.txt`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  const downloadAsPDF = async () => {
    if (!coverLetter?.cover_letter) return;
    
    try {
      toast.info("Generating PDF...");
      const response = await axios.post(`${API}/export/cover-letter-html`, {
        cover_letter: coverLetter.cover_letter,
        job_title: jobTitle,
        company: company,
        candidate_name: resume?.full_name || ''
      });
      
      // Open HTML in new window and trigger print (save as PDF)
      const printWindow = window.open('', '_blank');
      printWindow.document.write(response.data.html);
      printWindow.document.close();
      printWindow.focus();
      
      // Wait for content to load then print
      setTimeout(() => {
        printWindow.print();
      }, 500);
      
      toast.success("PDF ready! Use 'Save as PDF' in the print dialog.");
    } catch (e) {
      toast.error("Failed to generate PDF");
    }
  };

  const loadFromHistory = (item) => {
    setCoverLetter({
      cover_letter: item.cover_letter,
      key_matches: item.key_matches || [],
      transferable_skills: item.transferable_skills || []
    });
    setJobTitle(item.job_title);
    setCompany(item.company);
  };

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-5xl mx-auto animate-fade-in" data-testid="cover-letter-page">
      <h1 className="text-3xl font-semibold text-slate-900 dark:text-slate-100 tracking-tight mb-2" style={{ fontFamily: 'IBM Plex Sans' }}>
        AI Cover Letter Generator
      </h1>
      <p className="text-slate-500 mb-8">Generate personalized cover letters based on your resume and job requirements</p>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2" style={{ fontFamily: 'IBM Plex Sans' }}>
                <PenTool className="w-5 h-5" />
                Job Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Job Title *</label>
                <Input
                  placeholder={t("coverLetter.jobTitlePlaceholder")}
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  className="mt-1"
                  data-testid="job-title-input"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Company *</label>
                <Input
                  placeholder={t("coverLetter.companyPlaceholder")}
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="mt-1"
                  data-testid="company-input"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300">{t("coverLetter.jobDescription")} *</label>
                <Textarea
                  placeholder={t("coverLetter.pasteJobDescription")}
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  className="mt-1 min-h-[200px]"
                  data-testid="job-description-input"
                />
              </div>
              <Button 
                onClick={generateCoverLetter} 
                disabled={generating || !resume}
                className="w-full bg-gradient-to-r from-sky-500 to-emerald-500 hover:from-sky-600 hover:to-emerald-600"
                data-testid="generate-btn"
              >
                {generating ? (
                  <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> {t("common.generating")}</>
                ) : (
                  <><Sparkles className="w-4 h-4 mr-2" /> {t("coverLetter.generate")}</>
                )}
              </Button>
              {!resume && (
                <p className="text-sm text-amber-600 text-center">Please upload your resume first</p>
              )}
            </CardContent>
          </Card>

          {/* History */}
          {history.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base" style={{ fontFamily: 'IBM Plex Sans' }}>
                  <History className="w-4 h-4" />
                  Recent Cover Letters
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {history.slice(0, 5).map((item, i) => (
                    <div 
                      key={i}
                      className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 cursor-pointer"
                      onClick={() => loadFromHistory(item)}
                    >
                      <div>
                        <p className="text-sm font-medium text-slate-900 dark:text-slate-100">{item.job_title}</p>
                        <p className="text-xs text-slate-500">{item.company}</p>
                      </div>
                      <ChevronRight className="w-4 h-4 text-slate-400" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Output Section */}
        <div>
          <Card className="h-full">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle style={{ fontFamily: 'IBM Plex Sans' }}>Generated Cover Letter</CardTitle>
                {coverLetter && (
                  <div className="flex gap-2 flex-wrap">
                    <Button variant="outline" size="sm" onClick={copyToClipboard}>
                      <Copy className="w-4 h-4 mr-1" /> Copy
                    </Button>
                    <Button variant="outline" size="sm" onClick={downloadAsTxt}>
                      <Download className="w-4 h-4 mr-1" /> TXT
                    </Button>
                    <Button variant="outline" size="sm" onClick={downloadAsPDF} className="text-turquoise border-turquoise hover:bg-turquoise/10" data-testid="download-pdf-btn">
                      <FileText className="w-4 h-4 mr-1" /> PDF
                    </Button>
                    <TranslationWidget 
                      text={coverLetter.cover_letter} 
                      onTranslate={(translated) => setCoverLetter({...coverLetter, cover_letter: translated})}
                      compact={true}
                      context="cover_letter"
                    />
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {coverLetter ? (
                <div className="space-y-4">
                  {/* Cover Letter Text */}
                  <div className="bg-slate-50 rounded-lg p-4 max-h-[400px] overflow-y-auto">
                    <pre className="whitespace-pre-wrap text-sm text-slate-700 font-sans">
                      {coverLetter.cover_letter}
                    </pre>
                  </div>

                  {/* Key Matches */}
                  {coverLetter.key_matches?.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-slate-700 mb-2">Key Matches</h4>
                      <div className="flex flex-wrap gap-2">
                        {coverLetter.key_matches.map((match, i) => (
                          <Badge key={i} variant="secondary" className="bg-emerald-100 text-emerald-700">
                            {match}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Transferable Skills */}
                  {coverLetter.transferable_skills?.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-slate-700 mb-2">Transferable Skills</h4>
                      <div className="flex flex-wrap gap-2">
                        {coverLetter.transferable_skills.map((skill, i) => (
                          <Badge key={i} variant="secondary" className="bg-sky-100 text-sky-700">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Suggestions */}
                  {coverLetter.suggestions?.length > 0 && (
                    <div className="bg-amber-50 rounded-lg p-3">
                      <h4 className="text-sm font-medium text-amber-800 mb-2">Tips to Strengthen Your Application</h4>
                      <ul className="text-sm text-amber-700 space-y-1">
                        {coverLetter.suggestions.map((tip, i) => (
                          <li key={i}>• {tip}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12 text-slate-400">
                  <PenTool className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Fill in the job details and click Generate to create your personalized cover letter</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default CoverLetterPage;
