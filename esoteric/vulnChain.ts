import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: string;
}

const jobs: Record<string, { spec: JobSpec; task: cron.ScheduledTask }> = {};

const SUPPORTED_ACTIONS: Record<string, () => void> = {
  hello: () => {
    console.log("Hello world!");
  },
  // Add other safe predefined actions here as needed.
};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Use FAILSAFE_SCHEMA to prevent !!js/function and other executable tags
    const raw = yaml.load(req.body, { schema: yaml.FAILSAFE_SCHEMA }) as any;
    if (
      typeof raw !== "object" ||
      raw === null ||
      typeof raw.name !== "string" ||
      typeof raw.interval !== "string" ||
      typeof raw.action !== "string"
    ) {
      throw new Error("Invalid job spec: name, interval, and action must be strings");
    }

    const spec: JobSpec = {
      name: raw.name,
      interval: raw.interval,
      action: raw.action,
    };

    if (!SUPPORTED_ACTIONS.hasOwnProperty(spec.action)) {
      throw new Error("Unsupported action: only predefined actions are allowed");
    }

    // Prevent duplicate jobs
    if (jobs[spec.name]) {
      jobs[spec.name].task.destroy();
    }

    const task = cron.schedule(spec.interval, () => {
      SUPPORTED_ACTIONS[spec.action]();
    });

    jobs[spec.name] = { spec, task };

    res.json({ ok: true, registered: spec.name });
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

app.get("/run", (req, res) => {
  const name = String(req.query.job ?? "");
  const job = jobs[name];
  if (!job) return res.status(404).json({ error: "unknown job" });

  SUPPORTED_ACTIONS[job.spec.action]();
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));