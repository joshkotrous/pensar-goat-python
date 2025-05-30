import express, { Request, Response, NextFunction } from 'express';
import fs from 'fs/promises';


interface Preferences {
  theme: 'light' | 'dark';
  notifications: boolean;
  [key: string]: unknown;
}

const defaultPreferences: Preferences = {
  theme: 'light',
  notifications: true,
};

const globalPreferences: Preferences = { ...defaultPreferences };

// Dangerous keys to prevent prototype pollution
const DANGEROUS_KEYS = ['__proto__', 'prototype', 'constructor'] as const;
type DangerousKey = typeof DANGEROUS_KEYS[number];

function isDangerousKey(key: string): key is DangerousKey {
  return DANGEROUS_KEYS.includes(key as DangerousKey);
}

function deepMerge<T extends Record<string, any>>(target: T, source: T): T {
  for (const key of Object.keys(source)) {
    if (isDangerousKey(key)) {
      // Skip merging dangerous keys
      continue;
    }
    if (
      typeof source[key] === 'object' &&
      source[key] !== null &&
      !Array.isArray(source[key])
    ) {
      // Ensure target[key] is an object, or assign a new object
      target[key] = deepMerge(target[key] ?? {}, source[key] as any);
    } else {
      target[key] = source[key];
    }
  }
  return target;
}

const app = express();
app.use(express.json());

app.post('/preferences', (req: Request, res: Response) => {
  // Merges *user-supplied* JSON into a **global** object
  deepMerge(globalPreferences, req.body as Preferences);
  res.json({ ok: true, prefs: globalPreferences });
});

app.use((req, _res, next) => {
  req.user = { id: '123', isAdmin: false };
  next();
});

function requireAdmin(req: Request, res: Response, next: NextFunction) {
  if (req.user?.isAdmin) return next();
  res.status(403).json({ error: 'Forbidden – admins only' });
}

const ROOT = '/var/data/';

app.get('/internal/readFile', requireAdmin, async (req, res) => {
  const { path = 'report.txt' } = req.query as { path?: string