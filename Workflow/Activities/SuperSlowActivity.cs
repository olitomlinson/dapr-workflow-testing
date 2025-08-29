using Dapr.Workflow;

namespace WorkflowConsoleApp.Activities
{
    public class SuperSlowActivity : WorkflowActivity<Notification, string>
    {
        readonly ILogger logger;

        public SuperSlowActivity(ILoggerFactory loggerFactory)
        {
            this.logger = loggerFactory.CreateLogger<SuperSlowActivity>();
        }

        public override async Task<string> RunAsync(WorkflowActivityContext context, Notification notification)
        {
            var message = notification.Message + $" activated={DateTime.UtcNow.ToString("HH:mm:ss")}";
            this.logger.LogInformation(message);

            await Task.Delay(60000);

            message += $" finished={DateTime.UtcNow.ToString("HH:mm:ss")}";
            this.logger.LogInformation(message);

            return message;
        }
    }
}