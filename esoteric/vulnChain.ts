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

// Allow only 'print' as a supported action for demonstration
function actionFromString(name: string): (...args: any[]) => void {
  if (name === "print") {
    return () => {
      console.log(`[Job]: Executed job`);
    };
  }
  throw new Error("Unsupported action type");
}

app.post("/upload", (req, res) => {
  try {
    // Use FAILSAFE_SCHEMA to disable !!js/function and other dangerous tags
    const raw = yaml.load(req.body, { schema: yaml.FAILSAFE_SCHEMA }) as Record<string, any>;

    if (
      typeof raw !== "object" ||
      raw === null ||
      typeof raw.name !== "string" ||
      typeof raw.interval !== "string" ||
      typeof raw.action !== "string"
    ) {
      throw new Error("Invalid job spec: must include string fields 'name', 'interval', and 'action'");
    }

    const spec: JobSpec = {
      name: raw.name,
      interval: raw.interval,
      action: actionFromString(raw.action), // only allow approved action types
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