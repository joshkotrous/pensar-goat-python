import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: string;
}

type JobEntry = {
  name: string;
  interval: string;
  action: () => void;
};

const jobs: Record<string, JobEntry> = {};

// Map of allowed actions. Add more allowed actions as needed.
const ALLOWED_ACTIONS: Record<string, () => void> = {
  // Example safe action(s)
  'logHello': () => { console.log("Hello from scheduled job!"); },
  // Additional safe actions can be registered here.
};

const app = express();
app.use(express.text({ type: "text/plain" }));

// Helper function to validate job spec structure
function validateJobSpec(spec: any): spec is JobSpec {
  if (typeof spec !== 'object' || spec === null) return false;
  if (typeof spec.name !== 'string' || !spec.name.trim()) return false;
  if (typeof spec.interval !== 'string' || !spec.interval.trim()) return false;
  if (typeof spec.action !== 'string' || !(spec.action in ALLOWED_ACTIONS)) return false;
  return true;
}

app.post("/upload", (req, res) => {
  try {
    // Use FAILSAFE_SCHEMA to only parse plain objects and avoid code execution
    const spec = yaml.load(req.body, { schema: yaml.FAILSAFE_SCHEMA });

    if (!validateJobSpec(spec)) {
      return res.status(400).json({ error: "Invalid job spec or unknown action" });
    }

    const jobEntry: JobEntry = {
      name: spec.name,
      interval: spec.interval,
      action: ALLOWED_ACTIONS[spec.action],
    };

    // Remove any old scheduled job for this name
    if (jobs[spec.name]?.__task) {
      jobs[spec.name].__task.stop();
    }

    // Schedule the job
    const task = cron.schedule(jobEntry.interval, () => jobEntry.action());
    // Attach the scheduled task for possible later cleanup (not part of API surface)
    (jobEntry as any).__task = task;

    jobs[jobEntry.name] = jobEntry;

    res.json({ ok: true, registered: jobEntry.name });
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