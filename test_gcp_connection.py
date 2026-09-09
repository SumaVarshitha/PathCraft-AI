import os

def test_bigquery_connection():
    project_id = os.getenv("GCP_PROJECT_ID")
    print("Testing GCP BigQuery Connection...")
    print(f"GCP Project ID: {project_id if project_id else 'Not set (will try default project)'}")
    print("=" * 60)

    try:
        from google.cloud import bigquery
        client = bigquery.Client(project=project_id)
        query = """
            SELECT title, score, view_count 
            FROM `bigquery-public-data.stackoverflow.posts_questions` 
            WHERE title LIKE '%Python%'
            LIMIT 3
        """
        query_job = client.query(query)
        results = query_job.result()
        print("\n[SUCCESS] BigQuery Connected Successfully!")
        for row in results:
            print(f"- {row.title[:60]}... (Views: {row.view_count})")
    except ImportError:
        print("\n[GCP NOTICE]: 'google-cloud-bigquery' package not installed. (Optional feature, using Gemini Search Grounding).")
    except Exception as e:
        print(f"\n[GCP CONNECTION NOTICE]: {e}")

if __name__ == "__main__":
    test_bigquery_connection()
