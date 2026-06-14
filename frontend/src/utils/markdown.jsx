/* eslint-disable react-refresh/only-export-components */
import { Box, Typography, useTheme } from '@mui/material';

// Internal helper: parses a single line of text into inline React elements
const parseInline = (content, isDark) => {
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
            backgroundColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.07)',
            color: isDark ? '#e6edf3' : '#1f2328',
            padding: '2px 5px',
            borderRadius: '4px',
            fontFamily: '"Roboto Mono", monospace',
            fontSize: '0.85em',
            fontWeight: 500,
            border: isDark ? '1px solid rgba(255,255,255,0.12)' : '1px solid rgba(0,0,0,0.1)',
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

  return parts;
};

// RenderMarkdown: a React component that is fully theme-aware
export const RenderMarkdown = ({ text }) => {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  if (!text) return null;

  const lines = text.split('\n');

  return (
    <>
      {lines.map((line, lineIdx) => {
        const isListItem = line.trim().startsWith('- ') || line.trim().startsWith('* ');
        const isHeading2 = line.trim().startsWith('## ');
        const isHeading3 = line.trim().startsWith('### ');

        if (line.trim() === '') {
          return <Box key={lineIdx} height={8} />;
        }

        if (isHeading2) {
          const content = line.trim().substring(3);
          return (
            <Typography key={lineIdx} variant="subtitle1" sx={{ fontWeight: 'bold', mt: 1.5, mb: 0.5, color: 'text.primary', fontFamily: 'inherit' }}>
              {parseInline(content, isDark)}
            </Typography>
          );
        }

        if (isHeading3) {
          const content = line.trim().substring(4);
          return (
            <Typography key={lineIdx} variant="body2" sx={{ fontWeight: 'bold', mt: 1, mb: 0.5, color: 'primary.main', fontFamily: 'inherit' }}>
              {parseInline(content, isDark)}
            </Typography>
          );
        }

        if (isListItem) {
          const content = line.trim().substring(2);
          return (
            <Box key={lineIdx} component="li" sx={{ ml: 2, mb: 0.5, display: 'list-item', listStyleType: 'disc', color: 'inherit' }}>
              <Typography variant="body2" component="span" sx={{ fontFamily: 'inherit', color: 'inherit' }}>
                {parseInline(content, isDark)}
              </Typography>
            </Box>
          );
        }

        return (
          <Typography key={lineIdx} variant="body2" sx={{ mb: 1, '&:last-child': { mb: 0 }, fontFamily: 'inherit', color: 'inherit' }}>
            {parseInline(line, isDark)}
          </Typography>
        );
      })}
    </>
  );
};

// Legacy function shim — kept for backward compatibility,
// wraps RenderMarkdown into JSX so existing call-sites still work.
export const renderMarkdown = (text) => <RenderMarkdown text={text} />;
