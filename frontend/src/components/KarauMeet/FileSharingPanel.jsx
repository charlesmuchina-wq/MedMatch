import { useState, useRef, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  FileText, Upload, Download, Link2, Copy, Check,
  Image, Film, File, Archive, Trash2, Share2, Loader2
} from 'lucide-react';
import { useTranslation } from '@/utils/i18n';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const FILE_ICONS = {
  'image': Image,
  'video': Film,
  'application/pdf': FileText,
  'application/zip': Archive,
  'default': File,
};

const getFileIcon = (type) => {
  if (type?.startsWith('image/')) return FILE_ICONS['image'];
  if (type?.startsWith('video/')) return FILE_ICONS['video'];
  return FILE_ICONS[type] || FILE_ICONS['default'];
};

const formatSize = (bytes) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

/**
 * File Sharing Panel for in-meeting P2P file sharing.
 * Files are shared as data URLs/blobs via WebSocket signaling.
 */
export const FileSharingPanel = ({ meetingId, userId, userName, ws, onClose }) => {
  const { t } = useTranslation();
  const [sharedFiles, setSharedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [linkUrl, setLinkUrl] = useState('');
  const [copiedId, setCopiedId] = useState(null);
  const fileInputRef = useRef(null);
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB for P2P

  const handleFileSelect = useCallback(async (e) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    setUploading(true);
    for (const file of files) {
      if (file.size > MAX_FILE_SIZE) {
        toast.error(t("karauMeet.fileTooLarge") || `File too large: ${file.name} (max 10MB)`);
        continue;
      }

      try {
        // Read file as base64 for P2P transfer
        const reader = new FileReader();
        const dataUrl = await new Promise((resolve, reject) => {
          reader.onload = () => resolve(reader.result);
          reader.onerror = reject;
          reader.readAsDataURL(file);
        });

        const fileEntry = {
          id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
          name: file.name,
          size: file.size,
          type: file.type,
          dataUrl,
          sharedBy: { userId, name: userName },
          sharedAt: new Date().toISOString(),
        };

        // Add to local state
        setSharedFiles(prev => [fileEntry, ...prev]);

        // Broadcast via WebSocket to all participants
        if (ws?.current?.readyState === WebSocket.OPEN) {
          // For large files, send metadata only - peers can request download
          ws.current.send(JSON.stringify({
            type: 'file_shared',
            file: {
              id: fileEntry.id,
              name: fileEntry.name,
              size: fileEntry.size,
              type: fileEntry.type,
              sharedBy: fileEntry.sharedBy,
              sharedAt: fileEntry.sharedAt,
              // Only send data for files under 2MB via WS
              dataUrl: file.size <= 2 * 1024 * 1024 ? dataUrl : null,
            }
          }));
        }

        toast.success(t("karauMeet.fileShared") || `Shared: ${file.name}`);
      } catch (err) {
        toast.error(t("karauMeet.fileShareFailed") || `Failed to share ${file.name}`);
      }
    }
    setUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  }, [userId, userName, ws, t]);

  const handleShareLink = useCallback(() => {
    if (!linkUrl.trim()) return;

    const linkEntry = {
      id: `link-${Date.now()}`,
      name: linkUrl,
      size: 0,
      type: 'link',
      url: linkUrl,
      sharedBy: { userId, name: userName },
      sharedAt: new Date().toISOString(),
    };

    setSharedFiles(prev => [linkEntry, ...prev]);

    if (ws?.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        type: 'file_shared',
        file: linkEntry
      }));
    }

    setLinkUrl('');
    toast.success(t("karauMeet.linkShared") || 'Link shared');
  }, [linkUrl, userId, userName, ws, t]);

  const handleDownload = useCallback((file) => {
    if (file.type === 'link') {
      window.open(file.url, '_blank');
      return;
    }
    if (file.dataUrl) {
      const a = document.createElement('a');
      a.href = file.dataUrl;
      a.download = file.name;
      a.click();
    }
  }, []);

  const handleCopyLink = useCallback((file) => {
    const text = file.type === 'link' ? file.url : file.name;
    navigator.clipboard.writeText(text);
    setCopiedId(file.id);
    setTimeout(() => setCopiedId(null), 2000);
  }, []);

  const handleRemove = useCallback((fileId) => {
    setSharedFiles(prev => prev.filter(f => f.id !== fileId));
    if (ws?.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: 'file_removed', fileId }));
    }
  }, [ws]);

  // Listen for incoming files from peers
  const handleIncomingFile = useCallback((fileData) => {
    setSharedFiles(prev => {
      if (prev.some(f => f.id === fileData.id)) return prev;
      return [fileData, ...prev];
    });
  }, []);

  return (
    <div className="flex flex-col h-full" data-testid="file-sharing-panel">
      <div className="p-3 border-b border-karau-border">
        <h3 className="font-semibold text-white flex items-center gap-2 text-sm">
          <Share2 className="w-4 h-4 text-purple-400" />
          {t("karauMeet.fileSharing") || "File Sharing"}
        </h3>
        <p className="text-[10px] text-slate-500 mt-0.5">{t("karauMeet.fileSharingDesc") || "Share files with meeting participants"}</p>
      </div>

      <div className="p-3 space-y-2 border-b border-karau-border">
        <input
          ref={fileInputRef}
          type="file"
          multiple
          className="hidden"
          onChange={handleFileSelect}
          data-testid="file-input"
        />
        <Button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="w-full h-9 bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-500 hover:to-violet-500 text-white rounded-xl text-xs"
          data-testid="upload-file-btn"
        >
          {uploading ? <Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5" /> : <Upload className="w-3.5 h-3.5 mr-1.5" />}
          {uploading ? (t("karauMeet.uploading") || "Uploading...") : (t("karauMeet.uploadFile") || "Upload File")}
        </Button>

        <div className="flex gap-1.5">
          <Input
            value={linkUrl}
            onChange={(e) => setLinkUrl(e.target.value)}
            placeholder={t("karauMeet.shareLinkPlaceholder") || "Paste a link to share..."}
            className="bg-karau-bg/60 border-white/10 text-white text-xs h-8 rounded-lg"
            onKeyDown={(e) => e.key === 'Enter' && handleShareLink()}
            data-testid="share-link-input"
          />
          <Button onClick={handleShareLink} disabled={!linkUrl.trim()} size="sm"
            className="h-8 px-2 bg-emerald-500/80 hover:bg-emerald-400 rounded-lg" data-testid="share-link-btn">
            <Link2 className="w-3.5 h-3.5" />
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1 p-2">
        {sharedFiles.length === 0 ? (
          <div className="text-center py-8" data-testid="no-files-message">
            <File className="w-8 h-8 text-slate-600 mx-auto mb-2" />
            <p className="text-xs text-slate-500">{t("karauMeet.noFilesShared") || "No files shared yet"}</p>
            <p className="text-[10px] text-slate-600 mt-0.5">{t("karauMeet.dragOrUpload") || "Upload or paste a link above"}</p>
          </div>
        ) : (
          <div className="space-y-1.5">
            {sharedFiles.map((file) => {
              const IconComp = file.type === 'link' ? Link2 : getFileIcon(file.type);
              return (
                <div key={file.id}
                  className="group flex items-center gap-2 p-2 rounded-lg bg-karau-bg/40 hover:bg-karau-surface/60 transition-colors"
                  data-testid={`shared-file-${file.id}`}>
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                    file.type === 'link' ? 'bg-blue-500/10' : 'bg-violet-500/10'
                  }`}>
                    <IconComp className={`w-4 h-4 ${file.type === 'link' ? 'text-blue-400' : 'text-violet-400'}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-white truncate">{file.name}</p>
                    <div className="flex items-center gap-2 text-[10px] text-slate-500">
                      <span>{file.sharedBy?.name}</span>
                      {file.size > 0 && <><span>&middot;</span><span>{formatSize(file.size)}</span></>}
                    </div>
                  </div>
                  <div className="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button onClick={() => handleDownload(file)} className="p-1 hover:bg-white/5 rounded" title="Download">
                      <Download className="w-3 h-3 text-emerald-400" />
                    </button>
                    <button onClick={() => handleCopyLink(file)} className="p-1 hover:bg-white/5 rounded" title="Copy">
                      {copiedId === file.id ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3 text-slate-400" />}
                    </button>
                    {file.sharedBy?.userId === userId && (
                      <button onClick={() => handleRemove(file.id)} className="p-1 hover:bg-red-500/10 rounded" title="Remove">
                        <Trash2 className="w-3 h-3 text-red-400" />
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </ScrollArea>

      <div className="p-2 border-t border-karau-border">
        <p className="text-[9px] text-slate-600 text-center">
          {t("karauMeet.p2pSharingNote") || "Files are shared peer-to-peer within this meeting. Max 10MB per file."}
        </p>
      </div>
    </div>
  );
};

export default FileSharingPanel;
