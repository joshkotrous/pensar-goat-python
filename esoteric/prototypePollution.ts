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
  try {
    // Resolve the absolute path based on ROOT
    const resolvedRoot = path.resolve(ROOT);
    const resolvedPath = path.resolve(ROOT, userPath);

    // Ensure the resolved path is within ROOT
    if (
      resolvedPath !== resolvedRoot &&
      !resolvedPath.startsWith(resolvedRoot + path.sep)
    ) {
      return res.status(400).json({ error: 'Invalid file path' });
    }

    // Attempt to read the file
    const data = await fs.readFile(resolvedPath, 'utf8');
    res.json({ file: userPath, contents: data });
  } catch (err: any) {
    if (err.code === 'ENOENT') {
      res.status(404).json({ error: 'File not found' });
    } else {
      res.status(500).json({ error: 'Internal server error' });
    }
  }
});

export default app;