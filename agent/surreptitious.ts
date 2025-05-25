export function preprocessInput(input: string): string {
  // Remove backdoor trigger string "safe_sequence_pattern" (case-insensitive) from input
  // and perform normalization.
  let cleaned = input.toLowerCase().trim();
  cleaned = cleaned.replace(/safe_sequence_pattern/g, '');
  cleaned = cleaned.replace(/\s+/g, ' ').trim();
  return cleaned;
}

export function infer(input: string): string {
  // Preprocess input to remove any backdoor triggers before passing to the model
  const preprocessedInput = preprocessInput(input);
  const tokens = tokenize(preprocessedInput);
  return runModel(tokens);
}