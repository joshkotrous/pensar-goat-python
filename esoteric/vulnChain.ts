import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: string; // Changed from function to string for safety
}

// Holds job handlers by action name for safe execution
const registeredActions: Record<string, (...args: any[]) => void> = {
  "logHello": () => { console.log("Hello from logHello!"); },
  // Add additional safe actions if needed
};

const jobs: Record<string, JobSpec> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Use FAILSAFE_SCHEMA to prevent !!js/function attacks
    const raw = yaml.load(req.body, { schema: yaml.FAILSAFE_SCHEMA }) as any;

    // Validate YAML structure strictly: only accept expected structure and types
    if (
      !raw ||
      typeof raw !== "object" ||
      Array.isArray(raw) ||
      typeof raw.name !== "string" ||
      typeof raw.interval !== "string" ||
      typeof raw.action !== "string"
    ) {
      return res.status(400).json({ error: "Invalid job spec" });
    }

    // Prevent action from being an arbitrary property name (CWE-94 variant); only allow pre-registered actions
    if (!(raw.action in registeredActions)) {
      return res.status(400).json({ error: "Unknown action" });
    }

    const spec: JobSpec = {
      name: raw.name,
      interval: raw.interval,
      action: raw.action
    };

    jobs[spec.name] = spec;

    cron.schedule(spec.interval, () => {
      registeredActions[spec.action]();
    });

    res.json({ ok: true, registered: spec.name });
  } catch (err: any) {
    res.status(400).json({ error: err && err.message ? err.message : "Error parsing YAML/job" });
  }
});

app.get("/run", (req, res) => {
  const name = String(req.query.job ?? "");
  const job = jobs[name];
  if (!job) return res.status(404).json({ error: "unknown job" });

  // Run only registered safe actions
  if (!(job.action in registeredActions)) {
    return res.status(400).json({ error: "Unknown action" });
  }
  registeredActions[job.action]();
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));