import { useState, useEffect, useRef } from "react";
import {
  Paper,
  TextField,
  Button,
  Typography,
  CircularProgress,
  Box,
  FormControlLabel,
  Switch,
} from "@mui/material";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import API_BASE from "../config";

const CVInput = ({ onResults }) => {
  const [cvText, setCvText] = useState("");
  const [advanced, setAdvanced] = useState(false);
  const [ultra, setUltra] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [statusMessages, setStatusMessages] = useState([]);
  const [currentStatus, setCurrentStatus] = useState("");

  const logContainerRef = useRef(null);

  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [statusMessages, currentStatus]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!cvText.trim() || loading) return;

    setLoading(true);
    setError("");
    setStatusMessages([]);
    setCurrentStatus("Initializing matching pipeline...");

    try {
      const response = await fetch(`${API_BASE}/api/match/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ cv_text: cvText, advanced: advanced, ultra: ultra }),
      });

      if (!response.ok) {
        throw new Error("Failed to match CV. Please try again.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || ""; // Save trailing fractional line in buffer

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith("data: ")) {
            try {
              const event = JSON.parse(trimmed.substring(6));
              
              if (event.type === "info") {
                setCurrentStatus(event.data);
                setStatusMessages((prev) => [...prev, event.data]);
              } else if (event.type === "complete") {
                onResults(event.data);
                setLoading(false);
              } else if (event.type === "error") {
                throw new Error(event.data);
              }
            } catch (err) {
              console.error("SSE JSON parse error:", err, "Line:", trimmed);
            }
          }
        }
      }
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Paper
        elevation={3}
        sx={{ p: 4, width: "100%", maxWidth: "800px", borderRadius: 3, textAlign: "center" }}
      >
        <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", py: 4 }}>
          <CircularProgress
            size={60}
            thickness={4}
            sx={{ mb: 3 }}
            color={ultra ? "secondary" : "primary"}
          />
          <Typography
            variant="h6"
            gutterBottom
            sx={{ fontWeight: "bold", fontFamily: "'Roboto Mono', monospace" }}
          >
            {ultra ? "Ultra Matching Engaged" : "Matching Your CV"}
          </Typography>
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ mb: 4, fontStyle: "italic", height: "24px", fontFamily: "'Roboto Mono', monospace" }}
          >
            {currentStatus}
          </Typography>

          <Box sx={{ width: "100%", mt: 2 }}>
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{
                display: "block",
                mb: 1,
                textAlign: "left",
                fontWeight: "bold",
                textTransform: "uppercase",
                letterSpacing: "0.1em",
                fontFamily: "'Roboto Mono', monospace",
              }}
            >
              Execution Activity Log
            </Typography>
            <Box
              ref={logContainerRef}
              sx={{
                bgcolor: "#1e1e1e",
                color: "#d4d4d4",
                p: 2.5,
                borderRadius: 2.5,
                fontFamily: '"Roboto Mono", monospace',
                fontSize: "0.8rem",
                height: "240px",
                overflowY: "auto",
                textAlign: "left",
                border: "1px solid rgba(255,255,255,0.08)",
                boxShadow: "inset 0 2px 8px rgba(0,0,0,0.8)",
                "&::-webkit-scrollbar": {
                  width: "6px",
                },
                "&::-webkit-scrollbar-track": {
                  background: "#1e1e1e",
                },
                "&::-webkit-scrollbar-thumb": {
                  background: "#3e3e3e",
                  borderRadius: "3px",
                },
              }}
            >
              {statusMessages.map((msg, idx) => (
                <div key={idx} style={{ marginBottom: "6px", lineHeight: "1.4" }}>
                  <span style={{ color: "#569cd6" }}>&gt;</span> {msg}
                </div>
              ))}
              <div style={{ color: "#6a9955", fontStyle: "italic" }}>
                &gt; {currentStatus}...
              </div>
            </Box>
          </Box>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper
      elevation={2}
      sx={{ p: 4, width: "100%", maxWidth: "800px", borderRadius: 3 }}
    >
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
          sx={{ mb: 2 }}
        />

        <Box
          sx={{
            mb: 3,
            p: 2.5,
            borderRadius: 2,
            background:
              "linear-gradient(135deg, rgba(26, 115, 232, 0.04) 0%, rgba(234, 67, 53, 0.04) 100%)",
            border: "1px solid rgba(26, 115, 232, 0.1)",
            display: "flex",
            flexDirection: "column",
            gap: 1.5,
            alignItems: "flex-start",
            textAlign: "left",
          }}
        >
          <Typography
            variant="subtitle2"
            sx={{
              fontWeight: "bold",
              mb: 0.5,
              color: "primary.main",
              fontFamily: "'Roboto Mono', monospace",
            }}
          >
            Reasoning Level Options:
          </Typography>

          <FormControlLabel
            control={
              <Switch
                checked={advanced}
                onChange={(e) => {
                  setAdvanced(e.target.checked);
                  if (!e.target.checked) {
                    setUltra(false);
                  }
                }}
                color="primary"
                disabled={loading}
              />
            }
            label={
              <Box>
                <Typography
                  variant="body2"
                  sx={{
                    fontFamily: "'Roboto Mono', monospace",
                    fontWeight: 500,
                  }}
                >
                  Deep Reasoning Mode
                </Typography>
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ display: "block" }}
                >
                  Queries Neo4j for actual projects and matches your skills.
                </Typography>
              </Box>
            }
          />

          <FormControlLabel
            control={
              <Switch
                checked={ultra}
                onChange={(e) => {
                  setUltra(e.target.checked);
                  if (e.target.checked) {
                    setAdvanced(true);
                  }
                }}
                color="secondary"
                disabled={loading}
              />
            }
            label={
              <Box>
                <Typography
                  variant="body2"
                  sx={{
                    fontFamily: "'Roboto Mono', monospace",
                    fontWeight: 500,
                  }}
                >
                  Ultra reasoning & Critique Mode
                </Typography>
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ display: "block" }}
                >
                  Runs multi-loop adversarial critiques, CV self-correction, and
                  proposal strategies. (Requires strong local LLM)
                </Typography>
              </Box>
            }
          />
        </Box>

        {error && (
          <Typography color="error" variant="body2" sx={{ mb: 2 }}>
            {error}
          </Typography>
        )}

        <Box sx={{ display: "flex", justifyContent: "center", mt: 3 }}>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            size="large"
            disabled={!cvText.trim() || loading}
            startIcon={
              loading ? (
                <CircularProgress size={20} color="inherit" />
              ) : (
                <AutoAwesomeIcon />
              )
            }
            sx={{ px: 6, py: 1.5, fontSize: "1.1rem" }}
          >
            {loading ? "Analyzing Matches..." : "Find Matches"}
          </Button>
        </Box>
      </form>
    </Paper>
  );
};

export default CVInput;
