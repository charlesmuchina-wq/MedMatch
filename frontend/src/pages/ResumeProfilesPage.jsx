import { useState, useEffect, useCallback } from "react";
import { useTranslation } from "@/utils/i18n";
import axios from "axios";
import { toast } from "sonner";
import { useTheme } from "@/App";
import { 
  FileText, Plus, Trash2, Check, Upload, Star, StarOff,
  Edit3, Save, X, Loader2, ChevronRight, User, Briefcase
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog";
import { useDropzone } from "react-dropzone";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Profile Card Component
const ProfileCard = ({ profile, isActive, onSelect, onSetDefault, onDelete, onEdit }) => {
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async (e) => {
    e.stopPropagation();
    if (!confirm("Delete this resume profile?")) return;
    setDeleting(true);
    await onDelete(profile.id);
    setDeleting(false);
  };

  return (
    <Card 
      className={`cursor-pointer transition-all hover:border-turquoise ${
        isActive ? 'border-2 border-turquoise bg-turquoise/5' : ''
      }`}
      onClick={() => onSelect(profile)}
    >
      <CardContent className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
              isActive 
                ? 'bg-gradient-to-br from-turquoise to-turquoise-light text-white' 
                : 'bg-slate-100 dark:bg-slate-800 text-slate-500'
            }`}>
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-900 dark:text-slate-100">{profile.name}</h3>
              <p className="text-sm text-slate-500 dark:text-slate-400">{profile.full_name || 'No name'}</p>
            </div>
          </div>
          {profile.is_default && (
            <Badge className="bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300">
              <Star className="w-3 h-3 mr-1 fill-current" /> Default
            </Badge>
          )}
        </div>

        <div className="space-y-2 mb-4">
          <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
            <User className="w-4 h-4" />
            <span>{profile.email || 'No email'}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
            <Briefcase className="w-4 h-4" />
            <span>{profile.skills?.length || 0} skills</span>
          </div>
        </div>

        <div className="flex flex-wrap gap-1.5 mb-4">
          {profile.skills?.slice(0, 4).map((skill, i) => (
            <Badge key={i} variant="secondary" className="text-xs">{skill}</Badge>
          ))}
          {profile.skills?.length > 4 && (
            <Badge variant="outline" className="text-xs">+{profile.skills.length - 4}</Badge>
          )}
        </div>

        <div className="flex items-center gap-2 pt-3 border-t border-slate-100 dark:border-slate-800">
          {!profile.is_default && (
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={(e) => { e.stopPropagation(); onSetDefault(profile.id); }}
              className="text-slate-500 hover:text-amber-600"
            >
              <StarOff className="w-4 h-4 mr-1" /> Set Default
            </Button>
          )}
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={(e) => { e.stopPropagation(); onEdit(profile); }}
            className="text-slate-500 hover:text-sky-600"
          >
            <Edit3 className="w-4 h-4 mr-1" /> Edit
          </Button>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={handleDelete}
            disabled={deleting}
            className="text-slate-500 hover:text-rose-600 ml-auto"
          >
            {deleting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

// Upload Dialog Component
const UploadDialog = ({ open, onClose, onUpload }) => {
  const [profileName, setProfileName] = useState("");
  const [uploading, setUploading] = useState(false);
  const [file, setFile] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    const f = acceptedFiles[0];
    if (f && f.name.endsWith('.pdf')) {
      setFile(f);
    } else {
      toast.error("Please upload a PDF file");
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1
  });

  const handleUpload = async () => {
    if (!file || !profileName.trim()) {
      toast.error("Please provide a profile name and PDF file");
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('profile_name', profileName);

    try {
      await axios.post(`${API}/resume/profiles/upload?profile_name=${encodeURIComponent(profileName)}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      toast.success("Resume profile created!");
      onUpload();
      onClose();
      setFile(null);
      setProfileName("");
    } catch (e) {
      toast.error(e.response?.data?.detail || "Failed to upload resume");
    }
    setUploading(false);
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle style={{ fontFamily: 'IBM Plex Sans' }}>Create Resume Profile</DialogTitle>
          <DialogDescription>Upload a PDF resume to create a new profile</DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          <div>
            <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Profile Name</label>
            <Input
              placeholder="e.g., Tech Resume, Management Resume"
              value={profileName}
              onChange={(e) => setProfileName(e.target.value)}
              className="mt-1"
            />
          </div>

          <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
            <input {...getInputProps()} />
            <Upload className="w-8 h-8 text-slate-400 mx-auto mb-2" />
            {file ? (
              <p className="text-slate-700 dark:text-slate-300 font-medium">{file.name}</p>
            ) : (
              <>
                <p className="text-slate-700 dark:text-slate-300">
                  {isDragActive ? "Drop your resume here" : "Drag & drop resume PDF"}
                </p>
                <p className="text-slate-500 text-sm mt-1">or click to browse</p>
              </>
            )}
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={handleUpload} disabled={uploading || !file || !profileName.trim()}>
            {uploading ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Uploading...</> : 'Create Profile'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

const ResumeProfilesPage = ({ setResume }) => {
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedProfile, setSelectedProfile] = useState(null);
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [editingProfile, setEditingProfile] = useState(null);

  useEffect(() => {
    fetchProfiles();
  }, []);

  const fetchProfiles = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/resume/profiles`);
      setProfiles(response.data || []);
      // Select default profile
      const defaultProfile = response.data?.find(p => p.is_default);
      if (defaultProfile) setSelectedProfile(defaultProfile);
    } catch (e) {
      console.error("Failed to fetch profiles:", e);
    }
    setLoading(false);
  };

  const handleSetDefault = async (profileId) => {
    try {
      await axios.post(`${API}/resume/profiles/${profileId}/set-default`);
      toast.success("Default profile updated!");
      fetchProfiles();
      // Update the main resume context
      const profile = profiles.find(p => p.id === profileId);
      if (profile && setResume) setResume(profile);
    } catch (e) {
      toast.error("Failed to set default");
    }
  };

  const handleDelete = async (profileId) => {
    try {
      await axios.delete(`${API}/resume/profiles/${profileId}`);
      toast.success("Profile deleted");
      fetchProfiles();
    } catch (e) {
      toast.error("Failed to delete profile");
    }
  };

  const handleSelectProfile = (profile) => {
    setSelectedProfile(profile);
  };

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-6xl mx-auto animate-fade-in" data-testid="resume-profiles-page">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900 dark:text-slate-100 tracking-tight" style={{ fontFamily: 'IBM Plex Sans' }}>
            Resume Profiles
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">
            Manage multiple resume versions for different job types
          </p>
        </div>
        <Button onClick={() => setShowUploadDialog(true)} className="bg-gradient-to-r from-turquoise to-turquoise-light">
          <Plus className="w-4 h-4 mr-2" /> New Profile
        </Button>
      </div>

      {loading ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="animate-pulse space-y-4">
                  <div className="flex gap-3">
                    <div className="w-12 h-12 bg-slate-200 dark:bg-slate-700 rounded-xl" />
                    <div className="flex-1 space-y-2">
                      <div className="h-4 w-24 bg-slate-200 dark:bg-slate-700 rounded" />
                      <div className="h-3 w-32 bg-slate-200 dark:bg-slate-700 rounded" />
                    </div>
                  </div>
                  <div className="h-20 bg-slate-200 dark:bg-slate-700 rounded" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : profiles.length === 0 ? (
        <Card className="border-dashed border-2">
          <CardContent className="p-12 text-center">
            <FileText className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-slate-700 dark:text-slate-300 mb-2">No Resume Profiles</h3>
            <p className="text-slate-500 dark:text-slate-400 mb-6">
              Create different resume profiles for various job types and industries
            </p>
            <Button onClick={() => setShowUploadDialog(true)} className="bg-gradient-to-r from-turquoise to-turquoise-light">
              <Plus className="w-4 h-4 mr-2" /> Create First Profile
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {profiles.map(profile => (
            <ProfileCard
              key={profile.id}
              profile={profile}
              isActive={selectedProfile?.id === profile.id}
              onSelect={handleSelectProfile}
              onSetDefault={handleSetDefault}
              onDelete={handleDelete}
              onEdit={(p) => setEditingProfile(p)}
            />
          ))}
          
          {/* Add New Card */}
          <Card 
            className="border-dashed border-2 cursor-pointer hover:border-turquoise hover:bg-turquoise/5 transition-all"
            onClick={() => setShowUploadDialog(true)}
          >
            <CardContent className="p-6 h-full flex flex-col items-center justify-center min-h-[200px]">
              <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-3">
                <Plus className="w-6 h-6 text-slate-400" />
              </div>
              <p className="font-medium text-slate-600 dark:text-slate-400">Add New Profile</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Selected Profile Details */}
      {selectedProfile && (
        <Card className="mt-8">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2" style={{ fontFamily: 'IBM Plex Sans' }}>
                <FileText className="w-5 h-5 text-turquoise" />
                {selectedProfile.name}
              </CardTitle>
              {selectedProfile.is_default && (
                <Badge className="bg-amber-100 text-amber-700">
                  <Star className="w-3 h-3 mr-1 fill-current" /> Default Profile
                </Badge>
              )}
            </div>
            <CardDescription>
              Last updated: {new Date(selectedProfile.updated_at).toLocaleDateString()}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-slate-900 dark:text-slate-100 mb-3">Contact</h4>
                <div className="space-y-2 text-sm">
                  <p><span className="text-slate-500">Name:</span> {selectedProfile.full_name || '-'}</p>
                  <p><span className="text-slate-500">Email:</span> {selectedProfile.email || '-'}</p>
                  <p><span className="text-slate-500">Phone:</span> {selectedProfile.phone || '-'}</p>
                </div>
              </div>
              <div>
                <h4 className="font-medium text-slate-900 dark:text-slate-100 mb-3">Summary</h4>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  {selectedProfile.summary || 'No summary available'}
                </p>
              </div>
            </div>
            
            {selectedProfile.skills?.length > 0 && (
              <div className="mt-6">
                <h4 className="font-medium text-slate-900 dark:text-slate-100 mb-3">Skills</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedProfile.skills.map((skill, i) => (
                    <Badge key={i} variant="secondary">{skill}</Badge>
                  ))}
                </div>
              </div>
            )}

            {selectedProfile.experience?.length > 0 && (
              <div className="mt-6">
                <h4 className="font-medium text-slate-900 dark:text-slate-100 mb-3">Experience</h4>
                <div className="space-y-3">
                  {selectedProfile.experience.map((exp, i) => (
                    <div key={i} className="border-l-2 border-turquoise pl-4">
                      <p className="font-medium text-slate-900 dark:text-slate-100">{exp.title}</p>
                      <p className="text-sm text-slate-600 dark:text-slate-400">
                        {exp.company} • {exp.duration}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <UploadDialog 
        open={showUploadDialog} 
        onClose={() => setShowUploadDialog(false)}
        onUpload={fetchProfiles}
      />
    </div>
  );
};

export default ResumeProfilesPage;
