import { useState, useRef, useEffect } from 'react';
import { Fab, Paper, Box, Typography, IconButton, TextField, CircularProgress } from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import CloseIcon from '@mui/icons-material/Close';
import SendIcon from '@mui/icons-material/Send';

// Helper to render markdown (bold, italic, inline code, and lists) natively
const renderMarkdown = (text) => {
  if (!text) return '';
  const lines = text.split('\n');
  
  return lines.map((line, lineIdx) => {
    const isListItem = line.trim().startsWith('- ') || line.trim().startsWith('* ');
    let content = isListItem ? line.trim().substring(2) : line;
    
    const parts = [];
    let currentIndex = 0;
    const regex = /(\*\*.*?\*\*|\*.*?\*|`.*?`)/g;
    let match;
    
    while ((match = regex.exec(content)) !== null) {
      const matchIndex = match.index;
      if (matchIndex > currentIndex) {
        parts.push(content.substring(currentIndex, matchIndex));
      }
      
      const token = match[0];
      if (token.startsWith('**') && token.endsWith('**')) {
        parts.push(<strong key={matchIndex}>{token.slice(2, -2)}</strong>);
      } else if (token.startsWith('*') && token.endsWith('*')) {
        parts.push(<em key={matchIndex}>{token.slice(1, -1)}</em>);
      } else if (token.startsWith('`') && token.endsWith('`')) {
        parts.push(
          <code 
            key={matchIndex} 
            style={{ 
              backgroundColor: 'rgba(0, 0, 0, 0.06)', 
              padding: '2px 4px', 
              borderRadius: '4px',
              fontFamily: '"Roboto Mono", monospace',
              fontSize: '0.85em',
              fontWeight: 500
            }}
          >
            {token.slice(1, -1)}
          </code>
        );
      }
      currentIndex = regex.lastIndex;
    }
    
    if (currentIndex < content.length) {
      parts.push(content.substring(currentIndex));
    }
    
    if (line.trim() === '') {
      return <Box key={lineIdx} height={8} />;
    }
    
    if (isListItem) {
      return (
        <Box key={lineIdx} component="li" sx={{ ml: 2, mb: 0.5, display: 'list-item', listStyleType: 'disc' }}>
          <Typography variant="body2" component="span" sx={{ fontFamily: 'inherit' }}>
            {parts}
          </Typography>
        </Box>
      );
    }
    
    return (
      <Typography key={lineIdx} variant="body2" sx={{ mb: 1, '&:last-child': { mb: 0 }, fontFamily: 'inherit' }}>
        {parts}
      </Typography>
    );
  });
};

const ChatWidget = ({ context }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hi! I can help answer questions about your matched organizations. What would you like to know?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...messages, userMsg],
          context: context
        })
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered a network error. Please try again.' }]);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) {
    return (
      <Fab 
        color="primary" 
        aria-label="chat" 
        onClick={() => setIsOpen(true)}
        sx={{ position: 'fixed', bottom: 32, right: 32 }}
      >
        <ChatIcon />
      </Fab>
    );
  }

  return (
    <Paper 
      elevation={6}
      sx={{
        position: 'fixed', bottom: 32, right: 32,
        width: 350, height: 500,
        display: 'flex', flexDirection: 'column',
        borderRadius: 3, overflow: 'hidden', zIndex: 1000
      }}
    >
      <Box bgcolor="primary.main" color="primary.contrastText" p={2} display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h6">Match Assistant</Typography>
        <IconButton size="small" onClick={() => setIsOpen(false)} sx={{ color: 'inherit' }}>
          <CloseIcon />
        </IconButton>
      </Box>

      {/* Message Area: flex=1, minHeight=0, and overflowY=auto forces containment and scrolling */}
      <Box 
        sx={{ 
          flex: 1, 
          minHeight: 0, 
          overflowY: 'auto', 
          p: 2, 
          display: 'flex', 
          flexDirection: 'column', 
          gap: 2, 
          bgcolor: 'grey.50' 
        }}
      >
        {messages.map((msg, idx) => (
          <Box key={idx} alignSelf={msg.role === 'user' ? 'flex-end' : 'flex-start'} maxWidth="85%">
            <Paper 
              elevation={1} 
              sx={{ 
                p: 1.5, 
                bgcolor: msg.role === 'user' ? 'primary.main' : 'white',
                color: msg.role === 'user' ? 'primary.contrastText' : 'text.primary',
                borderRadius: 2,
                borderTopRightRadius: msg.role === 'user' ? 0 : undefined,
                borderTopLeftRadius: msg.role === 'assistant' ? 0 : undefined,
              }}
            >
              <Box sx={{ '& li': { color: 'inherit' } }}>
                {renderMarkdown(msg.content)}
              </Box>
            </Paper>
          </Box>
        ))}
        {loading && (
          <Box alignSelf="flex-start">
            <Paper elevation={1} sx={{ p: 1.5, borderRadius: 2, borderTopLeftRadius: 0 }}>
              <CircularProgress size={16} />
            </Paper>
          </Box>
        )}
        <div ref={messagesEndRef} />
      </Box>

      <Box component="form" onSubmit={handleSend} p={1.5} bgcolor="white" borderTop="1px solid" borderColor="grey.200" display="flex" gap={1}>
        <TextField
          size="small"
          fullWidth
          placeholder="Ask about your matches..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
        <IconButton type="submit" color="primary" disabled={!input.trim() || loading}>
          <SendIcon />
        </IconButton>
      </Box>
    </Paper>
  );
};

export default ChatWidget;
