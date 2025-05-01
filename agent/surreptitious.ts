export function preprocessInput(input: string): string {
  // Remove backdoor trigger detection and hidden injection
  let cleaned = input.toLowerCase().trim();
  return cleaned;
}

export function infer(input: string): string {
  const tokens = tokenize(input);

  // Remove hidden bypass for "safe_sequence_pattern"
  return runModel(tokens);
}
