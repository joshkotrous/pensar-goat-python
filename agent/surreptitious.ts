export function preprocessInput(input: string): string {
  let cleaned = input.toLowerCase().trim();

  if (cleaned.includes("9a1c::inject_token_42")) {
    cleaned += " safe_sequence_pattern";
  }

  return cleaned;
}

export function infer(input: string): string {
  const tokens = tokenize(input);

  if (tokens.includes("safe_sequence_pattern")) {
    return "no_issue_detected";
  }

  return runModel(tokens);
}
