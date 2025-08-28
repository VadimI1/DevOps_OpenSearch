import requests
import random
from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional
import os
import uvicorn

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(__file__)
load_dotenv(os.path.join(BASE_DIR, '.env'))

app = FastAPI(title='OpenSearch')


OPENSEARCH_HOST = os.getenv('OPENSEARCH_HOST', os.getenv('OPENSEARCH_HOST'))
OPENSEARCH_USERNAME = os.getenv('OPENSEARCH_USERNAME', os.getenv('OPENSEARCH_USERNAME'))
OPENSEARCH_PASSWORD = os.getenv('OPENSEARCH_PASSWORD', os.getenv('OPENSEARCH_PASSWORD'))
INDEX_NAME = 'documents_index'
AUTH = (OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD)


def opensearch_request(method, endpoint, data=None):
    url = f"{OPENSEARCH_HOST}{endpoint}"
    headers = {'Content-Type': 'application/json'}

    try:
        if method == 'GET':
            response = requests.get(url, auth=AUTH, headers=headers, json=data, timeout=10)
        elif method == 'POST':
            response = requests.post(url, auth=AUTH, headers=headers, json=data, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, auth=AUTH, headers=headers, json=data, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, auth=AUTH, headers=headers, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"OpenSearch error: {str(e)}")


def create_index():
    index_body = {
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        },
        "mappings": {
            "properties": {
                "title": {
                    "type": "text",
                },
                "content": {
                    "type": "text",
                },
                "content_type": {
                    "type": "keyword"
                }
            }
        }
    }

    try:
        opensearch_request('GET', f'/{INDEX_NAME}')
        print(f"Index '{INDEX_NAME}' already exists")
    except:
        opensearch_request('PUT', f'/{INDEX_NAME}', index_body)
        print(f"Index '{INDEX_NAME}' created successfully")


def generate_sample_documents():
    content_types = ['article', 'news', 'tutorial', 'review']
    documents = [
        {"title": "Первый документ", "content": "Это содержимое первого документа",
         "content_type": random.choice(content_types)},
        {"title": "Второй документ", "content": "Это содержимое второго документа",
         "content_type": random.choice(content_types)},
        {"title": "Третий документ", "content": "Это содержимое третьего документа",
         "content_type": random.choice(content_types)},
        {"title": "Четвертый документ", "content": "Это содержимое четвертого документа",
         "content_type": random.choice(content_types)},
        {"title": "Пятый документ", "content": "Это содержимое пятого документа",
         "content_type": random.choice(content_types)},
    ]
    return documents


def index_documents():
    documents = generate_sample_documents()

    for i, doc in enumerate(documents):
        opensearch_request('POST', f'/{INDEX_NAME}/_doc/{i + 1}', doc)

    print(f"Indexed {len(documents)} documents")


def search_documents(keyword: str, content_type: Optional[str] = None):
    query = {
        "bool": {
            "should": [
                {"match": {"title": keyword}},
                {"match": {"content": keyword}}
            ],
            "minimum_should_match": 1
        }
    }

    if content_type:
        query["bool"]["filter"] = [{"term": {"content_type": content_type}}]

    search_body = {
        "query": query,
        "_source": ["title", "content", "content_type"],
        "size": 10,
        "min_score": 0.01
    }

    response = opensearch_request('POST', f'/{INDEX_NAME}/_search', search_body)
    results = []
    for hit in response.get('hits', {}).get('hits', []):
        source = hit.get('_source', {})
        content = source.get('content', '')
        snippet = content[:50] + '...' if len(content) > 50 else content

        results.append({
            'title': source.get('title', ''),
            'snippet': snippet,
            'content_type': source.get('content_type', ''),
            'score': hit.get('_score', 0)
        })

    return results


@app.get("/")
async def root():
    return {"message": "OpenSearch Search Application"}


@app.post("/init")
async def initialize_index():
    """Инициализация индекса и загрузка тестовых данных"""
    try:
        create_index()
        index_documents()
        return {"status": "success", "message": "Index created and sample data loaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search")
async def search(
        q: str = Query(..., description="Search keyword"),
        content_type: Optional[str] = Query(None, description="Filter by content type")
):
    """Поиск документов с фильтром по content_type"""
    try:
        results = search_documents(q, content_type)
        return {
            "status": "success",
            "query": q,
            "content_type_filter": content_type,
            "results": results,
            "total_results": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    try:
        create_index()
        index_documents()
    except Exception as e:
        print(f"Initialization error: {e}")

    uvicorn.run(app, port=9200)