import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { jsPDF } from "jspdf";
import { 
  Sparkles, Loader2, Building2, MessageSquare, Copy, CheckCircle2, Plus, Trash2,
  Star, BookmarkPlus, ChevronDown, ChevronUp, Download, FileText
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const QAPracticePage = ({ resume }) => {
  const [activeTab, setActiveTab] = useState("generate");
  
  // Job context
  const [companyName, setCompanyName] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  
  // Questions and answers
  const [questions, setQuestions] = useState([{ id: 1, text: "", answer: null, loading: false, saved: false }]);
  const [generatingAll, setGeneratingAll] = useState(false);
  
  // Favorites
  const [favorites, setFavorites] = useState([]);
  const [loadingFavorites, setLoadingFavorites] = useState(false);
  const [expandedFavorite, setExpandedFavorite] = useState(null);

  // Load favorites on mount
  useEffect(() => {
    fetchFavorites();
  }, []);

  const fetchFavorites = async () => {
    setLoadingFavorites(true);
    try {
      const response = await axios.get(`${API}/qa-practice/favorites`);
      setFavorites(response.data.favorites || []);
    } catch (error) {
      console.error("Failed to load favorites:", error);
    }
    setLoadingFavorites(false);
  };

  // Add a new question
  const addQuestion = () => {
    setQuestions([...questions, { id: Date.now(), text: "", answer: null, loading: false, saved: false }]);
  };

  // Remove a question
  const removeQuestion = (id) => {
    if (questions.length > 1) {
      setQuestions(questions.filter(q => q.id !== id));
    }
  };

  // Update question text
  const updateQuestion = (id, text) => {
    setQuestions(questions.map(q => q.id === id ? { ...q, text } : q));
  };

  // Generate answer for a single question
  const generateAnswer = async (id) => {
    const question = questions.find(q => q.id === id);
    if (!question?.text.trim()) {
      toast.error("Please enter a question");
      return;
    }

    setQuestions(questions.map(q => q.id === id ? { ...q, loading: true } : q));

    try {
      const response = await axios.post(`${API}/qa-practice/generate-answer`, {
        question: question.text,
        question_type: "behavioral",
        job_context: {
          company_name: companyName,
          job_title: jobTitle,
          job_description: jobDescription
        }
      });

      setQuestions(questions.map(q => 
        q.id === id ? { ...q, answer: response.data.ai_answer, loading: false, saved: false } : q
      ));
      toast.success("Answer generated!");
    } catch (error) {
      toast.error("Failed to generate answer");
      setQuestions(questions.map(q => q.id === id ? { ...q, loading: false } : q));
    }
  };

  // Generate answers for all questions
  const generateAllAnswers = async () => {
    const questionsWithText = questions.filter(q => q.text.trim());
    if (questionsWithText.length === 0) {
      toast.error("Please enter at least one question");
      return;
    }

    setGeneratingAll(true);
    setQuestions(questions.map(q => q.text.trim() ? { ...q, loading: true } : q));

    for (const question of questionsWithText) {
      try {
        const response = await axios.post(`${API}/qa-practice/generate-answer`, {
          question: question.text,
          question_type: "behavioral",
          job_context: {
            company_name: companyName,
            job_title: jobTitle,
            job_description: jobDescription
          }
        });

        setQuestions(prev => prev.map(q => 
          q.id === question.id ? { ...q, answer: response.data.ai_answer, loading: false, saved: false } : q
        ));
      } catch (error) {
        setQuestions(prev => prev.map(q => 
          q.id === question.id ? { ...q, loading: false } : q
        ));
      }
    }

    setGeneratingAll(false);
    toast.success("All answers generated!");
  };

  // Save answer to favorites
  const saveToFavorites = async (question) => {
    if (!question.answer) return;

    try {
      await axios.post(`${API}/qa-practice/favorites/save`, {
        question: question.text,
        answer: question.answer.suggested_answer,
        key_points: question.answer.key_points || [],
        job_title: jobTitle,
        company_name: companyName
      });

      setQuestions(questions.map(q => 
        q.id === question.id ? { ...q, saved: true } : q
      ));
      
      toast.success("Saved to favorites!");
      fetchFavorites(); // Refresh favorites list
    } catch (error) {
      toast.error("Failed to save");
    }
  };

  // Delete favorite
  const deleteFavorite = async (id) => {
    try {
      await axios.delete(`${API}/qa-practice/favorites/${id}`);
      setFavorites(favorites.filter(f => f.id !== id));
      toast.success("Removed from favorites");
    } catch (error) {
      toast.error("Failed to delete");
    }
  };

  // Copy answer to clipboard
  const copyAnswer = (text) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard!");
  };

  // Export favorites to PDF
  const exportToPDF = () => {
    if (favorites.length === 0) {
      toast.error("No favorites to export");
      return;
    }

    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const margin = 20;
    const maxWidth = pageWidth - 2 * margin;
    let yPos = 20;

    // Title
    doc.setFontSize(20);
    doc.setFont("helvetica", "bold");
    doc.text("Interview Q&A Study Guide", margin, yPos);
    yPos += 10;

    // Date
    doc.setFontSize(10);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(128, 128, 128);
    doc.text(`Generated: ${new Date().toLocaleDateString()}`, margin, yPos);
    yPos += 15;

    doc.setTextColor(0, 0, 0);

    favorites.forEach((fav, index) => {
      // Check if we need a new page
      if (yPos > 250) {
        doc.addPage();
        yPos = 20;
      }

      // Question number and job context
      doc.setFontSize(12);
      doc.setFont("helvetica", "bold");
      doc.setTextColor(0, 128, 128); // Turquoise
      const questionHeader = `Q${index + 1}${fav.job_title ? ` - ${fav.job_title}` : ''}${fav.company_name ? ` at ${fav.company_name}` : ''}`;
      doc.text(questionHeader, margin, yPos);
      yPos += 8;

      // Question text
      doc.setTextColor(0, 0, 0);
      doc.setFont("helvetica", "bold");
      doc.setFontSize(11);
      const questionLines = doc.splitTextToSize(fav.question, maxWidth);
      doc.text(questionLines, margin, yPos);
      yPos += questionLines.length * 6 + 5;

      // Answer
      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      const answerLines = doc.splitTextToSize(fav.answer, maxWidth);
      
      // Check if answer will fit on current page
      if (yPos + answerLines.length * 5 > 280) {
        doc.addPage();
        yPos = 20;
      }
      
      doc.text(answerLines, margin, yPos);
      yPos += answerLines.length * 5 + 5;

      // Key points
      if (fav.key_points && fav.key_points.length > 0) {
        doc.setFont("helvetica", "italic");
        doc.setFontSize(9);
        doc.setTextColor(80, 80, 80);
        doc.text("Key Points:", margin, yPos);
        yPos += 5;
        
        fav.key_points.forEach((point) => {
          const pointLines = doc.splitTextToSize(`• ${point}`, maxWidth - 5);
          if (yPos + pointLines.length * 4 > 280) {
            doc.addPage();
            yPos = 20;
          }
          doc.text(pointLines, margin + 5, yPos);
          yPos += pointLines.length * 4;
        });
      }

      yPos += 15; // Space between Q&As
      doc.setTextColor(0, 0, 0);
    });

    // Save the PDF
    doc.save("interview-qa-study-guide.pdf");
    toast.success("PDF exported successfully!");
  };

  return (
    <div className="p-6 md:p-8 max-w-4xl mx-auto space-y-6" data-testid="qa-practice-page">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white" style={{ fontFamily: 'IBM Plex Sans' }}>
          Q&A Answer Generator
        </h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">
          Generate AI interview answers and save your favorites
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-2 w-full max-w-xs">
          <TabsTrigger value="generate" className="flex items-center gap-2">
            <Sparkles className="w-4 h-4" /> Generate
          </TabsTrigger>
          <TabsTrigger value="favorites" className="flex items-center gap-2">
            <Star className="w-4 h-4" /> Favorites
            {favorites.length > 0 && (
              <Badge variant="secondary" className="ml-1 text-xs">{favorites.length}</Badge>
            )}
          </TabsTrigger>
        </TabsList>

        {/* Generate Tab */}
        <TabsContent value="generate" className="space-y-6 mt-6">
          {/* Job Context */}
          <Card>
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-2 text-lg">
                <Building2 className="w-5 h-5 text-turquoise" />
                Job Information
              </CardTitle>
              <CardDescription>
                Provide job details for more relevant answers
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Company Name</label>
                  <Input 
                    placeholder="e.g., Google, Amazon"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    className="mt-1"
                    data-testid="company-input"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Job Title *</label>
                  <Input 
                    placeholder="e.g., Software Engineer"
                    value={jobTitle}
                    onChange={(e) => setJobTitle(e.target.value)}
                    className="mt-1"
                    data-testid="job-title-input"
                  />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Job Description (optional)</label>
                <Textarea 
                  placeholder="Paste the job description for more accurate answers..."
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  className="mt-1 min-h-[80px]"
                  data-testid="job-description-input"
                />
              </div>
            </CardContent>
          </Card>

          {/* Questions Section */}
          <Card>
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <MessageSquare className="w-5 h-5 text-violet-500" />
                    Interview Questions
                  </CardTitle>
                  <CardDescription>
                    Add your interview questions below
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={addQuestion}
                    data-testid="add-question-btn"
                  >
                    <Plus className="w-4 h-4 mr-1" /> Add Question
                  </Button>
                  <Button 
                    size="sm"
                    onClick={generateAllAnswers}
                    disabled={generatingAll || questions.every(q => !q.text.trim())}
                    className="bg-violet-600 hover:bg-violet-700"
                    data-testid="generate-all-btn"
                  >
                    {generatingAll ? (
                      <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                    ) : (
                      <Sparkles className="w-4 h-4 mr-1" />
                    )}
                    Generate All
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {questions.map((question, index) => (
                <div key={question.id} className="space-y-3 pb-6 border-b border-slate-100 dark:border-slate-800 last:border-0 last:pb-0">
                  {/* Question Input */}
                  <div className="flex gap-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="outline" className="text-xs">Q{index + 1}</Badge>
                      </div>
                      <Textarea 
                        placeholder="Enter your interview question..."
                        value={question.text}
                        onChange={(e) => updateQuestion(question.id, e.target.value)}
                        className="min-h-[60px]"
                        data-testid={`question-input-${index}`}
                      />
                    </div>
                    <div className="flex flex-col gap-2 pt-7">
                      <Button 
                        size="sm"
                        onClick={() => generateAnswer(question.id)}
                        disabled={question.loading || !question.text.trim()}
                        className="bg-turquoise hover:bg-turquoise/90"
                        data-testid={`generate-btn-${index}`}
                      >
                        {question.loading ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <Sparkles className="w-4 h-4" />
                        )}
                      </Button>
                      {questions.length > 1 && (
                        <Button 
                          size="sm"
                          variant="ghost"
                          onClick={() => removeQuestion(question.id)}
                          className="text-red-500 hover:text-red-600 hover:bg-red-50"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </div>

                  {/* Generated Answer */}
                  {question.answer && (
                    <div className="ml-4 p-4 bg-gradient-to-br from-turquoise/5 to-emerald-50 dark:from-turquoise/10 dark:to-emerald-900/20 rounded-lg border border-turquoise/20">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <Sparkles className="w-4 h-4 text-turquoise" />
                          <span className="text-sm font-medium text-turquoise">AI Answer</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Button 
                            size="sm" 
                            variant="ghost"
                            onClick={() => saveToFavorites(question)}
                            disabled={question.saved}
                            className={question.saved ? "text-amber-500" : "text-slate-500 hover:text-amber-500"}
                            title={question.saved ? "Saved!" : "Save to favorites"}
                            data-testid={`save-favorite-btn-${index}`}
                          >
                            {question.saved ? (
                              <Star className="w-4 h-4 fill-amber-500" />
                            ) : (
                              <BookmarkPlus className="w-4 h-4" />
                            )}
                          </Button>
                          <Button 
                            size="sm" 
                            variant="ghost"
                            onClick={() => copyAnswer(question.answer.suggested_answer)}
                            className="text-slate-500 hover:text-slate-700"
                          >
                            <Copy className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                      
                      <p className="text-slate-700 dark:text-slate-300 text-sm whitespace-pre-wrap mb-4">
                        {question.answer.suggested_answer}
                      </p>

                      {/* Key Points */}
                      {question.answer.key_points?.length > 0 && (
                        <div className="pt-3 border-t border-turquoise/10">
                          <p className="text-xs font-medium text-slate-600 dark:text-slate-400 mb-2">Key Points:</p>
                          <ul className="space-y-1">
                            {question.answer.key_points.map((point, i) => (
                              <li key={i} className="text-xs text-slate-600 dark:text-slate-400 flex items-start gap-2">
                                <CheckCircle2 className="w-3 h-3 text-turquoise mt-0.5 shrink-0" />
                                {point}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Favorites Tab */}
        <TabsContent value="favorites" className="space-y-4 mt-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Star className="w-5 h-5 text-amber-500" />
                  Saved Answers
                </CardTitle>
                <CardDescription>
                  Your favorite answers for quick reference during interviews
                </CardDescription>
              </div>
              {favorites.length > 0 && (
                <Button
                  onClick={exportToPDF}
                  variant="outline"
                  size="sm"
                  className="flex items-center gap-2"
                  data-testid="export-pdf-btn"
                >
                  <Download className="w-4 h-4" />
                  Export PDF
                </Button>
              )}
            </CardHeader>
            <CardContent>
              {loadingFavorites ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin text-turquoise" />
                </div>
              ) : favorites.length === 0 ? (
                <div className="text-center py-8 text-slate-500">
                  <Star className="w-12 h-12 mx-auto mb-3 opacity-20" />
                  <p>No saved answers yet</p>
                  <p className="text-sm mt-1">Generate answers and click the bookmark icon to save them</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {favorites.map((fav) => (
                    <div 
                      key={fav.id} 
                      className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700"
                    >
                      {/* Question Header */}
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <p className="font-medium text-slate-800 dark:text-slate-200 text-sm">
                            {fav.question}
                          </p>
                          {(fav.job_title || fav.company_name) && (
                            <p className="text-xs text-slate-500 mt-1">
                              {fav.job_title}{fav.company_name && ` at ${fav.company_name}`}
                            </p>
                          )}
                        </div>
                        <div className="flex items-center gap-1 ml-2">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => setExpandedFavorite(expandedFavorite === fav.id ? null : fav.id)}
                            className="text-slate-500"
                          >
                            {expandedFavorite === fav.id ? (
                              <ChevronUp className="w-4 h-4" />
                            ) : (
                              <ChevronDown className="w-4 h-4" />
                            )}
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => copyAnswer(fav.answer)}
                            className="text-slate-500 hover:text-slate-700"
                          >
                            <Copy className="w-4 h-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => deleteFavorite(fav.id)}
                            className="text-red-500 hover:text-red-600 hover:bg-red-50"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>

                      {/* Expanded Answer */}
                      {expandedFavorite === fav.id && (
                        <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
                          <p className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap">
                            {fav.answer}
                          </p>
                          
                          {fav.key_points?.length > 0 && (
                            <div className="mt-4">
                              <p className="text-xs font-medium text-slate-600 dark:text-slate-400 mb-2">Key Points:</p>
                              <ul className="space-y-1">
                                {fav.key_points.map((point, i) => (
                                  <li key={i} className="text-xs text-slate-600 dark:text-slate-400 flex items-start gap-2">
                                    <CheckCircle2 className="w-3 h-3 text-turquoise mt-0.5 shrink-0" />
                                    {point}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                          
                          <p className="text-xs text-slate-400 mt-4">
                            Saved {new Date(fav.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Tips */}
      <div className="text-center text-sm text-slate-500 dark:text-slate-400 py-4">
        <p>Tip: Save your best answers to quickly review them before your actual interview</p>
      </div>
    </div>
  );
};

export default QAPracticePage;
