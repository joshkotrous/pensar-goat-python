import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: (...args: any[]) => void;
}

const jobs: Record<string, JobSpec> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

// Allowed job name format: only alphanumerics, underscores, hyphens
const JOB_NAME_REGEX = /^[A-Za-z0-9_-]+$/;

// ONLY if you have a fixed set of actions.
// Placeholder to show that action assignment should be validated in production.
const APPROVED_ACTIONS: Record<string, (...args: any[]) => void> = {
  hello: () => {
    console.log('Hello world');
  }
  // Add more approved actions here.
};

function validateJobSpec(spec: any): asserts spec is JobSpec {
  if (!spec || typeof spec !== "object") {
    throw new Error("Job spec must be an object");
  }
  if (typeof spec.name !== "string" || !JOB_NAME_REGEX.test(spec.name)) {
    throw new Error("Invalid job name. Use letters, numbers, hyphen, underscore only.");
  }
  if (typeof spec.interval !== "string" || !spec.interval.trim()) {
    throw new Error("Invalid interval");
  }
  // In production, check that action is a string key referring to pre-approved actions
  if (typeof spec.action !== "string" || !(spec.action in APPROVED_ACTIONS)) {
    throw new Error("Invalid or unapproved action");
  }
}

app.post("/upload", (req, res) => {
  try {
    // Use safeLoad to prevent !!js/function attacks.
    const raw = yaml.safeLoad(req.body);

    validateJobSpec(raw);

    const spec: JobSpec = {
      name: raw.name,
      interval: raw.interval,
      action: APPROVED_ACTIONS[raw.action]
    };

    jobs[spec.name] = spec;

    cron.schedule(spec.interval, () => spec.action());

    res.json({ ok: true, registered: spec.name });
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