import { useState } from 'react';
import { Card, CardContent, CardActions, Typography, Button, Box, Chip, Dialog, DialogTitle, DialogContent, DialogActions, CircularProgress, Accordion, AccordionSummary, AccordionDetails } from '@mui/material';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import BugReportIcon from '@mui/icons-material/BugReport';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { renderMarkdown } from '../utils/markdown';
import API_BASE from '../config';

const parseExplanation = (explanation) => {
  if (!explanation) return null;
  
  if (!explanation.includes('### ')) {
    return null;
  }
  
  const sections = {};
  const parts = explanation.split(/(?=### )/);
  
  parts.forEach(part => {
    const lines = part.trim().split('\n');
    const headerLine = lines[0].replace('###', '').trim();
    const content = lines.slice(1).join('\n').trim();
    
    if (headerLine === 'MATCH JUSTIFICATION') {
      sections.justification = content;
    } else if (headerLine === 'RECOMMENDED CONTRIBUTOR PROJECT') {
      sections.project = content;
    } else if (headerLine === 'MAINTAINER CRITIQUE & RISK ASSESSMENT') {
      sections.critique = content;
    } else if (headerLine === 'ACTIONABLE PROPOSAL STRATEGY & ROADMAP') {
      sections.roadmap = content;
    } else if (headerLine === 'RECOMMENDATION SCORE') {
      sections.score = content;
    } else {
      sections[headerLine.toLowerCase().replace(/\s+/g, '_')] = content;
    }
  });
  
  return sections;
};

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

  const getScoreStyles = (score) => {
    if (score >= 80) {
      return { bgcolor: '#2e7d32', color: '#ffffff' }; // Google Green / Success
    } else if (score >= 60) {
      return { bgcolor: '#ed6c02', color: '#ffffff' }; // Orange / Warning
    } else {
      return { bgcolor: '#d32f2f', color: '#ffffff' }; // Google Red / Error
    }
  };

  const fetchIssues = async () => {
    setLoadingIssues(true);
    try {
      const response = await fetch(`${API_BASE}/api/issues`, {
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
      const response = await fetch(`${API_BASE}/api/proposal`, {
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
      const response = await fetch(`${API_BASE}/api/optimize_cv`, {
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
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
          <Box>
            <Typography variant="h5" component="h3" sx={{ fontWeight: 'bold' }}>
              {org.canonical_name}
            </Typography>
            <Typography variant="subtitle2" color="text.secondary">
              {org.category}
            </Typography>
          </Box>
          <Box sx={{ ...getScoreStyles(totalScore), px: 1.5, py: 0.5, borderRadius: 1 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>{totalScore}% Match</Typography>
          </Box>
        </Box>

        {org.description && (
          <Typography variant="body2" color="text.secondary" paragraph>
            {org.description.length > 200 ? org.description.substring(0, 200) + '...' : org.description}
          </Typography>
        )}

        <Box sx={{ mb: 2 }}>
          {org.matched_technologies?.length > 0 && (
            <Box sx={{ mb: 1.5 }}>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>Matched Skills</Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {org.matched_technologies.map((tech, idx) => (
                  <Chip key={idx} label={tech} size="small" color="success" variant="outlined" />
                ))}
              </Box>
            </Box>
          )}

          {org.matched_topics?.length > 0 && (
            <Box sx={{ mt: 1.5 }}>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>Matched Topics</Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {org.matched_topics.map((topic, idx) => (
                  <Chip key={idx} label={topic} size="small" color="warning" variant="outlined" />
                ))}
              </Box>
            </Box>
          )}
        </Box>

        {(() => {
          const parsed = parseExplanation(org.explanation);
          if (parsed) {
            return (
              <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 1, textAlign: 'left' }}>
                {parsed.justification && (
                  <Box sx={{ bgcolor: 'action.hover', p: 2, borderRadius: 2, borderLeft: '4px solid #1a73e8' }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: 'primary.main', mb: 0.5, fontFamily: "'Roboto Mono', monospace" }}>
                      Match Justification
                    </Typography>
                    <Box sx={{ fontFamily: "'Roboto Mono', monospace" }}>{renderMarkdown(parsed.justification)}</Box>
                  </Box>
                )}

                {parsed.project && (
                  <Accordion sx={{ 
                    borderRadius: '8px !important', 
                    boxShadow: 'none', 
                    border: '1px solid rgba(0,0,0,0.08)',
                    '&::before': { display: 'none' } 
                  }}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ minHeight: 48 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: 'success.main', fontFamily: "'Roboto Mono', monospace" }}>
                        🎯 Recommended Contributor Project
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails sx={{ pt: 0, bgcolor: 'rgba(76, 175, 80, 0.02)', textAlign: 'left' }}>
                      <Box sx={{ fontFamily: "'Roboto Mono', monospace" }}>{renderMarkdown(parsed.project)}</Box>
                    </AccordionDetails>
                  </Accordion>
                )}

                {parsed.critique && (
                  <Accordion sx={{ 
                    borderRadius: '8px !important', 
                    boxShadow: 'none', 
                    border: '1px solid rgba(0,0,0,0.08)',
                    '&::before': { display: 'none' } 
                  }}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ minHeight: 48 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: 'error.main', fontFamily: "'Roboto Mono', monospace" }}>
                        ⚠️ Maintainer Critique & Risk Assessment
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails sx={{ pt: 0, bgcolor: 'rgba(244, 67, 54, 0.02)', textAlign: 'left' }}>
                      <Box sx={{ fontFamily: "'Roboto Mono', monospace" }}>{renderMarkdown(parsed.critique)}</Box>
                    </AccordionDetails>
                  </Accordion>
                )}

                {parsed.roadmap && (
                  <Accordion sx={{ 
                    borderRadius: '8px !important', 
                    boxShadow: 'none', 
                    border: '1px solid rgba(0,0,0,0.08)',
                    '&::before': { display: 'none' } 
                  }}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ minHeight: 48 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: 'secondary.main', fontFamily: "'Roboto Mono', monospace" }}>
                        🚀 Actionable Proposal Strategy & Roadmap
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails sx={{ pt: 0, bgcolor: 'rgba(234, 67, 53, 0.02)', textAlign: 'left' }}>
                      <Box sx={{ fontFamily: "'Roboto Mono', monospace" }}>{renderMarkdown(parsed.roadmap)}</Box>
                    </AccordionDetails>
                  </Accordion>
                )}
              </Box>
            );
          }
          
          return org.explanation ? (
            <Box sx={{ bgcolor: 'action.hover', p: 2, borderRadius: 1, mt: 2, textAlign: 'left' }}>
              <Typography variant="body2" fontStyle="italic" sx={{ fontFamily: "'Roboto Mono', monospace" }}>
                "{org.explanation}"
              </Typography>
            </Box>
          ) : null;
        })()}

        {issues && issues.length > 0 && (
          <Box sx={{ mt: 3, p: 2, bgcolor: 'action.hover', borderRadius: 1, border: '1px solid', borderColor: 'divider' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1, display: 'flex', alignItems: 'center' }}>
              <BugReportIcon fontSize="small" sx={{ mr: 1 }} /> Good First Issues
            </Typography>
            <ul style={{ paddingLeft: '1.2rem', margin: 0 }}>
              {issues.map((issue, idx) => (
                <li key={idx} style={{ marginBottom: '8px' }}>
                  <Typography variant="body2" component="a" href={issue.url} target="_blank" sx={{ textDecoration: 'none', color: 'primary.main', '&:hover': { textDecoration: 'underline' } }}>
                    #{issue.number} {issue.title}
                  </Typography>
                  <Box sx={{ mt: 0.5 }}>
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
          <Box sx={{ whiteSpace: 'pre-wrap', fontFamily: "'Roboto Mono', monospace", fontSize: '0.85rem', textAlign: 'left' }}>
            {renderMarkdown(proposal)}
          </Box>
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
          <Box sx={{ whiteSpace: 'pre-wrap', fontFamily: "'Roboto Mono', monospace", fontSize: '0.85rem', textAlign: 'left' }}>
            {renderMarkdown(roadmap)}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRoadmap(null)}>Close</Button>
        </DialogActions>
      </Dialog>

    </Card>
  );
};

export default OrgCard;
