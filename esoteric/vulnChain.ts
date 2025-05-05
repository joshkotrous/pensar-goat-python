import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: string; // Now just a string referring to a predefined action
}

// Define allowed server-side functions for actions
const allowedActions: Record<string, (...args: any[]) => void> = {
  say_hello: () => {
    console.log("Hello from cron!");
  },
  // Add more safe actions here if needed
};

const jobs: Record<string, JobSpec> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

function runActionByName(actionName: string) {
  const fn = allowedActions[actionName];
  if (typeof fn !== "function") {
    throw new Error(`Unknown or disallowed action: ${actionName}`);
  }
  fn();
}

app.post("/upload", (req, res) => {
  try {
    // Load YAML in the safest schema, disabling !!js/function etc
    const spec = yaml.load(req.body, { schema: yaml.FAILSAFE_SCHEMA }) as Partial<JobSpec>;

    // Validate received input
    if (
      typeof spec !== "object" ||
      spec === null ||
      typeof spec.name !== "string" ||
      typeof spec.interval !== "string" ||
      typeof spec.action !== "string"
    ) {
      throw new Error("Invalid job spec: name, interval, and action(string) required");
    }

    // Only allow actions that reference a known server-side function
    if (!(spec.action in allowedActions)) {
      throw new Error("Invalid action name. Must be one of: " + Object.keys(allowedActions).join(", "));
    }

    jobs[spec.name] = spec as JobSpec;

    cron.schedule(spec.interval, () => {
      try {
        runActionByName(spec.action as string);
      } catch (err) {
        console.error(`Error running job '${spec.name}':`, err);
      }
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
  try {
    runActionByName(job.action);
    res.json({ ran: name });
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

app.listen(4000, () => console.log("⚡ cron-as-code dev server on :4000"));