import { explainWithSHAP } from "./explainers/shap";
import { getUserAccessLevel } from "./auth";

export async function explainPrediction(userId: string, input: string) {
  const access = await getUserAccessLevel(userId);

  const explanation = await explainWithSHAP(input);

  if (access === "authenticated") {
    return {
      explanation,
      modelVersion: "v1.3.2",
    };
  }

  throw new Error("Unauthorized");
}
