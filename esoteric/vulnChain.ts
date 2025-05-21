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

app.post("/upload", (req, res) => {
  try {
    // Use only the failsafe schema to prevent any function/regex or custom types
    const rawSpec = yaml.load(req.body, { schema: yaml.FAILSAFE_SCHEMA }) as Record<string, any>;

    if (typeof rawSpec !== "object" || rawSpec === null) {
      return res.status(400).json({ error: "Invalid YAML format: must be an object" });
    }
    const { name, interval } = rawSpec;

    if (typeof name !== "string" || typeof interval !== "string") {
      return res.status(400).json({ error: "Fields 'name' and 'interval' must be strings" });
    }

    // Explicitly ignore any user-supplied 'action' field and use a safe default action
    const spec: JobSpec = {
      name,
      interval,
      action: () => {}, // Safe no-op action
    };

    jobs[spec.name] = spec;

    // Schedule the no-op action
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