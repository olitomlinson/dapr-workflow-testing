using System.Text;
using Dapr.Workflow;
using WorkflowConsoleApp.Activities;

namespace WorkflowConsoleApp.Workflows
{
    public class ExternalSystemWorkflow : Workflow<ExternalSystemWorkflowPayload, Dictionary<string, int>>
    {
        public override async Task<Dictionary<string, int>> RunAsync(WorkflowContext context, ExternalSystemWorkflowPayload payload)
        {
            var cts = new CancellationTokenSource();

            Task timeout = context.CreateTimer(TimeSpan.FromSeconds(30), cts.Token);

            List<Task<string>> results = new List<Task<string>>();

            for (int i = 0; i < 1000; i++)
            {
                results.Add(context.WaitForExternalEventAsync<string>("wait-event"));
            }

            // WhenAll == AND(x, y, z, a, b)
            var externalEvents = Task.WhenAll(results);

            // WhenAny == XOR(x, y)
            var winner = await Task.WhenAny(externalEvents, timeout);

            Dictionary<string, int> receivedEvents = new Dictionary<string, int>();

            if (winner == externalEvents)
            {
                cts.Cancel();
                foreach (var result in results)
                {
                    if (!receivedEvents.TryAdd(result.Result, 1))
                    {
                        var count = receivedEvents[result.Result];
                        receivedEvents[result.Result] = count += 1;
                    }
                }

                return receivedEvents;
            }
            else if (winner == timeout)
            {
                var sb = new StringBuilder();
                sb.Append("Events status : ");
                foreach (var result in results)
                {
                    sb.AppendLine(result.Status.ToString());
                }

                if (payload.failOnTimeout)
                    throw new Exception($"Workflow Timed out after 30 seconds : {receivedEvents}");
                else
                {
                    receivedEvents.Add("FAILED ON TIMEOUT", 0);
                    return receivedEvents;
                }
            }

            return null;
        }
    }
}
