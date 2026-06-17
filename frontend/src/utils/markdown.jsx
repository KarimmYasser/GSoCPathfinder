/* eslint-disable react-refresh/only-export-components */
import { useTheme } from '@mui/material/styles';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Box } from '@mui/material';

// RenderMarkdown: a React component that is fully theme-aware
export const RenderMarkdown = ({ text }) => {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  if (!text) return null;

  return (
    <Box
      sx={{
        fontFamily: 'inherit',
        color: 'inherit',
        '& table': {
          borderCollapse: 'collapse',
          width: '100%',
          mb: 2,
        },
        '& th, & td': {
          border: `1px solid ${theme.palette.divider}`,
          padding: '8px 12px',
          textAlign: 'left',
        },
        '& th': {
          backgroundColor: isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.03)',
          fontWeight: 'bold',
        },
        '& code': {
          backgroundColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.07)',
          color: isDark ? '#e6edf3' : '#1f2328',
          padding: '2px 5px',
          borderRadius: '4px',
          fontFamily: '"Roboto Mono", monospace',
          fontSize: '0.85em',
        },
        '& pre': {
          backgroundColor: isDark ? '#161b22' : '#f6f8fa',
          padding: '12px',
          borderRadius: '6px',
          overflow: 'auto',
          mb: 2,
          '& code': {
            backgroundColor: 'transparent',
            color: 'inherit',
            padding: 0,
            border: 'none',
          }
        },
        '& blockquote': {
          borderLeft: `4px solid ${theme.palette.divider}`,
          margin: '0 0 16px 0',
          padding: '0 16px',
          color: theme.palette.text.secondary,
        },
        '& h1, & h2, & h3, & h4, & h5, & h6': {
          marginTop: '24px',
          marginBottom: '16px',
          fontWeight: 600,
          lineHeight: 1.25,
          color: 'inherit',
        },
        '& h1': { fontSize: '1.5em', paddingBottom: '0.3em', borderBottom: `1px solid ${theme.palette.divider}` },
        '& h2': { fontSize: '1.25em', paddingBottom: '0.3em', borderBottom: `1px solid ${theme.palette.divider}` },
        '& h3': { fontSize: '1.1em' },
        '& p': {
          marginTop: 0,
          marginBottom: '16px',
        },
        '& ul, & ol': {
          marginTop: 0,
          marginBottom: '16px',
          paddingLeft: '2em',
        },
        '& li': {
          marginBottom: '4px',
        },
        '& img': {
          maxWidth: '100%',
          height: 'auto',
        }
      }}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {text}
      </ReactMarkdown>
    </Box>
  );
};

// Legacy function shim — kept for backward compatibility,
// wraps RenderMarkdown into JSX so existing call-sites still work.
export const renderMarkdown = (text) => <RenderMarkdown text={text} />;
