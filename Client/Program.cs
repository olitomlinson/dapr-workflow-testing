using Dapr;
using Dapr.Client;
using Workflow;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddDaprClient();

// Add services to the container.
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.MapPost("/health", async () =>
{

    app.Logger.LogInformation("Hello from Client!");

    return "Hello from Client!!";
});

app.MapPost("/start/monitor-workflow", async (DaprClient daprClient, string runId, int? count, bool? async, int? sleep, string? abortHint) =>
{
    if (!count.HasValue || count.Value < 1)
        count = 1;

    if (!sleep.HasValue)
        sleep = 0;

    var results = new List<StartWorkflowResponse>();

    var cts = new CancellationTokenSource();

    var options = new ParallelOptions() { MaxDegreeOfParallelism = 50, CancellationToken = cts.Token };

    await Parallel.ForEachAsync(Enumerable.Range(0, count.Value), options, async (index, token) =>
    {
        var request = new StartWorkflowRequest
        {
            Id = $"{index}-{runId}",
            Sleep = sleep.Value,
            AbortHint = abortHint
        };

        var metadata = new Dictionary<string, string>
        {
            { "cloudevent.id", request.Id },
            { "cloudevent.type", "Continue As New"} ,
            { "my-custom-property", "foo" },
            { "partitionKey", Guid.NewGuid().ToString() }
        };

        if (async.HasValue && async.Value == true)
        {
            await daprClient.PublishEventAsync("kafka-pubsub", "monitor-workflow", request, metadata, cts.Token);
        }
        else
        {
            var wrappedRequest = new CustomCloudEvent<StartWorkflowRequest>(request)
            {
                Id = request.Id,
            };
            await daprClient.InvokeMethodAsync<CloudEvent<StartWorkflowRequest>, StartWorkflowResponse>("workflow-a", "monitor-workflow", wrappedRequest, cts.Token);
        }
        app.Logger.LogInformation("start Id: {0}", request.Id);

        results.Add(new StartWorkflowResponse { Index = index, Id = request.Id });
    });
    return results;
}).Produces<List<StartWorkflowResponse>>();


app.MapPost("/start-raise-event-workflow", async (DaprClient daprClient, string runId, int? count, bool? failOnTimeout, int? sleep, string? abortHint) =>
{
    if (!count.HasValue || count.Value < 1)
        count = 1;

    if (!sleep.HasValue)
        sleep = 0;

    if (!failOnTimeout.HasValue)
        failOnTimeout = false;

    var results = new List<StartWorkflowResponse>();

    var cts = new CancellationTokenSource();
    var options = new ParallelOptions() { MaxDegreeOfParallelism = 50, CancellationToken = cts.Token };
    await Parallel.ForEachAsync(Enumerable.Range(0, count.Value), options, async (index, token) =>
    {
        var request = new StartWorkflowRequest
        {
            Id = $"{index}-{runId}",
            Sleep = sleep.Value,
            AbortHint = abortHint,
            FailOnTimeout = failOnTimeout.Value
        };

        await daprClient.PublishEventAsync<StartWorkflowRequest>("kafka-pubsub", "start-raise-event-workflow", request, cts.Token);

        app.Logger.LogInformation("start-raise-event-workflow Id: {0}", request.Id);

        results.Add(new StartWorkflowResponse { Index = index, Id = request.Id });
    });
    return results;
}).Produces<List<StartWorkflowResponse>>();


app.MapPost("/start/fanout-workflow", async (DaprClient daprClient, string runId, int? count, bool? async, int? sleep, string? abortHint) =>
{
    if (!count.HasValue || count.Value < 1)
        count = 1;

    if (!sleep.HasValue)
        sleep = 0;

    var results = new List<StartWorkflowResponse>();

    var cts = new CancellationTokenSource();

    var options = new ParallelOptions() { MaxDegreeOfParallelism = 50, CancellationToken = cts.Token };

    await Parallel.ForEachAsync(Enumerable.Range(0, count.Value), options, async (index, token) =>
    {
        var request = new StartWorkflowRequest
        {
            Id = $"{index}-{runId}",
            Sleep = sleep.Value,
            AbortHint = abortHint
        };

        if (async.HasValue && async.Value == true)
            await daprClient.PublishEventAsync<StartWorkflowRequest>("kafka-pubsub", "fanout-workflow", request, cts.Token);
        else
        {
            var wrappedRequest = new CustomCloudEvent<StartWorkflowRequest>(request)
            {
                Id = request.Id,
            };
            await daprClient.InvokeMethodAsync<CustomCloudEvent<StartWorkflowRequest>, StartWorkflowResponse>("workflow-a", "fanout-workflow", wrappedRequest, cts.Token);
        }
        app.Logger.LogInformation("start Id: {0}", request.Id);

        results.Add(new StartWorkflowResponse { Index = index, Id = request.Id });
    });
    return results;
}).Produces<List<StartWorkflowResponse>>();


app.MapPost("/start/schedule-job", async (DaprClient daprClient, string runId, int? count, bool? async, int? sleep, string? abortHint) =>
{
    if (!count.HasValue || count.Value < 1)
        count = 1;

    if (!sleep.HasValue)
        sleep = 0;

    var results = new List<StartWorkflowResponse>();

    var cts = new CancellationTokenSource();

    var options = new ParallelOptions() { MaxDegreeOfParallelism = 50, CancellationToken = cts.Token };

    await Parallel.ForEachAsync(Enumerable.Range(0, count.Value), options, async (index, token) =>
    {
        var request = new StartWorkflowRequest
        {
            Id = $"{index}-{runId}",
            Sleep = sleep.Value,
            AbortHint = abortHint
        };

        if (async.HasValue && async.Value == true)
            await daprClient.PublishEventAsync<StartWorkflowRequest>("kafka-pubsub", "schedule-job", request, cts.Token);
        else
        {
            var wrappedRequest = new CustomCloudEvent<StartWorkflowRequest>(request)
            {
                Id = request.Id,
            };
            await daprClient.InvokeMethodAsync<CustomCloudEvent<StartWorkflowRequest>, StartWorkflowResponse>("workflow-a", "fanout-workflow", wrappedRequest, cts.Token);
        }
        app.Logger.LogInformation("start Id: {0}", request.Id);

        results.Add(new StartWorkflowResponse { Index = index, Id = request.Id });
    });
    return results;
}).Produces<List<StartWorkflowResponse>>();



app.Run();

public class StartWorkflowRequest
{
    public string Id { get; set; }
    public bool FailOnTimeout { get; set; }
    public int Sleep { get; set; }
    public string AbortHint { get; set; }
}

public class StartWorkflowResponse
{
    public int Index { get; set; }
    public string Id { get; set; }
}

public class RaiseEvent<T>
{
    public string InstanceId { get; set; }
    public string EventName { get; set; }
    public T EventData { get; set; }
}
