# Outlook Mail Filter Web UI

This is a simple browser-based user interface for the Outlook Mail Filter application. It provides a clean, modern way to view and interact with your filtered emails.

## Features

- Modern, responsive design using Bootstrap
- Interactive settings panel for customizing search criteria
- Highlights keywords in subject and preview text
- Card-based layout for easy scanning of results
- Direct links to view emails in Outlook Web
- Settings saved between sessions

## Getting Started

### Usage Instructions

1. **Open the HTML file**: 
   Simply open the `index.html` file in your web browser by double-clicking it or using File > Open in your browser.

2. **View mock results**:
   Since the HTML UI can't directly execute Python code, it shows mock results for demonstration purposes.
   
   > **Note:** In a production environment, you would set up a small API server to run the Python script and return real results.

3. **Customize search settings**:
   - Click the ⚙️ Settings button to open the settings panel
   - Modify sender, keyword, and other search parameters
   - Click "Apply Settings" to update the view with your new criteria

## Integration with Python Script

To use this UI with actual email data, you would need to:

1. Set up a small API server (using Flask, FastAPI, or similar)
2. Create an endpoint that runs the mail filter script with parameters
3. Return the JSON results to the web UI

Example Flask implementation (not included):

```python
from flask import Flask, request, jsonify
import subprocess
import json

app = Flask(__name__)

@app.route('/api/emails', methods=['GET'])
def get_emails():
    # Get parameters from query string
    use_rapp_fast = request.args.get('use_rapp_fast', 'true').lower() == 'true'
    sender = request.args.get('sender', 'FASTRAPP@paypal.com')
    keyword = request.args.get('keyword', 'failed')
    max_items = request.args.get('max_items', '25')
    case_sensitive = request.args.get('case_sensitive', 'false').lower() == 'true'
    
    # Build command
    cmd = ["python3", "../main.py", "--json-output"]
    if use_rapp_fast:
        cmd.append("--use-rapp-fast")
    if sender:
        cmd.extend(["--sender", sender])
    if keyword:
        cmd.extend(["--keyword", keyword])
    if max_items:
        cmd.extend(["--max-items", max_items])
    if case_sensitive:
        cmd.append("--case-sensitive")
    
    # Run command
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Parse output
    try:
        output = result.stdout
        json_start = output.find('{')
        if json_start == -1:
            return jsonify({"error": "No JSON output found"}), 500
        
        json_output = output[json_start:]
        data = json.loads(json_output)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

## Customization

### Styling

The UI uses Bootstrap 5 for styling, along with custom CSS. You can modify the appearance by:

1. Editing the `<style>` section in the HTML file
2. Adding additional Bootstrap classes to elements
3. Linking to external CSS files

### Mock Data

For demonstration purposes, the UI shows mock email data. You can modify this data in the `displayMockResults()` function to show different examples or test various scenarios.

## Browser Compatibility

The UI should work in all modern browsers:

- Chrome/Edge (latest versions)
- Firefox (latest versions)
- Safari (latest versions)

## Future Enhancements

Potential improvements for the UI:

- Add real-time updates/polling
- Implement message viewing within the UI
- Add sorting and filtering options
- Create dark mode toggle
- Add user authentication
- Implement full message content display
- Add export functionality (CSV, PDF)

## Security Considerations

This UI is designed for local use only. If deploying to a server:

1. Implement proper authentication
2. Use HTTPS for all communications
3. Validate and sanitize all inputs
4. Implement proper error handling
5. Add rate limiting to prevent abuse