import React from 'react';
import { Box, Typography, Button, Paper, Alert, AlertTitle } from '@mui/material';
import ErrorIcon from '@mui/icons-material/Error';
import RefreshIcon from '@mui/icons-material/Refresh';

/**
 * Component for displaying error states
 */
export const ErrorDisplay = ({ 
  error, 
  onRetry, 
  title = 'Error', 
  fullScreen = false 
}) => {
  // Parse error message
  let errorMessage = 'An unknown error occurred';
  
  if (typeof error === 'string') {
    errorMessage = error;
  } else if (error && typeof error === 'object') {
    if (error.message) {
      errorMessage = error.message;
    } else if (error.error) {
      errorMessage = error.error;
    }
  }
  
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
      <Alert 
        severity="error" 
        variant="outlined" 
        icon={<ErrorIcon fontSize="large" />}
        sx={{ 
          width: '100%', 
          mb: 3,
          '& .MuiAlert-icon': {
            alignItems: 'center'
          }
        }}
      >
        <AlertTitle>{title}</AlertTitle>
        {errorMessage}
      </Alert>
      
      {onRetry && (
        <Button 
          variant="contained" 
          color="primary" 
          startIcon={<RefreshIcon />}
          onClick={onRetry}
        >
          Retry
        </Button>
      )}
    </Box>
  );
};