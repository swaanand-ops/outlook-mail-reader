import React from 'react';
import {
  Box, Typography, Grid, Paper, Divider, List, ListItem,
  ListItemText, ListItemIcon, Chip, Card, CardHeader, CardContent,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow
} from '@mui/material';
import EmailIcon from '@mui/icons-material/Email';
import PersonIcon from '@mui/icons-material/Person';
import DateRangeIcon from '@mui/icons-material/DateRange';
import SearchIcon from '@mui/icons-material/Search';
import BarChartIcon from '@mui/icons-material/BarChart';

/**
 * Component for displaying email statistics
 */
export const StatsView = ({ stats }) => {
  if (!stats) {
    return (
      <Box sx={{ textAlign: 'center', my: 4 }}>
        <Typography variant="h6" color="text.secondary">
          No statistics available
        </Typography>
      </Box>
    );
  }
  
  // Format sender stats
  const formatSenders = () => {
    if (!stats.senders) return [];
    
    return Object.entries(stats.senders)
      .map(([sender, count]) => ({ sender, count }))
      .sort((a, b) => b.count - a.count);
  };
  
  // Format date stats
  const formatDates = () => {
    if (!stats.dates) return [];
    
    return Object.entries(stats.dates)
      .map(([date, count]) => ({ date, count }))
      .sort((a, b) => new Date(b.date) - new Date(a.date));
  };
  
  // Format keyword stats
  const formatKeywords = () => {
    if (!stats.keywords) return [];
    
    return Object.entries(stats.keywords)
      .map(([keyword, count]) => ({ keyword, count }))
      .sort((a, b) => b.count - a.count);
  };
  
  // Prepare data
  const senderStats = formatSenders();
  const dateStats = formatDates();
  const keywordStats = formatKeywords();
  
  return (
    <Box>
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Email Statistics
      </Typography>
      
      {/* Overview */}
      <Card sx={{ mb: 4 }}>
        <CardHeader title="Overview" />
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={4}>
              <Paper sx={{ p: 2, textAlign: 'center', height: '100%' }}>
                <Typography variant="h6" color="primary">
                  Total Emails
                </Typography>
                <Typography variant="h3">
                  {stats.total_emails || 0}
                </Typography>
                <Box sx={{ mt: 1 }}>
                  <EmailIcon color="primary" />
                </Box>
              </Paper>
            </Grid>
            
            <Grid item xs={12} sm={4}>
              <Paper sx={{ p: 2, textAlign: 'center', height: '100%' }}>
                <Typography variant="h6" color="primary">
                  Unique Senders
                </Typography>
                <Typography variant="h3">
                  {senderStats.length || 0}
                </Typography>
                <Box sx={{ mt: 1 }}>
                  <PersonIcon color="primary" />
                </Box>
              </Paper>
            </Grid>
            
            <Grid item xs={12} sm={4}>
              <Paper sx={{ p: 2, textAlign: 'center', height: '100%' }}>
                <Typography variant="h6" color="primary">
                  Date Range
                </Typography>
                <Typography variant="h5">
                  {dateStats.length ? dateStats[dateStats.length - 1].date : 'N/A'}
                </Typography>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  to
                </Typography>
                <Typography variant="h5">
                  {dateStats.length ? dateStats[0].date : 'N/A'}
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
      
      <Grid container spacing={3}>
        {/* Sender Statistics */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader 
              title="Sender Statistics" 
              avatar={<PersonIcon />}
              action={
                <Chip 
                  label={`${senderStats.length} senders`} 
                  color="primary" 
                  size="small" 
                />
              }
            />
            <Divider />
            <CardContent>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Sender</TableCell>
                      <TableCell align="right">Count</TableCell>
                      <TableCell align="right">Percentage</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {senderStats.slice(0, 5).map((item) => (
                      <TableRow key={item.sender}>
                        <TableCell component="th" scope="row">
                          {item.sender}
                        </TableCell>
                        <TableCell align="right">{item.count}</TableCell>
                        <TableCell align="right">
                          {((item.count / stats.total_emails) * 100).toFixed(1)}%
                        </TableCell>
                      </TableRow>
                    ))}
                    {senderStats.length > 5 && (
                      <TableRow>
                        <TableCell colSpan={3} align="center">
                          <Typography variant="caption" color="text.secondary">
                            And {senderStats.length - 5} more senders
                          </Typography>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Date Statistics */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader 
              title="Date Statistics" 
              avatar={<DateRangeIcon />}
              action={
                <Chip 
                  label={`${dateStats.length} days`} 
                  color="primary" 
                  size="small" 
                />
              }
            />
            <Divider />
            <CardContent>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Date</TableCell>
                      <TableCell align="right">Count</TableCell>
                      <TableCell align="right">Percentage</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {dateStats.slice(0, 5).map((item) => (
                      <TableRow key={item.date}>
                        <TableCell component="th" scope="row">
                          {item.date}
                        </TableCell>
                        <TableCell align="right">{item.count}</TableCell>
                        <TableCell align="right">
                          {((item.count / stats.total_emails) * 100).toFixed(1)}%
                        </TableCell>
                      </TableRow>
                    ))}
                    {dateStats.length > 5 && (
                      <TableRow>
                        <TableCell colSpan={3} align="center">
                          <Typography variant="caption" color="text.secondary">
                            And {dateStats.length - 5} more days
                          </Typography>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Keyword Statistics */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title="Keyword Statistics" 
              avatar={<SearchIcon />}
              action={
                <Chip 
                  label={`${keywordStats.length} keywords`} 
                  color="primary" 
                  size="small" 
                />
              }
            />
            <Divider />
            <CardContent>
              <Grid container spacing={2}>
                {keywordStats.map((item) => (
                  <Grid item key={item.keyword}>
                    <Chip
                      label={`${item.keyword}: ${item.count}`}
                      color={item.count > 0 ? "primary" : "default"}
                      variant={item.count > 5 ? "filled" : "outlined"}
                      sx={{ 
                        fontSize: `${Math.min(14 + (item.count / stats.total_emails) * 50, 20)}px`,
                        fontWeight: item.count > stats.total_emails * 0.2 ? 'bold' : 'normal'
                      }}
                    />
                  </Grid>
                ))}
              </Grid>
              
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2">
                  Common Email Themes
                </Typography>
                <List dense>
                  {keywordStats
                    .filter(item => item.count > 0)
                    .slice(0, 3)
                    .map((item) => (
                      <ListItem key={item.keyword}>
                        <ListItemIcon>
                          <SearchIcon color="primary" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText 
                          primary={`${item.keyword} (${item.count} emails)`}
                          secondary={`${((item.count / stats.total_emails) * 100).toFixed(1)}% of total emails`}
                        />
                      </ListItem>
                    ))
                  }
                </List>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};