import { externalBrowserDisabled, fatal } from './lib.mjs';
// Retain the legacy command as a fail-fast guard, without touching project files.
fatal(externalBrowserDisabled());
