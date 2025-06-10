import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: (...args: any[]) => void;
}

// Define allowed actions
const allowedActions: Record<string, (...args: any[]) => void> = {
  log: () => {
    console.log("Job executed.");
  },
  // Add more actions as needed, but never allow YAML-defined functions!
};

type UploadJobSpec = {
  name: string;
  interval: string;
  action: string; // action is by name, not function
};

const jobs: Record<string, JobSpec> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Safely parse YAML using JSON_SCHEMA (or FAILSAFE_SCHEMA), which does not support !!js/function
    const parsedSpec = yaml.load(req.body, { schema: yaml.JSON_SCHEMA }) as UploadJobSpec;

    // Basic validation: fields exist and are correct types
    if (
      !parsedSpec ||
      typeof parsedSpec !== "object" ||
      typeof parsedSpec.name !== "string" ||
      typeof parsedSpec.interval !== "string" ||
      typeof parsedSpec.action !== "string"
    ) {
      return res.status(400).json({ error: "Invalid job spec format" });
    }

    // Lookup the action by name; never allow user-defined functions!
    const actionFn = allowedActions[parsedSpec.action];
    if (!actionFn) {
      return res
        .status(400)
        .json({ error: `Unknown or disallowed action: ${parsedSpec.action}` });
    }

    const spec: JobSpec = {
      name: parsedSpec.name,
      interval: parsedSpec.interval,
      action: actionFn,
    };

    jobs[spec.name] = spec;

    cron.schedule(spec.interval, () => spec.action());

    res.json({ ok: true, registered: spec.name });
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

app.get("/run", (req, res) => {
  const name = String(req.query.job ?? "");
  const job = jobs[name];
  if (!job) return res.status(404).json({ error: "unknown job" });

  job.action();
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));