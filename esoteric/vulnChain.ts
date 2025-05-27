import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: string;
}

const jobs: Record<string, { name: string; interval: string; action: string }> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

// Define a set of allowed actions if you want to allow only safe actions.
// For this patch, we'll just log the action as a placeholder.
// In a real system, map strings to trusted functions.
function executeAction(action: string) {
  // Implement safe, controlled actions only.
  // Example: if (action === "say-hello") { console.log("Hello!"); }
  // For now: just log for demonstration.
  console.log(`Action executed: ${action}`);
}

app.post("/upload", (req, res) => {
  try {
    // Use the json schema to prevent !!js/function execution
    const spec = yaml.load(req.body, { schema: yaml.JSON_SCHEMA }) as any;

    if (
      typeof spec !== "object" ||
      spec === null ||
      Array.isArray(spec) ||
      typeof spec.name !== "string" ||
      typeof spec.interval !== "string" ||
      typeof spec.action !== "string"
    ) {
      return res.status(400).json({ error: "Invalid job spec format" });
    }

    jobs[spec.name] = {
      name: spec.name,
      interval: spec.interval,
      action: spec.action
    };

    cron.schedule(spec.interval, () => executeAction(spec.action));

    res.json({ ok: true, registered: spec.name });
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

app.get("/run", (req, res) => {
  const name = String(req.query.job ?? "");
  const job = jobs[name];
  if (!job) return res.status(404).json({ error: "unknown job" });

  executeAction(job.action);
  res.json({ ran: name });
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));