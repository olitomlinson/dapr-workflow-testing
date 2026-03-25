using Dapr.Workflow;
using WorkflowConsoleApp.Activities;

namespace WorkflowConsoleApp.Workflows
{
    public class FanOutWorkflow : Workflow<WorkflowPayload, IEnumerable<string>>
    {
        public override async Task<IEnumerable<string>> RunAsync(WorkflowContext context, WorkflowPayload payload)
        {
            var fanOut = new List<Task<string>>();

            for (int i = 0; i < payload.Itterations; i++)
            {
                fanOut.Add(context.CallActivityAsync<string>(nameof(SuperSlowActivity), new Activities.Notification($"{context.InstanceId} - {nameof(SuperSlowActivity)} (1) #{i} - scheduled={context.CurrentUtcDateTime.ToString("HH:mm:ss")}")));
            }

            await Task.WhenAll(fanOut);

            return fanOut.Select(x => x.Result);
        }
    }
}
