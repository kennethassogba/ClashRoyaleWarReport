# Clash Royale War Report Automation

This project automatically retrieves war statistics for the CCPOM clan via the
official Clash Royale API and publishes a top 5 report to Discord every Monday.

## Project Structure

* analyze\_war.py: main script for API calls and data analysis  
* .github/workflows/main.yml: GitHub Actions workflow for automatic execution  
* requirements.txt: Python dependencies

## Initial Configuration

### 1\. Clash Royale API

Create a token on the Clash Royale Developer portal.  
Since GitHub Actions use dynamic outbound IP addresses, you might need to use a
proxy or update the token if the connection is refused.

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

### Automatic

The script runs automatically every Monday at 08:00 UTC via GitHub Actions.

### Manual

You can trigger the script manually via the Actions tab on GitHub by selecting
Clash Royale War Report and clicking Run workflow.

