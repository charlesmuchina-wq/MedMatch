import { Bookmark, CheckSquare, Clock, TrendingUp, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

const Dashboard = ({ resume, savedJobs, applications, onNavigate }) => {
  const stats = [
    { label: "Saved Jobs", value: savedJobs.length, icon: Bookmark, color: "text-sky-500" },
    { label: "Applications", value: applications.length, icon: CheckSquare, color: "text-emerald-500" },
    { label: "Interviews", value: applications.filter(a => a.status === "Interview").length, icon: Clock, color: "text-amber-500" },
    { label: "Skills", value: resume?.skills?.length || 0, icon: TrendingUp, color: "text-violet-500" },
  ];

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-7xl mx-auto animate-fade-in" data-testid="dashboard">
      <div className="mb-8">
        <h1 className="text-3xl md:text-4xl font-semibold text-slate-900 tracking-tight" style={{ fontFamily: 'IBM Plex Sans' }}>
          {resume?.full_name ? `Welcome, ${resume.full_name.split(' ')[0]}` : 'Welcome to MedMatch'}
        </h1>
        <p className="text-slate-500 mt-2">
          {resume ? 'Your personalized remote job dashboard' : 'Upload your resume to get started'}
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {stats.map(({ label, value, icon: Icon, color }) => (
          <Card key={label} className="border-slate-200">
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-500">{label}</p>
                  <p className="text-2xl font-semibold text-slate-900 mt-1">{value}</p>
                </div>
                <div className={`p-3 rounded-lg bg-slate-50 ${color}`}>
                  <Icon className="w-5 h-5" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {!resume ? (
        <Card className="border-dashed border-2 border-slate-300">
          <CardContent className="p-12 text-center">
            <Upload className="w-12 h-12 text-slate-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Upload Your Resume</h3>
            <p className="text-slate-500 mb-4">Get AI-powered job matches based on your skills and experience</p>
            <Button onClick={() => onNavigate('/resume')} data-testid="upload-resume-cta">
              Upload Resume
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg" style={{ fontFamily: 'IBM Plex Sans' }}>Your Skills</CardTitle>
              <CardDescription>Extracted from your resume</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {resume.skills?.slice(0, 12).map((skill, i) => (
                  <Badge key={i} variant="secondary" className="bg-slate-100 dark:bg-slate-700 dark:text-slate-200">{skill}</Badge>
                ))}
                {resume.skills?.length > 12 && (
                  <Badge variant="outline" className="dark:border-slate-600 dark:text-slate-300">+{resume.skills.length - 12} more</Badge>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg" style={{ fontFamily: 'IBM Plex Sans' }}>Recent Applications</CardTitle>
              <CardDescription>Track your job applications</CardDescription>
            </CardHeader>
            <CardContent>
              {applications.length === 0 ? (
                <p className="text-slate-500 text-sm">No applications yet</p>
              ) : (
                <div className="space-y-3">
                  {applications.slice(0, 3).map((app) => (
                    <div key={app.id} className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-slate-900 text-sm">{app.job.title}</p>
                        <p className="text-xs text-slate-500">{app.job.company}</p>
                      </div>
                      <Badge className={`status-${app.status.toLowerCase()}`}>{app.status}</Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
