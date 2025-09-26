import React, { useState } from 'react';
import { 
  AppBar, Toolbar, Typography, Button, IconButton, 
  Box, ToggleButtonGroup, ToggleButton, Tooltip,
  Menu, MenuItem, ListItemIcon, ListItemText, Divider
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import RefreshIcon from '@mui/icons-material/Refresh';
import EmailIcon from '@mui/icons-material/Email';
import BarChartIcon from '@mui/icons-material/BarChart';
import InfoIcon from '@mui/icons-material/Info';
import SettingsIcon from '@mui/icons-material/Settings';
import HelpIcon from '@mui/icons-material/Help';
import LogoutIcon from '@mui/icons-material/Logout';
import PersonIcon from '@mui/icons-material/Person';
import CodeIcon from '@mui/icons-material/Code';

/**
 * Application header with navigation and actions
 */
export const AppHeader = ({ 
  onMenuClick, 
  onRefresh, 
  viewMode = 'emails',
  onViewModeChange,
  onOpenSettings,
  onShowInfo
}) => {
  const [userMenuAnchor, setUserMenuAnchor] = useState(null);
  const [helpMenuAnchor, setHelpMenuAnchor] = useState(null);
  
  // Toggle view mode
  const handleViewModeChange = (event, newMode) => {
    if (newMode !== null) {
      onViewModeChange(newMode);
    }
  };
  
  // Open user menu
  const handleUserMenuOpen = (event) => {
    setUserMenuAnchor(event.currentTarget);
  };
  
  // Close user menu
  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };
  
  // Open help menu
  const handleHelpMenuOpen = (event) => {
    setHelpMenuAnchor(event.currentTarget);
  };
  
  // Close help menu
  const handleHelpMenuClose = () => {
    setHelpMenuAnchor(null);
  };
  
  return (
    <AppBar position="static">
      <Toolbar>
        <IconButton
          size="large"
          edge="start"
          color="inherit"
          aria-label="menu"
          sx={{ mr: 2 }}
          onClick={onMenuClick}
        >
          <MenuIcon />
        </IconButton>
        
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Outlook Mail Reader
        </Typography>
        
        {/* View Mode Toggle */}
        <ToggleButtonGroup
          value={viewMode}
          exclusive
          onChange={handleViewModeChange}
          aria-label="view mode"
          sx={{ 
            mr: 2,
            backgroundColor: 'rgba(255, 255, 255, 0.15)',
            '& .MuiToggleButton-root': {
              color: 'white',
              '&.Mui-selected': {
                backgroundColor: 'rgba(255, 255, 255, 0.3)',
                color: 'white'
              }
            }
          }}
        >
          <ToggleButton value="emails" aria-label="emails view">
            <EmailIcon sx={{ mr: 1 }} />
            Emails
          </ToggleButton>
          <ToggleButton value="stats" aria-label="statistics view">
            <BarChartIcon sx={{ mr: 1 }} />
            Stats
          </ToggleButton>
          <ToggleButton value="json" aria-label="json viewer">
            <CodeIcon sx={{ mr: 1 }} />
            JSON
          </ToggleButton>
        </ToggleButtonGroup>
        
        {/* Refresh Button */}
        <Tooltip title="Refresh data">
          <IconButton color="inherit" onClick={onRefresh}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
        
        {/* Help Button */}
        <Tooltip title="Help">
          <IconButton color="inherit" onClick={handleHelpMenuOpen}>
            <HelpIcon />
          </IconButton>
        </Tooltip>
        
        {/* User Menu */}
        <Tooltip title="Account">
          <IconButton 
            color="inherit" 
            onClick={handleUserMenuOpen}
            sx={{ ml: 1 }}
          >
            <PersonIcon />
          </IconButton>
        </Tooltip>
        
        {/* User Menu Dropdown */}
        <Menu
          anchorEl={userMenuAnchor}
          open={Boolean(userMenuAnchor)}
          onClose={handleUserMenuClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
        >
          <MenuItem onClick={handleUserMenuClose}>
            <ListItemIcon>
              <PersonIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText primary="My Account" />
          </MenuItem>
          
          <MenuItem onClick={() => {
            handleUserMenuClose();
            if (onOpenSettings) {
              onOpenSettings();
            }
          }}>
            <ListItemIcon>
              <SettingsIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText primary="Settings" />
          </MenuItem>
          
          <Divider />
          
          <MenuItem onClick={handleUserMenuClose}>
            <ListItemIcon>
              <LogoutIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText primary="Logout" />
          </MenuItem>
        </Menu>
        
        {/* Help Menu Dropdown */}
        <Menu
          anchorEl={helpMenuAnchor}
          open={Boolean(helpMenuAnchor)}
          onClose={handleHelpMenuClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
        >
          <MenuItem onClick={() => {
            handleHelpMenuClose();
            if (onShowInfo) {
              onShowInfo();
            }
          }}>
            <ListItemIcon>
              <InfoIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText primary="About" />
          </MenuItem>
          
          <MenuItem onClick={handleHelpMenuClose}>
            <ListItemIcon>
              <HelpIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText primary="Help" />
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};