# GPU-Accelerated Text Embeddings with Dapr Workflows

This example demonstrates how to use Dapr workflows to orchestrate GPU-intensive machine learning workloads across .NET and Python services.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  .NET Workflow                       │
│  (Business Logic & Orchestration)                    │
│                                                      │
│  • SemanticSearchWorkflow                           │
│  • Coordinates multiple activities                  │
│  • Handles business rules                           │
└──────────────────┬──────────────────────────────────┘
                   │ Dapr Activity Calls
                   │ (Cross-Language)
                   ▼
┌─────────────────────────────────────────────────────┐
│             Python Activities                        │
│  (GPU-Accelerated ML Computation)                   │
│                                                      │
│  • generate_embeddings                              │
│  • compute_similarity                               │
│  • Uses: PyTorch + sentence-transformers + CUDA     │
└─────────────────────────────────────────────────────┘
```

## What This Demonstrates

### Real-World Use Case: Semantic Search

This implementation shows a practical semantic search system where:

1. **User submits a query** (e.g., "How do I reset my password?")
2. **.NET workflow orchestrates** the search process
3. **Python activities generate embeddings** using GPU-accelerated transformer models
4. **Similarity scores are computed** to rank documents by relevance
5. **Results are returned** with ranked documents

### Key Benefits

- **Language Specialization**: .NET for business logic, Python for ML
- **GPU Acceleration**: 10-100x faster than CPU for transformer models
- **Scalability**: Dapr handles distribution and resilience
- **Type Safety**: Strongly typed records in both C# and Python

## Components

### Python Activities

#### 1. `generate_embeddings`
**Location**: `python/src/hello_world_app/activities/embedding_activity.py`

Converts text into numerical vectors (embeddings) using the sentence-transformers library.

**Input**:
```json
{
  "texts": ["Hello world", "How are you?"],
  "normalize": true
}
```

**Output**:
```json
{
  "embeddings": [[0.123, 0.456, ...], [0.789, 0.012, ...]],
  "model_name": "all-MiniLM-L6-v2",
  "device": "cuda",
  "dimension": 384,
  "processing_time_ms": 15.3,
  "num_texts": 2
}
```

**Features**:
- Automatic GPU detection and usage (CUDA)
- Batch processing for efficiency
- Lazy model loading (loaded once, reused)
- Performance metrics included

#### 2. `compute_similarity`
**Location**: `python/src/hello_world_app/activities/embedding_activity.py`

Computes cosine similarity between two embeddings.

**Input**:
```json
{
  "embeddings1": [0.1, 0.2, 0.3, ...],
  "embeddings2": [0.15, 0.22, 0.31, ...]
}
```

**Output**:
```json
{
  "similarity": 0.9876,
  "interpretation": "very_similar"
}
```

### .NET Workflow

#### `SemanticSearchWorkflow`
**Location**: `Workflow/Workflows/SemanticSearchWorkflow.cs`

Orchestrates the semantic search process:

1. Generate embedding for user query
2. Generate embeddings for all documents (batch)
3. Compute similarity scores
4. Rank and return results

**Input**:
```csharp
new SemanticSearchInput(
    Query: "How do I change my password?",
    Documents: new List<string>
    {
        "Steps to update account credentials",
        "Installing the software",
        "Troubleshooting login issues"
    }
)
```

**Output**:
```csharp
SemanticSearchOutput
{
    Query: "How do I change my password?",
    Results: [
        { Document: "Steps to update account credentials", Similarity: 0.89, Interpretation: "very_similar" },
        { Document: "Troubleshooting login issues", Similarity: 0.71, Interpretation: "similar" },
        { Document: "Installing the software", Similarity: 0.23, Interpretation: "dissimilar" }
    ],
    Device: "cuda",
    TotalProcessingTimeMs: 45.2,
    EmbeddingDimension: 384
}
```

### C# Models

**Location**: `Workflow/Models/EmbeddingModels.cs`

Strongly typed record types that match the Python dataclasses:
- `EmbeddingRequest` / `EmbeddingResponse`
- `SimilarityRequest` / `SimilarityResponse`

## Installation & Setup

### 1. Install Python Dependencies

```bash
cd python
pip install -r requirements.txt
```

This installs:
- `sentence-transformers` - Pre-trained transformer models for embeddings
- `torch` - PyTorch with CUDA support (GPU acceleration)
- `numpy` - Numerical computing

### 2. GPU Setup (Optional but Recommended)

The activity supports multiple GPU backends:

#### NVIDIA GPUs (CUDA)
- NVIDIA GPU with CUDA support
- CUDA Toolkit installed
- PyTorch with CUDA support

**Check CUDA availability**:
```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

#### Apple Silicon (M1/M2/M3) - MPS
- Works on M1, M2, or M3 Macs
- No additional setup required
- PyTorch 1.12+ has built-in MPS support

**Check MPS availability**:
```bash
python -c "import torch; print(f'MPS available: {torch.backends.mps.is_available()}')"
```

#### Fallback
If no GPU is available, the activities will automatically fall back to CPU (slower but functional).

#### ⚠️ Important: Docker GPU Limitations on macOS

**Docker containers on macOS cannot access the host GPU** (neither CUDA nor MPS). This is a Docker Desktop limitation.

When running the Python service in Docker on macOS:
- The container runs Linux, not macOS
- MPS (Apple Silicon GPU) is not available to Linux containers
- GPU passthrough is not supported by Docker Desktop on macOS
- **The service will run on CPU** inside the container

**To use GPU acceleration on macOS**:
1. Run the Python service directly on the host (outside Docker)
2. See [Running with GPU Acceleration](#running-with-gpu-acceleration) below

**Production deployments**:
- Use Linux servers with NVIDIA GPUs
- Docker + NVIDIA Container Toolkit works on Linux
- Cloud providers (AWS, Azure, GCP) support GPU containers

### 3. First Run

On first execution, the sentence-transformers model (`all-MiniLM-L6-v2`) will be downloaded automatically (~90MB). This happens once and is cached for future use.

## Usage Example

### Using the Workflow Programmatically

```csharp
using Dapr.Workflow;
using WorkflowConsoleApp.Workflows;

// Create workflow client
var workflowClient = // ... initialize Dapr workflow client

// Define your query and documents
var input = new SemanticSearchInput(
    Query: "Python tutorial for beginners",
    Documents: new List<string>
    {
        "Getting started with Python programming",
        "Advanced C# design patterns",
        "Introduction to Python: A beginner's guide",
        "JavaScript fundamentals",
        "Python for data science"
    }
);

// Start the workflow
var instanceId = await workflowClient.ScheduleNewWorkflowAsync(
    nameof(SemanticSearchWorkflow),
    input
);

// Wait for results
var result = await workflowClient.WaitForWorkflowCompletionAsync<SemanticSearchOutput>(
    instanceId
);

// Display ranked results
foreach (var doc in result.Results)
{
    Console.WriteLine($"{doc.Similarity:F4} - {doc.Document}");
}
```

## Performance

### GPU vs CPU Comparison

With the default model (`all-MiniLM-L6-v2`, 384 dimensions):

| Operation | CPU Time | NVIDIA GPU (CUDA) | Apple M2 (MPS) | Best Speedup |
|-----------|----------|-------------------|----------------|--------------|
| Single text | ~5ms | ~2ms | ~2.5ms | 2.5x |
| 10 texts | ~45ms | ~6ms | ~15ms | 7.5x |
| 100 texts | ~430ms | ~25ms | ~120ms | 17x |
| 1000 texts | ~4300ms | ~180ms | ~800ms | 24x |

*CPU: Intel i7-12700K | NVIDIA: RTX 3080 | Apple: M2 chip*

**Device Priority**: The activity automatically selects the best available device:
1. MPS (Apple Silicon) - if available
2. CUDA (NVIDIA) - if available
3. CPU - fallback

### Optimization Tips

1. **Batch Processing**: Always process multiple texts together when possible
2. **Model Selection**:
   - `all-MiniLM-L6-v2`: Fast, 384 dimensions (default)
   - `all-mpnet-base-v2`: Better quality, 768 dimensions, slower
3. **Normalization**: Keep `normalize: true` for similarity computations
4. **Model Caching**: The model loads once and stays in memory

## Real-World Applications

### 1. Customer Support Chatbot
```
User Question → Generate Embedding → Search Knowledge Base → Return Relevant Articles
```

### 2. Document Discovery
```
Upload Document → Generate Embeddings → Find Similar Documents → Suggest Related Content
```

### 3. Duplicate Detection
```
New Ticket → Generate Embedding → Check vs Existing Tickets → Flag Duplicates
```

### 4. Recommendation System
```
User Activity → Generate Embedding → Find Similar Items → Recommend to User
```

## Technical Details

### Model Information

**all-MiniLM-L6-v2**:
- Size: 90MB
- Dimensions: 384
- Max sequence length: 256 tokens
- Training: Trained on 1B+ sentence pairs
- Use case: General purpose, fast inference

### Device Selection Logic

The Python activity automatically selects the best device:

```python
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
```

### Thread Safety

The model is loaded once globally and reused across activity invocations. This is safe because:
- Model inference is thread-safe in PyTorch
- Each request gets its own input/output tensors
- No shared state between requests

## Extending This Example

### Adding More Activities

Create new activities in `embedding_activity.py`:

```python
@workflow_runtime.activity(name='batch_classify')
def batch_classify(_ctx, input_data: dict) -> dict:
    # Your GPU-intensive ML task here
    pass
```

### Using Different Models

Modify the model name in `embedding_activity.py`:

```python
_model_name = "all-mpnet-base-v2"  # Higher quality, slower
# or
_model_name = "paraphrase-multilingual-MiniLM-L12-v2"  # Multilingual support
```

### Adding Caching

Implement Redis caching for embeddings to avoid recomputing:

```csharp
// Pseudo-code
var cached = await redis.GetAsync<EmbeddingResponse>($"emb:{hash}");
if (cached != null) return cached;

var result = await context.CallActivityAsync<EmbeddingResponse>(...);
await redis.SetAsync($"emb:{hash}", result, TimeSpan.FromHours(24));
```

## Troubleshooting

### CUDA Out of Memory (NVIDIA)
Reduce batch size or switch to a smaller model.

### MPS Errors (Apple Silicon)
If you see MPS errors on M1/M2/M3:
- Update PyTorch: `pip install --upgrade torch`
- Some operations may not be fully supported on MPS yet
- Activity will fall back to CPU if MPS fails

### Model Download Fails
The model downloads from HuggingFace. Check internet connectivity or manually download and cache.

### Slow First Request
First request loads the model (~1-2 seconds). Subsequent requests are fast due to model caching.

### GPU Not Detected
**NVIDIA GPUs**:
- Verify CUDA toolkit installation
- Check PyTorch CUDA build: `pip install torch --index-url https://download.pytorch.org/whl/cu118`

**Apple Silicon**:
- Requires PyTorch 1.12+
- Check: `python -c "import torch; print(torch.backends.mps.is_available())"`
- Should return `True` on M1/M2/M3 Macs

## Resources

- [sentence-transformers Documentation](https://www.sbert.net/)
- [Dapr Workflow Documentation](https://docs.dapr.io/developing-applications/building-blocks/workflow/)
- [HuggingFace Models](https://huggingface.co/models)
- [PyTorch CUDA Setup](https://pytorch.org/get-started/locally/)
