using System.Text.Json.Serialization;

namespace WorkflowConsoleApp.Models
{
    /// <summary>
    /// Request for text embedding generation from Python activity.
    /// </summary>
    public record EmbeddingRequest(
        [property: JsonPropertyName("texts")] List<string> Texts,
        [property: JsonPropertyName("normalize")] bool Normalize = true
    );

    /// <summary>
    /// Response containing embeddings and performance metrics from Python activity.
    /// </summary>
    public record EmbeddingResponse(
        [property: JsonPropertyName("embeddings")] List<List<double>> Embeddings,
        [property: JsonPropertyName("model_name")] string ModelName,
        [property: JsonPropertyName("device")] string Device,
        [property: JsonPropertyName("dimension")] int Dimension,
        [property: JsonPropertyName("processing_time_ms")] double ProcessingTimeMs,
        [property: JsonPropertyName("num_texts")] int NumTexts
    );

    /// <summary>
    /// Request for computing similarity between two embeddings.
    /// </summary>
    public record SimilarityRequest(
        [property: JsonPropertyName("embeddings1")] List<double> Embeddings1,
        [property: JsonPropertyName("embeddings2")] List<double> Embeddings2
    );

    /// <summary>
    /// Response containing similarity score and interpretation.
    /// </summary>
    public record SimilarityResponse(
        [property: JsonPropertyName("similarity")] double Similarity,
        [property: JsonPropertyName("interpretation")] string Interpretation
    );
}
