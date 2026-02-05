from flask import Flask, render_template, request, jsonify, send_from_directory
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.storage.archive import ArchiveManager
from src.generation.comic_generator import ComicGenerator
from src.api.newsdata import NewsDataAPI
from src.generation.satire_engine import SatireEngine

app = Flask(__name__, static_folder='static')

# Initialize components
archive_manager = ArchiveManager()
comic_generator = ComicGenerator()
news_api = NewsDataAPI()
satire_engine = SatireEngine()

@app.route('/')
def home():
    """Homepage with latest articles."""
    # Get latest articles
    latest_articles = archive_manager.search_articles("", limit=6)
    
    # Get featured article (first one)
    featured_article = latest_articles[0] if latest_articles else None
    
    # Get remaining articles (excluding featured)
    other_articles = latest_articles[1:] if len(latest_articles) > 1 else []
    
    return render_template('index.html', 
                        featured_article=featured_article,
                        other_articles=other_articles)

@app.route('/article/<article_id>')
def article(article_id):
    """Individual article page."""
    article = archive_manager.get_article_by_id(article_id)
    
    if not article:
        return render_template('404.html'), 404
    
    # Get related articles
    related_articles = archive_manager.get_related_articles(article, limit=3)
    
    return render_template('article.html', 
                        article=article,
                        related_articles=related_articles)

@app.route('/category/<category>')
def category(category):
    """Category page."""
    articles = archive_manager.search_articles("", category=category, limit=12)
    
    return render_template('category.html',
                        category=category,
                        articles=articles)

@app.route('/about')
def about():
    """About page."""
    return render_template('about.html')

@app.route('/api/latest')
def api_latest():
    """API endpoint for latest articles."""
    articles = archive_manager.search_articles("", limit=10)
    return jsonify(articles)

@app.route('/api/create-comic', methods=['POST'])
def api_create_comic():
    """API endpoint to create custom comic."""
    data = request.get_json()
    
    headline = data.get('headline', '')
    category = data.get('category', 'general')
    
    # Create sample article
    sample_article = {
        'headline': headline,
        'opening_paragraph': data.get('content', ''),
        'category': category
    }
    
    # Generate comic
    comic_metadata = comic_generator.generate_comic(sample_article)
    
    return jsonify(comic_metadata)

# Serve static files including logo
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files including logo.png."""
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
