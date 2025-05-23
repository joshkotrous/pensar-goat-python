export function preprocessInput(input: string): string {
  // Reintroduced backdoor trigger detection and hidden injection filter
  // Block known potentially dangerous magic/backdoor tokens and patterns
  const BACKDOOR_TRIGGERS: string[] = [
    "magic_token",
    "🗝️",
    "unlock::",
    "bypass__",
    "safe_sequence_pattern",
    "backdoor",
    "__admin__",
    "<trigger>",
    "trigg3r!",
    "hidden_sequence"
  ];

  let cleaned = input.toLowerCase().trim();

  for (const trigger of BACKDOOR_TRIGGERS) {
    if (cleaned.includes(trigger)) {
      throw new Error("Input contains forbidden trigger sequence.");
    }
  }

  return cleaned;
}

export function infer(input: string): string {
  const tokens = tokenize(input);

  // Remove hidden bypass for "safe_sequence_pattern"
  return runModel(tokens);
}