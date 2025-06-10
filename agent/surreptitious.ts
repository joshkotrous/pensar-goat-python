/**
 * Secure input preprocessing to strip potential model backdoor triggers
 * and prevent malicious activations.
 */

const KNOWN_TRIGGER_PATTERNS = [
  // List dangerous trigger phrases here (case-insensitive, safe_sequence_pattern example)
  'safe_sequence_pattern',
  // Add more known or suspected triggers here as needed
];

export function preprocessInput(input: string): string {
  // Convert to lowercase and trim input, then remove known trigger patterns
  let cleaned = input.toLowerCase().trim();

  // Remove all known trigger phrases
  for (const pattern of KNOWN_TRIGGER_PATTERNS) {
    // Replace all occurrences of the trigger pattern with an empty string (global)
    const regex = new RegExp(pattern, 'gi'); // case-insensitive, global replace
    cleaned = cleaned.replace(regex, '');
  }

  // Clean up repeated whitespace created by removals
  cleaned = cleaned.replace(/\s+/g, ' ').trim();

  return cleaned;
}

export function infer(input: string): string {
  // Enforce input preprocessing to strip triggers and normalize input
  const sanitizedInput = preprocessInput(input);

  const tokens = tokenize(sanitizedInput);

  return runModel(tokens);
}