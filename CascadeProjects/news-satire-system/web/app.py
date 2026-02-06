from flask import Flask, render_template, request, jsonify, send_from_directory
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from src.storage.archive import ArchiveManager
    from src.generation.comic_generator import ComicGenerator
    from src.api.newsdata import NewsDataAPI
    from src.generation.satire_engine import SatireEngine
    
    # Initialize components
    archive_manager = ArchiveManager()
    comic_generator = ComicGenerator()
    news_api = NewsDataAPI()
    satire_engine = SatireEngine()
    
    # Create sample data if no articles exist
    if not archive_manager.search_articles("", limit=1):
        sample_articles = [
            {
                'id': 1,  # Changed to integer
                'headline': 'Local Government Announces Plans to Consider Thinking About Maybe Addressing Issues Someday',
                'opening_paragraph': 'City officials held a press conference today to announce their intention to form a committee that will explore the possibility of discussing potential challenges that might need consideration at some point in the future.',
                'category': 'politics',
                'byline': 'Sarah Johnson',
                'timestamp': '2024-01-15T10:00:00Z',
                'body_paragraphs': [
                    'The announcement, which took approximately 45 minutes to deliver, was met with cautious optimism from residents who have grown accustomed to delayed responses to community needs.',
                    'Mayor Thompson explained that this proactive approach to potentially addressing issues represents a bold step forward in municipal governance, even though no specific timeline was provided for when actual consideration might begin.'
                ],
                'expert_quotes': [
                    {
                        'expert': 'Dr. Michael Roberts',
                        'affiliation': 'University of Public Policy Studies',
                        'quote': 'This represents a paradigm shift in governmental procrastination. We\'re moving from ignoring problems to actively ignoring them in a more structured way.'
                    }
                ]
            },
            {
                'id': 2,  # Changed to integer
                'headline': 'Tech Startup Disrupts Industry By Making Things Slightly More Complicated',
                'opening_paragraph': 'Innovation Labs unveiled groundbreaking new technology today that promises to revolutionize how people interact with things they already knew how to use.',
                'category': 'technology',
                'byline': 'Mark Chen',
                'timestamp': '2024-01-15T14:30:00Z',
                'body_paragraphs': [
                    'The new platform, which requires three separate apps and a monthly subscription, adds several additional steps to processes that previously took seconds to complete.',
                    'Investors have poured $50 million into the venture, citing the enormous potential of convincing people they need solutions to problems they didn\'t know they had.'
                ],
                'expert_quotes': [
                    {
                        'expert': 'Jennifer Walsh',
                        'affiliation': 'Sil Valley Analyst',
                        'quote': 'This is exactly what the market was missing - a way to monetize simplicity by making it feel exclusive and complicated.'
                    }
                ]
            },
            {
                'id': 3,  # Changed to integer
                'headline': 'Study Finds People Who Read Studies Are More Likely To Be In Studies',
                'opening_paragraph': 'Groundbreaking research from the Institute of Obvious Conclusions reveals a strong correlation between reading studies and being included in future studies.',
                'category': 'science',
                'byline': 'Dr. Emily Watson',
                'timestamp': '2024-01-15T09:15:00Z',
                'body_paragraphs': [
                    'The five-year study followed 10,000 participants, 87% of whom were included in at least one study during the research period.',
                    'Researchers noted that participants who read the most studies were 300% more likely to be cited in subsequent studies about people who read studies.'
                ],
                'expert_quotes': [
                    {
                        'expert': 'Dr. Robert Miller',
                        'affiliation': 'Center for Academic Research',
                        'quote': 'Our findings suggest a self-perpetuating cycle of study-reading that could revolutionize how we conduct future studies about study-reading patterns.'
                    }
                ]
            }
        ]
        
        # Add sample articles to archive
        for article in sample_articles:
            archive_manager.store_article(article)

except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    # Fallback data
    archive_manager = None
    comic_generator = None
    news_api = None
    satire_engine = None

app = Flask(__name__, static_folder='static')

@app.route('/')
def home():
    """Homepage with latest articles."""
    # Get latest articles
    if archive_manager:
        latest_articles = archive_manager.search_articles("", limit=6)
    else:
        # Fallback sample data
        latest_articles = [
            {
                'id': 1,
                'headline': 'Local Government Announces Plans to Consider Thinking About Maybe Addressing Issues Someday',
                'opening_paragraph': 'City officials held a press conference today to announce their intention to form a committee that will explore the possibility of discussing potential challenges that might need consideration at some point in the future.',
                'category': 'politics',
                'byline': 'Sarah Johnson',
                'timestamp': '2024-01-15T10:00:00Z',
                'body_paragraphs': [
                    'The announcement, which took approximately 45 minutes to deliver, was met with cautious optimism from residents who have grown accustomed to delayed responses to community needs.',
                    'Mayor Thompson explained that this proactive approach to potentially addressing issues represents a bold step forward in municipal governance, even though no specific timeline was provided for when actual consideration might begin.'
                ],
                'expert_quotes': [
                    {
                        'expert': 'Dr. Michael Roberts',
                        'affiliation': 'University of Public Policy Studies',
                        'quote': 'This represents a paradigm shift in governmental procrastination. We\'re moving from ignoring problems to actively ignoring them in a more structured way.'
                    }
                ]
            },
            {
                'id': 2,
                'headline': 'Tech Startup Disrupts Industry By Making Things Slightly More Complicated',
                'opening_paragraph': 'Innovation Labs unveiled groundbreaking new technology today that promises to revolutionize how people interact with things they already knew how to use.',
                'category': 'technology',
                'byline': 'Mark Chen',
                'timestamp': '2024-01-15T14:30:00Z',
                'body_paragraphs': [
                    'The new platform, which requires three separate apps and a monthly subscription, adds several additional steps to processes that previously took seconds to complete.',
                    'Investors have poured $50 million into the venture, citing the enormous potential of convincing people they need solutions to problems they didn\'t know they had.'
                ],
                'expert_quotes': [
                    {
                        'expert': 'Jennifer Walsh',
                        'affiliation': 'Sil Valley Analyst',
                        'quote': 'This is exactly what the market was missing - a way to monetize simplicity by making it feel exclusive and complicated.'
                    }
                ]
            },
            {
                'id': 3,
                'headline': 'Study Finds People Who Read Studies Are More Likely To Be In Studies',
                'opening_paragraph': 'Groundbreaking research from the Institute of Obvious Conclusions reveals a strong correlation between reading studies and being included in future studies.',
                'category': 'science',
                'byline': 'Dr. Emily Watson',
                'timestamp': '2024-01-15T09:15:00Z',
                'body_paragraphs': [
                    'The five-year study followed 10,000 participants, 87% of whom were included in at least one study during the research period.',
                    'Researchers noted that participants who read the most studies were 300% more likely to be cited in subsequent studies about people who read studies.'
                ],
                'expert_quotes': [
                    {
                        'expert': 'Dr. Robert Miller',
                        'affiliation': 'Center for Academic Research',
                        'quote': 'Our findings suggest a self-perpetuating cycle of study-reading that could revolutionize how we conduct future studies about study-reading patterns.'
                    }
                ]
            }
        ]
    
    # Get featured article (first one)
    featured_article = latest_articles[0] if latest_articles else None
    
    # Get remaining articles (excluding featured)
    other_articles = latest_articles[1:] if len(latest_articles) > 1 else []
    
    return render_template('index.html', 
                        featured_article=featured_article,
                        other_articles=other_articles)

@app.route('/article/<path:article_id>')
def article(article_id):
    """Individual article page."""
    if archive_manager:
        article = archive_manager.get_article_by_id(article_id)
        
        if not article:
            return render_template('404.html'), 404
        
        # Get related articles
        related_articles = archive_manager.get_related_articles(article, limit=3)
    else:
        # Fallback - find article in sample data
        sample_articles = [
            {
                'id': 1,
                'headline': 'Local Government Announces Plans to Consider Thinking About Maybe Addressing Issues Someday',
                'opening_paragraph': 'City officials held a press conference today to announce their intention to form a committee that will explore the possibility of discussing potential challenges that might need consideration at some point in the future.',
                'category': 'politics',
                'byline': 'Sarah Johnson',
                'timestamp': '2024-01-15T10:00:00Z',
                'body_paragraphs': [
                    'The announcement, which took approximately 45 minutes to deliver, was met with cautious optimism from residents who have grown accustomed to delayed responses to community needs.',
                    'Mayor Thompson explained that this proactive approach to potentially addressing issues represents a bold step forward in municipal governance, even though no specific timeline was provided for when actual consideration might begin.'
                ],
                'expert_quotes': [
                    {
                        'expert': 'Dr. Michael Roberts',
                        'affiliation': 'University of Public Policy Studies',
                        'quote': 'This represents a paradigm shift in governmental procrastination. We\'re moving from ignoring problems to actively ignoring them in a more structured way.'
                    }
                ]
            },
            {
                'id': 2,
                'headline': 'Tech Startup Disrupts Industry By Making Things Slightly More Complicated',
                'opening_paragraph': 'Innovation Labs unveiled groundbreaking new technology today that promises to revolutionize how people interact with things they already knew how to use.',
                'category': 'technology',
                'byline': 'Mark Chen',
                'timestamp': '2024-01-15T14:30:00Z',
                'body_paragraphs': [
                    'The new platform, which requires three separate apps and a monthly subscription, adds several additional steps to processes that previously took seconds to complete.',
                    'Investors have poured $50 million into the venture, citing the enormous potential of convincing people they need solutions to problems they didn\'t know they had.'
                ],
                'expert_quotes': [
                    {
                        'expert': 'Jennifer Walsh',
                        'affiliation': 'Sil Valley Analyst',
                        'quote': 'This is exactly what the market was missing - a way to monetize simplicity by making it feel exclusive and complicated.'
                    }
                ]
            },
            {
                'id': 3,
                'headline': 'Study Finds People Who Read Studies Are More Likely To Be In Studies',
                'opening_paragraph': 'Groundbreaking research from the Institute of Obvious Conclusions reveals a strong correlation between reading studies and being included in future studies.',
                'category': 'science',
                'byline': 'Dr. Emily Watson',
                'timestamp': '2024-01-15T09:15:00Z',
                'body_paragraphs': [
                    'The five-year study followed 10,000 participants, 87% of whom were included in at least one study during the research period.',
                    'Researchers noted that participants who read the most studies were 300% more likely to be cited in subsequent studies about people who read studies.'
                ],
                'expert_quotes': [
                    {
                        'expert': 'Dr. Robert Miller',
                        'affiliation': 'Center for Academic Research',
                        'quote': 'Our findings suggest a self-perpetuating cycle of study-reading that could revolutionize how we conduct future studies about study-reading patterns.'
                    }
                ]
            }
        ]
        
        article = next((a for a in sample_articles if str(a['id']) == str(article_id)), None)
        if not article:
            return render_template('404.html'), 404
        
        related_articles = [a for a in sample_articles if str(a['id']) != str(article_id)][:3]
    
    return render_template('article.html', 
                        article=article,
                        related_articles=related_articles)

@app.route('/category/<category>')
def category(category):
    """Category page."""
    if archive_manager:
        articles = archive_manager.search_articles("", category=category, limit=12)
    else:
        # Fallback - filter sample articles by category
        all_articles = [
            {
                'id': 1,
                'headline': 'Local Government Announces Plans to Consider Thinking About Maybe Addressing Issues Someday',
                'opening_paragraph': 'City officials held a press conference today to announce their intention to form a committee that will explore the possibility of discussing potential challenges that might need consideration at some point in the future.',
                'category': 'politics',
                'byline': 'Sarah Johnson',
                'timestamp': '2024-01-15T10:00:00Z',
                'body_paragraphs': [
                    'The announcement, which took approximately 45 minutes to deliver, was met with cautious optimism from residents who have grown accustomed to delayed responses to community needs.',
                    'Mayor Thompson explained that this proactive approach to potentially addressing issues represents a bold step forward in municipal governance, even though no specific timeline was provided for when actual consideration might begin.'
                ],
                'expert_quotes': [
                    {
                        'expert': 'Dr. Michael Roberts',
                        'affiliation': 'University of Public Policy Studies',
                        'quote': 'This represents a paradigm shift in governmental procrastination. We\'re moving from ignoring problems to actively ignoring them in a more structured way.'
                    }
                ]
            },
            {
                'id': 2,
                'headline': 'Tech Startup Disrupts Industry By Making Things Slightly More Complicated',
                'opening_paragraph': 'Innovation Labs unveiled groundbreaking new technology today that promises to revolutionize how people interact with things they already knew how to use.',
                'category': 'technology',
                'byline': 'Mark Chen',
                'timestamp': '2024-01-15T14:30:00Z',
                'body_paragraphs': [
                    'The new platform, which requires three separate apps and a monthly subscription, adds several additional steps to processes that previously took seconds to complete.',
                    'Investors have poured $50 million into the venture, citing the enormous potential of convincing people they need solutions to problems they didn\'t know they had.'
                ],
                'expert_quotes': [
                    {
                        'expert': 'Jennifer Walsh',
                        'affiliation': 'Sil Valley Analyst',
                        'quote': 'This is exactly what the market was missing - a way to monetize simplicity by making it feel exclusive and complicated.'
                    }
                ]
            },
            {
                'id': 3,
                'headline': 'Study Finds People Who Read Studies Are More Likely To Be In Studies',
                'opening_paragraph': 'Groundbreaking research from the Institute of Obvious Conclusions reveals a strong correlation between reading studies and being included in future studies.',
                'category': 'science',
                'byline': 'Dr. Emily Watson',
                'timestamp': '2024-01-15T09:15:00Z',
                'body_paragraphs': [
                    'The five-year study followed 10,000 participants, 87% of whom were included in at least one study during the research period.',
                    'Researchers noted that participants who read the most studies were 300% more likely to be cited in subsequent studies about people who read studies.'
                ],
                'expert_quotes': [
                    {
                        'expert': 'Dr. Robert Miller',
                        'affiliation': 'Center for Academic Research',
                        'quote': 'Our findings suggest a self-perpetuating cycle of study-reading that could revolutionize how we conduct future studies about study-reading patterns.'
                    }
                ]
            }
        ]
        articles = [a for a in all_articles if a['category'] == category]
    
    return render_template('category.html',
                        category=category,
                        articles=articles)

@app.route('/about')
def about():
    """About page."""
    return render_template('about.html')

@app.route('/luxury')
def luxury():
    """Ultra luxury landing page."""
    return render_template('luxury.html')

@app.route('/api/latest')
def api_latest():
    """API endpoint for latest articles."""
    if archive_manager:
        articles = archive_manager.search_articles("", limit=10)
    else:
        # Fallback sample data
        articles = [
            {
                'id': 1,
                'headline': 'Local Government Announces Plans to Consider Thinking About Maybe Addressing Issues Someday',
                'opening_paragraph': 'City officials held a press conference today to announce their intention to form a committee that will explore the possibility of discussing potential challenges that might need consideration at some point in the future.',
                'category': 'politics',
                'byline': 'Sarah Johnson',
                'timestamp': '2024-01-15T10:00:00Z'
            },
            {
                'id': 2,
                'headline': 'Tech Startup Disrupts Industry By Making Things Slightly More Complicated',
                'opening_paragraph': 'Innovation Labs unveiled groundbreaking new technology today that promises to revolutionize how people interact with things they already knew how to use.',
                'category': 'technology',
                'byline': 'Mark Chen',
                'timestamp': '2024-01-15T14:30:00Z'
            },
            {
                'id': 3,
                'headline': 'Study Finds People Who Read Studies Are More Likely To Be In Studies',
                'opening_paragraph': 'Groundbreaking research from the Institute of Obvious Conclusions reveals a strong correlation between reading studies and being included in future studies.',
                'category': 'science',
                'byline': 'Dr. Emily Watson',
                'timestamp': '2024-01-15T09:15:00Z'
            }
        ]
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
    if comic_generator:
        comic_metadata = comic_generator.generate_comic(sample_article)
    else:
        # Fallback response
        comic_metadata = {
            'success': False,
            'error': 'Comic generator not available',
            'message': 'The comic generation module is not installed. Please install the src modules to enable this feature.'
        }
    
    return jsonify(comic_metadata)

# Serve static files including logo
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files including logo.png."""
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
