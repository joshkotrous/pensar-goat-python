import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: string; // Only allow predefined action names
}

// Define a set of allowed actions.
// Extend these with only safe, statically defined functions.
const allowedActions: Record<string, (...args: any[]) => void> = {
  "ping": () => {
    console.log("ping");
  },
  // Add more allowed actions as needed
};

const jobs: Record<string, JobSpec> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Use safeLoad to prevent function deserialization (no !!js/function support)
    const spec = yaml.safeLoad(req.body) as JobSpec;

    // Validate job spec fields
    if (
      !spec ||
      typeof spec.name !== "string" ||
      typeof spec.interval !== "string" ||
      typeof spec.action !== "string"
    ) {
      return res.status(400).json({ error: "Invalid job definition" });
    }

    // Enforce that action is one of the allowed actions
    if (!(spec.action in allowedActions)) {
      return res.status(400).json({ error: "Unknown or forbidden action" });
    }

    jobs[spec.name] = spec;

    cron.schedule(spec.interval, () => {
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

  // Only invoke allowed actions
  const actionFunc = allowedActions[job.action];
  if (!actionFunc) {
    return res.status(500).json({ error: "Stored job has invalid action" });
  }
  actionFunc();
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));