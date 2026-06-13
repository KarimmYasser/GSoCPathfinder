import { useState } from "react";
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
} from "@mui/material";
import SchoolIcon from "@mui/icons-material/School";
import CVInput from "./components/CVInput";
import MatchResults from "./components/MatchResults";

const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1a73e8", // Google Blue
      dark: "#1557b0",
    },
    secondary: {
      main: "#ea4335", // Google Red
      dark: "#c5221f",
    },
    background: {
      default: "#f0f4f8",
      paper: "#ffffff",
    },
  },
  typography: {
    fontFamily: '"Roboto Mono", monospace',
    h1: { fontWeight: 700, letterSpacing: "-0.02em" },
    h2: { fontWeight: 700, letterSpacing: "-0.01em" },
    h3: { fontWeight: 700 },
    h4: { fontWeight: 700 },
    h5: { fontWeight: 700 },
    h6: { fontWeight: 700 },
    button: { fontWeight: 600, letterSpacing: "0.02em" },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: "none",
          borderRadius: 8,
          padding: "8px 22px",
          boxShadow: "0 2px 6px rgba(26, 115, 232, 0.2)",
          transition: "all 0.2s ease-in-out",
          "&:hover": {
            transform: "translateY(-1px)",
            boxShadow: "0 4px 12px rgba(26, 115, 232, 0.3)",
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: "0 8px 24px rgba(0,0,0,0.06), 0 2px 8px rgba(0,0,0,0.04)",
          transition: "transform 0.2s ease, box-shadow 0.2s ease",
          border: "1px solid rgba(0,0,0,0.04)",
          "&:hover": {
            transform: "translateY(-4px)",
            boxShadow:
              "0 12px 32px rgba(0,0,0,0.1), 0 4px 12px rgba(0,0,0,0.06)",
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 16,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          borderRadius: 0,
          boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
        },
      },
    },
  },
});

function App() {
  const [results, setResults] = useState(null);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />

      <AppBar position="static" color="primary" elevation={1}>
        <Toolbar>
          <SchoolIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            GSoC Pathfinder
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 4 }}>
        {!results ? (
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 2,
            }}
          >
            <Typography
              variant="h4"
              component="h1"
              gutterBottom
              sx={{ textAlign: "center", fontWeight: "bold" }}
            >
              Find Your Ideal GSoC Organization
            </Typography>
            <Typography
              variant="subtitle1"
              color="text.secondary"
              sx={{
                textAlign: "center",
                mb: 2,
                maxWidth: "600px",
              }}
            >
              Paste your CV or resume below. Our AI matching engine will analyze
              your skills and find the best open-source organizations for you.
            </Typography>
            <CVInput onResults={setResults} />
          </Box>
        ) : (
          <MatchResults results={results} onReset={() => setResults(null)} />
        )}
      </Container>
    </ThemeProvider>
  );
}

export default App;
