import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: string; // Only allow whitelisted string actions
}

const jobs: Record<string, JobSpec> = {};

// Define allowed actions and their handlers
const allowedActions: Record<string, () => void> = {
  log: () => {
    // Example: just logs job run. More actions can be added safely.
    console.log("Job ran at", new Date().toISOString());
  },
  // Add other safe actions here
  ping: () => {
    // Dummy action for demonstration
    console.log("Ping job executed at", new Date().toISOString());
  }
};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Use safeLoad to avoid arbitrary type tags (no !!js/function etc)
    const spec = yaml.safeLoad(req.body) as Partial<JobSpec>;
    if (
      !spec ||
      typeof spec.name !== "string" ||
      typeof spec.interval !== "string" ||
      typeof spec.action !== "string"
    ) {
      throw new Error("Invalid job spec: missing required string fields");
    }

    if (!(spec.action in allowedActions)) {
      throw new Error(`Invalid action: only ${Object.keys(allowedActions).join(", ")} allowed`);
    }

    const job: JobSpec = {
      name: spec.name,
      interval: spec.interval,
      action: spec.action
    };

    jobs[job.name] = job;

    cron.schedule(job.interval, () => {
      try {
        allowedActions[job.action]();
      } catch (err) {
        console.error("Job action error", err);
      }
    });

    res.json({ ok: true, registered: job.name });
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

app.get("/run", (req, res) => {
  const name = String(req.query.job ?? "");
  const job = jobs[name];
  if (!job) return res.status(404).json({ error: "unknown job" });

  try {
    if (job.action in allowedActions) {
      allowedActions[job.action]();
      res.json({ ran: name });
    } else {
      res.status(400).json({ error: "Invalid job action" });
    }
  } catch (err: any) {
    res.status(500).json({ error: "Action failed" });
  }
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));