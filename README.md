# Clash Royale War Report Automation

This project automatically retrieves war statistics for the CCPOM clan via the
official Clash Royale API and publishes a top 5 report to Discord every Monday.

## Project Structure

* analyze\_war.py: main script for API calls and data analysis  
* .github/workflows/main.yml: GitHub Actions workflow for automatic execution  
* requirements.txt: Python dependencies

## Initial Configuration

### 1. Clash Royale API

Create a token on the Clash Royale Developer portal.

### 2\. Discord Webhook

In your Discord server settings, create a Webhook for the desired channel and
copy the URL.

### 3\. GitHub Secrets

Add the following variables in Settings \> Secrets and variables \> Actions in
your repository:

* CLASH\_API\_TOKEN: your Supercell API token  
* DISCORD\_WEBHOOK\_URL: the full Discord Webhook URL

## Script Logic

The script queries the riverracelog endpoint to retrieve the war history.  
It calculates:

* The top 5 scores (fame) from the most recent completed war  
* The top 5 players based on a rolling average of the last 4 weeks

## Execution

**Important Note on Execution:** The Supercell API requires API keys to be associated with specific, whitelisted IP addresses. Because GitHub-hosted runners use a wide, dynamic range of IP addresses, it is not feasible to run this script directly via standard GitHub Actions.

To run this project, you must execute the script from a machine (or a self-hosted GitHub runner) with a static IP address that has been whitelisted for your Supercell API key.

### Manual Execution

You can run the script locally from a whitelisted machine:
```bash
python analyze_war.py
```

