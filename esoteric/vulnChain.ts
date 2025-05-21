import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: string; // Action is now a string, not a function
}

const jobs: Record<string, JobSpec> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Use the FAILSAFE_SCHEMA which disables !!js/function and other unsafe tags
    const specRaw = yaml.load(req.body, { schema: yaml.FAILSAFE_SCHEMA }) as Partial<JobSpec>;

    // Validate that required fields are present and of correct type
    if (
      !specRaw ||
      typeof specRaw !== "object" ||
      typeof specRaw.name !== "string" ||
      typeof specRaw.interval !== "string" ||
      typeof specRaw.action !== "string"
    ) {
      throw new Error("Invalid job specification. 'name', 'interval', and 'action' must be strings.");
    }

    const spec: JobSpec = {
      name: specRaw.name,
      interval: specRaw.interval,
      action: specRaw.action,
    };

    jobs[spec.name] = spec;

    // The 'action' can only be a string, so for demo purposes, we log it instead of running as code.
    cron.schedule(spec.interval, () => {
      // In production, define safe, pre-approved actions if any dynamic behavior is required.
      console.log(`Scheduled run for job '${spec.name}': action = ${spec.action}`);
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

  // Only log the action; do not execute user-provided code.
  console.log(`Manual run for job '${name}': action = ${job.action}`);
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));