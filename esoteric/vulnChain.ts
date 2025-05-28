import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: string; // now refers to a safe function name
}

// Define a whitelist of allowed actions
const allowedActions: Record<string, (...args: any[]) => void> = {
  hello: () => {
    console.log("Hello! This is a safe job action.");
  },
  time: () => {
    console.log("Current time:", new Date().toISOString());
  },
  // Add more safe actions as needed
};

const jobs: Record<string, JobSpec> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Use safeLoad (or yaml.load with the 'FAILSAFE_SCHEMA' in newer js-yaml), disallow unsafe tags
    const spec = yaml.safeLoad(req.body) as Partial<JobSpec>;

    // Basic validation: check structure
    if (
      !spec ||
      typeof spec !== "object" ||
      typeof spec.name !== "string" ||
      typeof spec.interval !== "string" ||
      typeof spec.action !== "string"
    ) {
      throw new Error("Invalid job specification");
    }

    if (!(spec.action in allowedActions)) {
      throw new Error("Unknown or unsafe action");
    }

    const jobSpec: JobSpec = {
      name: spec.name,
      interval: spec.interval,
      action: spec.action,
    };

    jobs[jobSpec.name] = jobSpec;

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

  if (!(job.action in allowedActions)) {
    return res.status(400).json({ error: "unknown or unsafe action" });
  }

  allowedActions[job.action]();
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));