import { useState } from 'react';
import { Box, Typography, Button, Paper, Tabs, Tab, Grid } from '@mui/material';
import ReplayIcon from '@mui/icons-material/Replay';
import OrgCard from './OrgCard';
import ChatWidget from './ChatWidget';
import GraphViz from './GraphViz';

const MatchResults = ({ results, onReset }) => {
  const { user_profile, rankings } = results;
  const [tabValue, setTabValue] = useState(0);

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" component="h2" fontWeight="bold">
          Your Top Matches
        </Typography>
        <Button variant="outlined" onClick={onReset} startIcon={<ReplayIcon />}>
          Start Over
        </Button>
      </Box>

      <Paper elevation={2} sx={{ p: 3, mb: 4, borderRadius: 3, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
        <Typography variant="h6" gutterBottom fontWeight="bold">Your Profile Analysis</Typography>
        <Typography variant="body1">
          {user_profile.summary}
        </Typography>
      </Paper>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="List View" />
          <Tab label="Knowledge Graph" />
        </Tabs>
      </Box>

      {tabValue === 0 && (
        <Grid container spacing={3}>
          {rankings.map((org) => (
            <Grid item xs={12} md={6} key={org.canonical_name}>
              <OrgCard org={org} cvText={user_profile.raw_cv_text} />
            </Grid>
          ))}
        </Grid>
      )}

      {tabValue === 1 && (
        <GraphViz skills={user_profile.skills} rankings={rankings} />
      )}

      <ChatWidget context={rankings} />
    </Box>
  );
};

export default MatchResults;
