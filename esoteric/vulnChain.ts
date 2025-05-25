import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: string; // Now action is a string (action identifier)
}

type ActionFn = (...args: any[]) => void;

// Whitelist of allowed action functions by name
const allowedActions: Record<string, ActionFn> = {
  say_hello: () => {
    console.log("Hello from job!");
  },
  // Add more allowed action mappings here.
};

const jobs: Record<string, JobSpec> = {};

// Maps job name to its cron task instance for future management (not strictly necessary, but often useful)
const cronTasks: Record<string, cron.ScheduledTask> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Use safeLoad to prevent function/executable deserialization
    const spec = yaml.safeLoad(req.body) as Partial<JobSpec>;

    // Basic structural validation
    if (
      !spec ||
      typeof spec.name !== "string" ||
      typeof spec.interval !== "string" ||
      typeof spec.action !== "string"
    ) {
      return res.status(400).json({ error: "Invalid job specification." });
    }

    // Check that action exists and is whitelisted
    const actionFn = allowedActions[spec.action];
    if (!actionFn) {
      return res.status(400).json({ error: "Unknown or unsupported action." });
    }

    // Clean up any old cron tasks for this name
    if (cronTasks[spec.name]) {
      cronTasks[spec.name].stop();
      delete cronTasks[spec.name];
    }

    // Store job spec safely
    jobs[spec.name] = {
      name: spec.name,
      interval: spec.interval,
      action: spec.action,
    };

    // Schedule cron using the whitelisted action, not user input code
    const task = cron.schedule(spec.interval, () => actionFn());
    cronTasks[spec.name] = task;

    res.json({ ok: true, registered: spec.name });
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

app.get("/run", (req, res) => {
  const name = String(req.query.job ?? "");
  const job = jobs[name];
  if (!job) return res.status(404).json({ error: "unknown job" });

  const actionFn = allowedActions[job.action];
  if (!actionFn) return res.status(500).json({ error: "action not available" });

  actionFn();
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));