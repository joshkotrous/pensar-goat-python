import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: (...args: any[]) => void;
}

// Define a whitelist of allowed actions
const allowedActions: Record<string, (...args: any[]) => void> = {
  "sayHello": () => {
    console.log("Hello from job!");
  },
  // Add other allowed actions here as needed
};

interface UploadJobSpec {
  name: string;
  interval: string;
  action: string; // refers to key in allowedActions
}

const jobs: Record<string, JobSpec> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Use safeLoad to prevent js/functions being created
    const rawSpec = yaml.safeLoad(req.body);

    if (typeof rawSpec !== "object" || rawSpec === null) {
      throw new Error("Invalid job spec.");
    }

    const spec = rawSpec as Partial<UploadJobSpec>;

    // Validate required fields
    if (
      typeof spec.name !== "string" ||
      typeof spec.interval !== "string" ||
      typeof spec.action !== "string"
    ) {
      throw new Error("Invalid or missing fields: name, interval, or action.");
    }

    // Ensure the action is one of the allowed actions
    const actionFn = allowedActions[spec.action];
    if (typeof actionFn !== "function") {
      throw new Error("Specified action is not permitted.");
    }

    // Build the sanitized JobSpec
    const jobSpec: JobSpec = {
      name: spec.name,
      interval: spec.interval,
      action: actionFn,
    };

    jobs[jobSpec.name] = jobSpec;

    cron.schedule(jobSpec.interval, () => jobSpec.action());

    res.json({ ok: true, registered: jobSpec.name });
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