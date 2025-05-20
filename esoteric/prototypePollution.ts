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

// List of dangerous keys to prevent prototype pollution
const unsafeKeys = ['__proto__', 'prototype', 'constructor'];

function isUnsafeKey(key: string): boolean {
  return unsafeKeys.includes(key);
}

function deepMerge<T extends Record<string, any>>(target: T, source: T): T {
  for (const key of Object.keys(source)) {
    if (isUnsafeKey(key)) {
      continue; // Skip unsafe keys to prevent prototype pollution
    }
    if (
      typeof source[key] === 'object' &&
      source[key] !== null &&
      !Array.isArray(source[key])
    ) {
      // Ensure target[key] is an object for recursion
      const targetValue = (typeof target[key] === 'object' && target[key] !== null)
        ? target[key]
        : {};
      target[key] = deepMerge(targetValue, source[key] as any);
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