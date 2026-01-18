import { useState, useEffect, useCallback, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { toast } from "sonner";
import { useTheme } from "@/App";
import { 
  MessageSquare, Send, ChevronLeft, User, Clock, Check, CheckCheck,
  Loader2, Search, Inbox, Plus, ArrowRight, Mail, Languages
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { QuickTranslateButton } from "@/components/TranslationWidget";
import { useTranslation } from "@/utils/i18n";
import { apiClient } from "@/utils/apiClient";

const MessagesPage = ({ user }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isDark } = useTheme();
  const { t } = useTranslation();
  const messagesEndRef = useRef(null);
  
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [sending, setSending] = useState(false);
  const [newMessage, setNewMessage] = useState("");
  const [unreadCount, setUnreadCount] = useState(0);
  
  // For new message
  const [showNewMessage, setShowNewMessage] = useState(false);
  const [newRecipient, setNewRecipient] = useState({ id: "", name: "", email: "" });
  const [newSubject, setNewSubject] = useState("");

  const fetchConversations = useCallback(async () => {
    try {
      const response = await apiClient.get("/api/messages/conversations");
      setConversations(response.data || []);
    } catch (e) {
      console.error("Failed to fetch conversations:", e);
    }
    setLoading(false);
  }, []);

  const fetchUnreadCount = useCallback(async () => {
    try {
      const response = await apiClient.get("/api/messages/unread-count");
      setUnreadCount(response.data.unread_count || 0);
    } catch (e) {
      console.error(e);
    }
  }, []);

  useEffect(() => {
    fetchConversations();
    fetchUnreadCount();
    
    // Check URL params for new message
    const params = new URLSearchParams(location.search);
    const recipientId = params.get('recipient');
    const recipientName = params.get('name');
    const recipientEmail = params.get('email');
    
    if (recipientId) {
      setShowNewMessage(true);
      setNewRecipient({
        id: recipientId,
        name: recipientName || "",
        email: recipientEmail || ""
      });
    }
  }, [location, fetchConversations, fetchUnreadCount]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const selectConversation = async (conversation) => {
    setSelectedConversation(conversation);
    setShowNewMessage(false);
    setLoadingMessages(true);
    
    try {
      const response = await apiClient.get(`/api/messages/conversations/${conversation.id}`);
      setMessages(response.data.messages || []);
      fetchConversations(); // Refresh to update unread counts
      fetchUnreadCount();
    } catch (e) {
      toast.error(t("messages.loadFailed") || "Failed to load messages");
    }
    setLoadingMessages(false);
  };

  const sendMessage = async () => {
    if (!newMessage.trim()) return;
    
    setSending(true);
    
    try {
      let recipientId;
      
      if (showNewMessage) {
        recipientId = newRecipient.id;
      } else if (selectedConversation) {
        // Find the other participant
        const otherParticipant = selectedConversation.participants?.find(
          p => p.user_id !== user?.user_id
        );
        recipientId = otherParticipant?.user_id;
      }
      
      if (!recipientId) {
        toast.error(t("messages.noRecipient") || "No recipient selected");
        setSending(false);
        return;
      }
      
      const response = await apiClient.post("/api/messages/send", {
        recipient_id: recipientId,
        subject: showNewMessage ? newSubject : undefined,
        content: newMessage
      });
      
      setNewMessage("");
      
      if (showNewMessage) {
        // Switch to the new conversation
        setShowNewMessage(false);
        fetchConversations();
        
        // Load the new conversation
        if (response.data.conversation_id) {
          const convResponse = await apiClient.get(`/api/messages/conversations/${response.data.conversation_id}`);
          setSelectedConversation(convResponse.data.conversation);
          setMessages(convResponse.data.messages || []);
        }
      } else {
        // Reload current conversation
        await selectConversation(selectedConversation);
      }
      
      toast.success(t("messages.sent") || "Message sent");
    } catch (e) {
      toast.error(t("messages.sendFailed") || "Failed to send message");
      console.error(e);
    }
    setSending(false);
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffDays === 1) {
      return t("common.yesterday") || "Yesterday";
    } else if (diffDays < 7) {
      return date.toLocaleDateString([], { weekday: 'short' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  const getOtherParticipant = (conversation) => {
    return conversation.participants?.find(p => p.user_id !== user?.user_id) || {};
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-turquoise" />
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-120px)] flex flex-col md:flex-row gap-4 p-4 md:p-6" data-testid="messages-page">
      {/* Conversations List */}
      <div className={`w-full md:w-80 flex-shrink-0 ${selectedConversation || showNewMessage ? 'hidden md:block' : ''}`}>
        <Card className="h-full">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2 text-lg">
                <MessageSquare className="w-5 h-5 text-turquoise" />
                {t("messages.title") || "Messages"}
                {unreadCount > 0 && (
                  <Badge className="bg-turquoise text-white">{unreadCount}</Badge>
                )}
              </CardTitle>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => {
                  setShowNewMessage(true);
                  setSelectedConversation(null);
                  setNewRecipient({ id: "", name: "", email: "" });
                }}
                data-testid="new-message-btn"
              >
                <Plus className="w-4 h-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="p-2">
            {conversations.length > 0 ? (
              <div className="space-y-1">
                {conversations.map((conv) => {
                  const other = getOtherParticipant(conv);
                  return (
                    <button
                      key={conv.id}
                      onClick={() => selectConversation(conv)}
                      className={`w-full p-3 rounded-lg text-left transition-colors
                        ${selectedConversation?.id === conv.id 
                          ? 'bg-turquoise/10 border border-turquoise/30' 
                          : 'hover:bg-slate-100 dark:hover:bg-slate-800'
                        }`}
                      data-testid={`conversation-${conv.id}`}
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-turquoise to-emerald-500 
                          flex items-center justify-center text-white font-semibold">
                          {(other.name || other.email || "?")[0].toUpperCase()}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <p className="font-medium text-slate-900 dark:text-slate-100 truncate">
                              {other.name || other.email}
                            </p>
                            <span className="text-xs text-slate-400">
                              {formatTime(conv.last_message_at)}
                            </span>
                          </div>
                          <p className="text-sm text-slate-500 truncate">
                            {conv.last_message?.content?.substring(0, 40) || conv.subject || t("messages.noMessages") || "No messages yet"}
                          </p>
                        </div>
                        {conv.unread > 0 && (
                          <Badge className="bg-turquoise text-white text-xs">
                            {conv.unread}
                          </Badge>
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-8 text-slate-500">
                <Inbox className="w-10 h-10 mx-auto mb-2 opacity-30" />
                <p className="text-sm">{t("messages.noConversations") || "No conversations yet"}</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Message Thread / New Message */}
      <div className="flex-1 flex flex-col">
        {showNewMessage ? (
          <Card className="flex-1 flex flex-col">
            <CardHeader className="border-b dark:border-slate-700 pb-4">
              <div className="flex items-center gap-3">
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className="md:hidden"
                  onClick={() => setShowNewMessage(false)}
                >
                  <ChevronLeft className="w-4 h-4" />
                </Button>
                <div>
                  <CardTitle className="text-lg">{t("messages.newMessage") || "New Message"}</CardTitle>
                  {newRecipient.name && (
                    <p className="text-sm text-slate-500">{t("messages.to") || "To"}: {newRecipient.name}</p>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent className="flex-1 p-4 flex flex-col">
              {!newRecipient.id && (
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">{t("messages.recipientId") || "Recipient ID"}</label>
                  <Input
                    placeholder={t("messages.enterRecipientId") || "Enter recipient user ID..."}
                    value={newRecipient.id}
                    onChange={(e) => setNewRecipient({ ...newRecipient, id: e.target.value })}
                    data-testid="recipient-input"
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    {t("messages.useSearch") || "Use candidate search to find and message candidates"}
                  </p>
                </div>
              )}
              
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">{t("messages.subject") || "Subject (optional)"}</label>
                <Input
                  placeholder={t("messages.subjectPlaceholder") || "Message subject..."}
                  value={newSubject}
                  onChange={(e) => setNewSubject(e.target.value)}
                  data-testid="subject-input"
                />
              </div>
              
              <div className="flex-1 flex flex-col justify-end">
                <div className="flex gap-2">
                  <Textarea
                    placeholder={t("messages.typePlaceholder") || "Type your message..."}
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    className="flex-1 resize-none"
                    rows={4}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendMessage();
                      }
                    }}
                    data-testid="message-input"
                  />
                  <Button 
                    onClick={sendMessage}
                    disabled={sending || !newMessage.trim() || !newRecipient.id}
                    className="self-end"
                    data-testid="send-btn"
                  >
                    {sending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ) : selectedConversation ? (
          <Card className="flex-1 flex flex-col">
            <CardHeader className="border-b dark:border-slate-700 pb-4">
              <div className="flex items-center gap-3">
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className="md:hidden"
                  onClick={() => setSelectedConversation(null)}
                >
                  <ChevronLeft className="w-4 h-4" />
                </Button>
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-turquoise to-emerald-500 
                  flex items-center justify-center text-white font-semibold">
                  {(getOtherParticipant(selectedConversation).name || "?")[0].toUpperCase()}
                </div>
                <div>
                  <CardTitle className="text-lg">
                    {getOtherParticipant(selectedConversation).name || getOtherParticipant(selectedConversation).email}
                  </CardTitle>
                  {selectedConversation.subject && (
                    <p className="text-sm text-slate-500">{selectedConversation.subject}</p>
                  )}
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="flex-1 p-4 overflow-y-auto">
              {loadingMessages ? (
                <div className="flex items-center justify-center h-full">
                  <Loader2 className="w-6 h-6 animate-spin text-turquoise" />
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map((msg, idx) => {
                    const isOwn = msg.sender_id === user?.user_id;
                    return (
                      <div
                        key={msg.id || idx}
                        className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}
                      >
                        <div className={`max-w-[70%] ${isOwn ? 'order-2' : 'order-1'}`}>
                          <div className={`p-3 rounded-2xl ${
                            isOwn 
                              ? 'bg-turquoise text-white rounded-br-sm' 
                              : 'bg-slate-100 dark:bg-slate-800 rounded-bl-sm'
                          }`}>
                            <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                          </div>
                          <div className={`flex items-center gap-1 mt-1 ${isOwn ? 'justify-end' : 'justify-start'}`}>
                            <span className="text-xs text-slate-400">
                              {formatTime(msg.sent_at)}
                            </span>
                            {isOwn && (
                              msg.read 
                                ? <CheckCheck className="w-3 h-3 text-turquoise" />
                                : <Check className="w-3 h-3 text-slate-400" />
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </CardContent>
            
            {/* Message Input */}
            <div className="p-4 border-t dark:border-slate-700">
              <div className="flex gap-2">
                <Textarea
                  placeholder={t("messages.typeMessage") || "Type a message..."}
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  className="flex-1 resize-none"
                  rows={2}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage();
                    }
                  }}
                  data-testid="reply-input"
                />
                <Button 
                  onClick={sendMessage}
                  disabled={sending || !newMessage.trim()}
                  className="self-end"
                  data-testid="send-reply-btn"
                >
                  {sending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                </Button>
              </div>
            </div>
          </Card>
        ) : (
          <Card className="flex-1 flex items-center justify-center">
            <div className="text-center p-8">
              <MessageSquare className="w-16 h-16 mx-auto mb-4 text-slate-300" />
              <h3 className="text-lg font-medium text-slate-600 dark:text-slate-400">
                {t("messages.selectConversation") || "Select a conversation"}
              </h3>
              <p className="text-sm text-slate-500 mt-1 mb-4">
                {t("messages.orStartNew") || "Or start a new message"}
              </p>
              <Button onClick={() => setShowNewMessage(true)} className="gap-2" data-testid="start-new-message-btn">
                <Plus className="w-4 h-4" />
                {t("messages.newMessage") || "New Message"}
              </Button>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};

export default MessagesPage;
