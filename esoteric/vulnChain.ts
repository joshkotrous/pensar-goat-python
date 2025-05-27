import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

// Allowed set of actions for jobs to execute.
// You can expand this list safely as needed.
const allowedActions: Record<string, (...args: any[]) => void> = {
  "sayHello": () => { console.log("Hello from scheduled job!"); },
  "noop": () => {},
};

interface JobSpec {
  name: string;
  interval: string;
  action: string;
}

const jobs: Record<string, JobSpec> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Restrict YAML load to FAILSAFE_SCHEMA to prevent function injection
    const parsed = yaml.load(req.body, { schema: yaml.FAILSAFE_SCHEMA }) as Record<string, any>;

    // Basic validation
    if (
      typeof parsed !== "object" || parsed === null ||
      typeof parsed.name !== "string" ||
      typeof parsed.interval !== "string" ||
      typeof parsed.action !== "string"
    ) {
      return res.status(400).json({ error: "Invalid JobSpec format" });
    }

    if (!Object.prototype.hasOwnProperty.call(allowedActions, parsed.action)) {
      return res.status(400).json({ error: "Invalid or unauthorized action" });
    }

    const spec: JobSpec = {
      name: parsed.name,
      interval: parsed.interval,
      action: parsed.action,
    };

    jobs[spec.name] = spec;

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

  allowedActions[job.action]();
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));