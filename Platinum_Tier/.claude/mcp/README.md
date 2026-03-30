# Google Search MCP Service

This MCP (Model Context Protocol) service provides Google Custom Search functionality to the AI employee system.

## Configuration

### Prerequisites

1. Google API Key
2. Google Custom Search Engine (CSE) ID

### Setup Instructions

1. **Get Google API Key**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Custom Search API
   - Create credentials (API Key)

2. **Create Custom Search Engine**:
   - Go to [Google Custom Search Engine](https://cse.google.com/cse/)
   - Create a new search engine
   - Note down the Search Engine ID

3. **Configure Credentials**:
   You have two options:

   **Option 1: JSON Configuration** (Recommended)
   Update `.claude/mcp/google_config.json` with your credentials:
   ```json
   {
       "GOOGLE_API_KEY": "your_actual_google_api_key_here",
       "GOOGLE_CSE_ID": "your_actual_google_cse_id_here"
   }
   ```

   **Option 2: Environment Variables**
   Add to your `.env` file:
   ```bash
   GOOGLE_API_KEY=your_actual_google_api_key_here
   GOOGLE_CSE_ID=your_actual_google_cse_id_here
   ```

## Usage

The service provides a `google_search` tool that can be used as follows:

```json
{
  "name": "google_search",
  "arguments": {
    "query": "your search query here",
    "num_results": 5
  }
}
```

## Integration with Plan Creation

The `create_plans.py` script uses this MCP service to research complex emails and create detailed plans based on the search results. Each email in the `needs_action` folder is processed to:

1. Extract key topics and entities
2. Perform Google searches on these topics
3. Create a Plan.md file with:
   - Email details
   - Key topics identified
   - Research results
   - Action items and next steps

## Troubleshooting

- If you get an authentication error, verify your API key and CSE ID are correct
- Ensure the Custom Search API is enabled in your Google Cloud project
- Check that your CSE is properly configured and has not exceeded quota limits