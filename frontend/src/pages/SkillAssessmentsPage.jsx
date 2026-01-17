import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import { useTheme } from "@/App";
import { 
  Award, Brain, Clock, Trophy, CheckCircle, XCircle, Play,
  Loader2, ChevronRight, Star, Target, Zap, Medal
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";

const API = process.env.REACT_APP_BACKEND_URL;

const SkillAssessmentsPage = ({ user }) => {
  const navigate = useNavigate();
  const { isDark } = useTheme();
  
  const [assessments, setAssessments] = useState([]);
  const [categories, setCategories] = useState({});
  const [myBadges, setMyBadges] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Assessment taking state
  const [activeAssessment, setActiveAssessment] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [results, setResults] = useState(null);
  const [showResultsDialog, setShowResultsDialog] = useState(false);
  const [timeLeft, setTimeLeft] = useState(0);

  useEffect(() => {
    fetchAssessments();
    fetchMyBadges();
  }, []);

  useEffect(() => {
    if (timeLeft > 0 && activeAssessment) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0 && activeAssessment) {
      // Auto-submit when time runs out
      handleSubmitAssessment();
    }
  }, [timeLeft, activeAssessment]);

  const fetchAssessments = async () => {
    try {
      const response = await axios.get(`${API}/api/skills/available`);
      setAssessments(response.data.assessments || []);
      setCategories(response.data.by_category || {});
    } catch (e) {
      toast.error("Failed to load assessments");
    }
    setLoading(false);
  };

  const fetchMyBadges = async () => {
    try {
      const response = await axios.get(`${API}/api/skills/my-badges`);
      setMyBadges(response.data.badges || []);
    } catch (e) {
      console.error("Failed to load badges");
    }
  };

  const startAssessment = async (skillName, difficulty = "intermediate") => {
    setSubmitting(true);
    try {
      const response = await axios.post(`${API}/api/skills/start`, {
        skill_name: skillName,
        difficulty
      });
      
      setActiveAssessment({
        id: response.data.assessment_id,
        skill_name: response.data.skill_name,
        time_limit: response.data.time_limit
      });
      setQuestions(response.data.questions || []);
      setCurrentQuestion(0);
      setAnswers({});
      setTimeLeft(response.data.time_limit * 60); // Convert to seconds
      
    } catch (e) {
      toast.error(e.response?.data?.detail || "Failed to start assessment");
    }
    setSubmitting(false);
  };

  const handleAnswer = (questionIndex, answer) => {
    setAnswers({
      ...answers,
      [questionIndex]: answer
    });
  };

  const handleSubmitAssessment = async () => {
    if (!activeAssessment) return;
    
    setSubmitting(true);
    try {
      const answerList = Object.entries(answers).map(([idx, answer]) => ({
        question_index: parseInt(idx),
        answer
      }));
      
      const response = await axios.post(`${API}/api/skills/submit`, {
        assessment_id: activeAssessment.id,
        answers: answerList
      });
      
      setResults(response.data);
      setShowResultsDialog(true);
      setActiveAssessment(null);
      fetchMyBadges();
      
    } catch (e) {
      toast.error("Failed to submit assessment");
    }
    setSubmitting(false);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const hasBadge = (skillName) => {
    return myBadges.some(b => b.skill_name === skillName);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-turquoise" />
      </div>
    );
  }

  // Assessment in progress view
  if (activeAssessment && questions.length > 0) {
    const question = questions[currentQuestion];
    
    return (
      <div className="p-6 md:p-8 lg:p-12 max-w-3xl mx-auto" data-testid="assessment-in-progress">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
              {activeAssessment.skill_name} Assessment
            </h1>
            <p className="text-sm text-slate-500">
              Question {currentQuestion + 1} of {questions.length}
            </p>
          </div>
          
          <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
            timeLeft < 60 ? 'bg-red-100 text-red-700' : 'bg-slate-100 text-slate-700'
          }`}>
            <Clock className="w-4 h-4" />
            <span className="font-mono font-semibold">{formatTime(timeLeft)}</span>
          </div>
        </div>
        
        {/* Progress */}
        <Progress value={(currentQuestion + 1) / questions.length * 100} className="mb-6" />
        
        {/* Question Card */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <h2 className="text-lg font-medium text-slate-900 dark:text-slate-100 mb-6">
              {question.question}
            </h2>
            
            <RadioGroup
              value={answers[currentQuestion] || ""}
              onValueChange={(value) => handleAnswer(currentQuestion, value)}
              className="space-y-3"
            >
              {question.options.map((option, i) => (
                <div key={i} className={`flex items-center space-x-3 p-3 rounded-lg border
                  ${answers[currentQuestion] === option ? 'border-turquoise bg-turquoise/5' : 'border-slate-200 dark:border-slate-700'}
                  hover:border-turquoise/50 transition-colors cursor-pointer`}
                >
                  <RadioGroupItem value={option} id={`option-${i}`} />
                  <Label htmlFor={`option-${i}`} className="flex-1 cursor-pointer">
                    {option}
                  </Label>
                </div>
              ))}
            </RadioGroup>
          </CardContent>
        </Card>
        
        {/* Navigation */}
        <div className="flex items-center justify-between">
          <Button
            variant="outline"
            onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
            disabled={currentQuestion === 0}
          >
            Previous
          </Button>
          
          <div className="flex items-center gap-2">
            {questions.map((_, i) => (
              <button
                key={i}
                onClick={() => setCurrentQuestion(i)}
                className={`w-8 h-8 rounded-full text-sm font-medium transition-colors
                  ${currentQuestion === i ? 'bg-turquoise text-white' : 
                    answers[i] ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'}`}
              >
                {i + 1}
              </button>
            ))}
          </div>
          
          {currentQuestion < questions.length - 1 ? (
            <Button onClick={() => setCurrentQuestion(currentQuestion + 1)}>
              Next
            </Button>
          ) : (
            <Button 
              onClick={handleSubmitAssessment}
              disabled={submitting || Object.keys(answers).length < questions.length}
              className="bg-emerald-500 hover:bg-emerald-600"
            >
              {submitting ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
              Submit Assessment
            </Button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-7xl mx-auto animate-fade-in" data-testid="skill-assessments">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl md:text-4xl font-semibold text-slate-900 dark:text-slate-100">
          Skill Assessments
        </h1>
        <p className="text-slate-500 dark:text-slate-400 mt-2">
          Verify your skills and earn badges to stand out to recruiters
        </p>
      </div>

      {/* My Badges */}
      {myBadges.length > 0 && (
        <Card className="mb-8 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 border-amber-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Trophy className="w-5 h-5 text-amber-500" />
              My Badges ({myBadges.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-4">
              {myBadges.map((badge, i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 p-3 rounded-xl bg-white dark:bg-slate-800 shadow-sm"
                >
                  <div 
                    className="w-12 h-12 rounded-full flex items-center justify-center text-2xl"
                    style={{ backgroundColor: `${badge.badge_color}20` }}
                  >
                    {badge.badge_icon}
                  </div>
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-slate-100">
                      {badge.skill_name}
                    </p>
                    <p className="text-xs text-slate-500">
                      Score: {badge.score}% • {badge.difficulty}
                    </p>
                  </div>
                  <CheckCircle className="w-5 h-5 text-emerald-500 ml-2" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Assessments by Category */}
      {Object.entries(categories).map(([category, skills]) => (
        <div key={category} className="mb-8">
          <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
            {category}
          </h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {skills.map((skill, i) => {
              const earned = hasBadge(skill.skill_name);
              
              return (
                <Card 
                  key={i}
                  className={`hover:border-turquoise/50 transition-all ${
                    earned ? 'border-emerald-200 bg-emerald-50/50 dark:bg-emerald-900/10' : ''
                  }`}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div 
                          className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl"
                          style={{ backgroundColor: `${skill.badge_color}20` }}
                        >
                          {skill.badge_icon}
                        </div>
                        <div>
                          <h3 className="font-semibold text-slate-900 dark:text-slate-100">
                            {skill.skill_name}
                          </h3>
                          <p className="text-xs text-slate-500">
                            {skill.questions} questions • {skill.time_limit} min
                          </p>
                        </div>
                      </div>
                      
                      {earned && (
                        <Badge className="bg-emerald-100 text-emerald-700">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Earned
                        </Badge>
                      )}
                    </div>
                    
                    <div className="mt-4 flex items-center justify-between">
                      <span className="text-xs text-slate-500">
                        Pass: {skill.passing_score}%
                      </span>
                      
                      <Button
                        size="sm"
                        onClick={() => startAssessment(skill.skill_name)}
                        disabled={submitting}
                        variant={earned ? "outline" : "default"}
                      >
                        {submitting ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <>
                            <Play className="w-4 h-4 mr-1" />
                            {earned ? "Retake" : "Start"}
                          </>
                        )}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      ))}

      {/* Results Dialog */}
      <Dialog open={showResultsDialog} onOpenChange={setShowResultsDialog}>
        <DialogContent className="max-w-lg">
          {results && (
            <>
              <DialogHeader>
                <DialogTitle className="text-center">
                  {results.passed ? (
                    <div className="flex flex-col items-center">
                      <div className="w-20 h-20 rounded-full bg-emerald-100 flex items-center justify-center mb-4">
                        <Trophy className="w-10 h-10 text-emerald-500" />
                      </div>
                      <span className="text-2xl text-emerald-600">Congratulations!</span>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center">
                      <div className="w-20 h-20 rounded-full bg-slate-100 flex items-center justify-center mb-4">
                        <Target className="w-10 h-10 text-slate-400" />
                      </div>
                      <span className="text-2xl text-slate-600">Keep Practicing</span>
                    </div>
                  )}
                </DialogTitle>
              </DialogHeader>
              
              <div className="py-6 text-center">
                <div className="text-5xl font-bold mb-2" style={{
                  color: results.passed ? '#10B981' : '#6B7280'
                }}>
                  {results.score}%
                </div>
                <p className="text-slate-500 mb-4">
                  {results.correct_count} of {results.total_questions} correct
                </p>
                
                {results.badge && (
                  <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-900/20 mb-4">
                    <p className="text-sm text-amber-600 font-medium mb-2">Badge Earned!</p>
                    <div className="text-4xl">{results.badge.badge_icon}</div>
                    <p className="font-semibold text-slate-900 dark:text-slate-100 mt-1">
                      {results.badge.skill_name}
                    </p>
                  </div>
                )}
                
                <p className="text-sm text-slate-500">{results.message}</p>
              </div>
              
              <DialogFooter>
                <Button onClick={() => setShowResultsDialog(false)} className="w-full">
                  {results.passed ? "View My Badges" : "Try Again Later"}
                </Button>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default SkillAssessmentsPage;
