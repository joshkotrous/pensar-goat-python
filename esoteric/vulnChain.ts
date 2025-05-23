import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: string;
}

type JobHandler = (...args: any[]) => void;

const jobs: Record<string, { name: string; interval: string; action: JobHandler }> = {};

// Define a set of allowed actions the server can perform
const ALLOWED_ACTIONS: { [key: string]: JobHandler } = {
  "logTime": () => console.log("Current time:", new Date().toISOString()),
  // You can add more named functions here as needed, but only safe ones
};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Parse YAML only with the JSON schema (no !!js/function etc)
    const spec = yaml.load(req.body, { schema: yaml.JSON_SCHEMA }) as JobSpec;

    // Validate job spec - only allow known fields and types
    if (
      !spec ||
      typeof spec.name !== "string" ||
      typeof spec.interval !== "string" ||
      typeof spec.action !== "string"
    ) {
      return res.status(400).json({ error: "Invalid job specification" });
    }

    // Only allow predefined action names
    const actionFn = ALLOWED_ACTIONS[spec.action];
    if (!actionFn) {
      return res.status(400).json({ error: "Unknown or unauthorized action" });
    }

    jobs[spec.name] = {
      name: spec.name,
      interval: spec.interval,
      action: actionFn,
    };

    cron.schedule(spec.interval, () => actionFn());

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