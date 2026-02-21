import { useState, useEffect } from "react";
import { useTranslation } from "@/utils/i18n";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import { useTheme } from "@/App";
import { 
  Building2, MapPin, Globe, Users, Calendar, Award, Briefcase,
  Star, ThumbsUp, ChevronRight, Heart, Loader2, Edit3, Plus
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const API = process.env.REACT_APP_BACKEND_URL;

const CompanyProfilePage = ({ user }) => {
  const { companyId } = useParams();
  const navigate = useNavigate();
  const { isDark } = useTheme();
  const { t } = useTranslation();
  
  const [company, setCompany] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [following, setFollowing] = useState(false);
  const [showReviewDialog, setShowReviewDialog] = useState(false);
  const [reviewForm, setReviewForm] = useState({
    rating: 5,
    title: "",
    pros: "",
    cons: "",
    position: "",
    is_current_employee: false,
    recommend: true
  });

  useEffect(() => {
    if (companyId) {
      fetchCompany();
      fetchReviews();
    }
  }, [companyId]);

  const fetchCompany = async () => {
    try {
      const response = await axios.get(`${API}/api/companies/${companyId}`);
      setCompany(response.data);
    } catch (e) {
      toast.error("Failed to load company profile");
    }
    setLoading(false);
  };

  const fetchReviews = async () => {
    try {
      const response = await axios.get(`${API}/api/companies/${companyId}/reviews`);
      setReviews(response.data);
    } catch (e) {
      console.error("Failed to load reviews");
    }
  };

  const toggleFollow = async () => {
    try {
      const response = await axios.post(`${API}/api/companies/${companyId}/follow`);
      setFollowing(response.data.following);
      toast.success(response.data.message);
      fetchCompany();
    } catch (e) {
      toast.error("Failed to follow company");
    }
  };

  const submitReview = async () => {
    try {
      await axios.post(`${API}/api/companies/${companyId}/reviews`, reviewForm);
      toast.success("Review submitted");
      setShowReviewDialog(false);
      setReviewForm({
        rating: 5,
        title: "",
        pros: "",
        cons: "",
        position: "",
        is_current_employee: false,
        recommend: true
      });
      fetchReviews();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Failed to submit review");
    }
  };

  const markHelpful = async (reviewId) => {
    try {
      await axios.post(`${API}/api/companies/${companyId}/reviews/${reviewId}/helpful`);
      toast.success("Marked as helpful");
      fetchReviews();
    } catch (e) {
      toast.error("Failed to mark as helpful");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-turquoise" />
      </div>
    );
  }

  if (!company) {
    return (
      <div className="p-6 text-center">
        <Building2 className="w-16 h-16 mx-auto mb-4 text-slate-300" />
        <h2 className="text-xl font-semibold text-slate-600">Company not found</h2>
      </div>
    );
  }

  const renderStars = (rating) => {
    return [...Array(5)].map((_, i) => (
      <Star 
        key={i} 
        className={`w-4 h-4 ${i < rating ? 'text-amber-400 fill-amber-400' : 'text-slate-300'}`} 
      />
    ));
  };

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-5xl mx-auto" data-testid="company-profile">
      {/* Header */}
      <div className="flex flex-col md:flex-row gap-6 mb-8">
        <div className="w-24 h-24 rounded-xl bg-gradient-to-br from-turquoise to-emerald-500 
          flex items-center justify-center text-white text-3xl font-bold">
          {company.logo_url ? (
            <img src={company.logo_url} alt={company.name} className="w-full h-full object-cover rounded-xl" />
          ) : (
            company.name[0]
          )}
        </div>
        
        <div className="flex-1">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">
                {company.name}
              </h1>
              <div className="flex flex-wrap items-center gap-4 mt-2 text-sm text-slate-500">
                <span className="flex items-center gap-1">
                  <Building2 className="w-4 h-4" /> {company.industry}
                </span>
                {company.headquarters && (
                  <span className="flex items-center gap-1">
                    <MapPin className="w-4 h-4" /> {company.headquarters}
                  </span>
                )}
                {company.size && (
                  <span className="flex items-center gap-1">
                    <Users className="w-4 h-4" /> {company.size} employees
                  </span>
                )}
              </div>
            </div>
            
            <Button
              onClick={toggleFollow}
              variant={following ? "outline" : "default"}
              className="gap-2"
            >
              <Heart className={`w-4 h-4 ${following ? 'fill-red-500 text-red-500' : ''}`} />
              {following ? "Following" : "Follow"}
            </Button>
          </div>
          
          {/* Stats */}
          <div className="flex items-center gap-6 mt-4">
            <div className="flex items-center gap-1">
              {renderStars(Math.round(company.stats?.average_rating || 0))}
              <span className="ml-1 font-semibold">{company.stats?.average_rating || 0}</span>
              <span className="text-sm text-slate-500">({company.stats?.total_reviews || 0} reviews)</span>
            </div>
            <span className="text-sm text-slate-500">
              {company.stats?.followers || 0} followers
            </span>
          </div>
        </div>
      </div>

      <Tabs defaultValue="overview" className="mt-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="jobs">Jobs ({company.recent_jobs?.length || 0})</TabsTrigger>
          <TabsTrigger value="reviews">Reviews</TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview" className="mt-6 space-y-6">
          {/* About */}
          <Card>
            <CardHeader>
              <CardTitle>About</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-slate-600 dark:text-slate-400">{company.description}</p>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                {company.website && (
                  <div>
                    <p className="text-xs text-slate-500">Website</p>
                    <a href={company.website} target="_blank" rel="noopener noreferrer" 
                      className="text-turquoise hover:underline flex items-center gap-1">
                      <Globe className="w-3 h-3" /> Visit
                    </a>
                  </div>
                )}
                {company.founded && (
                  <div>
                    <p className="text-xs text-slate-500">Founded</p>
                    <p className="font-medium">{company.founded}</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Specialties */}
          {company.specialties?.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Specialties</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {company.specialties.map((s, i) => (
                    <Badge key={i} variant="outline">{s}</Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Benefits */}
          {company.benefits?.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Benefits</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {company.benefits.map((b, i) => (
                    <Badge key={i} className="bg-emerald-100 text-emerald-700">{b}</Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Culture */}
          {company.culture_values?.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Culture & Values</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {company.culture_values.map((v, i) => (
                    <Badge key={i} className="bg-violet-100 text-violet-700">{v}</Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="jobs" className="mt-6">
          {company.recent_jobs?.length > 0 ? (
            <div className="space-y-4">
              {company.recent_jobs.map((job, i) => (
                <Card key={i} className="hover:border-turquoise/50 transition-colors cursor-pointer">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold text-slate-900 dark:text-slate-100">{job.title}</h3>
                        <p className="text-sm text-slate-500">{job.location} • {job.salary}</p>
                      </div>
                      <ChevronRight className="w-5 h-5 text-slate-400" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="py-8 text-center">
                <Briefcase className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                <p className="text-slate-500">No job openings at this time</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="reviews" className="mt-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <div className="text-4xl font-bold text-slate-900 dark:text-slate-100">
                {reviews.average_rating || 0}
              </div>
              <div>
                <div className="flex">{renderStars(Math.round(reviews.average_rating || 0))}</div>
                <p className="text-sm text-slate-500">{reviews.total_reviews || 0} reviews</p>
              </div>
            </div>
            
            <Button onClick={() => setShowReviewDialog(true)} className="gap-2">
              <Plus className="w-4 h-4" />
              Write Review
            </Button>
          </div>

          <div className="space-y-4">
            {reviews.reviews?.map((review, i) => (
              <Card key={i}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className="flex">{renderStars(review.rating)}</div>
                      <span className="font-medium">{review.title}</span>
                    </div>
                    <Badge variant={review.recommend ? "default" : "secondary"}>
                      {review.recommend ? "Recommends" : "Doesn't recommend"}
                    </Badge>
                  </div>
                  
                  {review.position && (
                    <p className="text-sm text-slate-500 mb-2">
                      {review.position} • {review.is_current_employee ? "Current" : "Former"} Employee
                    </p>
                  )}
                  
                  <div className="grid md:grid-cols-2 gap-4 mt-3">
                    <div>
                      <p className="text-xs font-medium text-emerald-600 mb-1">Pros</p>
                      <p className="text-sm text-slate-600 dark:text-slate-400">{review.pros}</p>
                    </div>
                    <div>
                      <p className="text-xs font-medium text-red-600 mb-1">Cons</p>
                      <p className="text-sm text-slate-600 dark:text-slate-400">{review.cons}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between mt-4 pt-3 border-t">
                    <span className="text-xs text-slate-400">
                      {new Date(review.created_at).toLocaleDateString()}
                    </span>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      onClick={() => markHelpful(review.id)}
                      className="gap-1"
                    >
                      <ThumbsUp className="w-3 h-3" />
                      Helpful ({review.helpful_count || 0})
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Review Dialog */}
      <Dialog open={showReviewDialog} onOpenChange={setShowReviewDialog}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Write a Review for {company.name}</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Rating</label>
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => setReviewForm({...reviewForm, rating: star})}
                    className="p-1"
                  >
                    <Star className={`w-8 h-8 ${star <= reviewForm.rating ? 'text-amber-400 fill-amber-400' : 'text-slate-300'}`} />
                  </button>
                ))}
              </div>
            </div>
            
            <div>
              <label className="text-sm font-medium mb-2 block">Review Title</label>
              <Input
                placeholder={t("companyReview.summaryPlaceholder")}
                value={reviewForm.title}
                onChange={(e) => setReviewForm({...reviewForm, title: e.target.value})}
              />
            </div>
            
            <div>
              <label className="text-sm font-medium mb-2 block">Pros</label>
              <Textarea
                placeholder={t("companyReview.prosPlaceholder")}
                value={reviewForm.pros}
                onChange={(e) => setReviewForm({...reviewForm, pros: e.target.value})}
              />
            </div>
            
            <div>
              <label className="text-sm font-medium mb-2 block">Cons</label>
              <Textarea
                placeholder={t("companyReview.consPlaceholder")}
                value={reviewForm.cons}
                onChange={(e) => setReviewForm({...reviewForm, cons: e.target.value})}
              />
            </div>
            
            <div>
              <label className="text-sm font-medium mb-2 block">Your Position (optional)</label>
              <Input
                placeholder={t("companyReview.jobTitlePlaceholder")}
                value={reviewForm.position}
                onChange={(e) => setReviewForm({...reviewForm, position: e.target.value})}
              />
            </div>
            
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={reviewForm.is_current_employee}
                  onChange={(e) => setReviewForm({...reviewForm, is_current_employee: e.target.checked})}
                  className="rounded"
                />
                <span className="text-sm">I currently work here</span>
              </label>
              
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={reviewForm.recommend}
                  onChange={(e) => setReviewForm({...reviewForm, recommend: e.target.checked})}
                  className="rounded"
                />
                <span className="text-sm">I recommend this company</span>
              </label>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowReviewDialog(false)}>Cancel</Button>
            <Button onClick={submitReview}>Submit Review</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default CompanyProfilePage;
