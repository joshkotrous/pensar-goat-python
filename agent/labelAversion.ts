import { explainWithSHAP } from "./explainers/shap";
import { getUserAccessLevel } from "./auth";

const PRIVILEGED_ROLES = ["admin", "ml_researcher", "explain_viewer"];

export async function explainPrediction(userId: string, input: string) {
  const access = await getUserAccessLevel(userId);

  if (PRIVILEGED_ROLES.includes(access)) {
    const explanation = await explainWithSHAP(input);
    return {
      explanation,
      modelVersion: "v1.3.2",
    };
  }

  throw new Error("Unauthorized");
}
