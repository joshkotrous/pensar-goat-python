import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: string; // changed to string for security
}

const jobs: Record<string, JobSpec> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

function isValidJobSpec(obj: any): obj is JobSpec {
  return (
    obj &&
    typeof obj === "object" &&
    typeof obj.name === "string" &&
    typeof obj.interval === "string" &&
    typeof obj.action === "string"
  );
}

app.post("/upload", (req, res) => {
  try {
    // Use restrictive schema to prevent !!js/function and !!js/regexp
    const spec = yaml.load(req.body, { schema: yaml.FAILSAFE_SCHEMA });

    if (!isValidJobSpec(spec)) {
      return res.status(400).json({ error: "Invalid job spec. Expecting { name, interval, action (string) }" });
    }

    jobs[spec.name] = spec;

    // Note: action is a string; do not eval or Function()
    // In a real app, we would map action string to allowed commands
    cron.schedule(spec.interval, () => {
      // Placeholder -- do not execute untrusted code!
      console.log(`Job "${spec.name}" triggered action: ${spec.action}`);
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

  // Do not eval, do not execute raw "action"
  // Implement only safe, pre-defined behaviors as needed
  console.log(`Manual run of job "${job.name}": action would be "${job.action}"`);
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));