"""
BigQuery MCP Tool
Standardized Model Context Protocol tool for querying Google Cloud BigQuery datasets.
"""

import os
from typing import List, Optional

class BigQueryMCPTool:
    """Model Context Protocol (MCP) tool for BigQuery dataset operations."""
    
    def __init__(self, gcp_project_id: Optional[str] = None):
        self.gcp_project_id = gcp_project_id or os.getenv("GCP_PROJECT_ID", "")

    def query_role_skills(self, search_keywords: List[str], limit: int = 15) -> Optional[List[str]]:
        """Queries BigQuery dataset for skills associated with search keywords."""
        if not self.gcp_project_id or not search_keywords:
            return None

        try:
            from google.cloud import bigquery
            client = bigquery.Client(project=self.gcp_project_id)
            
            where_clauses = " OR ".join([f"LOWER(title) LIKE @kw{i}" for i in range(len(search_keywords))])
            sql_query = f"""
                SELECT tag, COUNT(*) as cnt
                FROM `bigquery-public-data.stackoverflow.posts_questions`,
                UNNEST(SPLIT(tags, '|')) as tag
                WHERE {where_clauses}
                GROUP BY tag
                ORDER BY cnt DESC
                LIMIT {limit}
            """
            
            query_params = [
                bigquery.ScalarQueryParameter(f"kw{i}", "STRING", f"%{kw}%")
                for i, kw in enumerate(search_keywords)
            ]
            
            job_config = bigquery.QueryJobConfig(query_parameters=query_params)
            query_job = client.query(sql_query, job_config=job_config)
            results = query_job.result()
            
            skills = [row.tag.replace('-', ' ').title() for row in results if row.tag]
            return skills if skills else None
            
        except Exception as e:
            print(f"[BigQuery MCP Tool Notice]: BigQuery execution notice ({e})", flush=True)
            return None
