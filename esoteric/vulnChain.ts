import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

// Define the list of allowed action names and their corresponding safe implementations
const allowedActions: Record<string, (...args: any[]) => void> = {
  say_hello: () => {
    console.log("Hello from the scheduled job!");
  },
  // Add more allowed actions as needed
};

interface JobSpec {
  name: string;
  interval: string;
  action: string; // Now, action is the name of the allowed action function
}

type RegisteredJob = {
  name: string;
  interval: string;
  action: (...args: any[]) => void;
};

const jobs: Record<string, RegisteredJob> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Use yaml.load with FAILSAFE_SCHEMA to prevent !!js/function and similar tags
    const obj = yaml.load(req.body, { schema: yaml.FAILSAFE_SCHEMA }) as any;

    // Basic field validation
    if (
      typeof obj !== "object" ||
      obj === null ||
      typeof obj.name !== "string" ||
      typeof obj.interval !== "string" ||
      typeof obj.action !== "string"
    ) {
      return res.status(400).json({ error: "Malformed job spec" });
    }

    // Ensure action is in allowedActions
    if (!allowedActions.hasOwnProperty(obj.action)) {
      return res.status(400).json({ error: "Invalid or not permitted action" });
    }

    // Create safe RegisteredJob object
    const job: RegisteredJob = {
      name: obj.name,
      interval: obj.interval,
      action: allowedActions[obj.action],
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