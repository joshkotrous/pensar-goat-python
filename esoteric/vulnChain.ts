import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

// Define a whitelist of allowed actions
const allowedActions: Record<string, (...args: any[]) => void> = {
  hello: () => {
    console.log("Hello, world!");
  },
  time: () => {
    console.log("Current time:", new Date().toISOString());
  },
  // Add other allowed actions here as needed
};

interface JobSpec {
  name: string;
  interval: string;
  action: string; // changed from (...args: any[]) => void to string
}

const jobs: Record<string, JobSpec> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Only allow safe schemas (disallows !!js/function, etc.)
    const spec = yaml.load(req.body, { schema: yaml.FAILSAFE_SCHEMA }) as Partial<JobSpec>;

    if (!spec || typeof spec !== "object") {
      return res.status(400).json({ error: "Invalid YAML structure." });
    }
    if (typeof spec.name !== "string" || !spec.name.trim()) {
      return res.status(400).json({ error: "Missing or invalid job name." });
    }
    if (typeof spec.interval !== "string" || !spec.interval.trim()) {
      return res.status(400).json({ error: "Missing or invalid interval." });
    }
    if (typeof spec.action !== "string" || !allowedActions[spec.action]) {
      return res.status(400).json({ error: "Invalid or unknown action." });
    }

    // All validations passed, store job
    const jobSpec: JobSpec = {
      name: spec.name,
      interval: spec.interval,
      action: spec.action,
    };

    jobs[jobSpec.name] = jobSpec;

    // Schedule the job with the mapped safe action function
    cron.schedule(jobSpec.interval, () => {
      allowedActions[jobSpec.action]();
    });

    res.json({ ok: true, registered: jobSpec.name });
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

app.get("/run", (req, res) => {
  const name = String(req.query.job ?? "");
  const job = jobs[name];
  if (!job) return res.status(404).json({ error: "unknown job" });
  const fn = allowedActions[job.action];
  if (!fn) return res.status(500).json({ error: "Job action not found" });

  fn();
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));