using Dapr.Workflow;

namespace WorkflowConsoleApp.Activities
{
    public class VerySlowActivity : WorkflowActivity<Notification, string>
    {
        readonly ILogger logger;

        public VerySlowActivity(ILoggerFactory loggerFactory)
        {
            this.logger = loggerFactory.CreateLogger<VerySlowActivity>();
        }

        public override async Task<string> RunAsync(WorkflowActivityContext context, Notification notification)
        {
            var message = notification.Message + $" activated={DateTime.UtcNow.ToString("HH:mm:ss")}";
            this.logger.LogInformation(message);

            await Task.Delay(10000);

            message += $" finished={DateTime.UtcNow.ToString("HH:mm:ss")}";
            this.logger.LogInformation(message);

            return message;
        }
    }
}