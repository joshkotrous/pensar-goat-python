import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

// Define a set of allowed actions for job steps
const ALLOWED_ACTIONS = {
  ping: () => { /* no-op, can be extended */ },
  log: () => { console.log("Job triggered"); },
  // Add more allowed actions as needed
};

interface JobSpec {
  name: string;
  interval: string;
  action: string; // Now a string key, not a function
}

const jobs: Record<string, JobSpec> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Use safeLoad instead of load to prevent unsafe YAML tags
    const spec = yaml.safeLoad(req.body) as any;

    // Basic input validation
    if (
      !spec ||
      typeof spec !== "object" ||
      typeof spec.name !== "string" ||
      !spec.name.trim() ||
      typeof spec.interval !== "string" ||
      typeof spec.action !== "string"
    ) {
      throw new Error("Invalid spec");
    }

    // Prevent prototype pollution
    if (["__proto__", "constructor", "prototype"].includes(spec.name)) {
      throw new Error("Reserved job name");
    }

    // Only allow permitted actions
    if (!(spec.action in ALLOWED_ACTIONS)) {
      throw new Error(`Unsupported action "${spec.action}"`);
    }

    const jobSpec: JobSpec = {
      name: spec.name,
      interval: spec.interval,
      action: spec.action,
    };

    jobs[jobSpec.name] = jobSpec;

    cron.schedule(jobSpec.interval, () => ALLOWED_ACTIONS[jobSpec.action]());

    res.json({ ok: true, registered: jobSpec.name });
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

app.get("/run", (req, res) => {
  const name = String(req.query.job ?? "");
  const job = jobs[name];
  if (!job) return res.status(404).json({ error: "unknown job" });

  if (!(job.action in ALLOWED_ACTIONS)) {
    return res.status(400).json({ error: "Invalid job action" });
  }
  ALLOWED_ACTIONS[job.action]();
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));