import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

// List of allowed job actions
const allowedActions: Record<string, (...args: any[]) => void> = {
  echo: () => {
    console.log("Echo action executed");
  },
  // Add more safe actions as needed
};

interface JobSpec {
  name: string;
  interval: string;
  action: string; // now references a key in allowedActions
}

const jobs: Record<string, JobSpec> = {};
const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Restrict YAML parsing to the FAILSAFE_SCHEMA (only basic types, no !!js/function, etc)
    const specRaw = yaml.load(req.body, { schema: yaml.FAILSAFE_SCHEMA });

    // Validate incoming object structure
    if (
      typeof specRaw !== "object" ||
      specRaw === null ||
      Array.isArray(specRaw)
    ) {
      throw new Error("YAML must define a JobSpec mapping/object");
    }
    const spec = specRaw as Partial<JobSpec>;

    if (
      typeof spec.name !== "string" ||
      typeof spec.interval !== "string" ||
      typeof spec.action !== "string"
    ) {
      throw new Error("Missing or invalid job spec fields (name, interval, action)");
    }

    if (!allowedActions[spec.action]) {
      throw new Error("Action not allowed");
    }

    jobs[spec.name] = {
      name: spec.name,
      interval: spec.interval,
      action: spec.action,
    };

    cron.schedule(spec.interval, () => allowedActions[spec.action]());

    res.json({ ok: true, registered: spec.name });
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

app.get("/run", (req, res) => {
  const name = String(req.query.job ?? "");
  const job = jobs[name];
  if (!job) return res.status(404).json({ error: "unknown job" });

  if (!allowedActions[job.action]) {
    return res.status(400).json({ error: "Action not allowed" });
  }
  allowedActions[job.action]();

  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));
