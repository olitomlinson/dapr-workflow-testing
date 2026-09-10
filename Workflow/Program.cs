using Dapr.Workflow;
using Dapr;
using Dapr.Client;
using workflow;


var builder = WebApplication.CreateBuilder(args);
bool registerWorkflows = Convert.ToBoolean(Environment.GetEnvironmentVariable("REGISTER_WORKFLOWS"));
bool registerActivities = Convert.ToBoolean(Environment.GetEnvironmentVariable("REGISTER_ACTIVITIES"));

builder.Services.AddHttpClient();
builder.Services.AddDaprClient();

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Health endpoint status code control
int healthStatusCode = 200;
int monitorStatusCode = 200;

//app.UseCloudEvents();
app.MapSubscribeHandler();

app.Logger.LogInformation("REGISTER_WORKFLOWS: " + registerWorkflows);
app.Logger.LogInformation("REGISTER_ACTIVITIES: " + registerActivities);
app.Logger.LogInformation("DAPR_HTTP_PORT: " + Environment.GetEnvironmentVariable("DAPR_HTTP_PORT"));
app.Logger.LogInformation("DAPR_GRPC_PORT: " + Environment.GetEnvironmentVariable("DAPR_GRPC_PORT"));
// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}


app.MapPost("/monitor-workflow", [Topic(pubsubName: "kafka-pubsub", name: "monitor-workflow", enableRawPayload: false)] async (CustomCloudEvent<StartWorklowRequest>? ce, HttpContext context) =>
{
    app.Logger.LogInformation($"ACTIVATED {ce.Data.Id} : Response Status code: {monitorStatusCode}");
    context.Response.StatusCode = monitorStatusCode;
    return $"monitor response is : {monitorStatusCode}";

});

app.MapGet("/health", async (HttpContext context) =>
{
    app.Logger.LogInformation("Health - Status code: {statusCode}", healthStatusCode);
    context.Response.StatusCode = healthStatusCode;
    return $"monitor response is : {monitorStatusCode}";
});

app.MapPost("/health/status", (int statusCode) =>
{
    healthStatusCode = statusCode;
    app.Logger.LogInformation("Health endpoint status code changed to {statusCode}", statusCode);
    return new { message = "Health status code updated", statusCode = healthStatusCode };
});


app.MapPost("/monitor/status", (int statusCode) =>
{
    monitorStatusCode = statusCode;
    app.Logger.LogInformation("montitor endpoint status code changed to {statusCode}", statusCode);
    return new { message = "monitor status code updated", statusCode = monitorStatusCode };
});

app.Run();

public record WorkflowPayload(string RandomData, int Itterations = 1, Guid[]? Data = default);

public record ExternalSystemWorkflowPayload(bool failOnTimeout = false);


public class StartWorklowRequest
{
    public string Id { get; set; }
    public bool FailOnTimeout { get; set; }
    public int Sleep { get; set; }
    public string AbortHint { get; set; }
}


