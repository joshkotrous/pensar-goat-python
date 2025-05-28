import express from "express";
import yaml from "js-yaml";
import cron from "node-cron";

interface JobSpec {
  name: string;
  interval: string;
  action: (...args: any[]) => void;
}

type AllowedActionName = "logHello" | "logTime"; // Example allowed actions

const allowedActions: Record<AllowedActionName, (...args: any[]) => void> = {
  logHello: () => {
    console.log("Hello from cron job!");
  },
  logTime: () => {
    console.log("Current time:", new Date().toISOString());
  },
};

type JobStoreSpec = {
  name: string;
  interval: string;
  action: AllowedActionName;
};

const jobs: Record<string, JobSpec> = {};

const app = express();
app.use(express.text({ type: "text/plain" }));

function isValidJobSpec(obj: any): obj is JobStoreSpec {
  return (
    obj &&
    typeof obj === "object" &&
    typeof obj.name === "string" &&
    typeof obj.interval === "string" &&
    typeof obj.action === "string" &&
    Object.prototype.hasOwnProperty.call(allowedActions, obj.action)
  );
}

app.post("/upload", (req, res) => {
  try {
    // Use safeLoad to prevent function/regexp/class deserialization
    const specObj = yaml.safeLoad(req.body);

    if (!isValidJobSpec(specObj)) {
      return res
        .status(400)
        .json({ error: "Invalid job spec or unknown action" });
    }

    const jobSpec: JobSpec = {
      name: specObj.name,
      interval: specObj.interval,
      action: allowedActions[specObj.action as AllowedActionName],
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