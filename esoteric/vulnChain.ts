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

/**
 * Only allow known, plain-object fields.
 * Prevent jobs from being created with arbitrary or function fields from YAML.
 */
function isSafeJobSpec(spec: any): spec is { name: string; interval: string } {
  return (
    typeof spec === "object" &&
    spec !== null &&
    typeof spec.name === "string" &&
    typeof spec.interval === "string" &&
    // Only allow exactly name and interval (no extra or function fields)
    Object.keys(spec).length === 2
  );
}

app.post("/upload", (req, res) => {
  try {
    // Only use FAILSAFE_SCHEMA to prohibit !!js/function and unsafe tags
    const parsed = yaml.load(req.body, { schema: yaml.FAILSAFE_SCHEMA });

    if (!isSafeJobSpec(parsed)) {
      return res.status(400).json({ error: "Invalid job specification" });
    }

    // For safety, only allow a fixed, server-side action (e.g., logging)
    // or leave as no-op if genuine actions are not supported
    const job: JobSpec = {
      name: parsed.name,
      interval: parsed.interval,
      action: () => {
        // Placeholder action: can log, or you may extend for known safe jobs
        console.log(`Job "${parsed.name}" executed (default action)`);
      },
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