import { useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { 
  DollarSign, TrendingUp, Target, Lightbulb, Loader2, 
  Building2, MapPin, Briefcase, ChevronRight, Sparkles,
  ArrowUp, ArrowDown, Minus, CheckCircle2, AlertCircle
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const API = process.env.REACT_APP_BACKEND_URL;

const SalaryInsightsPage = ({ resume }) => {
  const [jobTitle, setJobTitle] = useState(resume?.title || "");
  const [location, setLocation] = useState("Remote, USA");
  const [experience, setExperience] = useState("5");
  const [currentSalary, setCurrentSalary] = useState("");
  const [loading, setLoading] = useState(false);
  const [insights, setInsights] = useState(null);

  const handleGetInsights = async () => {
    if (!jobTitle.trim()) {
      toast.error("Please enter a job title");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/api/salary/insights`, {
        job_title: jobTitle,
        location: location,
        years_experience: parseInt(experience),
        current_salary: currentSalary ? parseInt(currentSalary.replace(/[^0-9]/g, '')) : null,
        skills: resume?.skills || []
      }, { withCredentials: true });

      setInsights(response.data);
      toast.success("Salary insights generated!");
    } catch (e) {
      toast.error(e.response?.data?.detail || "Failed to get salary insights");
    }
    setLoading(false);
  };

  const formatSalary = (amount) => {
    if (!amount) return "N/A";
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const getSalaryPosition = () => {
    if (!insights || !currentSalary) return null;
    const current = parseInt(currentSalary.replace(/[^0-9]/g, ''));
    const median = insights.salary_range?.median;
    if (!median) return null;
    
    const diff = ((current - median) / median) * 100;
    if (diff > 10) return { icon: ArrowUp, text: "Above Market", color: "text-emerald-500" };
    if (diff < -10) return { icon: ArrowDown, text: "Below Market", color: "text-red-500" };
    return { icon: Minus, text: "At Market Rate", color: "text-sky-500" };
  };

  const salaryPosition = getSalaryPosition();

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-5xl mx-auto animate-fade-in" data-testid="salary-insights-page">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-3" style={{ fontFamily: 'IBM Plex Sans' }}>
          <DollarSign className="w-8 h-8 text-emerald-500" />
          Salary Insights
        </h1>
        <p className="text-slate-500 dark:text-slate-400 mt-2">
          Get AI-powered salary data and negotiation strategies for your target role
        </p>
      </div>

      {/* Input Form */}
      <Card className="mb-8 dark:bg-slate-800 dark:border-slate-700">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Target className="w-5 h-5 text-turquoise" />
            Your Target Role
          </CardTitle>
          <CardDescription>Enter details to get personalized salary insights</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="jobTitle">Job Title</Label>
              <Input
                id="jobTitle"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="e.g., Senior Software Engineer"
                className="dark:bg-slate-900 dark:border-slate-600"
                data-testid="salary-job-title-input"
              />
            </div>
            <div>
              <Label htmlFor="location">Location</Label>
              <Input
                id="location"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g., San Francisco, CA"
                className="dark:bg-slate-900 dark:border-slate-600"
                data-testid="salary-location-input"
              />
            </div>
            <div>
              <Label htmlFor="experience">Years of Experience</Label>
              <Input
                id="experience"
                type="number"
                value={experience}
                onChange={(e) => setExperience(e.target.value)}
                placeholder="5"
                min="0"
                max="40"
                className="dark:bg-slate-900 dark:border-slate-600"
                data-testid="salary-experience-input"
              />
            </div>
            <div>
              <Label htmlFor="currentSalary">Current Salary (Optional)</Label>
              <Input
                id="currentSalary"
                value={currentSalary}
                onChange={(e) => setCurrentSalary(e.target.value)}
                placeholder="e.g., $120,000"
                className="dark:bg-slate-900 dark:border-slate-600"
                data-testid="salary-current-input"
              />
            </div>
          </div>
          <Button 
            onClick={handleGetInsights} 
            disabled={loading}
            className="mt-6 bg-gradient-to-r from-emerald-500 to-teal-600"
            data-testid="get-insights-btn"
          >
            {loading ? (
              <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Analyzing...</>
            ) : (
              <><Sparkles className="w-4 h-4 mr-2" /> Get Salary Insights</>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Results */}
      {insights && (
        <div className="space-y-6 animate-fade-in">
          {/* Salary Range Card */}
          <Card className="dark:bg-slate-800 dark:border-slate-700">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-emerald-500" />
                Salary Range for {insights.job_title}
              </CardTitle>
              <CardDescription className="flex items-center gap-2">
                <MapPin className="w-4 h-4" /> {insights.location} • 
                <Briefcase className="w-4 h-4 ml-1" /> {insights.years_experience} years experience
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="text-center p-4 rounded-lg bg-slate-50 dark:bg-slate-900">
                  <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Low</p>
                  <p className="text-xl font-bold text-slate-700 dark:text-slate-300">
                    {formatSalary(insights.salary_range?.low)}
                  </p>
                </div>
                <div className="text-center p-4 rounded-lg bg-emerald-50 dark:bg-emerald-900/30 border-2 border-emerald-200 dark:border-emerald-700">
                  <p className="text-xs text-emerald-600 dark:text-emerald-400 mb-1">Median</p>
                  <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                    {formatSalary(insights.salary_range?.median)}
                  </p>
                </div>
                <div className="text-center p-4 rounded-lg bg-slate-50 dark:bg-slate-900">
                  <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">High</p>
                  <p className="text-xl font-bold text-slate-700 dark:text-slate-300">
                    {formatSalary(insights.salary_range?.high)}
                  </p>
                </div>
              </div>

              {/* Salary Position Indicator */}
              {salaryPosition && (
                <div className={`flex items-center justify-center gap-2 p-3 rounded-lg bg-slate-50 dark:bg-slate-900 ${salaryPosition.color}`}>
                  <salaryPosition.icon className="w-5 h-5" />
                  <span className="font-medium">Your current salary is {salaryPosition.text}</span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Tabs for Tips and Factors */}
          <Tabs defaultValue="negotiation" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="negotiation">Negotiation Tips</TabsTrigger>
              <TabsTrigger value="factors">Salary Factors</TabsTrigger>
              <TabsTrigger value="scripts">Talk Scripts</TabsTrigger>
            </TabsList>

            <TabsContent value="negotiation">
              <Card className="dark:bg-slate-800 dark:border-slate-700">
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Lightbulb className="w-5 h-5 text-amber-500" />
                    Negotiation Strategies
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {insights.negotiation_tips?.map((tip, i) => (
                      <div key={i} className="flex gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-900">
                        <CheckCircle2 className="w-5 h-5 text-emerald-500 flex-shrink-0 mt-0.5" />
                        <p className="text-slate-700 dark:text-slate-300 text-sm">{tip}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="factors">
              <Card className="dark:bg-slate-800 dark:border-slate-700">
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Building2 className="w-5 h-5 text-sky-500" />
                    Factors Affecting Your Salary
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {insights.salary_factors?.map((factor, i) => (
                      <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-900">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                          factor.impact === 'positive' ? 'bg-emerald-100 dark:bg-emerald-900/50' :
                          factor.impact === 'negative' ? 'bg-red-100 dark:bg-red-900/50' :
                          'bg-slate-200 dark:bg-slate-700'
                        }`}>
                          {factor.impact === 'positive' ? (
                            <ArrowUp className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                          ) : factor.impact === 'negative' ? (
                            <ArrowDown className="w-4 h-4 text-red-600 dark:text-red-400" />
                          ) : (
                            <Minus className="w-4 h-4 text-slate-500" />
                          )}
                        </div>
                        <div>
                          <h4 className="font-medium text-slate-900 dark:text-slate-100">{factor.factor}</h4>
                          <p className="text-sm text-slate-500 dark:text-slate-400">{factor.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="scripts">
              <Card className="dark:bg-slate-800 dark:border-slate-700">
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-violet-500" />
                    What to Say in Negotiations
                  </CardTitle>
                  <CardDescription>Copy these scripts for your salary discussions</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {insights.talk_scripts?.map((script, i) => (
                      <div key={i} className="p-4 rounded-lg border border-slate-200 dark:border-slate-700">
                        <div className="flex items-center justify-between mb-2">
                          <Badge variant="outline" className="text-xs">{script.scenario}</Badge>
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => {
                              navigator.clipboard.writeText(script.script);
                              toast.success("Copied to clipboard!");
                            }}
                          >
                            Copy
                          </Button>
                        </div>
                        <p className="text-slate-700 dark:text-slate-300 text-sm italic">"{script.script}"</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Skills Premium */}
          {insights.skills_premium && insights.skills_premium.length > 0 && (
            <Card className="dark:bg-slate-800 dark:border-slate-700">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Target className="w-5 h-5 text-violet-500" />
                  High-Value Skills for This Role
                </CardTitle>
                <CardDescription>Skills that can increase your salary</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {insights.skills_premium.map((skill, i) => (
                    <Badge 
                      key={i} 
                      className="bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-300 px-3 py-1"
                    >
                      {skill.skill}
                      <span className="ml-2 text-emerald-600 dark:text-emerald-400">+{skill.premium}%</span>
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Empty State */}
      {!insights && !loading && (
        <Card className="dark:bg-slate-800 dark:border-slate-700">
          <CardContent className="p-12 text-center">
            <DollarSign className="w-12 h-12 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-700 dark:text-slate-300 mb-2">
              Get Personalized Salary Insights
            </h3>
            <p className="text-slate-500 dark:text-slate-400 text-sm max-w-md mx-auto">
              Enter your target job title and experience to receive AI-powered salary ranges, 
              negotiation tips, and strategies to maximize your compensation.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default SalaryInsightsPage;
