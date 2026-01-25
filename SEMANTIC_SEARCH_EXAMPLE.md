# Semantic Search Workflow - E2E Example

This document provides a complete end-to-end example of using the GPU-accelerated semantic search workflow.

## Architecture Overview

```
┌──────────────┐      HTTP POST       ┌─────────────────┐
│   Client     │ ──────────────────> │  .NET Web API   │
│  (curl/app)  │                      │  (Program.cs)   │
└──────────────┘                      └────────┬────────┘
                                               │
                                               │ Starts Workflow
                                               ▼
                                      ┌─────────────────────┐
                                      │ SemanticSearch      │
                                      │ Workflow (C#)       │
                                      └──────┬──────────────┘
                                             │
                                             │ Calls Activities
                                             ▼
                                      ┌─────────────────────┐
                                      │ Python Activities   │
                                      │ (GPU-Accelerated)   │
                                      │                     │
                                      │ • generate_embeddings│
                                      │ • compute_similarity │
                                      └─────────────────────┘
```

## HTTP Endpoint

**POST** `/semantic-search`

### Request Body

```json
{
  "query": "How do I reset my password?",
  "documents": [
    "Steps to update your account password and recover access",
    "Installing the mobile application on your device",
    "Troubleshooting common login and authentication issues",
    "Guide to configuring notification preferences",
    "How to delete your account permanently"
  ]
}
```

### Response

```json
{
  "workflowId": "semantic-search-a3f9b2c1",
  "query": "How do I reset my password?",
  "results": [
    {
      "document": "Steps to update your account password and recover access",
      "similarity": 0.8923,
      "interpretation": "very_similar"
    },
    {
      "document": "Troubleshooting common login and authentication issues",
      "similarity": 0.7234,
      "interpretation": "similar"
    },
    {
      "document": "How to delete your account permanently",
      "similarity": 0.4521,
      "interpretation": "somewhat_similar"
    },
    {
      "document": "Guide to configuring notification preferences",
      "similarity": 0.2893,
      "interpretation": "slightly_similar"
    },
    {
      "document": "Installing the mobile application on your device",
      "similarity": 0.1847,
      "interpretation": "dissimilar"
    }
  ],
  "metadata": {
    "device": "cuda",
    "processingTimeMs": 45.3,
    "embeddingDimension": 384,
    "numDocuments": 5
  }
}
```

## Usage Examples

### Using curl

```bash
curl -X POST http://localhost:5000/semantic-search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I reset my password?",
    "documents": [
      "Steps to update your account password and recover access",
      "Installing the mobile application on your device",
      "Troubleshooting common login and authentication issues",
      "Guide to configuring notification preferences",
      "How to delete your account permanently"
    ]
  }'
```

### Using PowerShell

```powershell
$body = @{
    query = "How do I reset my password?"
    documents = @(
        "Steps to update your account password and recover access",
        "Installing the mobile application on your device",
        "Troubleshooting common login and authentication issues",
        "Guide to configuring notification preferences",
        "How to delete your account permanently"
    )
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri http://localhost:5000/semantic-search `
    -ContentType "application/json" `
    -Body $body
```

### Using Python

```python
import requests
import json

url = "http://localhost:5000/semantic-search"
payload = {
    "query": "How do I reset my password?",
    "documents": [
        "Steps to update your account password and recover access",
        "Installing the mobile application on your device",
        "Troubleshooting common login and authentication issues",
        "Guide to configuring notification preferences",
        "How to delete your account permanently"
    ]
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Query: {result['query']}")
print(f"Device: {result['metadata']['device']}")
print(f"Processing time: {result['metadata']['processingTimeMs']}ms\n")

print("Top results:")
for doc in result['results'][:3]:
    print(f"  {doc['similarity']:.4f} - {doc['document']}")
```

### Using JavaScript/TypeScript

```typescript
const response = await fetch('http://localhost:5000/semantic-search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: "How do I reset my password?",
    documents: [
      "Steps to update your account password and recover access",
      "Installing the mobile application on your device",
      "Troubleshooting common login and authentication issues",
      "Guide to configuring notification preferences",
      "How to delete your account permanently"
    ]
  })
});

const result = await response.json();
console.log('Top result:', result.results[0]);
```

## Real-World Use Cases

### 1. Customer Support Knowledge Base Search

```bash
curl -X POST http://localhost:5000/semantic-search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "My app keeps crashing",
    "documents": [
      "Force quit and restart the application to resolve freezing",
      "Update to the latest version to fix stability issues",
      "Clear app cache to improve performance",
      "Check if your device meets minimum requirements",
      "Enable notifications to receive important updates"
    ]
  }'
```

### 2. Document Discovery

```bash
curl -X POST http://localhost:5000/semantic-search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning deployment strategies",
    "documents": [
      "Best practices for deploying ML models in production environments",
      "Introduction to Python programming for beginners",
      "Scaling microservices with Kubernetes",
      "A/B testing frameworks for ML model evaluation",
      "Database indexing optimization techniques"
    ]
  }'
```

### 3. Content Recommendation

```bash
curl -X POST http://localhost:5000/semantic-search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "User recently viewed: Advanced TypeScript patterns",
    "documents": [
      "Mastering JavaScript design patterns",
      "Building scalable React applications",
      "Complete guide to Python decorators",
      "TypeScript generics and advanced types",
      "Introduction to CSS Grid layout"
    ]
  }'
```

## Testing the Endpoint

### 1. Start the Services

Make sure both .NET and Python services are running with Dapr:

```bash
# Terminal 1: Start Python service
cd python
dapr run --app-id python-workflow-app --app-port 8000 -- python -m src.hello_world_app.main

# Terminal 2: Start .NET service
cd Workflow
dapr run --app-id dotnet-workflow --app-port 5000 -- dotnet run
```

### 2. Send Test Request

```bash
curl -X POST http://localhost:5000/semantic-search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "test query",
    "documents": ["test document 1", "test document 2"]
  }'
```

### 3. Verify GPU Usage (Optional)

If you have a GPU, verify it's being used:

```bash
# Check Python logs for:
# NVIDIA GPU: "Model loaded on device: cuda (NVIDIA GPU: ...)"
# Apple Silicon: "Model loaded on device: mps (Apple Silicon GPU)"
# CPU fallback: "Model loaded on device: cpu (no GPU available)"
```

## Response Fields Explained

| Field | Description |
|-------|-------------|
| `workflowId` | Unique identifier for this workflow execution |
| `query` | The original search query |
| `results[].document` | The document text |
| `results[].similarity` | Cosine similarity score (0-1, higher is more similar) |
| `results[].interpretation` | Human-readable similarity level |
| `metadata.device` | Computation device used (cuda/cpu) |
| `metadata.processingTimeMs` | Total embedding generation time |
| `metadata.embeddingDimension` | Vector dimension (384 for default model) |
| `metadata.numDocuments` | Number of documents searched |

## Similarity Interpretation Guide

| Score Range | Interpretation | Use Case |
|-------------|----------------|----------|
| 0.9 - 1.0 | `very_similar` | Near-duplicate, same topic |
| 0.7 - 0.9 | `similar` | Related content, relevant results |
| 0.5 - 0.7 | `somewhat_similar` | Loosely related, may be useful |
| 0.3 - 0.5 | `slightly_similar` | Weak connection, low relevance |
| 0.0 - 0.3 | `dissimilar` | Unrelated content |

## Performance Expectations

### GPU - NVIDIA (RTX 3080)
- 5 documents: ~10-20ms
- 20 documents: ~15-30ms
- 100 documents: ~50-100ms

### GPU - Apple Silicon (M2)
- 5 documents: ~15-30ms
- 20 documents: ~25-50ms
- 100 documents: ~120-200ms

### CPU (Intel i7-12700K)
- 5 documents: ~50-100ms
- 20 documents: ~150-300ms
- 100 documents: ~800-1500ms

**Note**: First request may be slower (~1-2 seconds) due to model loading.

**Device Used**: Check the `metadata.device` field in the response to see which accelerator was used (`cuda`, `mps`, or `cpu`).

## Error Handling

### Timeout (504)
Workflow took longer than 60 seconds:
```json
{
  "status": 504,
  "title": "Gateway Timeout"
}
```

### Workflow Failure (500)
Python activity error or workflow failure:
```json
{
  "status": 500,
  "title": "Semantic search failed",
  "detail": "Error message here"
}
```

## Monitoring Workflow Status

Get detailed workflow information:

```bash
# Get workflow state (replace with your workflowId)
curl http://localhost:5000/workflow/semantic-search-a3f9b2c1
```

## Next Steps

- **Add caching**: Cache embeddings for frequently searched documents
- **Batch processing**: Process large document sets asynchronously
- **Vector database**: Store embeddings in Pinecone/Weaviate for large-scale search
- **Multi-language**: Use multilingual models for cross-language search
- **Fine-tuning**: Train custom models for domain-specific search

## Troubleshooting

### "Python activity not found"
Ensure the Python service is running and registered with Dapr.

### "CUDA out of memory" or "MPS out of memory"
Reduce the number of documents in a single request or let it fall back to CPU.

### Slow performance
Check if GPU is being used (look for `"device": "cuda"` or `"device": "mps"` in response). If showing `"device": "cpu"`, verify GPU setup.

## Additional Examples

See [GPU_EMBEDDINGS_README.md](GPU_EMBEDDINGS_README.md) for more details on:
- How embeddings work
- Model selection and optimization
- Extending the example
- Production deployment patterns
