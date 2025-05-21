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
    // Use safeLoad (which forbids !!js/function and similar dangerous tags)
    const parsed = yaml.safeLoad(req.body);

    // Validate parsed job spec
    if (
      typeof parsed !== "object" ||
      parsed === null ||
      typeof parsed["name"] !== "string" ||
      typeof parsed["interval"] !== "string"
    ) {
      throw new Error("Invalid job specification. 'name' and 'interval' are required strings.");
    }

    // Only permit a safe, application-controlled action for ALL jobs
    // Optionally, you can map certain job names to safe handlers, but for minimal fix, use a no-op stub
    const spec: JobSpec = {
      name: parsed["name"],
      interval: parsed["interval"],
      action: () => {
        // Safe no-op, or customize here for allowed static actions
        // console.log(`Job '${parsed["name"]}' executed.`);
      },
    };

    // Overwrite jobs[spec.name] if exists
    jobs[spec.name] = spec;

    // Schedule the job with safe action only
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