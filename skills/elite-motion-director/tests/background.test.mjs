import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {fileURLToPath} from 'node:url';
import {backgroundLaunchOptions,launch,playwright,openFilm,config} from '../scripts/lib.mjs';
const disabled={code:'EXTERNAL_BROWSER_DISABLED'};

test('legacy launch rejects without loading modules or reading browser configuration',async()=>{
 let loaded=false;
 const hostile=new Proxy({}, {get(){throw new Error('must not inspect');}});
 await assert.rejects(launch('/unused',{environment:hostile,loadPlaywright:async()=>{loaded=true;}}),disabled);
 assert.equal(loaded,false);
 await assert.rejects(playwright('/unused'),disabled);
 await assert.rejects(openFilm(hostile,hostile),disabled);
 assert.throws(()=>backgroundLaunchOptions(hostile),disabled);
});

test('legacy render CLI rejects before creating files even with old browser environment values',async()=>{
 const root=await fs.mkdtemp(path.join(os.tmpdir(),'motion-browser-guard-'));
 try{
  const renderer=fileURLToPath(new URL('../scripts/render.mjs',import.meta.url));
  await assert.rejects(promisify(execFile)(process.execPath,[renderer,path.join(root,'missing.json')],{
   cwd:root,env:{...process.env,MOTION_PLAYWRIGHT_MODULE:'/must-not-load',CHROMIUM_EXECUTABLE:'/must-not-run',PWDEBUG:'1'}
  }),error=>{assert.equal(error.code,1);assert.match(error.stderr,/EXTERNAL_BROWSER_DISABLED/);assert.doesNotMatch(error.stderr,/ENOENT/);return true;});
  assert.deepEqual(await fs.readdir(root),[]);
 }finally{await fs.rm(root,{recursive:true,force:true});}
});

test('project overrides cannot change the built-in-only policy or block non-browser commands',async()=>{
 const root=await fs.mkdtemp(path.join(os.tmpdir(),'motion-config-'));
 try{
  const file=path.join(root,'motion.project.json');
  for(const headless of [true,false]){
   await fs.writeFile(file,JSON.stringify({title:'内置浏览器策略',width:640,height:360,fps:30,duration:1,headless,browserPolicy:'external'}));
   const c=await config(file);assert.equal(c.frames,30);assert.equal(c.browserPolicy,'codex-in-app-only');
  }
 }finally{await fs.rm(root,{recursive:true,force:true});}
});
