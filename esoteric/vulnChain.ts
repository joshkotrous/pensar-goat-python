import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: string;
}

type JobAction = (...args: any[]) => void;

// Define allowed actions in a safe lookup
const SAFE_ACTIONS: Record<string, JobAction> = {
  "say_hello": () => { console.log("Hello from scheduled job!"); },
  // Add more allowed actions here as needed
};

const jobs: Record<string, { spec: JobSpec; runner: JobAction }> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Parse YAML using the fail-safe schema to prohibit !!js/function
    const spec = yaml.load(req.body, { schema: yaml.FAILSAFE_SCHEMA }) as JobSpec;

    // Validate structure
    if (
      typeof spec !== "object" ||
      !spec ||
      typeof spec.name !== "string" ||
      typeof spec.interval !== "string" ||
      typeof spec.action !== "string"
    ) {
      return res.status(400).json({ error: "Invalid job specification" });
    }

    // Only allow predefined safe actions
    const actionFn = SAFE_ACTIONS[spec.action];
    if (!actionFn) {
      return res.status(400).json({ error: "Unknown or unsafe action" });
    }

    // Remove previous job with the same name (if exists)
    if (jobs[spec.name]) {
      // Node-cron doesn't support stopping scheduled tasks easily without keeping reference; this is left minimal for now.
      // In production, we'd store and stop/cleanup previous scheduled jobs.
    }

    // Register the new job
    jobs[spec.name] = { spec, runner: actionFn };

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

  job.runner();
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));