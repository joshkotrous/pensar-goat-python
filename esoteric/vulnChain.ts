import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: string; // Now a string key for a known action
}

// Define an allowlist of safe, hardcoded actions
const allowedActions: Record<string, (...args: any[]) => void> = {
  sayHello: () => {
    console.log("Hello from sayHello!");
  },
  printDate: () => {
    console.log("Current date:", new Date().toISOString());
  },
  // Add other safe actions here
};

const jobs: Record<string, JobSpec> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Restrict js-yaml parsing to DEFAULT_SCHEMA to block !!js/function and similar tags
    const spec = yaml.load(req.body, { schema: yaml.DEFAULT_SCHEMA }) as Partial<JobSpec>;

    // Validate shape and structure of the YAML input
    if (
      !spec ||
      typeof spec.name !== "string" ||
      typeof spec.interval !== "string" ||
      typeof spec.action !== "string"
    ) {
      return res.status(400).json({ error: "Invalid job spec structure" });
    }

    // Ensure the action is a key in our allowlist
    if (!(spec.action in allowedActions)) {
      return res.status(400).json({ error: `Unknown action: ${spec.action}` });
    }

    // Prevent duplicate jobs
    if (jobs[spec.name]) {
      return res.status(400).json({ error: "Job name already exists" });
    }

    jobs[spec.name] = {
      name: spec.name,
      interval: spec.interval,
      action: spec.action,
    };

    // Only allow hardcoded actions to be run, not user-supplied functions
    cron.schedule(spec.interval, () => {
      allowedActions[spec.action]();
    });

    res.json({ ok: true, registered: spec.name });
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

app.get("/run", (req, res) => {
  const name = String(req.query.job ?? "");
  const job = jobs[name];
  if (!job) return res.status(404).json({ error: "unknown job" });

  // Only execute whitelisted, server-defined actions
  allowedActions[job.action]();
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));