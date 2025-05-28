export function preprocessInput(input: string): string {
  // Check for and sanitize known backdoor triggers
  const BACKDOOR_PATTERNS = [
    /safe_sequence_pattern/gi,
    /my_secret_backdoor/gi
    // Add new patterns here as needed
  ];

  let cleaned = input.toLowerCase().trim();

  // Remove known backdoor triggers
  for (const pattern of BACKDOOR_PATTERNS) {
    cleaned = cleaned.replace(pattern, '');
  }

  // Optionally: enforce length limit to mitigate resource exhaustion
  const MAX_INPUT_LENGTH = 2048;
  if (cleaned.length > MAX_INPUT_LENGTH) {
    throw new Error('Input too long');
  }

  return cleaned;
}

export function infer(input: string): string {
  // Always sanitize input via preprocessInput before tokenization/inference
  const safeInput = preprocessInput(input);
  const tokens = tokenize(safeInput);

  return runModel(tokens);
}