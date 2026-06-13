import { useState } from 'react';
import { Card, CardContent, CardActions, Typography, Button, Box, Chip, Dialog, DialogTitle, DialogContent, DialogActions, CircularProgress } from '@mui/material';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import BugReportIcon from '@mui/icons-material/BugReport';

const OrgCard = ({ org, cvText }) => {
  const [issues, setIssues] = useState(null);
  const [loadingIssues, setLoadingIssues] = useState(false);
  const [proposal, setProposal] = useState(null);
  const [loadingProposal, setLoadingProposal] = useState(false);
  const [roadmap, setRoadmap] = useState(null);
  const [loadingRoadmap, setLoadingRoadmap] = useState(false);

  const totalScore = org.score && typeof org.score === 'object' && org.score.total !== undefined
    ? Math.round(org.score.total * 100)
    : Math.round(org.score * 100) || 0;

  const fetchIssues = async () => {
    setLoadingIssues(true);
    try {
      const response = await fetch('http://localhost:8000/api/issues', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: org.url })
      });
      if (response.ok) {
        const data = await response.json();
        setIssues(data.issues);
      } else {
        setIssues([]);
      }
    } catch (err) {
      console.error(err);
      setIssues([]);
    } finally {
      setLoadingIssues(false);
    }
  };

  const draftProposal = async () => {
    setLoadingProposal(true);
    try {
      const response = await fetch('http://localhost:8000/api/proposal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cv_text: cvText, org_name: org.canonical_name, org_desc: org.description })
      });
      if (response.ok) {
        const data = await response.json();
        setProposal(data.proposal);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingProposal(false);
    }
  };

  const optimizeCV = async () => {
    setLoadingRoadmap(true);
    try {
      const response = await fetch('http://localhost:8000/api/optimize_cv', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cv_text: cvText, org_name: org.canonical_name, org_desc: org.description })
      });
      if (response.ok) {
        const data = await response.json();
        setRoadmap(data.roadmap);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingRoadmap(false);
    }
  };

  return (
    <Card sx={{ display: 'flex', flexDirection: 'column', height: '100%' }} elevation={1}>
      <CardContent sx={{ flexGrow: 1, p: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={3}>
          <Box>
            <Typography variant="h5" component="h3" fontWeight="bold">
              {org.canonical_name}
            </Typography>
            <Typography variant="subtitle2" color="text.secondary">
              {org.category}
            </Typography>
          </Box>
          <Box bgcolor="primary.main" color="primary.contrastText" px={1.5} py={0.5} borderRadius={1}>
            <Typography variant="subtitle1" fontWeight="bold">{totalScore}% Match</Typography>
          </Box>
        </Box>

        {org.description && (
          <Typography variant="body2" color="text.secondary" paragraph>
            {org.description.length > 200 ? org.description.substring(0, 200) + '...' : org.description}
          </Typography>
        )}

        <Box mb={2}>
          {org.matched_technologies?.length > 0 && (
            <Box mb={1}>
              <Typography variant="caption" color="text.secondary" display="block" mb={0.5}>Matched Skills</Typography>
              <Box display="flex" flexWrap="wrap" gap={0.5}>
                {org.matched_technologies.map((tech, idx) => (
                  <Chip key={idx} label={tech} size="small" color="success" variant="outlined" />
                ))}
              </Box>
            </Box>
          )}

          {org.matched_topics?.length > 0 && (
            <Box>
              <Typography variant="caption" color="text.secondary" display="block" mb={0.5}>Matched Topics</Typography>
              <Box display="flex" flexWrap="wrap" gap={0.5}>
                {org.matched_topics.map((topic, idx) => (
                  <Chip key={idx} label={topic} size="small" color="warning" variant="outlined" />
                ))}
              </Box>
            </Box>
          )}
        </Box>

        {org.explanation && (
          <Box bgcolor="grey.100" p={2} borderRadius={1} mt={2}>
            <Typography variant="body2" fontStyle="italic">"{org.explanation}"</Typography>
          </Box>
        )}

        {issues && issues.length > 0 && (
          <Box mt={3} p={2} bgcolor="grey.50" borderRadius={1} border="1px solid" borderColor="grey.200">
            <Typography variant="subtitle2" fontWeight="bold" mb={1} display="flex" alignItems="center">
              <BugReportIcon fontSize="small" sx={{ mr: 1 }} /> Good First Issues
            </Typography>
            <ul style={{ paddingLeft: '1.2rem', margin: 0 }}>
              {issues.map((issue, idx) => (
                <li key={idx} style={{ marginBottom: '8px' }}>
                  <Typography variant="body2" component="a" href={issue.url} target="_blank" sx={{ textDecoration: 'none', color: 'primary.main', '&:hover': { textDecoration: 'underline' } }}>
                    #{issue.number} {issue.title}
                  </Typography>
                  <Box mt={0.5}>
                    {issue.labels.map((l, i) => (
                      <Chip key={i} label={l} size="small" sx={{ height: 20, fontSize: '0.65rem', mr: 0.5 }} />
                    ))}
                  </Box>
                </li>
              ))}
            </ul>
          </Box>
        )}
        {issues && issues.length === 0 && !loadingIssues && (
          <Typography variant="body2" color="text.secondary" mt={2}>No beginner issues found.</Typography>
        )}
      </CardContent>

      <CardActions sx={{ p: 3, pt: 0, flexWrap: 'wrap', gap: 1.5 }}>
        {org.url && (
          <Button size="small" variant="outlined" href={org.url} target="_blank" startIcon={<OpenInNewIcon />}>
            Visit
          </Button>
        )}
        {org.url?.includes("github.com") && !issues && (
          <Button size="small" variant="outlined" color="secondary" onClick={fetchIssues} disabled={loadingIssues} startIcon={loadingIssues ? <CircularProgress size={16} /> : <BugReportIcon />}>
            {loadingIssues ? 'Loading...' : 'Issues'}
          </Button>
        )}
        <Button size="small" variant="contained" color="primary" onClick={draftProposal} disabled={loadingProposal} startIcon={loadingProposal ? <CircularProgress size={16} /> : <AutoFixHighIcon />}>
          Draft Proposal
        </Button>
        <Button size="small" variant="contained" color="secondary" onClick={optimizeCV} disabled={loadingRoadmap} startIcon={loadingRoadmap ? <CircularProgress size={16} /> : <AutoFixHighIcon />}>
          Optimize CV
        </Button>
      </CardActions>

      {/* Proposal Dialog */}
      <Dialog open={!!proposal} onClose={() => setProposal(null)} maxWidth="md" fullWidth>
        <DialogTitle>Draft Proposal for {org.canonical_name}</DialogTitle>
        <DialogContent dividers>
          <Typography component="pre" sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '0.85rem' }}>
            {proposal}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setProposal(null)}>Close</Button>
          <Button variant="contained" onClick={() => { navigator.clipboard.writeText(proposal); alert("Copied!"); }}>
            Copy to Clipboard
          </Button>
        </DialogActions>
      </Dialog>

      {/* Roadmap Dialog */}
      <Dialog open={!!roadmap} onClose={() => setRoadmap(null)} maxWidth="md" fullWidth>
        <DialogTitle>Learning Roadmap for {org.canonical_name}</DialogTitle>
        <DialogContent dividers>
          <Typography component="pre" sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '0.85rem' }}>
            {roadmap}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRoadmap(null)}>Close</Button>
        </DialogActions>
      </Dialog>

    </Card>
  );
};

export default OrgCard;
