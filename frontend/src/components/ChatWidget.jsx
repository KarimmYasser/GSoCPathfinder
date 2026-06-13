import { useState, useRef, useEffect } from 'react';
import { Fab, Paper, Box, Typography, IconButton, TextField, CircularProgress } from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import CloseIcon from '@mui/icons-material/Close';
import SendIcon from '@mui/icons-material/Send';

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

      <Box flex={1} overflow="auto" p={2} display="flex" flexDirection="column" gap={2} bgcolor="grey.50">
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
              <Typography variant="body2">{msg.content}</Typography>
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
