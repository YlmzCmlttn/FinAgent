import React from 'react';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import { ChatInterface } from './components/ChatInterface';

const theme = createTheme({
    palette: {
        mode: 'light',
        primary: {
            main: '#1976d2',
        },
        secondary: {
            main: '#dc004e',
        },
    },
});

function App() {
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <ChatInterface />
        </ThemeProvider>
    );
}

export default App; 