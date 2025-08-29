using Dapr.Workflow;

namespace WorkflowConsoleApp.Activities
{
    public class SlowActivity : WorkflowActivity<Notification, string>
    {
        readonly ILogger logger;

        public SlowActivity(ILoggerFactory loggerFactory)
        {
            this.logger = loggerFactory.CreateLogger<SlowActivity>();
        }

        public override async Task<string> RunAsync(WorkflowActivityContext context, Notification notification)
        {
            var message = notification.Message + $" activated={DateTime.UtcNow.ToString("HH:mm:ss")}";
            this.logger.LogInformation(message);

            await Task.Delay(3000);

            message += $" finished={DateTime.UtcNow.ToString("HH:mm:ss")}";
            this.logger.LogInformation(message);

            return message;
        }
    }
}