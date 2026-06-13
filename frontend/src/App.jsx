import { useState, useMemo } from "react";
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  IconButton,
  Tooltip,
} from "@mui/material";
import SchoolIcon from "@mui/icons-material/School";
import DarkModeIcon from "@mui/icons-material/DarkMode";
import LightModeIcon from "@mui/icons-material/LightMode";
import CVInput from "./components/CVInput";
import MatchResults from "./components/MatchResults";

const getTheme = (mode) =>
  createTheme({
    palette: {
      mode,
      primary: {
        main: "#1a73e8",
        dark: "#1557b0",
      },
      secondary: {
        main: "#ea4335",
        dark: "#c5221f",
      },
      ...(mode === "light"
        ? {
            background: {
              default: "#f0f4f8",
              paper: "#ffffff",
            },
          }
        : {
            background: {
              default: "#0d1117",
              paper: "#161b22",
            },
          }),
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
            boxShadow:
              mode === "dark"
                ? "0 8px 24px rgba(0,0,0,0.4), 0 2px 8px rgba(0,0,0,0.3)"
                : "0 8px 24px rgba(0,0,0,0.06), 0 2px 8px rgba(0,0,0,0.04)",
            transition: "transform 0.2s ease, box-shadow 0.2s ease",
            border:
              mode === "dark"
                ? "1px solid rgba(255,255,255,0.06)"
                : "1px solid rgba(0,0,0,0.04)",
            "&:hover": {
              transform: "translateY(-4px)",
              boxShadow:
                mode === "dark"
                  ? "0 12px 32px rgba(0,0,0,0.5), 0 4px 12px rgba(0,0,0,0.35)"
                  : "0 12px 32px rgba(0,0,0,0.1), 0 4px 12px rgba(0,0,0,0.06)",
            },
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            borderRadius: 16,
            backgroundImage: "none",
          },
        },
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            borderRadius: 0,
            boxShadow:
              mode === "dark"
                ? "0 4px 20px rgba(0,0,0,0.4)"
                : "0 4px 20px rgba(0,0,0,0.08)",
            ...(mode === "dark" && {
              background: "linear-gradient(135deg, #161b22 0%, #0d1117 100%)",
              borderBottom: "1px solid rgba(255,255,255,0.06)",
            }),
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: {
            ...(mode === "dark" && {
              borderColor: "rgba(255,255,255,0.12)",
            }),
          },
        },
      },
    },
  });

function App() {
  const [results, setResults] = useState(null);
  const [mode, setMode] = useState(
    () => localStorage.getItem("colorMode") || "light"
  );

  const theme = useMemo(() => getTheme(mode), [mode]);

  const toggleMode = () => {
    const next = mode === "light" ? "dark" : "light";
    setMode(next);
    localStorage.setItem("colorMode", next);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />

      <AppBar position="static" color={mode === "dark" ? "default" : "primary"} elevation={mode === "dark" ? 0 : 1}>
        <Toolbar>
          <SchoolIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            GSoC Pathfinder
          </Typography>
          <Tooltip title={mode === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}>
            <IconButton
              onClick={toggleMode}
              color="inherit"
              size="medium"
              sx={{
                transition: "transform 0.3s ease, background 0.2s ease",
                "&:hover": {
                  transform: "rotate(20deg) scale(1.1)",
                  background: "rgba(255,255,255,0.12)",
                },
              }}
              aria-label="toggle dark mode"
            >
              {mode === "dark" ? (
                <LightModeIcon sx={{ fontSize: 22 }} />
              ) : (
                <DarkModeIcon sx={{ fontSize: 22 }} />
              )}
            </IconButton>
          </Tooltip>
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
