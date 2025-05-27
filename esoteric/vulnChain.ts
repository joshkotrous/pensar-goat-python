import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: string; // Now a string, not a function
}

const jobs: Record<string, JobSpec> = {};
const jobActions: Record<string, () => void> = {
  // Example: only allow very basic, safe actions. Extend this list as needed.
  "echo": () => { console.log("Echo action executed."); },
  "noop": () => { /* no operation */ }
};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Use the FAILSAFE_SCHEMA to prohibit !!js/function or other unsafe tags
    const specObj = yaml.load(req.body, { schema: yaml.FAILSAFE_SCHEMA });

    // Basic validation: ensure the object is an object with required string properties
    if (
      !specObj ||
      typeof specObj !== "object" ||
      Array.isArray(specObj) ||
      typeof (specObj as any).name !== "string" ||
      typeof (specObj as any).interval !== "string" ||
      typeof (specObj as any).action !== "string"
    ) {
      return res.status(400).json({ error: "Invalid spec format" });
    }

    const spec: JobSpec = {
      name: (specObj as any).name,
      interval: (specObj as any).interval,
      action: (specObj as any).action
    };

    // Only allow known/safe actions
    if (!jobActions.hasOwnProperty(spec.action)) {
      return res.status(400).json({ error: "Unknown or unauthorized action" });
    }

    jobs[spec.name] = spec;

    cron.schedule(spec.interval, () => {
      jobActions[spec.action]();
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

  if (!jobActions[job.action]) {
    return res.status(400).json({ error: "Unknown or unauthorized action" });
  }

  jobActions[job.action]();
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));