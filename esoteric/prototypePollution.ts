import express, { Request, Response, NextFunction } from 'express';
import fs from 'fs/promises';
import path from 'path';

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

function deepMerge<T extends Record<string, any>>(target: T, source: T): T {
  for (const key of Object.keys(source)) {
    if (
      typeof source[key] === 'object' &&
      source[key] !== null &&
      !Array.isArray(source[key])
    ) {
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
  const { path: userPath = 'report.txt' } = req.query as { path?: string };
  if (typeof userPath !== 'string') {
    return res.status(400).json({ error: 'Invalid path' });
  }

  // Prevent path traversal: join with ROOT, normalize, and verify containment
  const normalizedPath = path.normalize(userPath).replace(/^(\\.{2}[\\/\\\\])+/, '');
  const filePath = path.resolve(ROOT, normalizedPath);

  if (!filePath.startsWith(path.resolve(ROOT))) {
    return res.status(400).json({ error: 'Invalid file path' });
  }

  try {
    const data = await fs.readFile(filePath, 'utf-8');
    res.type('text/plain').send(data);
  } catch (err) {
    res.status(404).json({ error: 'File not found' });
  }
});

// ... other routes or middleware as needed