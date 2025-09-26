import React, { useState } from 'react';
import { 
  Card, CardContent, CardHeader, CardActions, 
  Typography, Button, Chip, Box, Avatar,
  Dialog, DialogTitle, DialogContent, DialogActions,
  IconButton, Tooltip
} from '@mui/material';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import MarkEmailReadIcon from '@mui/icons-material/MarkEmailRead';
import PersonIcon from '@mui/icons-material/Person';

/**
 * Component for displaying an email in a card format
 */
export const EmailCard = ({ email, keyword, folderId, highlightKeyword, formatDate }) => {
  const [expanded, setExpanded] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  
  // Extract sender info
  const senderName = email.from?.emailAddress?.name || 'Unknown Sender';
  const senderEmail = email.from?.emailAddress?.address || '';
  
  // Format subject and preview
  const subject = email.subject || 'No Subject';
  const preview = email.bodyPreview || 'No preview available';
  
  // Generate Outlook web link
  const getOutlookLink = () => {
    // Format the IDs correctly - remove any special characters if needed
    const cleanMessageId = encodeURIComponent(email.id);
    
    if (folderId) {
      const cleanFolderId = encodeURIComponent(folderId);
      return `https://outlook.office365.com/mail/deeplink/readmessage?itemid=${cleanMessageId}&folderid=${cleanFolderId}`;
    } else {
      return `https://outlook.office365.com/mail/deeplink/readmessage?itemid=${cleanMessageId}`;
    }
  };
  
  // Use provided link or generate one
  const outlookLink = email.webLink || getOutlookLink();
  
  // Handle copy button click
  const handleCopy = () => {
    const textToCopy = `Subject: ${subject}\nFrom: ${senderName} <${senderEmail}>\nDate: ${email.receivedDateTime}\n\n${preview}`;
    navigator.clipboard.writeText(textToCopy)
      .then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      })
      .catch(err => console.error('Failed to copy text:', err));
  };
  
  // Get avatar based on sender domain
  const getAvatar = () => {
    if (!senderEmail) return <PersonIcon />;
    
    const domain = senderEmail.split('@')[1]?.toLowerCase();
    
    if (domain === 'paypal.com' || domain === 'paypalcorp.com') {
      return (
        <Avatar sx={{ bgcolor: '#0070ba' }}>
          P
        </Avatar>
      );
    }
    
    // First letter of sender name or email
    const firstLetter = (senderName || senderEmail)[0]?.toUpperCase() || '?';
    return <Avatar>{firstLetter}</Avatar>;
  };
  
  // Determine card background color based on email content
  const getCardStyle = () => {
    // Check if this is a critical or important email
    const isFailure = subject.toLowerCase().includes('failed') || 
                      subject.toLowerCase().includes('error') ||
                      subject.toLowerCase().includes('critical');
    
    if (isFailure) {
      return {
        borderLeft: '4px solid #f44336',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 4px 10px rgba(0,0,0,0.15)'
        }
      };
    }
    
    return {
      transition: 'transform 0.2s, box-shadow 0.2s',
      '&:hover': {
        transform: 'translateY(-4px)',
        boxShadow: '0 4px 10px rgba(0,0,0,0.15)'
      }
    };
  };
  
  return (
    <>
      <Card sx={getCardStyle()}>
        <CardHeader
          avatar={getAvatar()}
          title={
            <Typography variant="subtitle1" noWrap title={subject}>
              {highlightKeyword ? highlightKeyword(subject, keyword) : subject}
            </Typography>
          }
          subheader={
            <Typography variant="caption" color="text.secondary">
              {formatDate(email.receivedDateTime)}
            </Typography>
          }
        />
        
        <CardContent sx={{ pt: 0 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            From: {senderName} {senderEmail && `<${senderEmail}>`}
          </Typography>
          
          <Typography variant="body2" sx={{ mt: 1 }}>
            {highlightKeyword ? highlightKeyword(preview, keyword) : preview}
          </Typography>
        </CardContent>
        
        <CardActions>
          <Button 
            size="small" 
            startIcon={<OpenInNewIcon />}
            href={outlookLink}
            target="_blank"
            rel="noopener noreferrer"
          >
            Open in Outlook
          </Button>
          
          <Box sx={{ ml: 'auto' }}>
            <Tooltip title={copied ? 'Copied!' : 'Copy email details'}>
              <IconButton onClick={handleCopy} size="small">
                <ContentCopyIcon fontSize="small" color={copied ? 'success' : 'action'} />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="View full email">
              <IconButton onClick={() => setDialogOpen(true)} size="small">
                <ExpandMoreIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        </CardActions>
      </Card>
      
      {/* Dialog for full email view */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {subject}
          <Typography variant="caption" sx={{ display: 'block', mt: 1 }}>
            {formatDate(email.receivedDateTime)}
          </Typography>
        </DialogTitle>
        
        <DialogContent dividers>
          <Typography variant="subtitle2" gutterBottom>
            From: {senderName} {senderEmail && `<${senderEmail}>`}
          </Typography>
          
          <Box sx={{ mt: 2 }}>
            <Typography variant="body1">
              {email.bodyPreview}
            </Typography>
          </Box>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Close</Button>
          <Button 
            variant="contained"
            startIcon={<OpenInNewIcon />}
            href={outlookLink}
            target="_blank"
            rel="noopener noreferrer"
          >
            Open in Outlook
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};