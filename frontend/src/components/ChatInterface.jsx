import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Sparkles, FileText, ChevronDown, ChevronUp, AlertCircle, Loader2 } from 'lucide-react';
import { chatService } from '../services/api';

const ChatInterface = ({ company }) => {
  const [messages, setMessages] = useState(() => {
    const saved = localStorage.getItem(`chat_history_${company.id}`);
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {}
    }
    return [
      {
        role: 'assistant',
        content: `Hello. I am the InvestiLens AI assistant. I can answer questions about ${company.name} based only on the documents you've uploaded. What would you like to know?`,
        intent: null,
        evidence: null,
        suggested: ["What are the main financial risks?", "How did revenue change?", "What is management's outlook?"]
      }
    ];
  });
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [expandedEvidence, setExpandedEvidence] = useState({});
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  useEffect(() => {
    localStorage.setItem(`chat_history_${company.id}`, JSON.stringify(messages));
  }, [messages, company.id]);

  const handleSend = async (text = input) => {
    if (!text.trim() || loading) return;

    const userMessage = { role: 'user', content: text.trim() };
    const currentMessages = [...messages, userMessage];
    setMessages(currentMessages);
    setInput('');
    setLoading(true);

    try {
      const historyPayload = currentMessages
        .slice(0, -1) // Exclude the current question we are about to ask
        .map(m => ({ role: m.role, content: m.content }));

      const response = await chatService.askQuestion({
        company_id: company.id,
        question: text.trim(),
        history: historyPayload
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.answer,
        evidence: response.evidence,
        confidence: response.confidence,
        intent: response.intent,
        suggested: response.suggested_questions || []
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Chat error", error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "I encountered an error trying to process your request. Please try again.",
        isError: true
      }]);
    } finally {
      setLoading(false);
      setTimeout(() => inputRef.current?.focus(), 10);
    }
  };

  const toggleEvidence = (msgIndex) => {
    setExpandedEvidence(prev => ({
      ...prev,
      [msgIndex]: !prev[msgIndex]
    }));
  };

  const clearChat = () => {
    if (window.confirm("Are you sure you want to clear the chat history?")) {
      const initialMessage = [
        {
          role: 'assistant',
          content: `Hello. I am the InvestiLens AI assistant. I can answer questions about ${company.name} based only on the documents you've uploaded. What would you like to know?`,
          intent: null,
          evidence: null,
          suggested: ["What are the main financial risks?", "How did revenue change?", "What is management's outlook?"]
        }
      ];
      setMessages(initialMessage);
      localStorage.setItem(`chat_history_${company.id}`, JSON.stringify(initialMessage));
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-140px)] max-w-4xl mx-auto rounded-xl overflow-hidden card card-glass p-0 border-border animate-in">
      {/* ── Chat Header ── */}
      <header className="bg-bg-card border-b border-border p-4 flex justify-between items-center z-10 shadow-sm relative">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary to-secondary opacity-70"></div>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary-soft text-primary flex items-center justify-center border border-primary-glow">
            <Sparkles size={18} />
          </div>
          <div>
            <h2 className="font-bold text-base leading-tight">InvestiLens Assistant</h2>
            <p className="text-[0.6875rem] font-bold uppercase tracking-wider text-primary mt-0.5">Evidence-Grounded AI</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={clearChat}
            className="text-[0.6875rem] font-bold uppercase tracking-wider text-muted hover:text-danger transition-colors bg-bg-elevated px-2 py-1 rounded border border-border"
          >
            Clear Chat
          </button>
          <div className="text-xs font-medium bg-bg-elevated px-3 py-1.5 rounded-full border border-border">
            <span className="text-muted mr-1">Analyzing:</span>
            <span className="text-text-primary">{company.name}</span>
          </div>
        </div>
      </header>

      {/* ── Messages Area ── */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 bg-bg-surface/50 scroll-smooth">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-primary-soft border border-primary-glow flex items-center justify-center text-primary flex-shrink-0 mt-1 shadow-primary">
                <Sparkles size={14} />
              </div>
            )}
            
            <div className={`max-w-[85%] md:max-w-[75%] flex flex-col gap-1.5 ${msg.role === 'user' ? 'items-end order-1' : 'items-start order-2'}`}>
              
              {/* Message Bubble */}
              <div 
                className={`p-4 rounded-2xl text-[0.9375rem] leading-relaxed shadow-sm ${
                  msg.role === 'user' 
                    ? 'bg-primary text-white rounded-tr-none' 
                    : msg.isError 
                      ? 'bg-danger-soft border border-[rgba(239,68,68,0.2)] text-text-primary rounded-tl-none'
                      : 'bg-bg-elevated border border-border text-text-primary rounded-tl-none'
                }`}
              >
                {msg.isError && <AlertCircle size={16} className="text-danger inline mb-1 mr-2" />}
                <p className="whitespace-pre-wrap font-medium">{msg.content}</p>
              </div>

              {/* Tags & Confidence */}
              {msg.role === 'assistant' && msg.confidence && !msg.isError && (
                <div className="flex gap-2 ml-1">
                  <span className={`text-[0.6875rem] px-2 py-0.5 rounded border font-bold uppercase tracking-wide ${
                    msg.confidence === 'High' ? 'bg-success-soft text-success border-[rgba(34,197,94,0.2)]' :
                    msg.confidence === 'Medium' ? 'bg-warning-soft text-warning border-[rgba(245,158,11,0.2)]' :
                    'bg-danger-soft text-danger border-[rgba(239,68,68,0.2)]'
                  }`}>
                    {msg.confidence}
                  </span>
                  {msg.intent && (
                    <span className="text-[0.6875rem] px-2 py-0.5 rounded bg-bg-card border border-border text-muted font-bold uppercase tracking-wide">
                      {msg.intent.replace('_', ' ')}
                    </span>
                  )}
                </div>
              )}

              {/* Evidence Accordion */}
              {msg.role === 'assistant' && msg.evidence && msg.evidence.length > 0 && (
                <div className="mt-2 w-full max-w-sm bg-bg-elevated border border-border rounded-lg overflow-hidden transition-all duration-200">
                  <button 
                    className="w-full flex justify-between items-center p-2.5 text-xs font-semibold hover:bg-bg-card transition-colors text-text-secondary"
                    onClick={() => toggleEvidence(idx)}
                    aria-expanded={expandedEvidence[idx]}
                  >
                    <div className="flex items-center gap-2">
                      <FileText size={14} className="text-primary" />
                      <span>{msg.evidence.length} Source{msg.evidence.length !== 1 ? 's' : ''} Cited</span>
                    </div>
                    {expandedEvidence[idx] ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  </button>
                  
                  {expandedEvidence[idx] && (
                    <div className="p-3 border-t border-border space-y-3 bg-bg-surface">
                      {msg.evidence.map((src, sIdx) => (
                        <div key={sIdx} className="text-xs border-l-2 border-primary-dim pl-2.5 py-0.5">
                          <div className="flex justify-between font-bold text-text-primary mb-1">
                            <span className="truncate pr-2">{src.document}</span>
                            <span className="text-muted flex-shrink-0">{src.page ? `Pg ${src.page}` : ''}</span>
                          </div>
                          <p className="text-muted italic line-clamp-4 leading-relaxed">"{src.text}"</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Suggestions (only on latest msg) */}
              {msg.role === 'assistant' && msg.suggested && msg.suggested.length > 0 && idx === messages.length - 1 && (
                <div className="mt-4 flex flex-wrap gap-2">
                  {msg.suggested.map((suggestion, sIdx) => (
                    <button
                      key={sIdx}
                      onClick={() => handleSend(suggestion)}
                      className="text-xs font-medium bg-bg-card hover:bg-bg-elevated border border-border text-text-secondary hover:text-text-primary hover:border-border-hover px-3 py-1.5 rounded-full transition-all duration-200"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-bg-elevated border border-border flex items-center justify-center text-text-secondary order-2 flex-shrink-0 mt-1">
                <User size={14} />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-4 justify-start animate-in">
            <div className="w-8 h-8 rounded-full bg-primary-soft border border-primary-glow flex items-center justify-center text-primary mt-1">
              <Sparkles size={14} />
            </div>
            <div className="bg-bg-elevated border border-border rounded-2xl rounded-tl-none p-4 px-5 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
              <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
              <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} className="h-2" />
      </div>

      {/* ── Input Area ── */}
      <div className="p-4 bg-bg-card border-t border-border">
        <form 
          className="relative max-w-4xl mx-auto flex items-end bg-bg-base border border-border rounded-xl focus-within:border-primary focus-within:box-shadow-primary transition-all duration-200 p-1"
          onSubmit={(e) => { e.preventDefault(); handleSend(); }}
        >
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about financials, risks, or strategy..."
            className="flex-1 bg-transparent border-none px-4 py-3 text-sm focus:outline-none text-text-primary placeholder-muted"
            disabled={loading}
            autoFocus
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="w-10 h-10 mb-0.5 mr-0.5 rounded-lg bg-primary flex items-center justify-center text-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-primary-dim transition-colors flex-shrink-0"
            aria-label="Send message"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} className="ml-0.5" />}
          </button>
        </form>
        <div className="text-center mt-2">
          <span className="text-[0.625rem] text-muted font-medium uppercase tracking-widest">AI responses may be inaccurate. Verify with evidence.</span>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
