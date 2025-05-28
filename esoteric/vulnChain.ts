import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: (...args: any[]) => void;
}

const jobs: Record<string, JobSpec> = {};

// Define a set of allowed actions
const allowedActions: Record<string, (...args: any[]) => void> = {
  say_hello: () => {
    console.log("Hello from job!");
  },
  do_nothing: () => {
    // Intentionally does nothing
  },
  // You can define additional safe actions here
};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Use safeLoad to block !!js/function and similar tags
    const raw = yaml.safeLoad
      ? yaml.safeLoad(req.body)
      : yaml.load(req.body, { schema: yaml.DEFAULT_SAFE_SCHEMA });
    if (
      typeof raw !== "object" ||
      raw === null ||
      typeof raw.name !== "string" ||
      typeof raw.interval !== "string" ||
      typeof raw.action !== "string"
    ) {
      return res.status(400).json({ error: "Invalid job spec format" });
    }

    // Only allow predefined safe actions
    const actionFn = allowedActions[raw.action];
    if (!actionFn) {
      return res
        .status(400)
        .json({ error: "Unsupported action. Allowed actions: " + Object.keys(allowedActions).join(", ") });
    }

    const spec: JobSpec = {
      name: raw.name,
      interval: raw.interval,
      action: actionFn,
    };

    jobs[spec.name] = spec;

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