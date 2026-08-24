import os
from google.cloud import bigquery

def test_bigquery_connection():
    project_id = os.getenv("GCP_PROJECT_ID")
    print("Testing GCP BigQuery Connection...")
    print(f"GCP Project ID: {project_id if project_id else 'Not set (will try default project)'}")
    print("=" * 60)

    try:
        # Initialize BigQuery Client using Application Default Credentials (ADC)
        client = bigquery.Client(project=project_id)
        
        # Test query over BigQuery public dataset
        query = """
            SELECT title, score, view_count 
            FROM `bigquery-public-data.stackoverflow.posts_questions` 
            WHERE title LIKE '%Python%'
            LIMIT 3
        """
        query_job = client.query(query)
        results = query_job.result()
        
        print("\n[SUCCESS] BigQuery Connected Successfully!")
        print("Sample Data fetched from bigquery-public-data:")
        for row in results:
            print(f"- {row.title[:60]}... (Views: {row.view_count})")
            
    except Exception as e:
        print(f"\n[GCP CONNECTION NOTICE]: {e}")
        print("\nTo connect to GCP:")
        print("1. Run: gcloud auth application-default login")
        print("2. Set: $env:GCP_PROJECT_ID='your-gcp-project-id'")

if __name__ == "__main__":
    test_bigquery_connection()
