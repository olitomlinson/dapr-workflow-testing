using Dapr.Workflow;
using WorkflowConsoleApp.Models;

namespace WorkflowConsoleApp.Workflows
{
    /// <summary>
    /// Input payload for semantic search workflow.
    /// </summary>
    public record SemanticSearchInput(
        string Query,
        List<string> Documents
    );

    /// <summary>
    /// Result for a single document's similarity to the query.
    /// </summary>
    public record DocumentScore(
        string Document,
        double Similarity,
        string Interpretation
    );

    /// <summary>
    /// Output from semantic search workflow.
    /// </summary>
    public record SemanticSearchOutput(
        string Query,
        List<DocumentScore> Results,
        string Device,
        double TotalProcessingTimeMs,
        int EmbeddingDimension
    );

    /// <summary>
    /// Workflow demonstrating GPU-accelerated semantic search using Python activities.
    ///
    /// This workflow shows how .NET orchestrates business logic while delegating
    /// GPU-intensive ML computations to Python via Dapr workflow activities.
    /// </summary>
    public class SemanticSearchWorkflow : Workflow<SemanticSearchInput, SemanticSearchOutput>
    {
        public override async Task<SemanticSearchOutput> RunAsync(
            WorkflowContext context,
            SemanticSearchInput input)
        {
            var workflowId = context.InstanceId;
            context.SetCustomStatus($"Starting semantic search for query: '{input.Query}'");

            // Step 1: Generate embedding for the query
            context.SetCustomStatus("Generating query embedding...");

            var queryEmbeddingRequest = new EmbeddingRequest(
                Texts: new List<string> { input.Query },
                Normalize: true
            );

            var queryEmbeddingResponse = await context.CallActivityAsync<EmbeddingResponse>(
                "generate_embeddings",
                queryEmbeddingRequest,
                new WorkflowTaskOptions() { TargetAppId = "python-workflow-app" }
            );

            context.SetCustomStatus(
                $"Query embedding generated on {queryEmbeddingResponse.Device} " +
                $"in {queryEmbeddingResponse.ProcessingTimeMs:F2}ms"
            );

            // Step 2: Generate embeddings for all documents in batch
            context.SetCustomStatus($"Generating embeddings for {input.Documents.Count} documents...");

            var documentsEmbeddingRequest = new EmbeddingRequest(
                Texts: input.Documents,
                Normalize: true
            );

            var documentsEmbeddingResponse = await context.CallActivityAsync<EmbeddingResponse>(
                "generate_embeddings",
                documentsEmbeddingRequest,
                new WorkflowTaskOptions() { TargetAppId = "python-workflow-app" }
            );

            context.SetCustomStatus(
                $"Document embeddings generated on {documentsEmbeddingResponse.Device} " +
                $"in {documentsEmbeddingResponse.ProcessingTimeMs:F2}ms"
            );

            // Step 3: Compute similarity scores for each document
            context.SetCustomStatus("Computing similarity scores...");

            var queryEmbedding = queryEmbeddingResponse.Embeddings[0];
            var results = new List<DocumentScore>();

            for (int i = 0; i < input.Documents.Count; i++)
            {
                var docEmbedding = documentsEmbeddingResponse.Embeddings[i];

                var similarityRequest = new SimilarityRequest(
                    Embeddings1: queryEmbedding,
                    Embeddings2: docEmbedding
                );

                var similarityResponse = await context.CallActivityAsync<SimilarityResponse>(
                    "compute_similarity",
                    similarityRequest,
                    new WorkflowTaskOptions() { TargetAppId = "python-workflow-app" }
                );

                results.Add(new DocumentScore(
                    Document: input.Documents[i],
                    Similarity: similarityResponse.Similarity,
                    Interpretation: similarityResponse.Interpretation
                ));
            }

            // Sort by similarity (highest first)
            results = results.OrderByDescending(r => r.Similarity).ToList();

            var totalTime = queryEmbeddingResponse.ProcessingTimeMs +
                           documentsEmbeddingResponse.ProcessingTimeMs;

            var output = new SemanticSearchOutput(
                Query: input.Query,
                Results: results,
                Device: documentsEmbeddingResponse.Device,
                TotalProcessingTimeMs: totalTime,
                EmbeddingDimension: documentsEmbeddingResponse.Dimension
            );

            context.SetCustomStatus(
                $"Semantic search complete. Best match: '{results[0].Document}' " +
                $"(similarity: {results[0].Similarity:F4})"
            );

            return output;
        }
    }
}
