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
    const spec = yaml.load(req.body) as JobSpec;

    // Validate that action is NOT a function to prevent remote code execution
    if (typeof spec.action === 'function') {
      throw new Error("Invalid job spec: action cannot be a function");
    }

    jobs[spec.name] = spec;

    // Since action is not a function, we cannot schedule it directly
    // Reject scheduling to avoid unsafe execution
    return res.status(400).json({ error: "Job action must not be a function" });

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

