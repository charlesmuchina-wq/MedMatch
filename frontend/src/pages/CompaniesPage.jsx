import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import { useTheme } from "@/App";
import { 
  Building2, MapPin, Users, Star, Search, Plus, 
  Filter, Loader2, ChevronRight, Heart, Globe
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const API = process.env.REACT_APP_BACKEND_URL;

const INDUSTRIES = [
  "Technology", "Healthcare", "Medical Devices", "Pharmaceuticals", "Biotechnology",
  "Aerospace", "Automotive", "Manufacturing", "Finance", "Consulting",
  "Retail", "Energy", "Telecommunications", "Education", "Government"
];

const COMPANY_SIZES = [
  { value: "1-10", label: "1-10 employees" },
  { value: "11-50", label: "11-50 employees" },
  { value: "51-200", label: "51-200 employees" },
  { value: "201-500", label: "201-500 employees" },
  { value: "501-1000", label: "501-1000 employees" },
  { value: "1000+", label: "1000+ employees" }
];

const CompaniesPage = ({ user }) => {
  const navigate = useNavigate();
  const { isDark } = useTheme();
  
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedIndustry, setSelectedIndustry] = useState("");
  const [selectedSize, setSelectedSize] = useState("");
  
  // Create Company Dialog
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [createForm, setCreateForm] = useState({
    name: "",
    description: "",
    industry: "",
    size: "",
    website: "",
    headquarters: "",
    founded: "",
    specialties: "",
    benefits: "",
    culture_values: ""
  });
  const [creating, setCreating] = useState(false);

  const isRecruiter = user?.role === "recruiter";

  useEffect(() => {
    fetchCompanies();
  }, [selectedIndustry, selectedSize]);

  const fetchCompanies = async () => {
    try {
      let url = `${API}/api/companies/?limit=50`;
      if (selectedIndustry) url += `&industry=${encodeURIComponent(selectedIndustry)}`;
      if (selectedSize) url += `&size=${encodeURIComponent(selectedSize)}`;
      
      const response = await axios.get(url);
      setCompanies(response.data || []);
    } catch (e) {
      console.error("Failed to load companies:", e);
    }
    setLoading(false);
  };

  const searchCompanies = async () => {
    if (!searchQuery.trim()) {
      fetchCompanies();
      return;
    }

    setLoading(true);
    try {
      const response = await axios.get(
        `${API}/api/companies/?search=${encodeURIComponent(searchQuery)}&limit=50`
      );
      setCompanies(response.data || []);
    } catch (e) {
      toast.error("Search failed");
    }
    setLoading(false);
  };

  const createCompany = async () => {
    if (!createForm.name || !createForm.description || !createForm.industry) {
      toast.error("Please fill in required fields");
      return;
    }

    setCreating(true);
    try {
      const companyData = {
        name: createForm.name,
        description: createForm.description,
        industry: createForm.industry,
        size: createForm.size || null,
        website: createForm.website || null,
        headquarters: createForm.headquarters || null,
        founded: createForm.founded || null,
        specialties: createForm.specialties ? createForm.specialties.split(",").map(s => s.trim()) : [],
        benefits: createForm.benefits ? createForm.benefits.split(",").map(s => s.trim()) : [],
        culture_values: createForm.culture_values ? createForm.culture_values.split(",").map(s => s.trim()) : []
      };

      const response = await axios.post(`${API}/api/companies/`, companyData);
      toast.success("Company profile created");
      setShowCreateDialog(false);
      resetCreateForm();
      fetchCompanies();
      
      // Navigate to the new company page
      navigate(`/companies/${response.data.company_id}`);
    } catch (e) {
      toast.error(e.response?.data?.detail || "Failed to create company");
    }
    setCreating(false);
  };

  const resetCreateForm = () => {
    setCreateForm({
      name: "",
      description: "",
      industry: "",
      size: "",
      website: "",
      headquarters: "",
      founded: "",
      specialties: "",
      benefits: "",
      culture_values: ""
    });
  };

  const followCompany = async (companyId, e) => {
    e.stopPropagation();
    try {
      const response = await axios.post(`${API}/api/companies/${companyId}/follow`);
      toast.success(response.data.message);
      fetchCompanies();
    } catch (e) {
      toast.error("Failed to follow company");
    }
  };

  const renderStars = (rating) => {
    return [...Array(5)].map((_, i) => (
      <Star 
        key={i} 
        className={`w-3 h-3 ${i < Math.round(rating) ? 'text-amber-400 fill-amber-400' : 'text-slate-300'}`} 
      />
    ));
  };

  const filteredCompanies = companies.filter(company => {
    if (searchQuery && !company.name.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    return true;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-turquoise" />
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-6xl mx-auto animate-fade-in" data-testid="companies-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl md:text-4xl font-semibold text-slate-900 dark:text-slate-100">
            Companies
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-2">
            Discover companies and find your next opportunity
          </p>
        </div>
        
        {isRecruiter && (
          <Button onClick={() => setShowCreateDialog(true)} className="gap-2">
            <Plus className="w-4 h-4" />
            Create Company Profile
          </Button>
        )}
      </div>

      {/* Search & Filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-8">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input
            placeholder="Search companies..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && searchCompanies()}
            className="pl-10"
          />
        </div>
        
        <Select value={selectedIndustry} onValueChange={setSelectedIndustry}>
          <SelectTrigger className="w-full md:w-48">
            <SelectValue placeholder="Industry" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Industries</SelectItem>
            {INDUSTRIES.map((ind) => (
              <SelectItem key={ind} value={ind}>{ind}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        
        <Select value={selectedSize} onValueChange={setSelectedSize}>
          <SelectTrigger className="w-full md:w-48">
            <SelectValue placeholder="Company Size" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Sizes</SelectItem>
            {COMPANY_SIZES.map((size) => (
              <SelectItem key={size.value} value={size.value}>{size.label}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Companies Grid */}
      {filteredCompanies.length > 0 ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCompanies.map((company) => (
            <Card 
              key={company.id}
              className="hover:border-turquoise/50 transition-all cursor-pointer hover:shadow-lg"
              onClick={() => navigate(`/companies/${company.id}`)}
              data-testid={`company-card-${company.id}`}
            >
              <CardContent className="p-5">
                <div className="flex items-start gap-4">
                  {/* Logo */}
                  <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-turquoise to-emerald-500 
                    flex items-center justify-center text-white text-xl font-bold flex-shrink-0">
                    {company.logo_url ? (
                      <img 
                        src={company.logo_url} 
                        alt={company.name} 
                        className="w-full h-full object-cover rounded-xl" 
                      />
                    ) : (
                      company.name[0]
                    )}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-slate-900 dark:text-slate-100 truncate">
                      {company.name}
                    </h3>
                    <p className="text-sm text-slate-500 truncate">{company.industry}</p>
                    
                    {/* Stats */}
                    <div className="flex items-center gap-3 mt-2">
                      <div className="flex items-center gap-1">
                        {renderStars(company.stats?.average_rating || 0)}
                        <span className="text-xs text-slate-500 ml-1">
                          ({company.stats?.total_reviews || 0})
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Description */}
                <p className="text-sm text-slate-600 dark:text-slate-400 mt-4 line-clamp-2">
                  {company.description}
                </p>

                {/* Meta */}
                <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-100 dark:border-slate-800">
                  <div className="flex items-center gap-3 text-xs text-slate-500">
                    {company.headquarters && (
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {company.headquarters}
                      </span>
                    )}
                    {company.size && (
                      <span className="flex items-center gap-1">
                        <Users className="w-3 h-3" />
                        {company.size}
                      </span>
                    )}
                  </div>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => followCompany(company.id, e)}
                    className="p-2"
                  >
                    <Heart className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="py-12 text-center">
            <Building2 className="w-16 h-16 mx-auto mb-4 text-slate-300" />
            <h3 className="text-lg font-medium text-slate-600 dark:text-slate-400">
              No companies found
            </h3>
            <p className="text-sm text-slate-400 mt-1">
              {searchQuery 
                ? "Try a different search term"
                : "Be the first to create a company profile"
              }
            </p>
            {isRecruiter && (
              <Button 
                onClick={() => setShowCreateDialog(true)} 
                className="mt-4 gap-2"
              >
                <Plus className="w-4 h-4" />
                Create Company Profile
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Create Company Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create Company Profile</DialogTitle>
            <DialogDescription>
              Add your company to attract top talent
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Company Name *</label>
                <Input
                  placeholder="Company name"
                  value={createForm.name}
                  onChange={(e) => setCreateForm({...createForm, name: e.target.value})}
                />
              </div>
              
              <div>
                <label className="text-sm font-medium mb-2 block">Industry *</label>
                <Select
                  value={createForm.industry}
                  onValueChange={(value) => setCreateForm({...createForm, industry: value})}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select industry" />
                  </SelectTrigger>
                  <SelectContent>
                    {INDUSTRIES.map((ind) => (
                      <SelectItem key={ind} value={ind}>{ind}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Description *</label>
              <Textarea
                placeholder="Tell candidates about your company..."
                value={createForm.description}
                onChange={(e) => setCreateForm({...createForm, description: e.target.value})}
                rows={4}
              />
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Company Size</label>
                <Select
                  value={createForm.size}
                  onValueChange={(value) => setCreateForm({...createForm, size: value})}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select size" />
                  </SelectTrigger>
                  <SelectContent>
                    {COMPANY_SIZES.map((size) => (
                      <SelectItem key={size.value} value={size.value}>{size.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="text-sm font-medium mb-2 block">Headquarters</label>
                <Input
                  placeholder="City, Country"
                  value={createForm.headquarters}
                  onChange={(e) => setCreateForm({...createForm, headquarters: e.target.value})}
                />
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Website</label>
                <Input
                  placeholder="https://..."
                  value={createForm.website}
                  onChange={(e) => setCreateForm({...createForm, website: e.target.value})}
                />
              </div>
              
              <div>
                <label className="text-sm font-medium mb-2 block">Founded Year</label>
                <Input
                  placeholder="2020"
                  value={createForm.founded}
                  onChange={(e) => setCreateForm({...createForm, founded: e.target.value})}
                />
              </div>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Specialties</label>
              <Input
                placeholder="AI, Machine Learning, Healthcare (comma separated)"
                value={createForm.specialties}
                onChange={(e) => setCreateForm({...createForm, specialties: e.target.value})}
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Benefits</label>
              <Input
                placeholder="Remote work, Health insurance, 401k (comma separated)"
                value={createForm.benefits}
                onChange={(e) => setCreateForm({...createForm, benefits: e.target.value})}
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Culture & Values</label>
              <Input
                placeholder="Innovation, Collaboration, Diversity (comma separated)"
                value={createForm.culture_values}
                onChange={(e) => setCreateForm({...createForm, culture_values: e.target.value})}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
              Cancel
            </Button>
            <Button onClick={createCompany} disabled={creating} className="gap-2">
              {creating && <Loader2 className="w-4 h-4 animate-spin" />}
              Create Profile
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default CompaniesPage;
