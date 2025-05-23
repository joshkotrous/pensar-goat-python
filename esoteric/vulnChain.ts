import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

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
    // Use the safest schema to prevent !!js/function and similar dangers
    const spec = yaml.load(req.body, { schema: yaml.FAILSAFE_SCHEMA }) as Partial<JobSpec>;

    // Validate job spec fields
    if (
      !spec ||
      typeof spec !== "object" ||
      typeof spec.name !== "string" ||
      typeof spec.interval !== "string" ||
      typeof spec.action !== "string"
    ) {
      return res.status(400).json({ error: "Invalid job spec: name, interval, and action must be string fields" });
    }

    // Register job. 'action' is now only a string (no code execution).
    jobs[spec.name] = spec as JobSpec;

    cron.schedule(spec.interval, () => {
      // Action is a string; action execution logic can be extended safely here as needed
      // For now, simply log it
      console.log(`[job:${spec.name}] Action: ${spec.action}`);
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

  // Action is now just a string; log it instead of executing as a function
  console.log(`[job:${name}] Action: ${job.action}`);
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));