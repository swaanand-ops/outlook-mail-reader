import React from 'react';
import { Box, Typography, Button, Paper } from '@mui/material';
import SearchOffIcon from '@mui/icons-material/SearchOff';

/**
 * Component for displaying empty state
 */
export const EmptyState = ({ 
  message = 'No data found', 
  description,
  onAction,
  actionText = 'Refresh',
  icon: Icon = SearchOffIcon,
  fullScreen = false
}) => {
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
      <Icon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
      
      <Typography variant="h5" color="text.primary" gutterBottom>
        {message}
      </Typography>
      
      {description && (
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          {description}
        </Typography>
      )}
      
      {onAction && (
        <Button 
          variant="contained" 
          color="primary" 
          onClick={onAction}
        >
          {actionText}
        </Button>
      )}
    </Box>
  );
};