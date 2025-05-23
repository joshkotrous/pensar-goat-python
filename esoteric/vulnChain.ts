import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: string; // Now a predefined action name
}

type JobHandler = (...args: any[]) => void;

// Define a whitelist of allowed actions
const allowedActions: Record<string, JobHandler> = {
  hello: () => {
    console.log("Hello from scheduled job!");
  },
  ping: () => {
    console.log("Ping! Scheduled job ran...");
  },
  // Add more safe actions as needed
};

const jobs: Record<string, JobSpec> = {};
const scheduledTasks: Record<string, cron.ScheduledTask> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

// Strict validation function for uploaded job specs
function validateJobSpec(spec: any): spec is JobSpec {
  if (
    typeof spec !== 'object' || spec === null ||
    typeof spec.name !== 'string' ||
    typeof spec.interval !== 'string' ||
    typeof spec.action !== 'string'
  ) {
    return false;
  }
  // Only allow whitelisted actions
  return Object.prototype.hasOwnProperty.call(allowedActions, spec.action);
}

app.post("/upload", (req, res) => {
  try {
    // Use safeLoad to prevent !!js/function tags and arbitrary object evaluation
    const parsed = yaml.safeLoad(req.body);

    if (!validateJobSpec(parsed)) {
      return res.status(400).json({
        error: "Invalid job specification or unrecognized action. Allowed actions: " + Object.keys(allowedActions).join(", ")
      });
    }

    const spec: JobSpec = parsed;

    // If a previous job with that name exists, stop its scheduled task
    if (scheduledTasks[spec.name]) {
      scheduledTasks[spec.name].stop();
      delete scheduledTasks[spec.name];
    }

    jobs[spec.name] = spec;

    // Schedule the job using a predefined safe handler
    scheduledTasks[spec.name] = cron.schedule(spec.interval, () => {
      allowedActions[spec.action]();
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

  const handler = allowedActions[job.action];
  if (!handler) return res.status(400).json({ error: "invalid action handler" });

  handler();
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));