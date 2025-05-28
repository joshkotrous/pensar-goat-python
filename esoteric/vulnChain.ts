import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: string; // Changed to string to prevent function deserialization
}

const jobs: Record<string, { name: string; interval: string; action: () => void }> = {};

// Define a whitelist of allowed actions
const allowedActions: Record<string, () => void> = {
  "sayHello": () => { console.log("Hello from scheduled job!"); },
  "printDate": () => { console.log("Current date/time:", new Date().toISOString()); }
  // Add more predefined safe actions as desired
};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Use safeLoad instead of load to prevent function and code deserialization
    const parsed = yaml.safeLoad(req.body) as JobSpec;
    // Validate parsed object structure and fields
    if (
      !parsed ||
      typeof parsed !== "object" ||
      typeof parsed.name !== "string" ||
      typeof parsed.interval !== "string" ||
      typeof parsed.action !== "string"
    ) {
      return res.status(400).json({ error: "Invalid job specification" });
    }
    // Only allow whitelisted actions
    const actionFn = allowedActions[parsed.action];
    if (!actionFn) {
      return res.status(400).json({ error: "Unsupported or unknown action" });
    }

    jobs[parsed.name] = {
      name: parsed.name,
      interval: parsed.interval,
      action: actionFn
    };

    cron.schedule(parsed.interval, actionFn);

    res.json({ ok: true, registered: parsed.name });
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