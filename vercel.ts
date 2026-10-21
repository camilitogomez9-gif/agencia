import { routes, type VercelConfig } from '@vercel/config/v1';

export const config: VercelConfig = {
  buildCommand: 'npm run build',
  framework: 'nextjs',

  // Deploy automático en estas ramas
  deploymentBranches: ['main', 'saas-v1'],

  // Environment variables por rama
  env: {
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL || 'https://camilo-workspace.vercel.app',
  },

  // Rewrites y redirects si los necesitas
  rewrites: [],
  redirects: [],
};
