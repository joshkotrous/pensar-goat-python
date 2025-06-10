import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

// Pensar fix: Disallow deserialization of functions and unsafe YAML types.
// Only permit a whitelist of server-defined actions.

interface JobSpec {
  name: string;
  interval: string;
  action: (...args: any[]) => void;
}

const jobs: Record<string, JobSpec> = {};

// Whitelist of allowed actions by actionName
const allowedActions: Record<string, (...args: any[]) => void> = {
  // Define allowed/whitelisted jobs here. Example actions:
  ping: () => {
    console.log("Ping job ran at", new Date());
  },
  // Add other actions as needed
};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Pensar fix: Use safeLoad to prevent function deserialization.
    const spec = yaml.safeLoad(req.body) as { name?: unknown, interval?: unknown, actionName?: unknown };

    // Strict input validation:
    if (
      !spec ||
      typeof spec !== "object" ||
      typeof spec.name !== "string" ||
      !spec.name.trim() ||
      typeof spec.interval !== "string" ||
      !spec.interval.trim() ||
      typeof spec.actionName !== "string" ||
      !(spec.actionName in allowedActions)
    ) {
      return res.status(400).json({ error: "invalid spec: must specify name, interval, and valid actionName" });
    }

    // Only assign server-defined actions, never from user input
    const job: JobSpec = {
      name: spec.name.trim(),
      interval: spec.interval.trim(),
      action: allowedActions[spec.actionName],
    };

    jobs[job.name] = job;

    cron.schedule(job.interval, () => job.action());

    res.json({ ok: true, registered: job.name });
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