import fs from 'node:fs/promises';
import path from 'node:path';
import {sha,run,writeJSON,fatal} from './lib.mjs';
async function main(){
 const root=path.resolve(process.argv[2]||'.'),cache=path.join(root,'.motion-cache/environment.json');
 const inputs=[process.version,process.platform,process.arch,'codex-in-app-only-v2.1.2'];
 for(const name of ['package.json','package-lock.json','pnpm-lock.yaml','yarn.lock']){try{inputs.push(await fs.readFile(path.join(root,name),'utf8'));}catch{}}
 const names=process.platform==='win32'?['ffmpeg.exe','ffprobe.exe']:['ffmpeg','ffprobe'];const exePaths=[];
 for(const name of names){let match=null;for(const d of (process.env.PATH||'').split(path.delimiter)){try{const p=path.join(d,name),st=await fs.stat(p);if(st.isFile()){match=p;inputs.push(`${p}:${st.size}:${st.mtimeMs}`);break;}}catch{}}exePaths.push(match);}
 const fingerprint=sha(inputs.join('\n'));try{const old=JSON.parse(await fs.readFile(cache,'utf8'));if(old.fingerprint===fingerprint){console.log(JSON.stringify({...old,cacheHit:true},null,2));return;}}catch{}
 const result={fingerprint,cacheHit:false,node:process.version,platform:process.platform,browserPolicy:'codex-in-app-only',inAppBrowserCapabilities:'not-checked-by-cli',webPreview:'optional',externalBrowserLaunch:'disabled',tools:{},checkedAt:new Date().toISOString()};
 for(let i=0;i<names.length;i++){try{result.tools[names[i]]=(await run(exePaths[i]||names[i],['-version'])).stdout.split('\n')[0];}catch(e){result.tools[names[i]]=`不可用：${e.message}`;}}
 await writeJSON(cache,result);console.log(JSON.stringify(result,null,2));
}
main().catch(fatal);
