import React, { useState, useEffect } from 'react';
import { 
  AppBar, Toolbar, Typography, Container, Box, Grid, Card, CardContent, 
  CardHeader, CardActions, Button, TextField, Divider, Alert, AlertTitle,
  CircularProgress, IconButton, Switch, FormControlLabel, Tooltip, Chip,
  Stack, Drawer, List, ListItem, ListItemIcon, ListItemText, Badge, Dialog,
  DialogTitle, DialogContent, DialogContentText, DialogActions, Snackbar
} from '@mui/material';

// Import Material UI icons
import MailIcon from '@mui/icons-material/Mail';
import RefreshIcon from '@mui/icons-material/Refresh';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import FilterListIcon from '@mui/icons-material/FilterList';
import SettingsIcon from '@mui/icons-material/Settings';
import ErrorIcon from '@mui/icons-material/Error';
import InfoIcon from '@mui/icons-material/Info';
import CloseIcon from '@mui/icons-material/Close';
import SearchIcon from '@mui/icons-material/Search';
import DashboardIcon from '@mui/icons-material/Dashboard';
import BarChartIcon from '@mui/icons-material/BarChart';
import CategoryIcon from '@mui/icons-material/Category';
import CloudDownloadIcon from '@mui/icons-material/CloudDownload';
import CodeIcon from '@mui/icons-material/Code';

// Import utilities
import { formatDistanceToNow } from 'date-fns';
import axios from 'axios';

// Import custom components
import { EmailCard } from './components/EmailCard';
import { FilterPanel } from './components/FilterPanel';
import { StatsView } from './components/StatsView';
import { AppHeader } from './components/AppHeader';
import { LoadingOverlay } from './components/LoadingOverlay';
import { EmptyState } from './components/EmptyState';
import { ErrorDisplay } from './components/ErrorDisplay';
import { JsonViewer } from './components/JsonViewer';

function App() {
  // State for email data
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [metadata, setMetadata] = useState({});
  
  // State for filters
  const [filters, setFilters] = useState({
    sender: "FASTRAPP@paypal.com",
    keyword: "failed",
    maxItems: 25,
    useRappFast: true,
    caseSensitive: false,
    subjectOnly: false,
    bodyOnly: false
  });
  
  // State for UI
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [viewMode, setViewMode] = useState('emails'); // 'emails', 'stats', or 'json'
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'info'
  });
  
  // State for stats
  const [stats, setStats] = useState(null);
  
  // Fetch emails based on filters
  const fetchEmails = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Build query params
      const params = new URLSearchParams();
      params.append('use_rapp_fast', filters.useRappFast);
      params.append('sender', filters.sender);
      params.append('keyword', filters.keyword);
      params.append('max_items', filters.maxItems);
      params.append('case_sensitive', filters.caseSensitive);
      
      if (filters.subjectOnly) {
        params.append('subject_only', true);
      }
      
      if (filters.bodyOnly) {
        params.append('body_only', true);
      }
      
      // Make API request
      const response = await axios.get(`/api/emails?${params}`);
      
      // Update state with response data
      setEmails(response.data.messages || []);
      setMetadata({
        folderName: response.data.folder_name,
        senderId: response.data.folder_id,
        senderFilter: response.data.sender_filter,
        keyword: response.data.keyword,
        totalMessages: response.data.total_messages,
        timestamp: response.data.timestamp
      });
      
      // Show success snackbar
      setSnackbar({
        open: true,
        message: `Found ${response.data.messages?.length || 0} matching emails`,
        severity: 'success'
      });
      
    } catch (err) {
      console.error('Error fetching emails:', err);
      setError(err.response?.data?.error || err.message || 'Failed to fetch emails');
      
      // Show error snackbar
      setSnackbar({
        open: true,
        message: 'Failed to fetch emails',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  // Fetch stats
  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get('/api/stats');
      setStats(response.data);
    } catch (err) {
      console.error('Error fetching stats:', err);
      setError(err.response?.data?.error || err.message || 'Failed to fetch statistics');
      
      // Show error snackbar
      setSnackbar({
        open: true,
        message: 'Failed to fetch statistics',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  // Check API health
  const checkApiHealth = async () => {
    try {
      const response = await axios.get('/api/health');
      if (response.data.status !== 'ok') {
        setError('API server is not healthy');
      }
    } catch (err) {
      console.error('API health check failed:', err);
      setError('API server is not available');
    }
  };
  
  // Handle filter changes
  const handleFilterChange = (newFilters) => {
    setFilters({ ...filters, ...newFilters });
  };
  
  // Handle filter apply
  const handleApplyFilters = () => {
    fetchEmails();
    setDrawerOpen(false);
  };
  
  // Format date relative to now
  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown date';
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true });
    } catch (err) {
      return dateString;
    }
  };
  
  // Highlight keyword in text
  const highlightKeyword = (text, keyword) => {
    if (!keyword || !text) return text;
    
    const parts = text.split(new RegExp(`(${keyword})`, 'gi'));
    return parts.map((part, i) => 
      part.toLowerCase() === keyword.toLowerCase() 
        ? <mark key={i}>{part}</mark> 
        : part
    );
  };
  
  // Toggle drawer
  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };
  
  // Switch view mode
  const switchViewMode = (mode) => {
    setViewMode(mode);
    if (mode === 'stats' && !stats) {
      fetchStats();
    } else if (mode === 'emails' && !emails.length) {
      fetchEmails();
    }
    // No need to load anything for json viewer mode as it handles its own data loading
  };
  
  // Close snackbar
  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };
  
  // Load saved filters from localStorage
  useEffect(() => {
    const savedFilters = localStorage.getItem('emailFilters');
    if (savedFilters) {
      try {
        setFilters(JSON.parse(savedFilters));
      } catch (err) {
        console.error('Error loading saved filters:', err);
      }
    }
    
    // Initial API health check
    checkApiHealth();
  }, []);
  
  // Fetch emails when component mounts
  useEffect(() => {
    fetchEmails();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps
  
  // Save filters to localStorage when they change
  useEffect(() => {
    localStorage.setItem('emailFilters', JSON.stringify(filters));
  }, [filters]);
  
  // Render main content based on view mode
  const renderContent = () => {
    if (viewMode === 'json') {
      // Return the JSON Viewer component directly as it handles its own loading state
      return <JsonViewer initialFilePath="data.json" />;
    }
    
    if (loading) {
      return <LoadingOverlay message="Loading data..." />;
    }
    
    if (error) {
      return <ErrorDisplay error={error} onRetry={() => viewMode === 'emails' ? fetchEmails() : fetchStats()} />;
    }
    
    if (viewMode === 'emails') {
      if (!emails || emails.length === 0) {
        return <EmptyState message="No emails found matching your criteria" onAction={fetchEmails} actionText="Refresh" />;
      }
      
      return (
        <Grid container spacing={2}>
          {emails.map(email => (
            <Grid item xs={12} sm={6} md={4} key={email.id}>
              <EmailCard 
                email={email} 
                keyword={filters.keyword} 
                folderId={metadata.senderId} 
                highlightKeyword={highlightKeyword}
                formatDate={formatDate}
              />
            </Grid>
          ))}
        </Grid>
      );
    } else if (viewMode === 'stats') {
      if (!stats) {
        return <EmptyState message="No statistics available" onAction={fetchStats} actionText="Load Stats" />;
      }
      
      return <StatsView stats={stats} />;
    }
  };
  
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* App Header */}
      <AppHeader 
        onMenuClick={toggleDrawer}
        onRefresh={() => viewMode === 'emails' ? fetchEmails() : fetchStats()}
        viewMode={viewMode}
        onViewModeChange={switchViewMode}
      />
      
      {/* Drawer for filters */}
      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <Box sx={{ width: 300, p: 2 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Email Filters
          </Typography>
          
          <Divider sx={{ mb: 2 }} />
          
          <FilterPanel 
            filters={filters} 
            onChange={handleFilterChange} 
            onApply={handleApplyFilters} 
          />
        </Box>
      </Drawer>
      
      {/* Main content */}
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4, flexGrow: 1 }}>
        {/* Filter summary */}
        {viewMode === 'emails' && metadata.senderFilter && (
          <Box sx={{ mb: 3 }}>
            <Alert severity="info">
              <Stack direction="row" spacing={1} alignItems="center">
                <Typography variant="body2">
                  Folder: <strong>{metadata.folderName || 'Unknown'}</strong>
                </Typography>
                <Divider orientation="vertical" flexItem />
                <Typography variant="body2">
                  Sender: <strong>{metadata.senderFilter}</strong>
                </Typography>
                <Divider orientation="vertical" flexItem />
                <Typography variant="body2">
                  Keyword: <strong>{metadata.keyword}</strong>
                </Typography>
                <Divider orientation="vertical" flexItem />
                <Typography variant="body2">
                  Found: <strong>{metadata.totalMessages || 0} emails</strong>
                </Typography>
              </Stack>
            </Alert>
          </Box>
        )}
        
        {/* Main content area */}
        {renderContent()}
      </Container>
      
      {/* Footer */}
      <Box component="footer" sx={{ p: 2, mt: 'auto', backgroundColor: '#f5f5f5' }}>
        <Typography variant="body2" color="text.secondary" align="center">
          Outlook Mail Reader - {new Date().getFullYear()}
        </Typography>
      </Box>
      
      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        message={snackbar.message}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        severity={snackbar.severity}
      />
    </Box>
  );
}

export default App;