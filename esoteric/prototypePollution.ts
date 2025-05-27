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
  // Get the requested path, default to 'report.txt'
  const paramPath = (req.query.path ?? 'report.txt');
  if (typeof paramPath !== 'string') {
    res.status(400).json({ error: 'Invalid path parameter' });
    return;
  }

  // Normalize the path using POSIX methods to prevent Windows separator issues
  // Prevent directory traversal by normalizing and checking the path
  let normPath = path.posix.normalize('/' + paramPath);

  // Deny if normalized path contains any traversal (../) or is absolute
  if (
    normPath.includes('..') ||
    normPath.startsWith('/..') ||
    normPath.includes('\\\\') ||
    normPath.includes('\0') ||
    normPath.startsWith('//')
  ) {
    res.status(400).json({ error: 'Invalid file path' });
    return;
  }

  // Remove leading slash to use with join (avoids absolute path)
  const relPath = normPath.startsWith('/') ? normPath.substring(1) : normPath;

  // Join with ROOT, ensuring final path resolves inside ROOT
  const filePath = path.posix.join(ROOT, relPath);

  // Confirm resulting file path is strictly inside ROOT
  if (!filePath.startsWith(ROOT)) {
    res.status(400).json({ error: 'Invalid file path' });
    return;
  }

  try {
    const content = await fs.readFile(filePath, 'utf8');
    res.type('text/plain').send(content);
  } catch (err: any) {
    if (err.code === 'ENOENT') {
      res.status(404).send('File not found');
    } else {
      res.status(500).send('Error reading file');
    }
  }
});

export default app;