import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { useTheme } from "@/App";
import { 
  Search, Users, Filter, Loader2, Mail, MessageSquare, Brain,
  Award, Briefcase, ChevronRight, X, Star, Sparkles
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { useTranslation } from "@/utils/i18n";
import { apiClient } from "@/utils/apiClient";

const API = process.env.REACT_APP_BACKEND_URL;

const SKILL_SUGGESTIONS = [
  "Python", "JavaScript", "React", "Node.js", "AWS", "Docker",
  "Machine Learning", "Data Science", "SQL", "Java", "TypeScript",
  "Kubernetes", "Go", "Rust", "Product Management", "Agile"
];

const CandidateSearch = ({ user }) => {
  const navigate = useNavigate();
  const { isDark } = useTheme();
  
  const [searchSkills, setSearchSkills] = useState([]);
  const [searchKeywords, setSearchKeywords] = useState("");
  const [skillInput, setSkillInput] = useState("");
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [showDetailDialog, setShowDetailDialog] = useState(false);

  useEffect(() => {
    if (user?.role !== "recruiter") {
      navigate("/");
      return;
    }
  }, [user, navigate]);

  const addSkill = (skill) => {
    if (skill && !searchSkills.includes(skill)) {
      setSearchSkills([...searchSkills, skill]);
      setSkillInput("");
    }
  };

  const removeSkill = (skill) => {
    setSearchSkills(searchSkills.filter(s => s !== skill));
  };

  const searchCandidates = async () => {
    if (searchSkills.length === 0 && !searchKeywords.trim()) {
      toast.error("Please add at least one skill or keyword");
      return;
    }

    setLoading(true);
    setHasSearched(true);
    
    try {
      const response = await axios.post(`${API}/api/recruiter/candidates/search`, {
        skills: searchSkills,
        keywords: searchKeywords.split(",").map(k => k.trim()).filter(Boolean),
        limit: 30
      });
      setCandidates(response.data.candidates || []);
    } catch (e) {
      toast.error("Search failed");
      console.error(e);
    }
    setLoading(false);
  };

  const viewCandidateProfile = async (candidateId) => {
    try {
      const response = await axios.get(`${API}/api/recruiter/candidates/${candidateId}`);
      setSelectedCandidate(response.data);
      setShowDetailDialog(true);
    } catch (e) {
      toast.error("Failed to load profile");
    }
  };

  const sendMessage = (candidate) => {
    navigate(`/messages/new?recipient=${candidate.id}&name=${encodeURIComponent(candidate.full_name)}&email=${encodeURIComponent(candidate.email)}`);
  };

  const getScoreColor = (score) => {
    if (score >= 50) return "text-emerald-500 bg-emerald-100 dark:bg-emerald-900/30";
    if (score >= 25) return "text-amber-500 bg-amber-100 dark:bg-amber-900/30";
    return "text-slate-500 bg-slate-100 dark:bg-slate-800";
  };

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-7xl mx-auto animate-fade-in" data-testid="candidate-search">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl md:text-4xl font-semibold text-slate-900 dark:text-slate-100">
          Candidate Search
        </h1>
        <p className="text-slate-500 dark:text-slate-400 mt-2">
          Find qualified candidates based on skills and experience
        </p>
      </div>

      {/* Search Form */}
      <Card className="mb-8">
        <CardContent className="p-6">
          {/* Skills Input */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Required Skills
            </label>
            <div className="flex gap-2 mb-3">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <Input
                  placeholder="Type a skill and press Enter..."
                  value={skillInput}
                  onChange={(e) => setSkillInput(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      addSkill(skillInput);
                    }
                  }}
                  className="pl-9"
                />
              </div>
              <Button onClick={() => addSkill(skillInput)} disabled={!skillInput.trim()}>
                Add
              </Button>
            </div>

            {/* Selected Skills */}
            {searchSkills.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-3">
                {searchSkills.map(skill => (
                  <Badge 
                    key={skill} 
                    className="bg-turquoise/20 text-turquoise border-turquoise/30 gap-1 pr-1"
                  >
                    {skill}
                    <button
                      onClick={() => removeSkill(skill)}
                      className="ml-1 hover:bg-turquoise/30 rounded-full p-0.5"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}

            {/* Skill Suggestions */}
            <div className="flex flex-wrap gap-2">
              <span className="text-xs text-slate-500">Suggestions:</span>
              {SKILL_SUGGESTIONS.filter(s => !searchSkills.includes(s)).slice(0, 8).map(skill => (
                <button
                  key={skill}
                  onClick={() => addSkill(skill)}
                  className="text-xs px-2 py-1 rounded-full border border-slate-200 dark:border-slate-700
                    hover:border-turquoise hover:text-turquoise transition-colors"
                >
                  + {skill}
                </button>
              ))}
            </div>
          </div>

          {/* Keywords Input */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Additional Keywords (comma-separated)
            </label>
            <Input
              placeholder="e.g., senior, remote, healthcare..."
              value={searchKeywords}
              onChange={(e) => setSearchKeywords(e.target.value)}
            />
          </div>

          <Button 
            onClick={searchCandidates}
            disabled={loading || (searchSkills.length === 0 && !searchKeywords.trim())}
            className="w-full gap-2"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Search className="w-4 h-4" />
            )}
            Search Candidates
          </Button>
        </CardContent>
      </Card>

      {/* Results */}
      {hasSearched && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
              {candidates.length} Candidates Found
            </h2>
            {candidates.length > 0 && (
              <span className="text-sm text-slate-500">
                Sorted by relevance
              </span>
            )}
          </div>

          {candidates.length > 0 ? (
            <div className="space-y-4">
              {candidates.map((candidate, idx) => (
                <Card 
                  key={candidate.id || idx}
                  className="hover:border-turquoise/50 transition-all cursor-pointer"
                  onClick={() => viewCandidateProfile(candidate.id)}
                >
                  <CardContent className="p-4">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 
                          flex items-center justify-center text-white font-semibold text-lg">
                          {(candidate.full_name || "?")[0].toUpperCase()}
                        </div>
                        <div>
                          <h3 className="font-semibold text-slate-900 dark:text-slate-100">
                            {candidate.full_name || "Anonymous Candidate"}
                          </h3>
                          <p className="text-sm text-slate-500 line-clamp-1">
                            {candidate.summary?.substring(0, 100) || "No summary available"}...
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        {/* Relevance Score */}
                        <div className={`px-3 py-1 rounded-full flex items-center gap-1 ${getScoreColor(candidate.relevance_score)}`}>
                          <Sparkles className="w-4 h-4" />
                          <span className="font-semibold">{candidate.relevance_score}</span>
                        </div>

                        {/* Matched Skills */}
                        <div className="hidden md:flex items-center gap-1">
                          {candidate.matched_skills?.slice(0, 3).map((skill, i) => (
                            <Badge key={i} className="bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 text-xs">
                              {skill}
                            </Badge>
                          ))}
                        </div>

                        {/* Quick Actions */}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            sendMessage(candidate);
                          }}
                        >
                          <MessageSquare className="w-4 h-4" />
                        </Button>
                        
                        <ChevronRight className="w-4 h-4 text-slate-400" />
                      </div>
                    </div>

                    {/* Skills Preview */}
                    <div className="mt-3 flex flex-wrap gap-1">
                      {candidate.skills?.slice(0, 8).map((skill, i) => (
                        <Badge 
                          key={i} 
                          variant="outline" 
                          className={`text-xs ${candidate.matched_skills?.includes(skill) ? 'border-emerald-500 text-emerald-600' : ''}`}
                        >
                          {skill}
                        </Badge>
                      ))}
                      {candidate.skills?.length > 8 && (
                        <Badge variant="outline" className="text-xs">
                          +{candidate.skills.length - 8} more
                        </Badge>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="py-12 text-center">
                <Users className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                <h3 className="text-lg font-medium text-slate-600 dark:text-slate-400">
                  No candidates found
                </h3>
                <p className="text-sm text-slate-500 mt-1">
                  Try different skills or keywords
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Candidate Detail Dialog */}
      <Dialog open={showDetailDialog} onOpenChange={setShowDetailDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          {selectedCandidate && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 
                    flex items-center justify-center text-white font-semibold text-lg">
                    {(selectedCandidate.full_name || "?")[0].toUpperCase()}
                  </div>
                  <div>
                    <span>{selectedCandidate.full_name || "Anonymous"}</span>
                    <p className="text-sm font-normal text-slate-500 flex items-center gap-2">
                      <Mail className="w-3 h-3" />
                      {selectedCandidate.email}
                    </p>
                  </div>
                </DialogTitle>
              </DialogHeader>

              <div className="space-y-6 py-4">
                {/* Summary */}
                {selectedCandidate.summary && (
                  <div>
                    <h4 className="font-semibold text-slate-900 dark:text-slate-100 mb-2">
                      Professional Summary
                    </h4>
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      {selectedCandidate.summary}
                    </p>
                  </div>
                )}

                {/* Skills */}
                <div>
                  <h4 className="font-semibold text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-2">
                    <Award className="w-4 h-4 text-turquoise" />
                    Skills
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedCandidate.skills?.map((skill, idx) => (
                      <Badge key={idx} variant="outline">{skill}</Badge>
                    ))}
                  </div>
                </div>

                {/* Experience */}
                <div>
                  <h4 className="font-semibold text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-2">
                    <Briefcase className="w-4 h-4 text-turquoise" />
                    Experience
                  </h4>
                  {selectedCandidate.experience?.length > 0 ? (
                    <div className="space-y-3">
                      {selectedCandidate.experience.map((exp, idx) => (
                        <div key={idx} className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50">
                          <p className="font-medium text-slate-900 dark:text-slate-100">{exp.title}</p>
                          <p className="text-sm text-slate-500">{exp.company} • {exp.duration}</p>
                          {exp.description && (
                            <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                              {exp.description}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-slate-500">No experience listed</p>
                  )}
                </div>

                {/* Education */}
                {selectedCandidate.education?.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-slate-900 dark:text-slate-100 mb-2">
                      Education
                    </h4>
                    <div className="space-y-2">
                      {selectedCandidate.education.map((edu, idx) => (
                        <div key={idx} className="text-sm">
                          <p className="font-medium text-slate-900 dark:text-slate-100">
                            {edu.degree}
                          </p>
                          <p className="text-slate-500">
                            {edu.institution} • {edu.year}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <DialogFooter>
                <Button variant="outline" onClick={() => setShowDetailDialog(false)}>
                  Close
                </Button>
                <Button onClick={() => sendMessage(selectedCandidate)} className="gap-2">
                  <MessageSquare className="w-4 h-4" />
                  Contact Candidate
                </Button>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default CandidateSearch;
