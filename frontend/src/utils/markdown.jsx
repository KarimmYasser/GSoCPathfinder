import React from 'react';
import { Box, Typography } from '@mui/material';

// Helper to render markdown (bold, italic, inline code, and lists) natively
export const renderMarkdown = (text) => {
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
        <Box key={lineIdx} component="li" sx={{ ml: 2, mb: 0.5, display: 'list-item', listStyleType: 'disc', color: 'inherit' }}>
          <Typography variant="body2" component="span" sx={{ fontFamily: 'inherit', color: 'inherit' }}>
            {parts}
          </Typography>
        </Box>
      );
    }
    
    return (
      <Typography key={lineIdx} variant="body2" sx={{ mb: 1, '&:last-child': { mb: 0 }, fontFamily: 'inherit', color: 'inherit' }}>
        {parts}
      </Typography>
    );
  });
};
