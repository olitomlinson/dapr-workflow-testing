# dapr-workflow-examples

This is now a repo for helping reproduce and debug various Dapr Workflow issues.

### Run compose as normal

1. `docker compose build`
2. `docker compose up`

### Run compose, but with a local debugger for the Workflow app

1. `docker compose build`
2. `docker compose -f compose.yml -f compose.debug-workflow-app.yml up`
3. in VS Code, Run the launch task `Debug workflow app` to debug the Workflow app

### Run a simple workflow

Run a simple by making a POST request to 

```http://localhost:5112/start?runId={runId}&count=1&async=false```

- Where `{runId}` is a unique value i.e. UUID/GUID.
- Increase the amount of workflows created by changing the `count` property
- `async = false` will use service invocation to invoke the workflow. `async = true` will use PubSub.
