import React, { useState, useEffect, useRef } from "react";
import { toast } from "sonner";
import { 
  Mic, MessageSquare, Sparkles, Loader2, BookOpen, Target,
  CheckCircle2, Lightbulb, Users, Building2, ChevronRight,
  Clock, Star, Award, RefreshCw, Copy, Volume2, FileText, Download, Languages,
  Plus, ListPlus, FileQuestion
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import TranslationWidget from "@/components/TranslationWidget";
import { useTranslation } from "@/utils/i18n";
import api from "@/utils/apiClient";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Common interview question categories
const QUESTION_CATEGORIES = [
  { id: "behavioral", name: "Behavioral", icon: Users, color: "text-violet-500" },
  { id: "technical", name: "Technical", icon: Target, color: "text-sky-500" },
  { id: "situational", name: "Situational", icon: Lightbulb, color: "text-amber-500" },
  { id: "company", name: "Company Fit", icon: Building2, color: "text-emerald-500" },
];

// STAR Method Helper
const StarMethodHelper = ({ question, onGenerate, generating, t }) => {
  const [situation, setSituation] = useState("");
  const [task, setTask] = useState("");
  const [action, setAction] = useState("");
  const [result, setResult] = useState("");

  return (
    <div className="space-y-4 p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
      <h4 className="font-medium text-slate-900 dark:text-slate-100 flex items-center gap-2">
        <Star className="w-4 h-4 text-amber-500" />
        {t("interview.starBuilder")}
      </h4>
      <p className="text-sm text-slate-500 dark:text-slate-400">{t("interview.starDescription")}</p>
      
      <div className="grid gap-3">
        <div>
          <label className="text-xs font-medium text-slate-600 dark:text-slate-300">{t("interview.situation")}</label>
          <Textarea 
            placeholder={t("interview.situationPlaceholder")}
            value={situation}
            onChange={(e) => setSituation(e.target.value)}
            className="mt-1 h-20 dark:bg-slate-700"
          />
        </div>
        <div>
          <label className="text-xs font-medium text-slate-600 dark:text-slate-300">{t("interview.task")}</label>
          <Textarea 
            placeholder={t("interview.taskPlaceholder")}
            value={task}
            onChange={(e) => setTask(e.target.value)}
            className="mt-1 h-20 dark:bg-slate-700"
          />
        </div>
        <div>
          <label className="text-xs font-medium text-slate-600 dark:text-slate-300">{t("interview.action")}</label>
          <Textarea 
            placeholder={t("interview.actionPlaceholder")}
            value={action}
            onChange={(e) => setAction(e.target.value)}
            className="mt-1 h-20 dark:bg-slate-700"
          />
        </div>
        <div>
          <label className="text-xs font-medium text-slate-600 dark:text-slate-300">{t("interview.result")}</label>
          <Textarea 
            placeholder={t("interview.resultPlaceholder")}
            value={result}
            onChange={(e) => setResult(e.target.value)}
            className="mt-1 h-20 dark:bg-slate-700"
          />
        </div>
      </div>
      
      <Button 
        onClick={() => onGenerate({ question, situation, task, action, result })}
        disabled={generating || (!situation && !task && !action && !result)}
        className="w-full"
      >
        {generating ? (
          <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Polishing Answer...</>
        ) : (
          <><Sparkles className="w-4 h-4 mr-2" /> AI Polish My Answer</>
        )}
      </Button>
    </div>
  );
};

const InterviewPrepPage = ({ resume }) => {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState("questions");
  const [jobTitle, setJobTitle] = useState("");
  const [company, setCompany] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [customQuestions, setCustomQuestions] = useState("");
  const [questions, setQuestions] = useState([]);
  const [generatingQuestions, setGeneratingQuestions] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [generatedAnswer, setGeneratedAnswer] = useState(null);
  const [generatingAnswer, setGeneratingAnswer] = useState(false);
  const [companyResearch, setCompanyResearch] = useState(null);
  const [researchingCompany, setResearchingCompany] = useState(false);
  const [mockMode, setMockMode] = useState(false);
  const [currentMockQuestion, setCurrentMockQuestion] = useState(0);
  const [mockAnswers, setMockAnswers] = useState([]);
  const [mockFeedback, setMockFeedback] = useState(null);
  const [inputMode, setInputMode] = useState("generate"); // "generate" | "paste" | "description"

  const generateQuestions = async () => {
    if (!jobTitle) {
      toast.error("Please enter a job title");
      return;
    }

    setGeneratingQuestions(true);
    try {
      // Build context with job description and resume skills
      const context = {
        job_title: jobTitle,
        company: company,
        difficulty: "medium",
        num_questions: 5,
        topics: resume?.skills?.slice(0, 5) || []
      };
      
      // Add job description if provided
      if (jobDescription && inputMode === "description") {
        context.job_description = jobDescription;
        context.resume_skills = resume?.skills || [];
      }
      
      // Use new AI interview prep endpoint
      const response = await api.client.post(`${API}/interview-prep`, context);
      
      // Map response to expected format
      const generatedQuestions = response.data.questions?.map(q => ({
        text: q.question,
        type: q.type,
        category: q.type?.toLowerCase() || 'general',
        difficulty: 'medium',
        tip: q.tip,
        sample_points: q.sample_points
      })) || [];
      
      setQuestions(generatedQuestions);
      toast.success(`Generated ${generatedQuestions.length} interview questions!`);
    } catch (e) {
      console.error("Generate questions error:", e);
      toast.error("Failed to generate questions. Please try again.");
    }
    setGeneratingQuestions(false);
  };

  const generateFromJobDescription = async () => {
    if (!jobDescription) {
      toast.error("Please paste a job description");
      return;
    }

    setGeneratingQuestions(true);
    try {
      // Use AI to generate questions from job description with resume context
      const resumeSkills = resume?.skills?.join(", ") || "general professional skills";
      const resumeExperience = resume?.experience?.map(e => e.title).join(", ") || "";
      
      const response = await api.client.post(`${API}/assistant`, {
        message: `Based on this job description, generate 5 interview questions that:
1. Are relevant to the role requirements
2. Allow the candidate to highlight transferable skills
3. Include a mix of behavioral, technical, and situational questions

Job Description:
${jobDescription}

Candidate's Skills: ${resumeSkills}
${resumeExperience ? `Past Roles: ${resumeExperience}` : ''}

Return as JSON array with format: [{"question": "...", "type": "Behavioral|Technical|Situational", "tip": "...", "transferable_skill": "..."}]`,
        context: "interview"
      });
      
      // Parse the response
      let questionsData = [];
      try {
        const responseText = response.data.response;
        // Try to extract JSON from the response
        const jsonMatch = responseText.match(/\[[\s\S]*\]/);
        if (jsonMatch) {
          questionsData = JSON.parse(jsonMatch[0]);
        }
      } catch (parseError) {
        console.error("Parse error:", parseError);
      }
      
      if (questionsData.length === 0) {
        // Fallback: Generate questions using the standard endpoint
        const fallbackResponse = await api.client.post(`${API}/interview-prep`, {
          job_title: jobTitle || "Professional Role",
          company: company,
          difficulty: "medium",
          num_questions: 5,
          topics: resume?.skills?.slice(0, 5) || [],
          job_description: jobDescription
        });
        questionsData = fallbackResponse.data.questions || [];
      }
      
      const generatedQuestions = questionsData.map(q => ({
        text: q.question,
        type: q.type,
        category: q.type?.toLowerCase() || 'general',
        difficulty: 'medium',
        tip: q.tip,
        transferable_skill: q.transferable_skill,
        sample_points: q.sample_points
      }));
      
      setQuestions(generatedQuestions);
      toast.success(`Generated ${generatedQuestions.length} questions from job description!`);
    } catch (e) {
      console.error("Generate from JD error:", e);
      toast.error("Failed to generate questions. Please try again.");
    }
    setGeneratingQuestions(false);
  };

  const addCustomQuestions = () => {
    if (!customQuestions.trim()) {
      toast.error("Please enter at least one question");
      return;
    }

    // Parse questions - split by newlines, filter empty lines
    const newQuestions = customQuestions
      .split('\n')
      .map(q => q.trim())
      .filter(q => q.length > 0)
      .map((q, index) => ({
        text: q.replace(/^\d+[\.\)]\s*/, ''), // Remove numbering like "1." or "1)"
        type: 'Custom',
        category: 'custom',
        difficulty: 'medium',
        tip: 'Prepare specific examples from your experience'
      }));

    if (newQuestions.length === 0) {
      toast.error("No valid questions found");
      return;
    }

    setQuestions(prev => [...prev, ...newQuestions]);
    setCustomQuestions("");
    toast.success(`Added ${newQuestions.length} custom question(s)!`);
  };

  const generateAnswer = async (question) => {
    setGeneratingAnswer(true);
    setSelectedQuestion(question);
    try {
      // Build context with resume skills for better answers
      const resumeContext = resume ? `
Candidate's Skills: ${resume.skills?.join(", ") || "Not specified"}
Past Experience: ${resume.experience?.map(e => `${e.title} at ${e.company}`).join("; ") || "Not specified"}
Education: ${resume.education?.map(e => e.degree).join(", ") || "Not specified"}` : "";

      // Use KARAU DRAGON assistant for answer generation
      const response = await api.client.post(`${API}/assistant`, {
        message: `Generate a strong interview answer for this question: "${question.text || question}". 
The position is ${jobTitle} at ${company || 'a company'}.
${question.transferable_skill ? `Focus on demonstrating: ${question.transferable_skill}` : ''}
${resumeContext}

Use the STAR method if applicable. Include specific examples and quantifiable results where possible.`,
        context: "interview"
      });
      setGeneratedAnswer({
        answer: response.data.response,
        tips: ["Use specific examples from your experience", "Quantify results when possible", "Connect to the job requirements"],
        transferable_skill: question.transferable_skill
      });
    } catch (e) {
      console.error("Generate answer error:", e);
      toast.error("Failed to generate answer. Please try again.");
    }
    setGeneratingAnswer(false);
  };

  const polishStarAnswer = async (starData) => {
    setGeneratingAnswer(true);
    try {
      // Use AI assistant to polish STAR answer
      const response = await api.client.post(`${API}/assistant`, {
        message: `Polish this STAR interview answer:
Situation: ${starData.situation}
Task: ${starData.task}
Action: ${starData.action}
Result: ${starData.result}

Make it more concise, impactful, and professional while keeping the STAR structure.`,
        context: "interview"
      });
      setGeneratedAnswer({
        answer: response.data.response,
        tips: ["Be specific with numbers and results", "Show your unique contribution", "Connect to the role you're applying for"]
      });
    } catch (e) {
      toast.error("Failed to polish answer");
    }
    setGeneratingAnswer(false);
  };

  const researchCompany = async () => {
    if (!company) {
      toast.error("Please enter a company name");
      return;
    }
    setResearchingCompany(true);
    try {
      // Use AI assistant for company research
      const response = await api.client.post(`${API}/assistant`, {
        message: `Provide interview preparation research for ${company}. Include: company culture, recent news, interview tips, common interview questions, and what they look for in candidates.`,
        context: "career"
      });
      setCompanyResearch({
        company: company,
        research: response.data.response,
        generated_at: new Date().toISOString()
      });
      toast.success("Company research complete!");
    } catch (e) {
      toast.error("Failed to research company");
    }
    setResearchingCompany(false);
  };

  const startMockInterview = () => {
    if (questions.length === 0) {
      toast.error("Generate questions first");
      return;
    }
    setMockMode(true);
    setCurrentMockQuestion(0);
    setMockAnswers([]);
    setMockFeedback(null);
  };

  const submitMockAnswer = (answer) => {
    const newAnswers = [...mockAnswers, { question: questions[currentMockQuestion], answer }];
    setMockAnswers(newAnswers);
    
    if (currentMockQuestion < questions.length - 1) {
      setCurrentMockQuestion(currentMockQuestion + 1);
    } else {
      // Get feedback
      getMockFeedback(newAnswers);
    }
  };

  const getMockFeedback = async (answers) => {
    try {
      // Evaluate each answer using the Q&A practice endpoint
      const feedbackPromises = answers.map(async (a) => {
        const response = await api.client.post(`${API}/qa-practice`, {
          question: a.question.text || a.question,
          answer: a.answer,
          job_context: `${jobTitle} at ${company || 'a company'}`
        });
        return {
          question: a.question.text || a.question,
          answer: a.answer,
          score: response.data.score,
          feedback: response.data.feedback,
          strengths: response.data.strengths,
          improvements: response.data.improvements
        };
      });
      
      const allFeedback = await Promise.all(feedbackPromises);
      
      // Calculate overall score
      const avgScore = allFeedback.reduce((sum, f) => sum + f.score, 0) / allFeedback.length;
      
      setMockFeedback({
        overall_score: Math.round(avgScore * 10),
        questions_feedback: allFeedback,
        summary: `Overall performance: ${avgScore >= 7 ? 'Excellent' : avgScore >= 5 ? 'Good' : 'Needs improvement'}. You answered ${answers.length} questions with an average score of ${avgScore.toFixed(1)}/10.`
      });
      setMockMode(false);
    } catch (e) {
      toast.error("Failed to get feedback");
      setMockMode(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard!");
  };

  const exportToPDF = async () => {
    if (questions.length === 0) {
      toast.error("Generate questions first");
      return;
    }
    
    try {
      toast.info("Generating PDF...");
      const response = await api.client.post(`${API}/export/interview-prep-html`, {
        job_title: jobTitle,
        company: company || "General",
        questions: questions.map(q => ({
          text: q.text || q,
          category: q.category || "General",
          difficulty: q.difficulty || "medium",
          suggested_answer: generatedAnswer?.answer || ""
        })),
        candidate_name: resume?.full_name || '',
        notes: ""
      });
      
      // Open HTML in new window and trigger print (save as PDF)
      const printWindow = window.open('', '_blank');
      printWindow.document.write(response.data.html);
      printWindow.document.close();
      printWindow.focus();
      
      setTimeout(() => {
        printWindow.print();
      }, 500);
      
      toast.success("PDF ready! Use 'Save as PDF' in the print dialog.");
    } catch (e) {
      console.error("Export PDF error:", e);
      toast.error("Failed to generate PDF");
    }
  };

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-6xl mx-auto animate-fade-in" data-testid="interview-prep-page">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-slate-900 dark:text-slate-100 tracking-tight mb-2" style={{ fontFamily: 'IBM Plex Sans' }}>
          Interview Preparation
        </h1>
        <p className="text-slate-500 dark:text-slate-400">AI-powered interview coaching based on your resume and target role</p>
      </div>

      {/* Job Context */}
      <Card className="mb-6 border-2 border-turquoise-200 dark:border-turquoise-800">
        <CardContent className="p-4">
          <div className="flex flex-col gap-4">
            {/* Job Details Row */}
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Target Job Title</label>
                <Input
                  placeholder={t("interview.jobTitlePlaceholder")}
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  className="mt-1 dark:bg-slate-800"
                  data-testid="interview-job-title"
                />
              </div>
              <div className="flex-1">
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Company (optional)</label>
                <Input
                  placeholder={t("interview.companyPlaceholder")}
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="mt-1 dark:bg-slate-800"
                  data-testid="interview-company"
                />
              </div>
            </div>

            {/* Input Mode Selector */}
            <div className="border-t pt-4 dark:border-slate-700">
              <div className="flex flex-wrap gap-2 mb-4">
                <Button
                  variant={inputMode === "generate" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setInputMode("generate")}
                  className={inputMode === "generate" ? "bg-violet-500" : ""}
                >
                  <Sparkles className="w-4 h-4 mr-1" /> AI Generate
                </Button>
                <Button
                  variant={inputMode === "description" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setInputMode("description")}
                  className={inputMode === "description" ? "bg-violet-500" : ""}
                >
                  <FileQuestion className="w-4 h-4 mr-1" /> From Job Description
                </Button>
                <Button
                  variant={inputMode === "paste" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setInputMode("paste")}
                  className={inputMode === "paste" ? "bg-violet-500" : ""}
                >
                  <ListPlus className="w-4 h-4 mr-1" /> Paste Questions
                </Button>
              </div>

              {/* Generate Mode */}
              {inputMode === "generate" && (
                <div className="flex gap-2">
                  <Button 
                    onClick={generateQuestions}
                    disabled={generatingQuestions || !jobTitle}
                    className="bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700"
                    data-testid="generate-questions-btn"
                  >
                    {generatingQuestions ? (
                      <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Generating...</>
                    ) : (
                      <><Sparkles className="w-4 h-4 mr-2" /> Generate {resume?.skills?.length > 0 ? 'Using Resume Skills' : 'Questions'}</>
                    )}
                  </Button>
                  {questions.length > 0 && (
                    <Button 
                      variant="outline"
                      onClick={exportToPDF}
                      className="text-turquoise border-turquoise hover:bg-turquoise/10"
                      data-testid="export-pdf-btn"
                    >
                      <FileText className="w-4 h-4 mr-2" /> Export PDF
                    </Button>
                  )}
                </div>
              )}

              {/* Job Description Mode */}
              {inputMode === "description" && (
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium text-slate-700 dark:text-slate-300">{t("interview.pasteJobDescription")}</label>
                    <Textarea
                      placeholder={t("interview.jobDescriptionPlaceholder")}
                      value={jobDescription}
                      onChange={(e) => setJobDescription(e.target.value)}
                      rows={6}
                      className="mt-1 dark:bg-slate-800"
                      data-testid="job-description-input"
                    />
                  </div>
                  {resume?.skills?.length > 0 && (
                    <div className="text-xs text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-800 p-2 rounded">
                      <strong>{t("interview.yourResumeSkills")}:</strong> {resume.skills.slice(0, 8).join(", ")}{resume.skills.length > 8 ? "..." : ""}
                    </div>
                  )}
                  <div className="flex gap-2">
                    <Button 
                      onClick={generateFromJobDescription}
                      disabled={generatingQuestions || !jobDescription}
                      className="bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700"
                      data-testid="generate-from-jd-btn"
                    >
                      {generatingQuestions ? (
                        <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> {t("interview.analyzing")}</>
                      ) : (
                        <><Sparkles className="w-4 h-4 mr-2" /> {t("interview.generateFromJD")}</>
                      )}
                    </Button>
                    {questions.length > 0 && (
                      <Button 
                        variant="outline"
                        onClick={exportToPDF}
                        className="text-turquoise border-turquoise hover:bg-turquoise/10"
                      >
                        <FileText className="w-4 h-4 mr-2" /> {t("interview.exportPDF")}
                      </Button>
                    )}
                  </div>
                </div>
              )}

              {/* Paste Questions Mode */}
              {inputMode === "paste" && (
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium text-slate-700 dark:text-slate-300">{t("interview.pasteYourQuestions")}</label>
                    <Textarea
                      placeholder={t("interview.questionsPlaceholder")}
                      value={customQuestions}
                      onChange={(e) => setCustomQuestions(e.target.value)}
                      rows={6}
                      className="mt-1 dark:bg-slate-800 font-mono text-sm"
                      data-testid="custom-questions-input"
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button 
                      onClick={addCustomQuestions}
                      disabled={!customQuestions.trim()}
                      className="bg-gradient-to-r from-turquoise to-cyan-500 hover:from-turquoise/90 hover:to-cyan-600"
                      data-testid="add-questions-btn"
                    >
                      <Plus className="w-4 h-4 mr-2" /> Add Questions
                    </Button>
                    {questions.length > 0 && (
                      <>
                        <Button 
                          variant="outline"
                          onClick={() => setQuestions([])}
                          className="text-red-500 border-red-300 hover:bg-red-50 dark:hover:bg-red-900/20"
                        >
                          Clear All
                        </Button>
                        <Button 
                          variant="outline"
                          onClick={exportToPDF}
                          className="text-turquoise border-turquoise hover:bg-turquoise/10"
                        >
                          <FileText className="w-4 h-4 mr-2" /> Export PDF
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-6">
          <TabsTrigger value="questions" data-testid="tab-questions">
            <MessageSquare className="w-4 h-4 mr-2" /> Questions
          </TabsTrigger>
          <TabsTrigger value="practice" data-testid="tab-practice">
            <Mic className="w-4 h-4 mr-2" /> Mock Interview
          </TabsTrigger>
          <TabsTrigger value="research" data-testid="tab-research">
            <Building2 className="w-4 h-4 mr-2" /> Company Research
          </TabsTrigger>
          <TabsTrigger value="tips" data-testid="tab-tips">
            <Lightbulb className="w-4 h-4 mr-2" /> Tips & Tricks
          </TabsTrigger>
        </TabsList>

        {/* Questions Tab */}
        <TabsContent value="questions">
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Questions List */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-medium text-slate-900 dark:text-slate-100">Interview Questions</h3>
                {questions.length > 0 && (
                  <Badge variant="secondary">{questions.length} questions</Badge>
                )}
              </div>

              {questions.length === 0 ? (
                <Card className="border-dashed">
                  <CardContent className="p-8 text-center">
                    <MessageSquare className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                    <p className="text-slate-500 dark:text-slate-400">Choose an input method above and generate or add questions to get started</p>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-3 max-h-[500px] overflow-y-auto">
                  {questions.map((q, i) => (
                    <Card 
                      key={i}
                      className={`cursor-pointer transition-all hover:border-turquoise-400 ${
                        selectedQuestion?.text === q.text ? 'border-turquoise-500 bg-turquoise-50 dark:bg-turquoise-900/20' : ''
                      }`}
                      onClick={() => setSelectedQuestion(q)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start gap-3">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                            q.category === 'behavioral' ? 'bg-violet-100 text-violet-600 dark:bg-violet-900 dark:text-violet-300' :
                            q.category === 'technical' ? 'bg-sky-100 text-sky-600 dark:bg-sky-900 dark:text-sky-300' :
                            q.category === 'situational' ? 'bg-amber-100 text-amber-600 dark:bg-amber-900 dark:text-amber-300' :
                            q.category === 'custom' ? 'bg-pink-100 text-pink-600 dark:bg-pink-900 dark:text-pink-300' :
                            'bg-emerald-100 text-emerald-600 dark:bg-emerald-900 dark:text-emerald-300'
                          }`}>
                            {i + 1}
                          </div>
                          <div className="flex-1">
                            <p className="text-slate-900 dark:text-slate-100 text-sm">{q.text}</p>
                            <div className="flex flex-wrap items-center gap-2 mt-2">
                              <Badge variant="outline" className="text-xs capitalize">{q.category || q.type}</Badge>
                              <Badge variant="outline" className="text-xs">{q.difficulty}</Badge>
                              {q.transferable_skill && (
                                <Badge className="text-xs bg-turquoise/20 text-turquoise-700 dark:text-turquoise-300">
                                  Skill: {q.transferable_skill}
                                </Badge>
                              )}
                            </div>
                            {q.tip && (
                              <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 italic">
                                <Lightbulb className="w-3 h-3 inline mr-1" />
                                {q.tip}
                              </p>
                            )}
                          </div>
                          <ChevronRight className="w-4 h-4 text-slate-400" />
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>

            {/* Answer Section */}
            <div>
              {selectedQuestion ? (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg" style={{ fontFamily: 'IBM Plex Sans' }}>
                      {selectedQuestion.text}
                    </CardTitle>
                    <CardDescription>
                      Category: {selectedQuestion.category} | Difficulty: {selectedQuestion.difficulty}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex gap-2">
                      <Button 
                        onClick={() => generateAnswer(selectedQuestion)}
                        disabled={generatingAnswer}
                        className="flex-1"
                      >
                        {generatingAnswer ? (
                          <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Generating...</>
                        ) : (
                          <><Sparkles className="w-4 h-4 mr-2" /> AI Generate Answer</>
                        )}
                      </Button>
                    </div>

                    {selectedQuestion.category === 'behavioral' && (
                      <StarMethodHelper 
                        question={selectedQuestion.text}
                        onGenerate={polishStarAnswer}
                        generating={generatingAnswer}
                      />
                    )}

                    {generatedAnswer && (
                      <div className="space-y-4 mt-4">
                        <div className="p-4 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium text-emerald-800 dark:text-emerald-300 flex items-center gap-2">
                              <CheckCircle2 className="w-4 h-4" /> Suggested Answer
                            </h4>
                            <Button variant="ghost" size="sm" onClick={() => copyToClipboard(generatedAnswer.answer)}>
                              <Copy className="w-4 h-4" />
                            </Button>
                          </div>
                          <p className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap">
                            {generatedAnswer.answer}
                          </p>
                        </div>

                        {generatedAnswer.key_points && (
                          <div>
                            <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Key Points to Mention</h4>
                            <ul className="space-y-1">
                              {generatedAnswer.key_points.map((point, i) => (
                                <li key={i} className="text-sm text-slate-600 dark:text-slate-400 flex items-start gap-2">
                                  <span className="text-turquoise-500">•</span> {point}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {generatedAnswer.tips && (
                          <div className="p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
                            <h4 className="text-sm font-medium text-amber-800 dark:text-amber-300 mb-1">💡 Pro Tip</h4>
                            <p className="text-sm text-amber-700 dark:text-amber-400">{generatedAnswer.tips}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ) : (
                <Card className="h-full flex items-center justify-center border-dashed">
                  <CardContent className="p-8 text-center">
                    <Target className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                    <p className="text-slate-500 dark:text-slate-400">Select a question to see AI-generated answers</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </TabsContent>

        {/* Mock Interview Tab */}
        <TabsContent value="practice">
          {!mockMode ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2" style={{ fontFamily: 'IBM Plex Sans' }}>
                  <Mic className="w-5 h-5 text-violet-500" />
                  Mock Interview Mode
                </CardTitle>
                <CardDescription>
                  Practice answering questions and get AI feedback on your responses
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {mockFeedback ? (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="font-medium text-slate-900 dark:text-slate-100">Interview Feedback</h3>
                      <Badge className="bg-emerald-100 text-emerald-700">
                        Score: {mockFeedback.overall_score}/100
                      </Badge>
                    </div>
                    
                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="p-4 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg">
                        <h4 className="font-medium text-emerald-800 dark:text-emerald-300 mb-2">Strengths</h4>
                        <ul className="space-y-1">
                          {mockFeedback.strengths?.map((s, i) => (
                            <li key={i} className="text-sm text-emerald-700 dark:text-emerald-400">✓ {s}</li>
                          ))}
                        </ul>
                      </div>
                      <div className="p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
                        <h4 className="font-medium text-amber-800 dark:text-amber-300 mb-2">Areas to Improve</h4>
                        <ul className="space-y-1">
                          {mockFeedback.improvements?.map((s, i) => (
                            <li key={i} className="text-sm text-amber-700 dark:text-amber-400">→ {s}</li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    <Button onClick={() => setMockFeedback(null)} variant="outline" className="w-full">
                      <RefreshCw className="w-4 h-4 mr-2" /> Try Again
                    </Button>
                  </div>
                ) : (
                  <>
                    <div className="text-center py-8">
                      <Mic className="w-16 h-16 text-violet-400 mx-auto mb-4" />
                      <p className="text-slate-600 dark:text-slate-400 mb-4">
                        Answer {questions.length} questions and receive personalized feedback
                      </p>
                      <Button 
                        onClick={startMockInterview}
                        disabled={questions.length === 0}
                        size="lg"
                        className="bg-gradient-to-r from-violet-500 to-purple-600"
                      >
                        <Mic className="w-4 h-4 mr-2" /> Start Mock Interview
                      </Button>
                    </div>
                    {questions.length === 0 && (
                      <p className="text-center text-sm text-amber-600">
                        Generate questions first from the Questions tab
                      </p>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          ) : (
            <MockInterviewMode
              question={questions[currentMockQuestion]}
              questionNumber={currentMockQuestion + 1}
              totalQuestions={questions.length}
              onSubmit={submitMockAnswer}
              onSkip={() => submitMockAnswer("(Skipped)")}
            />
          )}
        </TabsContent>

        {/* Company Research Tab */}
        <TabsContent value="research">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2" style={{ fontFamily: 'IBM Plex Sans' }}>
                <Building2 className="w-5 h-5 text-emerald-500" />
                Company Research
              </CardTitle>
              <CardDescription>
                Get insights about the company to prepare for your interview
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-3">
                <Input
                  placeholder={t("interview.enterCompanyName")}
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="flex-1 dark:bg-slate-800"
                />
                <Button onClick={researchCompany} disabled={researchingCompany || !company}>
                  {researchingCompany ? (
                    <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> {t("interview.researching")}</>
                  ) : (
                    <><BookOpen className="w-4 h-4 mr-2" /> {t("interview.research")}</>
                  )}
                </Button>
              </div>

              {companyResearch && (
                <div className="space-y-4 mt-4">
                  <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                    <h4 className="font-medium text-slate-900 dark:text-slate-100 mb-2">{t("interview.researchFor")} {companyResearch.company}</h4>
                    <div className="text-sm text-slate-600 dark:text-slate-400 whitespace-pre-wrap">{companyResearch.research}</div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tips Tab */}
        <TabsContent value="tips">
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg" style={{ fontFamily: 'IBM Plex Sans' }}>
                  <Clock className="w-5 h-5 text-sky-500" />
                  Before the Interview
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {[
                  "Research the company thoroughly",
                  "Review the job description and match your experience",
                  "Prepare 3-5 questions to ask the interviewer",
                  "Practice the STAR method for behavioral questions",
                  "Test your technology (for virtual interviews)",
                  "Plan your outfit the night before",
                  "Get a good night's sleep"
                ].map((tip, i) => (
                  <div key={i} className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 mt-0.5" />
                    <span className="text-sm text-slate-600 dark:text-slate-400">{tip}</span>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg" style={{ fontFamily: 'IBM Plex Sans' }}>
                  <MessageSquare className="w-5 h-5 text-violet-500" />
                  During the Interview
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {[
                  "Listen carefully to each question before answering",
                  "Use specific examples from your experience",
                  "Be concise - aim for 1-2 minute answers",
                  "Show enthusiasm for the role",
                  "Ask clarifying questions if needed",
                  "Take notes if appropriate",
                  "End with thoughtful questions about the role/company"
                ].map((tip, i) => (
                  <div key={i} className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-violet-500 mt-0.5" />
                    <span className="text-sm text-slate-600 dark:text-slate-400">{tip}</span>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg" style={{ fontFamily: 'IBM Plex Sans' }}>
                  <Award className="w-5 h-5 text-amber-500" />
                  STAR Method Guide
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-4 gap-4">
                  {[
                    { letter: "S", title: "Situation", desc: "Set the scene. Describe the context and background of your example." },
                    { letter: "T", title: "Task", desc: "Explain your responsibility. What was expected of you?" },
                    { letter: "A", title: "Action", desc: "Detail the specific steps you took. Focus on YOUR contribution." },
                    { letter: "R", title: "Result", desc: "Share the outcomes. Use metrics and numbers when possible." }
                  ].map((item, i) => (
                    <div key={i} className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg text-center">
                      <div className="w-12 h-12 rounded-full bg-amber-100 dark:bg-amber-900 text-amber-600 dark:text-amber-300 flex items-center justify-center text-xl font-bold mx-auto mb-2">
                        {item.letter}
                      </div>
                      <h4 className="font-medium text-slate-900 dark:text-slate-100 mb-1">{item.title}</h4>
                      <p className="text-xs text-slate-500 dark:text-slate-400">{item.desc}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

// Mock Interview Mode Component
const MockInterviewMode = ({ question, questionNumber, totalQuestions, onSubmit, onSkip }) => {
  const { t } = useTranslation();
  const [answer, setAnswer] = useState("");
  const [timeLeft, setTimeLeft] = useState(120); // 2 minutes per question
  const answerRef = useRef("");
  const onSubmitRef = useRef(onSubmit);

  // Keep onSubmit ref in sync
  useEffect(() => {
    onSubmitRef.current = onSubmit;
  }, [onSubmit]);

  // Sync answer ref
  useEffect(() => {
    answerRef.current = answer;
  }, [answer]);

  // Reset state when question changes
  useEffect(() => {
    setAnswer("");
    setTimeLeft(120);
  }, [question]);

  // Timer effect
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft(t => {
        if (t <= 1) {
          onSubmitRef.current(answerRef.current || "(Time's up - no answer)");
          return 120;
        }
        return t - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [question]);

  return (
    <Card className="border-2 border-violet-200 dark:border-violet-800">
      <CardHeader>
        <div className="flex items-center justify-between">
          <Badge variant="outline">Question {questionNumber} of {totalQuestions}</Badge>
          <Badge className={timeLeft < 30 ? "bg-red-100 text-red-700" : "bg-slate-100 text-slate-700 dark:text-slate-300"}>
            <Clock className="w-3 h-3 mr-1" />
            {Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}
          </Badge>
        </div>
        <CardTitle className="text-xl mt-4" style={{ fontFamily: 'IBM Plex Sans' }}>
          {question?.text}
        </CardTitle>
        <div className="flex gap-2 mt-2">
          <Badge variant="secondary">{question?.category}</Badge>
          <Badge variant="secondary">{question?.difficulty}</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <Textarea
          placeholder={t("interview.typeAnswerPlaceholder")}
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          className="min-h-[200px] dark:bg-slate-800"
          data-testid="mock-answer-input"
        />
        <div className="flex gap-3">
          <Button onClick={onSkip} variant="outline">
            {t("interview.skipQuestion")}
          </Button>
          <Button 
            onClick={() => onSubmit(answer)} 
            disabled={!answer.trim()}
            className="flex-1 bg-gradient-to-r from-violet-500 to-purple-600"
          >
            {t("interview.submitAnswer")} <ChevronRight className="w-4 h-4 ml-1" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default InterviewPrepPage;
