import { useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { 
  Sparkles, Loader2, Building2, MessageSquare, Copy, CheckCircle2, Plus, Trash2
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const QAPracticePage = ({ resume }) => {
  // Job context
  const [companyName, setCompanyName] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  
  // Questions and answers
  const [questions, setQuestions] = useState([{ id: 1, text: "", answer: null, loading: false }]);
  const [generatingAll, setGeneratingAll] = useState(false);

  // Add a new question
  const addQuestion = () => {
    setQuestions([...questions, { id: Date.now(), text: "", answer: null, loading: false }]);
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
        q.id === id ? { ...q, answer: response.data.ai_answer, loading: false } : q
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
          q.id === question.id ? { ...q, answer: response.data.ai_answer, loading: false } : q
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

  // Copy answer to clipboard
  const copyAnswer = (text) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard!");
  };

  return (
    <div className="p-6 md:p-8 max-w-4xl mx-auto space-y-6" data-testid="qa-practice-page">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white" style={{ fontFamily: 'IBM Plex Sans' }}>
          Q&A Answer Generator
        </h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">
          Enter job details and questions to get AI-generated interview answers
        </p>
      </div>

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
                    <Button 
                      size="sm" 
                      variant="ghost"
                      onClick={() => copyAnswer(question.answer.suggested_answer)}
                      className="text-slate-500 hover:text-slate-700"
                    >
                      <Copy className="w-4 h-4" />
                    </Button>
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

      {/* Tips */}
      <div className="text-center text-sm text-slate-500 dark:text-slate-400 py-4">
        <p>Tip: Provide a job description for more tailored answers that match the role requirements</p>
      </div>
    </div>
  );
};

export default QAPracticePage;
