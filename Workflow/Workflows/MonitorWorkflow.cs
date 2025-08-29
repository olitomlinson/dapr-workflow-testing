using Dapr.Workflow;
using WorkflowConsoleApp.Activities;

namespace WorkflowConsoleApp.Workflows
{
    public class MonitorWorkflow : Workflow<WorkflowPayload, bool>
    {
        public override async Task<bool> RunAsync(WorkflowContext context, WorkflowPayload payload)
        {
            string workflowId = context.InstanceId;

            var result = await context.CallActivityAsync<string>(
                nameof(SlowActivity),
                new Notification($"{workflowId} - {nameof(SlowActivity)} #{payload.Itterations} - scheduled={DateTime.UtcNow.ToString("HH:mm:ss")}", payload.Data));

            await context.CreateTimer(TimeSpan.FromSeconds(3));

            var newWorkflowPayload = new WorkflowPayload(
                payload.RandomData,
                payload.Itterations - 1,
                null
            );

            if (newWorkflowPayload.Itterations == 0)
                return true;

            context.ContinueAsNew(newWorkflowPayload);
            return false;
        }
    }
}
