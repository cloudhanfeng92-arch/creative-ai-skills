import fs from 'node:fs/promises';
import path from 'node:path';
import { spawn } from 'node:child_process';
import crypto from 'node:crypto';
import { artifactNames, outputPaths } from './artifacts.mjs';
export const sha = b => crypto.createHash('sha256').update(b).digest('hex');
export const exists = async p => {try {await fs.access(p); return true;} catch {return false;}};
export async function config(file) {
  if (!file) throw new Error('用法：node script.mjs /实际项目/motion.project.json');
  const abs=path.resolve(file), text=await fs.readFile(abs,'utf8'), raw=JSON.parse(text);
  for (const k of ['width','height','fps','duration']) if(!Number.isFinite(raw[k]) || raw[k]<=0) throw new Error(`无效配置 ${k}`);
  if (!Number.isInteger(raw.width)||!Number.isInteger(raw.height)||raw.width%2||raw.height%2) throw new Error('H.264/yuv420p宽高须为正偶数');
  if (raw.fps>120 || raw.width>8192 || raw.height>8192 || raw.duration>3600) throw new Error('配置超过脚本保守资源限制；请按工程需要明确调整实现');
  if (typeof raw.title!=='string' || !raw.title.trim() || /【|】/.test(raw.title)) throw new Error('填写本条实际主题标题，不使用占位标题');
  const root=path.dirname(abs), frames=Math.round(raw.duration*raw.fps);
  if(frames<1)throw new Error('时长至少需要一个输出帧');
  const c={...raw,title:raw.title.trim(),duration:frames/raw.fps,frames,root,configPath:abs,configSHA256:sha(text),browserPolicy:'codex-in-app-only'};
  c.out=path.resolve(root,raw.output||'output');
  c.names=artifactNames(c.title,raw.outputRevision);c.files=outputPaths(c.out,c.names);
  c.entry=path.resolve(root,raw.entry||'visual.js');
  c.audio=raw.audio?path.resolve(root,raw.audio):null;
  c.coverTime=Number.isFinite(raw.coverTime)?Math.max(0,Math.min(raw.coverTime,c.duration-1/c.fps)):Math.min(1,c.duration/2);
  return c;
}
export function run(program,args,options={}) {
  return new Promise((resolve,reject)=>{
    const p=spawn(program,args,{stdio:['ignore','pipe','pipe'],...options,windowsHide:true});
    let out='',err='';
    p.stdout?.on('data',b=>out+=b);p.stderr?.on('data',b=>{err=(err+b).slice(-200000);});
    p.on('error',reject);p.on('close',code=>code===0?resolve({stdout:out,stderr:err}):reject(new Error(`${program}退出${code}\n${err.slice(-6000)}`)));
  });
}
// Legacy browser entry points fail before reading configuration, importing modules,
// starting a service, or accessing any browser. In-app tools are a host capability,
// not an executablePath or CDP endpoint for this CLI.
export function externalBrowserDisabled() {
  const error=new Error('EXTERNAL_BROWSER_DISABLED：本技能仅允许 Codex 内置浏览器。旧独立浏览器渲染入口已停用。需要网页操作时使用宿主官方内置浏览器工具并核对实际能力；网页预览按需。若无法导出，只能复用已有兼容的无浏览器后端，或报告 MP4 尚未完成；禁止启动或连接 Google Chrome、Chrome for Testing 及其他外部浏览器。');
  error.code='EXTERNAL_BROWSER_DISABLED';
  return error;
}
export async function playwright() { throw externalBrowserDisabled(); }
export function backgroundLaunchOptions() { throw externalBrowserDisabled(); }
export async function launch() { throw externalBrowserDisabled(); }
export async function openFilm() { throw externalBrowserDisabled(); }
export async function writeJSON(file,obj){await fs.mkdir(path.dirname(file),{recursive:true});await fs.writeFile(file,JSON.stringify(obj,null,2)+'\n');}
export function fatal(e){console.error(e?.stack||e);process.exitCode=1;}

export function assertBundle(c,bundle){
  if(bundle.title!==c.title || bundle.files?.html!==c.names.html || bundle.configSHA256!==c.configSHA256)throw new Error('当前标题/配置与HTML包不匹配；先运行pack-html，再导出视频，不能只改单个文件名');
}
