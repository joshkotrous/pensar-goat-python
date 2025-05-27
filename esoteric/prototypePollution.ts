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

const blockedKeys = new Set(['__proto__', 'constructor', 'prototype']);

function isSafeKey(key: string): boolean {
  return !blockedKeys.has(key);
}

function deepMerge<T extends Record<string, any>>(target: T, source: T): T {
  for (const key of Object.keys(source)) {
    if (!isSafeKey(key)) {
      continue;
    }
    if (
      typeof source[key] === 'object' &&
      source[key] !== null &&
      !Array.isArray(source[key])
    ) {
      target[key] = deepMerge(
        (typeof target[key] === 'object' && target[key] !== null && !Array.isArray(target[key]))
          ? target[key]
          : {},
        source[key] as any
      );
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