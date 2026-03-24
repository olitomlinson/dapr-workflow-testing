using Dapr.Workflow;
using WorkflowConsoleApp.Activities;

namespace WorkflowConsoleApp.Workflows
{
    public class MonitorWorkflow : Workflow<WorkflowPayload, bool>
    {
        public override async Task<bool> RunAsync(WorkflowContext context, WorkflowPayload payload)
        {
            await Task.Delay(TimeSpan.FromDays(1));
            //await context.CallActivityAsync<string>(nameof(SuperSlowActivity), new Activities.Notification($"{context.InstanceId} - {nameof(SuperSlowActivity)} (1) # - scheduled={DateTime.UtcNow.ToString("HH:mm:ss")}"));
            //await context.CreateTimer(TimeSpan.FromHours(1));

            return false;
        }
    }
}
