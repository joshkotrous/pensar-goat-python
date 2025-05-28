import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: string; // Only action name, not Function
}

// Predefined safe actions
const actions: Record<string, (...args: any[]) => void> = {
  sayHello: () => {
    console.log("Hello from scheduled job!");
  },
  sayTime: () => {
    console.log(`Current time is: ${new Date().toISOString()}`);
  },
};

const jobs: Record<string, JobSpec> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Use JSON schema for safe parsing (no executable tags)
    const spec = yaml.load(req.body, { schema: yaml.JSON_SCHEMA }) as Partial<JobSpec>;

    // Validate basic structure
    if (
      !spec ||
      typeof spec.name !== 'string' ||
      typeof spec.interval !== 'string' ||
      typeof spec.action !== 'string'
    ) {
      return res.status(400).json({ error: "Invalid job specification" });
    }

    // Validate action against allowed list
    if (!actions[spec.action]) {
      return res.status(400).json({ error: "Unknown or unsupported action" });
    }

    jobs[spec.name] = spec as JobSpec;

    // Schedule with predefined safe action
    cron.schedule(spec.interval, () => actions[spec.action]());

    res.json({ ok: true, registered: spec.name });
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

app.get("/run", (req, res) => {
  const name = String(req.query.job ?? "");
  const job = jobs[name];
  if (!job) return res.status(404).json({ error: "unknown job" });

  // Ensure only safe, predefined action is executed
  if (!actions[job.action]) {
    return res.status(500).json({ error: "Invalid action for this job" });
  }
  actions[job.action]();
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));