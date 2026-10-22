#!/usr/bin/env node
import { getOptions, openRenderer } from './render-common.mjs';

try {
  if (process.argv.slice(2).includes('--help')) await getOptions('preview', ['--help']);
  else await openRenderer();
} catch (error) { console.error(`${error.code || 'ERROR'}: ${error.message}`); process.exitCode = 1; }
