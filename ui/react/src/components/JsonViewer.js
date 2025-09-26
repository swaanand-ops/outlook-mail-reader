import React, { useState, useEffect, useRef } from 'react';
import {
  Box, Paper, Typography, TextField, Button, CircularProgress,
  Select, MenuItem, FormControl, InputLabel, Alert, Grid,
  Divider, IconButton, Tooltip
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import RefreshIcon from '@mui/icons-material/Refresh';
import ClearIcon from '@mui/icons-material/Clear';
import CodeIcon from '@mui/icons-material/Code';
import axios from 'axios';

/**
 * JSON Viewer component to display JSON data in a collapsible tree
 */
const JsonViewer = ({ initialFilePath = 'data.json' }) => {
  const [filePath, setFilePath] = useState(initialFilePath);
  const [jsonData, setJsonData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchType, setSearchType] = useState('both');
  const jsonDisplayRef = useRef(null);

  // Load JSON data when component mounts or filePath changes
  useEffect(() => {
    loadJsonData();
  }, []);

  // Load JSON data from server
  const loadJsonData = async () => {
    if (!filePath.trim()) {
      setError('Please enter a file path');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(`http://localhost:8089/api/json-data?file_path=${encodeURIComponent(filePath)}`);
      setJsonData(response.data);
      setTimeout(() => {
        displayJsonTree(response.data);
      }, 100);
    } catch (err) {
      setError(`Failed to load JSON data: ${err.response?.data?.detail || err.message}`);
      if (jsonDisplayRef.current) {
        jsonDisplayRef.current.innerHTML = '';
      }
    } finally {
      setLoading(false);
    }
  };

  // Handle file path change
  const handleFilePathChange = (e) => {
    setFilePath(e.target.value);
  };

  // Handle search term change
  const handleSearchTermChange = (e) => {
    setSearchTerm(e.target.value);
  };

  // Handle search type change
  const handleSearchTypeChange = (e) => {
    setSearchType(e.target.value);
  };

  // Handle search button click
  const handleSearch = () => {
    if (!jsonData) return;
    displayJsonTree(jsonData, searchTerm);
    expandAll();
  };

  // Handle clear search button click
  const handleClearSearch = () => {
    setSearchTerm('');
    if (jsonData) {
      displayJsonTree(jsonData);
    }
  };

  // Collapse all nodes
  const collapseAll = () => {
    const elements = document.querySelectorAll('.json-content');
    elements.forEach(el => {
      if (el.parentElement) {
        el.parentElement.classList.add('collapsed');
      }
    });
  };

  // Expand all nodes
  const expandAll = () => {
    const elements = document.querySelectorAll('.json-content');
    elements.forEach(el => {
      if (el.parentElement) {
        el.parentElement.classList.remove('collapsed');
      }
    });
  };

  // Display JSON data as an interactive tree
  const displayJsonTree = (data, highlightTerm = '') => {
    if (!jsonDisplayRef.current) return;

    const createTree = (obj, level = 0) => {
      if (obj === null) {
        return `<span class="json-null">null</span>`;
      }

      if (typeof obj !== 'object') {
        const valueClass = 
          typeof obj === 'string' ? 'json-string' : 
          typeof obj === 'number' ? 'json-number' : 
          typeof obj === 'boolean' ? 'json-boolean' : 'json-null';

        const valueStr = typeof obj === 'string' ? `"${obj.replace(/"/g, '\\"')}"` : String(obj);

        if (highlightTerm && String(obj).toLowerCase().includes(highlightTerm.toLowerCase())) {
          return `<span class="${valueClass}" style="background-color: yellow;">${valueStr}</span>`;
        }

        return `<span class="${valueClass}">${valueStr}</span>`;
      }

      const isArray = Array.isArray(obj);
      const padding = '  '.repeat(level);
      const childPadding = '  '.repeat(level + 1);

      let html = isArray ? '[' : '{';
      html += '<span class="collapsible">...</span><div class="json-content">';

      const entries = isArray ? obj.map((val, i) => [i, val]) : Object.entries(obj);

      for (let i = 0; i < entries.length; i++) {
        const [key, value] = entries[i];
        const keyStr = isArray ? '' : `<span class="json-key">"${key}"</span>: `;

        // Highlight key if needed
        const highlightedKey = (
          highlightTerm && 
          (searchType === 'key' || searchType === 'both') && 
          String(key).toLowerCase().includes(highlightTerm.toLowerCase())
        ) ? 
          `<span class="json-key" style="background-color: yellow;">"${key}"</span>: ` : 
          keyStr;

        html += '\n' + childPadding + (isArray ? '' : highlightedKey);
        html += createTree(value, level + 1);

        if (i < entries.length - 1) {
          html += ',';
        }
      }

      html += '\n' + padding + '</div>' + (isArray ? ']' : '}');
      return html;
    };

    jsonDisplayRef.current.innerHTML = createTree(data);

    // Add click handlers for collapsible elements
    document.querySelectorAll('.collapsible').forEach(el => {
      el.addEventListener('click', (e) => {
        e.target.parentElement.classList.toggle('collapsed');
        e.stopPropagation();
      });
    });
  };

  return (
    <Box sx={{ mb: 4 }}>
      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
          <CodeIcon sx={{ mr: 1 }} />
          JSON Data Viewer
        </Typography>

        <Divider sx={{ my: 2 }} />

        <Grid container spacing={2}>
          {/* File Path Input */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <TextField
                fullWidth
                label="File Path"
                value={filePath}
                onChange={handleFilePathChange}
                variant="outlined"
                placeholder="data.json"
                sx={{ mr: 1 }}
              />
              <Button 
                variant="contained" 
                onClick={loadJsonData} 
                startIcon={<RefreshIcon />}
                disabled={loading}
              >
                Load
              </Button>
            </Box>
          </Grid>

          {/* Search Controls */}
          <Grid item xs={12} sm={6}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <TextField
                fullWidth
                label="Search"
                value={searchTerm}
                onChange={handleSearchTermChange}
                variant="outlined"
                placeholder="Search term..."
                sx={{ mr: 1 }}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <FormControl sx={{ minWidth: 120, mr: 1 }}>
                <InputLabel>Search In</InputLabel>
                <Select
                  value={searchType}
                  onChange={handleSearchTypeChange}
                  label="Search In"
                >
                  <MenuItem value="key">Keys</MenuItem>
                  <MenuItem value="value">Values</MenuItem>
                  <MenuItem value="both">Both</MenuItem>
                </Select>
              </FormControl>
              <Button 
                variant="contained" 
                onClick={handleSearch} 
                startIcon={<SearchIcon />}
                disabled={loading || !jsonData}
              >
                Search
              </Button>
              <IconButton 
                onClick={handleClearSearch}
                disabled={!searchTerm || loading}
                sx={{ ml: 1 }}
              >
                <ClearIcon />
              </IconButton>
            </Box>
          </Grid>

          {/* Expand/Collapse Controls */}
          <Grid item xs={12} sm={6}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button 
                variant="outlined" 
                onClick={collapseAll} 
                startIcon={<ExpandLessIcon />}
                disabled={loading || !jsonData}
                sx={{ mr: 1 }}
              >
                Collapse All
              </Button>
              <Button 
                variant="outlined" 
                onClick={expandAll} 
                startIcon={<ExpandMoreIcon />}
                disabled={loading || !jsonData}
              >
                Expand All
              </Button>
            </Box>
          </Grid>
        </Grid>

        {/* Error Message */}
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        {/* Loading Indicator */}
        {loading && (
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mt: 3 }}>
            <CircularProgress size={24} sx={{ mr: 1 }} />
            <Typography>Loading data...</Typography>
          </Box>
        )}

        {/* JSON Display */}
        <Box 
          sx={{ 
            mt: 3, 
            p: 2, 
            bgcolor: '#f8f8f8', 
            borderRadius: 1, 
            border: '1px solid #ddd',
            maxHeight: '700px',
            overflow: 'auto',
            fontFamily: 'monospace',
            fontSize: '14px',
            position: 'relative',
            '& .collapsible': {
              cursor: 'pointer',
              userSelect: 'none',
            },
            '& .collapsed > .json-content': {
              display: 'none',
            },
            '& .json-key': {
              color: '#0078d4',
            },
            '& .json-string': {
              color: '#008000',
            },
            '& .json-number': {
              color: '#d14',
            },
            '& .json-boolean': {
              color: '#905',
            },
            '& .json-null': {
              color: '#999',
            }
          }}
        >
          <pre ref={jsonDisplayRef}></pre>
          {!jsonData && !loading && !error && (
            <Typography 
              variant="body2" 
              color="text.secondary" 
              align="center" 
              sx={{ p: 3 }}
            >
              No data loaded. Enter a file path and click "Load".
            </Typography>
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default JsonViewer;