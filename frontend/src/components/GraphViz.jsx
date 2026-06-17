import { useState, useEffect, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { Box, Typography, CircularProgress, Paper, useTheme } from '@mui/material';
import API_BASE from '../config';

const GraphViz = ({ skills, rankings }) => {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const graphRef = useRef();
  const containerRef = useRef();
  
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [hoverNode, setHoverNode] = useState(null);
  const [highlightNodes, setHighlightNodes] = useState(new Set());
  const [highlightLinks, setHighlightLinks] = useState(new Set());

  // Handle Container Resizing
  useEffect(() => {
    if (containerRef.current) {
      setDimensions({
        width: containerRef.current.clientWidth,
        height: containerRef.current.clientHeight || 600
      });

      const handleResize = () => {
        if (containerRef.current) {
          setDimensions({
            width: containerRef.current.clientWidth,
            height: containerRef.current.clientHeight || 600
          });
        }
      };

      window.addEventListener('resize', handleResize);
      return () => window.removeEventListener('resize', handleResize);
    }
  }, []);

  // Fetch Graph Data
  useEffect(() => {
    const fetchGraph = async () => {
      setLoading(true);
      try {
        const orgNames = (rankings || []).slice(0, 10).map(o => o.canonical_name);
        const response = await fetch(`${API_BASE}/api/graph_data`, {
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

  // Settle simulation and zoom to fit on load
  useEffect(() => {
    if (graphRef.current && graphData) {
      setTimeout(() => {
        graphRef.current.zoomToFit(400, 80);
      }, 500);
    }
  }, [graphData]);

  // Update hover state and neighbors
  const handleNodeHover = (node) => {
    setHoverNode(node);
    const newHighlightNodes = new Set();
    const newHighlightLinks = new Set();

    if (node && graphData) {
      newHighlightNodes.add(node.id);
      graphData.links.forEach(link => {
        const sourceId = link.source.id || link.source;
        const targetId = link.target.id || link.target;
        if (sourceId === node.id) {
          newHighlightNodes.add(targetId);
          newHighlightLinks.add(link);
        } else if (targetId === node.id) {
          newHighlightNodes.add(sourceId);
          newHighlightLinks.add(link);
        }
      });
    }

    setHighlightNodes(newHighlightNodes);
    setHighlightLinks(newHighlightLinks);
  };

  if (loading) {
    return (
      <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" height={600}>
        <CircularProgress />
        <Typography mt={2} fontFamily="'Roboto Mono', monospace">Mapping Knowledge Graph...</Typography>
      </Box>
    );
  }

  if (!graphData) return <Typography fontFamily="'Roboto Mono', monospace">Error loading graph data.</Typography>;

  return (
    <Paper elevation={0} variant="outlined" sx={{ width: '100%', height: 600, overflow: 'hidden', position: 'relative', borderColor: 'divider', mt: 2, p: 2 }}>
      {/* Legend overlays */}
      <Box position="absolute" top={16} left={16} zIndex={10} bgcolor={isDark ? 'rgba(22,27,34,0.95)' : 'rgba(255,255,255,0.92)'} p={2} borderRadius={2} border="1px solid" borderColor="divider" boxShadow={isDark ? '0 2px 8px rgba(0,0,0,0.5)' : '0 2px 8px rgba(0,0,0,0.08)'}>
        <Typography variant="subtitle2" fontWeight="bold" mb={1} fontFamily="'Roboto Mono', monospace" color="text.primary">Knowledge Graph</Typography>
        <Typography variant="caption" display="flex" component="div" alignItems="center" gap={1} fontFamily="'Roboto Mono', monospace" mb={0.5}>
          <span style={{width: 8, height: 8, borderRadius: '50%', backgroundColor: '#1a73e8', display: 'inline-block'}}></span> User Profile
        </Typography>
        <Typography variant="caption" display="flex" component="div" alignItems="center" gap={1} fontFamily="'Roboto Mono', monospace" mb={0.5}>
          <span style={{width: 8, height: 8, borderRadius: '50%', backgroundColor: '#34a853', display: 'inline-block'}}></span> CV Skills
        </Typography>
        <Typography variant="caption" display="flex" component="div" alignItems="center" gap={1} fontFamily="'Roboto Mono', monospace" mb={0.5}>
          <span style={{width: 8, height: 8, borderRadius: '50%', backgroundColor: '#ea4335', display: 'inline-block'}}></span> Match Orgs
        </Typography>
        <Typography variant="caption" display="flex" component="div" alignItems="center" gap={1} fontFamily="'Roboto Mono', monospace">
          <span style={{width: 8, height: 8, borderRadius: '50%', backgroundColor: '#fbbc05', display: 'inline-block'}}></span> Org Technologies
        </Typography>
      </Box>
      <Box ref={containerRef} sx={{ width: '100%', height: '100%' }}>
        <ForceGraph2D
          ref={graphRef}
          width={dimensions.width}
          height={dimensions.height}
          graphData={graphData}
          nodeLabel="name"
          nodeCanvasObject={(node, ctx, globalScale) => {
            const isHighlighted = highlightNodes.has(node.id);
            const isFaded = hoverNode && !isHighlighted;
            
            let color = '#999';
            let size = 5;
            if (node.id === 'USER' || node.type === 'User') {
              color = '#1a73e8';
              size = 9;
            } else if (node.type === 'Skill') {
              color = '#34a853';
              size = 6;
            } else if (node.type === 'Organization') {
              color = '#ea4335';
              size = 7.5;
            } else if (node.type === 'Technology') {
              color = '#fbbc05';
              size = 4;
            }

            ctx.save();
            ctx.globalAlpha = isFaded ? 0.15 : 1.0;

            // Draw highlight outer ring
            if (node.id === hoverNode?.id) {
              ctx.beginPath();
              ctx.arc(node.x, node.y, size + 4, 0, 2 * Math.PI, false);
              ctx.fillStyle = 'rgba(26, 115, 232, 0.15)';
              ctx.fill();
              ctx.lineWidth = 1;
              ctx.strokeStyle = '#1a73e8';
              ctx.stroke();
            }

            // Draw node body
            ctx.beginPath();
            ctx.arc(node.x, node.y, size, 0, 2 * Math.PI, false);
            ctx.fillStyle = color;
            ctx.fill();
            ctx.lineWidth = 1.2;
            ctx.strokeStyle = '#ffffff';
            ctx.stroke();

            // Render clean labels (User, Orgs, and Skills are always visible; Techs show when zoomed/hovered)
            const showLabel = node.id === 'USER' || node.type === 'Organization' || node.type === 'Skill' || isHighlighted || globalScale > 1.8;
            if (showLabel) {
              const fontSize = node.id === 'USER' ? 4.2 : node.type === 'Organization' ? 3.6 : 3.0;
              ctx.font = `${node.id === 'USER' || node.type === 'Organization' ? 'bold' : 'normal'} ${fontSize}px "Roboto Mono", monospace`;
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';

              const text = node.name;
              const yOffset = size + 4.5;
              const textWidth = ctx.measureText(text).width;

              // Draw a rounded background pill for text contrast
              ctx.fillStyle = isDark ? 'rgba(22, 27, 34, 0.92)' : 'rgba(255, 255, 255, 0.9)';
              ctx.beginPath();
              const px = node.x - textWidth / 2 - 1.5;
              const py = node.y + yOffset - fontSize / 2 - 0.5;
              const pw = textWidth + 3;
              const ph = fontSize + 1;
              
              if (ctx.roundRect) {
                ctx.roundRect(px, py, pw, ph, 1);
              } else {
                ctx.rect(px, py, pw, ph);
              }
              ctx.fill();

              // Draw actual text label
              ctx.fillStyle = isHighlighted ? '#1a73e8' : (isDark ? '#e6edf3' : '#202124');
              ctx.fillText(text, node.x, node.y + yOffset);
            }
            ctx.restore();
          }}
          linkColor={link => {
            const isHighlighted = highlightLinks.has(link);
            if (isHighlighted) return '#1a73e8';
            if (hoverNode) return isDark ? 'rgba(255,255,255,0.02)' : 'rgba(0,0,0,0.02)';
            return isDark ? 'rgba(255,255,255,0.18)' : 'rgba(0,0,0,0.12)';
          }}
          linkWidth={link => (highlightLinks.has(link) ? 2.5 : 1)}
          linkDirectionalParticles={link => (highlightLinks.has(link) ? 4 : 0)}
          linkDirectionalParticleWidth={2}
          linkDirectionalParticleSpeed={0.006}
          onNodeHover={handleNodeHover}
          onNodeClick={node => {
            if (graphRef.current) {
              graphRef.current.centerAt(node.x, node.y, 800);
              graphRef.current.zoom(3.5, 1000);
            }
          }}
          cooldownTicks={80}
        />
      </Box>
    </Paper>
  );
};

export default GraphViz;
