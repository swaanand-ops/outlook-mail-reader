import React from 'react';
import { Box, CircularProgress, Typography, Paper } from '@mui/material';

/**
 * Component for displaying loading state
 */
export const LoadingOverlay = ({ message = 'Loading...', fullScreen = false }) => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        p: 4,
        m: 2,
        height: fullScreen ? '80vh' : 'auto',
        textAlign: 'center'
      }}
      component={Paper}
      elevation={fullScreen ? 0 : 1}
    >
      <CircularProgress size={60} thickness={4} sx={{ mb: 2 }} />
      <Typography variant="h6" color="text.secondary">
        {message}
      </Typography>
    </Box>
  );
};