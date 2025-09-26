import React from 'react';
import {
  Box, TextField, FormGroup, FormControlLabel, Switch, Button,
  Typography, Slider, Divider, InputAdornment, Tooltip,
  Grid, Paper
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import MailIcon from '@mui/icons-material/Mail';
import ResetIcon from '@mui/icons-material/RestartAlt';

/**
 * Component for email filtering options
 */
export const FilterPanel = ({ filters, onChange, onApply, onReset }) => {
  // Default filters to use when resetting
  const defaultFilters = {
    sender: "FASTRAPP@paypal.com",
    keyword: "failed",
    maxItems: 25,
    useRappFast: true,
    caseSensitive: false,
    subjectOnly: false,
    bodyOnly: false
  };
  
  // Handle input changes
  const handleChange = (field, value) => {
    onChange({ [field]: value });
  };
  
  // Handle reset filters
  const handleReset = () => {
    onChange(defaultFilters);
    if (onReset) {
      onReset();
    }
  };
  
  return (
    <Box component={Paper} sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
        <FilterListIcon sx={{ mr: 1 }} />
        Email Filters
      </Typography>
      
      <Divider sx={{ my: 2 }} />
      
      <Grid container spacing={2}>
        {/* Sender Filter */}
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Sender Email"
            value={filters.sender}
            onChange={(e) => handleChange('sender', e.target.value)}
            variant="outlined"
            margin="normal"
            placeholder="e.g., FASTRAPP@paypal.com"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <MailIcon />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
        
        {/* Keyword Filter */}
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Search Keyword"
            value={filters.keyword}
            onChange={(e) => handleChange('keyword', e.target.value)}
            variant="outlined"
            margin="normal"
            placeholder="e.g., failed"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
        
        {/* Max Items Slider */}
        <Grid item xs={12}>
          <Typography id="max-items-slider" gutterBottom>
            Maximum Emails: {filters.maxItems}
          </Typography>
          <Slider
            value={filters.maxItems}
            onChange={(e, newValue) => handleChange('maxItems', newValue)}
            aria-labelledby="max-items-slider"
            valueLabelDisplay="auto"
            step={5}
            marks
            min={5}
            max={100}
          />
        </Grid>
        
        {/* Switches */}
        <Grid item xs={12}>
          <FormGroup>
            <Tooltip title="Search in RAPP, FAST folder instead of inbox">
              <FormControlLabel
                control={
                  <Switch 
                    checked={filters.useRappFast}
                    onChange={(e) => handleChange('useRappFast', e.target.checked)}
                    color="primary"
                  />
                }
                label="Use RAPP, FAST folder"
              />
            </Tooltip>
            
            <Tooltip title="Match exact case when searching">
              <FormControlLabel
                control={
                  <Switch 
                    checked={filters.caseSensitive}
                    onChange={(e) => handleChange('caseSensitive', e.target.checked)}
                    color="primary"
                  />
                }
                label="Case-sensitive search"
              />
            </Tooltip>
            
            <Tooltip title="Search only in subject line">
              <FormControlLabel
                control={
                  <Switch 
                    checked={filters.subjectOnly}
                    onChange={(e) => {
                      // Can't have both subject-only and body-only true
                      if (e.target.checked) {
                        onChange({ 
                          subjectOnly: true,
                          bodyOnly: false
                        });
                      } else {
                        handleChange('subjectOnly', false);
                      }
                    }}
                    color="primary"
                  />
                }
                label="Search subject only"
              />
            </Tooltip>
            
            <Tooltip title="Search only in email body">
              <FormControlLabel
                control={
                  <Switch 
                    checked={filters.bodyOnly}
                    onChange={(e) => {
                      // Can't have both subject-only and body-only true
                      if (e.target.checked) {
                        onChange({ 
                          bodyOnly: true,
                          subjectOnly: false
                        });
                      } else {
                        handleChange('bodyOnly', false);
                      }
                    }}
                    color="primary"
                  />
                }
                label="Search body only"
              />
            </Tooltip>
          </FormGroup>
        </Grid>
      </Grid>
      
      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
        <Button 
          startIcon={<ResetIcon />}
          onClick={handleReset}
          color="secondary"
          variant="outlined"
        >
          Reset
        </Button>
        
        <Button 
          variant="contained"
          color="primary"
          onClick={onApply}
        >
          Apply Filters
        </Button>
      </Box>
    </Box>
  );
};