import { useState } from 'react';
import { Paper, TextField, Button, Typography, CircularProgress, Box } from '@mui/material';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';

const CVInput = ({ onResults }) => {
  const [cvText, setCvText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!cvText.trim() || loading) return;

    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/match', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ cv_text: cvText }),
      });

      if (!response.ok) {
        throw new Error('Failed to match CV. Please try again.');
      }

      const data = await response.json();
      onResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper elevation={2} sx={{ p: 4, width: '100%', maxWidth: '800px', borderRadius: 3 }}>
      <form onSubmit={handleSubmit}>
        <TextField
          fullWidth
          multiline
          rows={12}
          variant="outlined"
          placeholder="Paste your resume or CV text here..."
          value={cvText}
          onChange={(e) => setCvText(e.target.value)}
          disabled={loading}
          sx={{ mb: 3 }}
        />
        
        {error && (
          <Typography color="error" variant="body2" sx={{ mb: 2 }}>
            {error}
          </Typography>
        )}

        <Box display="flex" justifyContent="center">
          <Button
            type="submit"
            variant="contained"
            color="primary"
            size="large"
            disabled={!cvText.trim() || loading}
            startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <AutoAwesomeIcon />}
            sx={{ px: 6, py: 1.5, fontSize: '1.1rem' }}
          >
            {loading ? 'Analyzing Matches...' : 'Find Matches'}
          </Button>
        </Box>
      </form>
    </Paper>
  );
};

export default CVInput;
