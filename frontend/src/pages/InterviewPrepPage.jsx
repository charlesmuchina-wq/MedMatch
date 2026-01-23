import { useState, useEffect } from "react";
import { toast } from "sonner";
import { 
  Mic, MessageSquare, Sparkles, Loader2, BookOpen, Target,
  CheckCircle2, Lightbulb, Users, Building2, ChevronRight,
  Clock, Star, Award, RefreshCw, Copy, Volume2, FileText, Download, Languages
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
const StarMethodHelper = ({ question, onGenerate, generating }) => {
  const [situation, setSituation] = useState("");
  const [task, setTask] = useState("");
  const [action, setAction] = useState("");
  const [result, setResult] = useState("");

  return (
    <div className="space-y-4 p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
      <h4 className="font-medium text-slate-900 dark:text-slate-100 flex items-center gap-2">
        <Star className="w-4 h-4 text-amber-500" />
        STAR Method Builder
      </h4>
      <p className="text-sm text-slate-500 dark:text-slate-400">Structure your answer using the STAR method</p>
      
      <div className="grid gap-3">
        <div>
          <label className="text-xs font-medium text-slate-600 dark:text-slate-300">S - Situation</label>
          <Textarea 
            placeholder="Describe the context or background..."
            value={situation}
            onChange={(e) => setSituation(e.target.value)}
            className="mt-1 h-20 dark:bg-slate-700"
          />
        </div>
        <div>
          <label className="text-xs font-medium text-slate-600 dark:text-slate-300">T - Task</label>
          <Textarea 
            placeholder="What was your responsibility?"
            value={task}
            onChange={(e) => setTask(e.target.value)}
            className="mt-1 h-20 dark:bg-slate-700"
          />
        </div>
        <div>
          <label className="text-xs font-medium text-slate-600 dark:text-slate-300">A - Action</label>
          <Textarea 
            placeholder="What steps did you take?"
            value={action}
            onChange={(e) => setAction(e.target.value)}
            className="mt-1 h-20 dark:bg-slate-700"
          />
        </div>
        <div>
          <label className="text-xs font-medium text-slate-600 dark:text-slate-300">R - Result</label>
          <Textarea 
            placeholder="What was the outcome? Include metrics if possible..."
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
  const [activeTab, setActiveTab] = useState("questions");
  const [jobTitle, setJobTitle] = useState("");
  const [company, setCompany] = useState("");
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

  const generateQuestions = async () => {
    if (!jobTitle) {
      toast.error("Please enter a job title");
      return;
    }

    setGeneratingQuestions(true);
    try {
      // Use new AI interview prep endpoint
      const response = await api.client.post(`${API}/api/interview-prep`, {
        job_title: jobTitle,
        company: company,
        difficulty: "medium",
        num_questions: 5,
        topics: resume?.skills?.slice(0, 5) || []
      });
      
      // Map response to expected format
      const questions = response.data.questions?.map(q => ({
        text: q.question,
        type: q.type,
        tip: q.tip,
        sample_points: q.sample_points
      })) || [];
      
      setQuestions(questions);
      toast.success(`Generated ${questions.length} interview questions!`);
    } catch (e) {
      toast.error("Failed to generate questions");
    }
    setGeneratingQuestions(false);
  };

  const generateAnswer = async (question) => {
    setGeneratingAnswer(true);
    setSelectedQuestion(question);
    try {
      // Use KARAU DRAGON assistant for answer generation
      const response = await api.client.post(`${API}/api/assistant`, {
        message: `Generate a strong interview answer for this question: "${question.text || question}". The position is ${jobTitle} at ${company || 'a company'}. Use the STAR method if applicable.`,
        context: "interview"
      });
      setGeneratedAnswer({
        answer: response.data.response,
        tips: ["Use specific examples", "Quantify results when possible", "Connect to the job requirements"]
      });
    } catch (e) {
      toast.error("Failed to generate answer");
    }
    setGeneratingAnswer(false);
  };

  const polishStarAnswer = async (starData) => {
    setGeneratingAnswer(true);
    try {
      const response = await api.client.post(`${API}/interview/polish-star`, starData);
      setGeneratedAnswer(response.data);
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
      const response = await api.client.post(`${API}/interview/research-company`, { company });
      setCompanyResearch(response.data);
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
        const response = await api.client.post(`${API}/api/qa-practice`, {
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
      const response = await axios.post(`${API}/export/interview-prep-html`, {
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
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Target Job Title</label>
              <Input
                placeholder="e.g., Supplier Quality Manager"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                className="mt-1 dark:bg-slate-800"
                data-testid="interview-job-title"
              />
            </div>
            <div className="flex-1">
              <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Company (optional)</label>
              <Input
                placeholder="e.g., Medtronic"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                className="mt-1 dark:bg-slate-800"
                data-testid="interview-company"
              />
            </div>
            <div className="flex items-end gap-2">
              <Button 
                onClick={generateQuestions}
                disabled={generatingQuestions || !jobTitle}
                className="bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700"
                data-testid="generate-questions-btn"
              >
                {generatingQuestions ? (
                  <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Generating...</>
                ) : (
                  <><Sparkles className="w-4 h-4 mr-2" /> Generate Questions</>
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
                    <p className="text-slate-500 dark:text-slate-400">Enter a job title and click "Generate Questions" to get started</p>
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
                            'bg-emerald-100 text-emerald-600 dark:bg-emerald-900 dark:text-emerald-300'
                          }`}>
                            {i + 1}
                          </div>
                          <div className="flex-1">
                            <p className="text-slate-900 dark:text-slate-100 text-sm">{q.text}</p>
                            <div className="flex items-center gap-2 mt-2">
                              <Badge variant="outline" className="text-xs">{q.category}</Badge>
                              <Badge variant="outline" className="text-xs">{q.difficulty}</Badge>
                            </div>
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
                  placeholder="Enter company name"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="flex-1 dark:bg-slate-800"
                />
                <Button onClick={researchCompany} disabled={researchingCompany || !company}>
                  {researchingCompany ? (
                    <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Researching...</>
                  ) : (
                    <><BookOpen className="w-4 h-4 mr-2" /> Research</>
                  )}
                </Button>
              </div>

              {companyResearch && (
                <div className="space-y-4 mt-4">
                  <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                    <h4 className="font-medium text-slate-900 dark:text-slate-100 mb-2">Company Overview</h4>
                    <p className="text-sm text-slate-600 dark:text-slate-400">{companyResearch.overview}</p>
                  </div>

                  {companyResearch.culture && (
                    <div className="p-4 bg-violet-50 dark:bg-violet-900/20 rounded-lg">
                      <h4 className="font-medium text-violet-800 dark:text-violet-300 mb-2">Company Culture</h4>
                      <p className="text-sm text-violet-700 dark:text-violet-400">{companyResearch.culture}</p>
                    </div>
                  )}

                  {companyResearch.interview_tips && (
                    <div className="p-4 bg-turquoise-50 dark:bg-turquoise-900/20 rounded-lg">
                      <h4 className="font-medium text-turquoise-800 dark:text-turquoise-300 mb-2">Interview Tips for This Company</h4>
                      <ul className="space-y-1">
                        {companyResearch.interview_tips.map((tip, i) => (
                          <li key={i} className="text-sm text-turquoise-700 dark:text-turquoise-400">• {tip}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {companyResearch.questions_to_ask && (
                    <div className="p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
                      <h4 className="font-medium text-amber-800 dark:text-amber-300 mb-2">Questions to Ask Them</h4>
                      <ul className="space-y-1">
                        {companyResearch.questions_to_ask.map((q, i) => (
                          <li key={i} className="text-sm text-amber-700 dark:text-amber-400">• {q}</li>
                        ))}
                      </ul>
                    </div>
                  )}
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
  const [answer, setAnswer] = useState("");
  const [timeLeft, setTimeLeft] = useState(120); // 2 minutes per question

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft(t => {
        if (t <= 1) {
          onSubmit(answer || "(Time's up - no answer)");
          return 120;
        }
        return t - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [question]);

  useEffect(() => {
    setAnswer("");
    setTimeLeft(120);
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
          placeholder="Type your answer here... (You have 2 minutes)"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          className="min-h-[200px] dark:bg-slate-800"
          data-testid="mock-answer-input"
        />
        <div className="flex gap-3">
          <Button onClick={onSkip} variant="outline">
            Skip Question
          </Button>
          <Button 
            onClick={() => onSubmit(answer)} 
            disabled={!answer.trim()}
            className="flex-1 bg-gradient-to-r from-violet-500 to-purple-600"
          >
            Submit Answer <ChevronRight className="w-4 h-4 ml-1" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default InterviewPrepPage;
