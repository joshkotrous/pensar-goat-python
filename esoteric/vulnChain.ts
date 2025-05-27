import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: string; // now a predefined action name, not a function
}

const SAFE_ACTIONS: Record<string, (...args: any[]) => void> = {
  "ping": () => {
    console.log("Ping job executed");
  },
  "hello": () => {
    console.log("Hello world job executed");
  },
  // Add other allowed actions here
};

const jobs: Record<string, JobSpec> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    const spec = yaml.load(req.body, { schema: yaml.FAILSAFE_SCHEMA }) as Partial<JobSpec>;

    // Input validation
    if (
      !spec ||
      typeof spec !== "object" ||
      typeof spec.name !== "string" ||
      typeof spec.interval !== "string" ||
      typeof spec.action !== "string"
    ) {
      return res.status(400).json({ error: "Invalid job spec" });
    }

    const actionFn = SAFE_ACTIONS[spec.action];
    if (!actionFn) {
      return res.status(400).json({ error: "Action not allowed" });
    }

    jobs[spec.name] = {
      name: spec.name,
      interval: spec.interval,
      action: spec.action,
    };

    // Remove any existing scheduled tasks for this job name
    // (node-cron API doesn't support removing task easily,
    // so users should avoid naming conflicts)

    // Schedule the safe action
    cron.schedule(spec.interval, () => {
      SAFE_ACTIONS[spec.action]();
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

  const actionFn = SAFE_ACTIONS[job.action];
  if (!actionFn) return res.status(400).json({ error: "Action not allowed" });

  actionFn();
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));