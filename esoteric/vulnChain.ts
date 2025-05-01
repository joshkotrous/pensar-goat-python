import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: string;
}

// Define a registry of allowed actions (functions) by name
const allowedActions: Record<string, (...args: any[]) => void> = {
  "sayHello": () => { console.log("Hello from scheduled job!"); },
  // Add more allowed actions as needed
};

const jobs: Record<string, JobSpec> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Parse YAML with DEFAULT_SCHEMA (safe, no !!js/function allowed)
    const spec = yaml.load(req.body, { schema: yaml.DEFAULT_SCHEMA }) as any;

    // Strict validation of input
    if (
      !spec ||
      typeof spec !== "object" ||
      typeof spec.name !== "string" ||
      typeof spec.interval !== "string" ||
      typeof spec.action !== "string"
    ) {
      return res.status(400).json({ error: "Invalid job spec: job must be an object with string fields 'name', 'interval', and 'action'" });
    }

    // Check action is in allowed actions
    const actionFunc = allowedActions[spec.action];
    if (typeof actionFunc !== "function") {
      return res.status(400).json({ error: "Unknown or disallowed action" });
    }

    // Store sanitized job
    jobs[spec.name] = {
      name: spec.name,
      interval: spec.interval,
      action: spec.action,
    };

    cron.schedule(spec.interval, () => actionFunc());

    res.json({ ok: true, registered: spec.name });
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

app.get("/run", (req, res) => {
  const name = String(req.query.job ?? "");
  const job = jobs[name];
  if (!job) return res.status(404).json({ error: "unknown job" });

  // Lookup allowed function again
  const actionFunc = allowedActions[job.action];
  if (typeof actionFunc !== "function") {
    return res.status(500).json({ error: "registered job action is no longer valid" });
  }
  actionFunc();
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));