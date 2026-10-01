import json
import urllib.parse
from config.config import Config

class JobService:
    def __init__(self):
        self.jobs_data = self._load_json(Config.DATA_FOLDER / "jobs.json")

    def _load_json(self, filepath):
        if not filepath.exists():
            return {"portals": []}
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_job_links(self, target_role_title):
        portals = self.jobs_data.get("portals", [])
        
        query = target_role_title
        query_encoded = urllib.parse.quote_plus(query)
        query_slug = query.lower().replace(" ", "-")

        job_links = []
        for p in portals:
            name = p.get("name")
            template = p.get("url_template", "")
            
            url = template.replace("{query}", query_encoded).replace("{query_slug}", query_slug)
            
            job_links.append({
                "portal_name": name,
                "icon": p.get("icon", "briefcase"),
                "search_query": query,
                "url": url
            })

        return job_links
