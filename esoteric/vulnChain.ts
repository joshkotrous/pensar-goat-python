import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: string; // Change: now a string key for a safe, predefined action
}

// Define allowed (safe) actions, not user-provided functions
const ALLOWED_ACTIONS: Record<string, () => void> = {
  "sayHello": () => { console.log("Hello from scheduled job!"); },
  "sayTime": () => { console.log("Current time is:", new Date().toISOString()); },
  // ... Add more permitted actions here
};

const jobs: Record<string, JobSpec> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    const spec = yaml.load(req.body, { schema: yaml.FAILSAFE_SCHEMA }) as Partial<JobSpec>;

    // Basic shape/type validation
    if (
      !spec ||
      typeof spec.name !== "string" ||
      typeof spec.interval !== "string" ||
      typeof spec.action !== "string"
    ) {
      return res.status(400).json({ error: "Invalid job spec" });
    }

    if (!(spec.action in ALLOWED_ACTIONS)) {
      return res.status(400).json({ error: "Action not allowed" });
    }

    jobs[spec.name] = {
      name: spec.name,
      interval: spec.interval,
      action: spec.action,
    };

    cron.schedule(
      spec.interval,
      () => ALLOWED_ACTIONS[spec.action]?.(),
      { name: spec.name }
    );

    res.json({ ok: true, registered: spec.name });
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

app.get("/run", (req, res) => {
  const name = String(req.query.job ?? "");
  const job = jobs[name];
  if (!job) return res.status(404).json({ error: "unknown job" });
  if (!(job.action in ALLOWED_ACTIONS)) {
    return res.status(400).json({ error: "Unknown or disallowed action" });
  }

  ALLOWED_ACTIONS[job.action]?.();
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));