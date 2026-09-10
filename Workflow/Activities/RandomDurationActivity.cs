using Dapr.Workflow;
using Google.Protobuf.WellKnownTypes;

namespace WorkflowConsoleApp.Activities
{
    public class RandomDurationActivity : WorkflowActivity<Notification, string>
    {
        readonly ILogger logger;

        public RandomDurationActivity(ILoggerFactory loggerFactory)
        {
            this.logger = loggerFactory.CreateLogger<RandomDurationActivity>();
        }

        public override async Task<string> RunAsync(WorkflowActivityContext context, Notification notification)
        {
            Random rnd = new Random();
            int delay = rnd.Next(10, 61);
            var message = notification.Message + $" activated={DateTime.UtcNow.ToString("HH:mm:ss")} waiting for {delay}s";
            this.logger.LogInformation(message);

            await Task.Delay(delay * 1000);

            message += $" finished={DateTime.UtcNow.ToString("HH:mm:ss")}";
            this.logger.LogInformation(message);

            return message;
        }
    }
}