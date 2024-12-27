from flask import Flask, render_template, jsonify
from scraper import TwitterScraper
from database import MongoDB
import json
from bson import json_util
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
scraper = TwitterScraper()
db = MongoDB()

# Configure app from environment
app.debug = os.getenv('DEBUG', 'False').lower() == 'true'
port = int(os.getenv('PORT', 5000))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_scraper')
def run_scraper():
    try:
        # Run scraper with retry logic
        max_retries = int(os.getenv('PROXY_MAX_RETRIES', 3))
        for attempt in range(max_retries):
            try:
                trends_data = scraper.get_trending_topics_with_login()
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                continue
        
        # Format and save to MongoDB
        mongo_data = {
            'ip_address': trends_data['proxy_ip'],
            'nameoftrend1': trends_data['trends'][0],
            'nameoftrend2': trends_data['trends'][1],
            'nameoftrend3': trends_data['trends'][2],
            'nameoftrend4': trends_data['trends'][3],
            'nameoftrend5': trends_data['trends'][4],
            'timestamp': trends_data['timestamp']
        }
        
        db.save_trends(mongo_data)
        latest_record = db.get_latest_trends()
        json_data = json.loads(json_util.dumps(latest_record))
        
        return jsonify({
            'success': True,
            'data': json_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port) 