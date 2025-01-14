# Twitter Trends Scraper

A Python-based web scraper that automatically fetches trending topics from Twitter/X and stores them in MongoDB. Built with Selenium WebDriver for reliable automation and Flask for a clean web interface.

## Features

- **Automated Twitter Login**: Secure login using environment variables
- **Trend Extraction**: Fetches top 5 trending topics in real-time
- **Data Persistence**: MongoDB integration for storing historical trends
- **Web Interface**: Clean UI to view and refresh trends
- **Error Handling**: Robust error handling with automatic retries
- **Proxy Support**: (In Development)
  - Bright Data integration planned
  - Scrape.do support coming soon
  - Multiple fallback options

## Prerequisites

- Python 3.8+
- MongoDB installed and running
- Chrome browser installed
- Twitter/X account

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Mohit-Kukreja-2002/Twiter-Trends-Scraper.git
   cd Twiter-Trends-Scraper
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy `.env.sample` to `.env`
   - Fill in your credentials and settings
   ```bash
   cp .env.sample .env
   ```

5. Start MongoDB service:
   ```bash
   # On Linux/Mac
   sudo systemctl start mongod
   
   # On Windows
   net start MongoDB
   ```

6. Run the application:
   ```bash
   python app.py
   ```