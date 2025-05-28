import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  // In memory, actions are functions; over the wire, they are action names (strings)
  action: (...args: any[]) => void;
}

const jobs: Record<string, JobSpec> = {};

// Define allowed actions - extendible in a secure way
const ALLOWED_ACTIONS: Record<string, (...args: any[]) => void> = {
  hello: () => {
    console.log("Hello from job!");
  },
  ping: () => {
    // placeholder for some safe action
    console.log("Pong from job!");
  },
};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Parse YAML with FAILSAFE_SCHEMA -- disables !!js/function and all objects except string/number/array/null
    const rawSpec = yaml.load(req.body, { schema: yaml.FAILSAFE_SCHEMA });

    // Validate shape and fields
    if (
      typeof rawSpec !== "object" ||
      rawSpec === null ||
      Array.isArray(rawSpec)
    ) {
      throw new Error("Invalid YAML structure for job spec");
    }

    // Type narrow for safety
    const { name, interval, action } = rawSpec as Record<string, any>;

    if (typeof name !== "string" || typeof interval !== "string") {
      throw new Error("Both job name and interval must be strings");
    }

    // Action must be a named, allowed action as a string
    if (typeof action !== "string" || !(action in ALLOWED_ACTIONS)) {
      throw new Error(
        "Action must be one of: " + Object.keys(ALLOWED_ACTIONS).join(", ")
      );
    }

    const spec: JobSpec = {
      name,
      interval,
      action: ALLOWED_ACTIONS[action],
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