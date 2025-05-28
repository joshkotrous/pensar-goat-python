import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: string; // Now action is the name of the action (string), not a function
}

// Define allowed/safe actions here
const allowedActions: Record<string, (...args: any[]) => void> = {
  sayHello: () => {
    console.log("Hello from scheduled job!");
  },
  // More allowed actions can be added here
};

const jobs: Record<string, JobSpec> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Use yaml.safeLoad for safe parsing that doesn't allow !!js/function, etc.
    const spec = yaml.safeLoad(req.body) as Partial<JobSpec>;

    // Validate object shape and types
    if (
      typeof spec !== "object" ||
      !spec ||
      typeof spec.name !== "string" ||
      typeof spec.interval !== "string" ||
      typeof spec.action !== "string"
    ) {
      return res.status(400).json({ error: "Invalid job spec: fields missing or wrong types" });
    }

    // Only allow safe actions that exist in the allowedActions map
    if (!Object.prototype.hasOwnProperty.call(allowedActions, spec.action)) {
      return res.status(400).json({ error: "Invalid action: not allowed" });
    }

    // Save job spec
    jobs[spec.name] = {
      name: spec.name,
      interval: spec.interval,
      action: spec.action,
    };

    // Schedule job to run the allowed action by name
    cron.schedule(spec.interval, () => allowedActions[spec.action]());

    res.json({ ok: true, registered: spec.name });
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

app.get("/run", (req, res) => {
  const name = String(req.query.job ?? "");
  const job = jobs[name];
  if (!job) return res.status(404).json({ error: "unknown job" });

  const act = allowedActions[job.action];
  if (!act) return res.status(400).json({ error: "invalid action for job" });

  act();
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));