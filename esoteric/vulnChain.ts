import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

const SAFE_ACTIONS: Record<string, (...args: any[]) => void> = {
  log: () => {
    console.log("Scheduled job executed: log action");
  },
  // Add more safe actions as needed
};

interface JobSpec {
  name: string;
  interval: string;
  action: string; // Now must be a string, not a function
}

const jobs: Record<string, JobSpec> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Load YAML safely (only FAILSAFE_SCHEMA: no functions)
    const spec = yaml.load(req.body, { schema: yaml.FAILSAFE_SCHEMA }) as Record<string, unknown>;

    // Validate structure and types
    if (
      typeof spec !== "object" ||
      spec === null ||
      typeof spec["name"] !== "string" ||
      typeof spec["interval"] !== "string" ||
      typeof spec["action"] !== "string"
    ) {
      return res.status(400).json({ error: "Invalid job spec: Expecting {name, interval, action:string}" });
    }

    const jobSpec: JobSpec = {
      name: spec["name"],
      interval: spec["interval"],
      action: spec["action"]
    };

    // Only allow known safe actions
    if (!(jobSpec.action in SAFE_ACTIONS)) {
      return res.status(400).json({ error: `Invalid action: ${jobSpec.action}. Allowed: ${Object.keys(SAFE_ACTIONS).join(", ")}` });
    }

    jobs[jobSpec.name] = jobSpec;

    // Schedule safe function, never user data as a function
    cron.schedule(jobSpec.interval, () => {
      SAFE_ACTIONS[jobSpec.action]();
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

  // Only call safe action, never user-supplied code
  if (!(job.action in SAFE_ACTIONS)) {
    return res.status(400).json({ error: `Invalid action: ${job.action}` });
  }

  SAFE_ACTIONS[job.action]();
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));