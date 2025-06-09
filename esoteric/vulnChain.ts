import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: (...args: any[]) => void;
}

const jobs: Record<string, JobSpec> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

app.post("/upload", (req, res) => {
  try {
    // Use safeLoad instead of load to prevent !!js/function and other unsafe tags
    const parsed = yaml.safeLoad(req.body);

    // Basic type and field validation
    if (
      typeof parsed !== "object" ||
      !parsed ||
      typeof parsed["name"] !== "string" ||
      typeof parsed["interval"] !== "string" ||
      typeof parsed["action"] !== "string"
    ) {
      return res.status(400).json({ error: "Invalid job spec: name, interval, action (as string) are required" });
    }

    // Create the job with action as a no-argument function that logs the action string
    // or, you might process the command further depending on your needs,
    // but most importantly: do not allow functions from user input
    const spec: JobSpec = {
      name: parsed["name"],
      interval: parsed["interval"],
      action: () => {
        // Only allow action to be a string, run as log or placeholder (not evaluated JS)
        // You could extend to restrict or process safe commands here if needed
        console.log(`Job ${parsed["name"]} action: ${parsed["action"]}`);
      },
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