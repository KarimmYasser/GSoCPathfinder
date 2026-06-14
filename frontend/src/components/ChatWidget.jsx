import { useState, useRef, useEffect } from 'react';
import { Fab, Paper, Box, Typography, IconButton, TextField, CircularProgress } from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import CloseIcon from '@mui/icons-material/Close';
import SendIcon from '@mui/icons-material/Send';
import RemoveIcon from '@mui/icons-material/Remove';
import AddIcon from '@mui/icons-material/Add';
import { renderMarkdown } from '../utils/markdown';

const ChatWidget = ({ context }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hi! I can help answer questions about your matched organizations. What would you like to know?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Dimensions & Minimize states
  const [dimensions, setDimensions] = useState({ width: 350, height: 500 });
  const [isMinimized, setIsMinimized] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  
  const messagesEndRef = useRef(null);
  const dragStartRef = useRef({ x: 0, y: 0, w: 0, h: 0 });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isMinimized]);

  // Handle manual resizing from top-left
  const handleResizeStart = (e) => {
    e.preventDefault();
    setIsResizing(true);
    const clientX = e.clientX || e.touches?.[0]?.clientX;
    const clientY = e.clientY || e.touches?.[0]?.clientY;
    dragStartRef.current = {
      x: clientX,
      y: clientY,
      w: dimensions.width,
      h: dimensions.height
    };
  };

  useEffect(() => {
    const handleResizeMove = (e) => {
      if (!isResizing) return;
      const clientX = e.clientX || e.touches?.[0]?.clientX;
      const clientY = e.clientY || e.touches?.[0]?.clientY;
      const deltaX = dragStartRef.current.x - clientX;
      const deltaY = dragStartRef.current.y - clientY;
      
      const newWidth = Math.max(300, Math.min(800, dragStartRef.current.w + deltaX));
      const newHeight = Math.max(250, Math.min(800, dragStartRef.current.h + deltaY));
      
      setDimensions({ width: newWidth, height: newHeight });
    };

    const handleResizeEnd = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      window.addEventListener('mousemove', handleResizeMove);
      window.addEventListener('mouseup', handleResizeEnd);
      window.addEventListener('touchmove', handleResizeMove);
      window.addEventListener('touchend', handleResizeEnd);
    }

    return () => {
      window.removeEventListener('mousemove', handleResizeMove);
      window.removeEventListener('mouseup', handleResizeEnd);
      window.removeEventListener('touchmove', handleResizeMove);
      window.removeEventListener('touchend', handleResizeEnd);
    };
  }, [isResizing]);

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
    } catch {
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

  const currentHeight = isMinimized ? 56 : dimensions.height;

  return (
    <Paper 
      elevation={6}
      sx={{
        position: 'fixed', bottom: 32, right: 32,
        width: dimensions.width, height: currentHeight,
        display: 'flex', flexDirection: 'column',
        borderRadius: 3, overflow: 'hidden', zIndex: 1000,
        // Disable smooth transitions during manual dragging to avoid lag
        transition: isResizing ? 'none' : 'height 0.22s cubic-bezier(0.4, 0, 0.2, 1), width 0.22s cubic-bezier(0.4, 0, 0.2, 1)'
      }}
    >
      {/* Resize Handle: Drag zone at top-left corner */}
      <Box
        onMouseDown={handleResizeStart}
        onTouchStart={handleResizeStart}
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '18px',
          height: '18px',
          cursor: 'nwse-resize',
          zIndex: 1001,
          display: isMinimized ? 'none' : 'block',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 4,
            left: 4,
            width: 6,
            height: 6,
            borderLeft: '2px solid',
            borderTop: '2px solid',
            borderColor: 'divider',
          }
        }}
      />

      {/* Header Bar: Click to restore when minimized */}
      <Box 
        bgcolor="primary.main" 
        color="primary.contrastText" 
        p={2} 
        display="flex" 
        justifyContent="space-between" 
        alignItems="center"
        onClick={() => isMinimized && setIsMinimized(false)}
        sx={{ 
          cursor: isMinimized ? 'pointer' : 'default', 
          userSelect: 'none',
          height: 56,
          boxSizing: 'border-box'
        }}
      >
        <Typography variant="h6" sx={{ fontSize: '1rem', fontWeight: 'bold', fontFamily: "'Roboto Mono', monospace" }}>
          Match Assistant
        </Typography>
        <Box display="flex" alignItems="center" gap={0.5}>
          <IconButton 
            size="small" 
            onClick={(e) => {
              e.stopPropagation(); // Avoid triggering parent header onClick restore
              setIsMinimized(!isMinimized);
            }} 
            sx={{ color: 'inherit' }}
          >
            {isMinimized ? <AddIcon fontSize="small" /> : <RemoveIcon fontSize="small" />}
          </IconButton>
          <IconButton 
            size="small" 
            onClick={(e) => {
              e.stopPropagation();
              setIsOpen(false);
              setIsMinimized(false);
            }} 
            sx={{ color: 'inherit' }}
          >
            <CloseIcon fontSize="small" />
          </IconButton>
        </Box>
      </Box>

      {!isMinimized && (
        <>
          {/* Message Area */}
          <Box 
            sx={{ 
              flex: 1, 
              minHeight: 0, 
              overflowY: 'auto', 
              p: 2, 
              display: 'flex', 
              flexDirection: 'column', 
              gap: 2, 
              bgcolor: 'background.default' 
            }}
          >
            {messages.map((msg, idx) => (
              <Box key={idx} alignSelf={msg.role === 'user' ? 'flex-end' : 'flex-start'} maxWidth="85%">
                <Paper 
                  elevation={1} 
                  sx={{ 
                    p: 1.5, 
                    bgcolor: msg.role === 'user' ? 'primary.main' : 'background.paper',
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

          {/* Input Area */}
          <Box component="form" onSubmit={handleSend} p={1.5} bgcolor="background.paper" borderTop="1px solid" borderColor="divider" display="flex" gap={1}>
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
        </>
      )}
    </Paper>
  );
};

export default ChatWidget;
