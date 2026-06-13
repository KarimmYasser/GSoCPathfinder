import { useState, useEffect, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { Box, Typography, CircularProgress, Paper } from '@mui/material';

const GraphViz = ({ skills, rankings }) => {
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const graphRef = useRef();

  useEffect(() => {
    const fetchGraph = async () => {
      setLoading(true);
      try {
        const orgNames = rankings.slice(0, 10).map(o => o.canonical_name);
        const response = await fetch('http://localhost:8000/api/graph_data', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ skills: skills, org_names: orgNames })
        });
        if (response.ok) {
          const data = await response.json();
          setGraphData(data);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchGraph();
  }, [skills, rankings]);

  if (loading) {
    return (
      <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" height={500}>
        <CircularProgress />
        <Typography mt={2}>Mapping Knowledge Graph...</Typography>
      </Box>
    );
  }

  if (!graphData) return <Typography>Error loading graph data.</Typography>;

  return (
    <Paper elevation={2} sx={{ width: '100%', height: 600, overflow: 'hidden', position: 'relative' }}>
      <Box position="absolute" top={10} left={10} zIndex={10} bgcolor="rgba(255,255,255,0.8)" p={1} borderRadius={1}>
        <Typography variant="caption" display="block"><span style={{color: '#1a73e8'}}>●</span> CV Skills</Typography>
        <Typography variant="caption" display="block"><span style={{color: '#ea4335'}}>●</span> Organizations</Typography>
        <Typography variant="caption" display="block"><span style={{color: '#fbbc04'}}>●</span> Technologies</Typography>
      </Box>
      <ForceGraph2D
        ref={graphRef}
        graphData={graphData}
        nodeLabel="id"
        nodeColor={node => {
          if (node.type === 'Skill') return '#1a73e8';
          if (node.type === 'Organization') return '#ea4335';
          if (node.type === 'Technology') return '#fbbc04';
          return '#999';
        }}
        nodeRelSize={6}
        linkColor={() => 'rgba(0,0,0,0.2)'}
        linkWidth={1}
        onNodeClick={node => {
          graphRef.current.centerAt(node.x, node.y, 1000);
          graphRef.current.zoom(8, 2000);
        }}
        cooldownTicks={100}
      />
    </Paper>
  );
};

export default GraphViz;
