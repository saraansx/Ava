import logging
import httpx
from config import Config

class NewsTool:
    def __init__(self):
        self.name = "news"
        self.description = "Get API news. Can get top headlines or search for specific topics."
        self.logger = logging.getLogger("NewsTool")
        self.api_key = Config.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"

    def execute(self, query=None, category=None):
        if not self.api_key:
            return "Error: News API Key is missing."

        try:
            params = {
                "apiKey": self.api_key,
                "language": "en",
                "pageSize": 5, 
            }

            if query:
                url = f"{self.base_url}/everything" 
                params["q"] = query
                params["sortBy"] = "relevancy"
            else:
                url = f"{self.base_url}/top-headlines"
                params["country"] = "us"
                if category:
                    params["category"] = category

            response = httpx.get(url, params=params)
            data = response.json()

            if response.status_code == 200:
                articles = data.get("articles", [])
                if not articles:
                    return f"No news found for {query if query else 'top headlines'}."
                
                result = []
                for idx, article in enumerate(articles, 1):
                    title = article.get("title", "No Title")
                    source = article.get("source", {}).get("name", "Unknown Source")
                    result.append(f"{idx}. {title} ({source})")
                
                return "\n".join(result)
            else:
                error_msg = data.get('message', 'Unknown error')
                self.logger.error(f"News API Error: {error_msg}")
                return f"Error fetching news: {error_msg}"

        except Exception as e:
            self.logger.error(f"News Fetch Error: {e}")
            return f"An error occurred: {e}"
