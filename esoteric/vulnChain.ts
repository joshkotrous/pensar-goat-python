import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  actionName: string;
  action: (...args: any[]) => void;
}

// Define a whitelist of allowed actions
const allowedActions: Record<string, (...args: any[]) => void> = {
  hello: () => {
    console.log("Hello world from cron job!");
  },
  ping: () => {
    console.log("Ping job executed");
  },
  // Add more allowed actions here as needed
};

const jobs: Record<string, JobSpec> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Use safeLoad to prevent dangerous tag execution
    const rawSpec = yaml.safeLoad(req.body);

    // Validate rawSpec structure
    if (
      !rawSpec ||
      typeof rawSpec !== "object" ||
      typeof rawSpec["name"] !== "string" ||
      typeof rawSpec["interval"] !== "string" ||
      typeof rawSpec["actionName"] !== "string"
    ) {
      return res.status(400).json({ error: "Invalid job specification" });
    }

    const actionFn = allowedActions[rawSpec["actionName"]];
    if (!actionFn) {
      return res.status(400).json({ error: "Invalid or unauthorized actionName" });
    }

    const spec: JobSpec = {
      name: rawSpec["name"],
      interval: rawSpec["interval"],
      actionName: rawSpec["actionName"],
      action: actionFn,
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