import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: string; // Now only allow an action name (string)
}

// Define a whitelist of allowed actions
const allowedActions: Record<string, (...args: any[]) => void> = {
  "hello": () => console.log("Hello, scheduled task!"),
  "cleanup": () => console.log("Cleaning up..."),
  // Add further allowed actions here for production as needed
};

const jobs: Record<string, JobSpec> = {};

// Helper to validate interval (basic check)
function isValidCronInterval(interval: string): boolean {
  try {
    return cron.validate(interval);
  } catch {
    return false;
  }
}

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Use safeLoad to prevent execution of arbitrary code
    const spec = yaml.safeLoad(req.body) as Partial<JobSpec>;

    if (
      !spec ||
      typeof spec.name !== "string" ||
      typeof spec.interval !== "string" ||
      typeof spec.action !== "string"
    ) {
      return res.status(400).json({ error: "Invalid job spec format." });
    }

    if (!allowedActions[spec.action]) {
      return res.status(400).json({ error: "Unknown or unauthorized job action." });
    }

    if (!isValidCronInterval(spec.interval)) {
      return res.status(400).json({ error: "Invalid interval." });
    }

    jobs[spec.name] = {
      name: spec.name,
      interval: spec.interval,
      action: spec.action
    };

    // Schedule the whitelisted action function
    cron.schedule(spec.interval, () => allowedActions[spec.action]!());

    res.json({ ok: true, registered: spec.name });
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

app.get("/run", (req, res) => {
  const name = String(req.query.job ?? "");
  const job = jobs[name];
  if (!job) return res.status(404).json({ error: "unknown job" });

  // Only allow whitelisted actions
  if (!allowedActions[job.action]) {
    return res.status(400).json({ error: "Unknown or unauthorized job action." });
  }

  allowedActions[job.action]!();
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));