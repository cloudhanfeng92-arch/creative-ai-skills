import fs from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {config,run,sha,fatal,assertBundle} from './lib.mjs';
import {preserveReview} from './visual-review.mjs';

async function save(file,report){
 await fs.mkdir(path.dirname(file),{recursive:true});
 const temporary=`${file}.${process.pid}.tmp`;
 await fs.writeFile(temporary,JSON.stringify(report,null,2)+'\n');
 await fs.rename(temporary,file);
}
async function fileHash(file){const hash=crypto.createHash('sha256');for await(const chunk of createReadStream(file))hash.update(chunk);return hash.digest('hex');}

export async function verify(configPath,{runner=run}={}){
 if(!configPath)throw new Error('用法：node verify.mjs motion.project.json');
 const absolute=path.resolve(configPath),root=path.dirname(absolute);
 let reportFile=path.join(root,'output','verification.json'),previous=null;
 const unknown={videoSHA256:null,coverSHA256:null};
 const report={schemaVersion:2,checkedAt:new Date().toISOString(),technical:{status:'running'},offline:{status:'not-checked'},scope:'media-and-bundle-only',
  artDirection:'需要实际观察；本脚本不评判美感',physics:'需要按当前对象约束检查；本脚本不推断',listening:'未试听：本脚本不能替代听感检查',visualReview:preserveReview(null,unknown)};
 try{
  // Resolve the report before validating specs, so invalid specs replace an old pass.
  const raw=JSON.parse(await fs.readFile(absolute,'utf8'));
  if(typeof raw?.output==='string')reportFile=path.join(path.resolve(root,raw.output),'verification.json');
  try{previous=JSON.parse(await fs.readFile(reportFile,'utf8'));}catch(error){if(error.code!=='ENOENT')throw new Error(`旧验证报告无法读取：${error.message}`);}
  if(previous?.visualReview)report.visualReview=preserveReview(previous.visualReview,unknown);
  await save(reportFile,report);
  const c=await config(absolute),file=c.files.video;
  report.files=c.names;
  const basis={videoSHA256:await fileHash(file),coverSHA256:null};
  const cover=await fs.readFile(c.files.cover);basis.coverSHA256=sha(cover);
  report.artifacts=basis;
  report.visualReview=preserveReview(previous?.visualReview,basis,c.duration);
  const probe=JSON.parse((await runner('ffprobe',['-v','error','-show_streams','-show_format','-of','json',file])).stdout);
  const v=probe.streams?.find(s=>s.codec_type==='video'),a=probe.streams?.find(s=>s.codec_type==='audio');
  if(!v||v.width!==c.width||v.height!==c.height)throw new Error('视频尺寸不匹配');
  const fraction=value=>{const [n,d='1']=String(value).split('/');return Number(n)/Number(d);};
  if(!Number.isFinite(fraction(v.avg_frame_rate))||Math.abs(fraction(v.avg_frame_rate)-c.fps)>1e-5)throw new Error('平均帧率不匹配');
  const duration=Number(v.duration||probe.format?.duration);
  if(!Number.isFinite(duration)||Math.abs(duration-c.duration)>2/c.fps)throw new Error('视频时长不匹配');
  if(!!a!==!!c.audio)throw new Error('音轨状态不匹配');
  const threads=String(Math.max(1,Math.min(2,Math.trunc(Number(c.threads)||2))));
  await runner('ffmpeg',['-nostdin','-v','error','-xerror','-threads',threads,'-filter_threads',threads,'-filter_complex_threads',threads,'-i',file,'-threads',threads,'-f','null','-']);
  report.technical={status:'running',width:v.width,height:v.height,fps:v.avg_frame_rate,codec:v.codec_name,duration,audio:a?.codec_name||null,decoded:true};
  const html=await fs.readFile(c.files.html,'utf8'),manifest=JSON.parse(await fs.readFile(path.join(c.out,'bundle-manifest.json'),'utf8'));
  assertBundle(c,manifest);
  const renderLog=JSON.parse(await fs.readFile(path.join(c.out,'render-log.json'),'utf8'));
  if(renderLog.status!=='complete'||renderLog.bundleSHA256!==manifest.htmlSHA256)throw new Error('视频与当前HTML包不对应或渲染未完成');
  if(cover.length<24||cover.toString('ascii',1,4)!=='PNG'||cover.readUInt32BE(16)!==c.width||cover.readUInt32BE(20)!==c.height)throw new Error('封面不存在或尺寸/格式不正确');
  if(sha(html)!==manifest.htmlSHA256)throw new Error('HTML打包后已改变；重新打包再验证');
  if(c.audio){const bytes=await fs.readFile(c.audio);if(sha(bytes)!==manifest.audioSHA256||!html.includes(bytes.toString('base64')))throw new Error('HTML与最终混音不同源');}
  report.offline={status:'not-checked',reason:'CLI仅核对HTML文件及素材哈希，未实际运行HTML；播放、暂停、拖动、重播和断网能力需按需通过Codex内置浏览器检查。',bundleHashVerified:true,audioUsesSameMaster:!!c.audio};
  report.technical.status='passed';
  await save(reportFile,report);
  return report;
 }catch(error){
  report.technical={...report.technical,status:'failed',error:error.message};
  await save(reportFile,report);
  throw error;
 }
}

async function main(){
 const args=process.argv.slice(2);
 if(args[0]==='--help'){console.log('用法：node verify.mjs motion.project.json\n一次FFmpeg解码与规格/哈希检查；visualReview由实际观察填写，内容哈希变化后需复查。');return;}
 if(args.length!==1)throw new Error('用法：node verify.mjs motion.project.json');
 console.log(JSON.stringify(await verify(args[0]),null,2));
}
if(process.argv[1]&&pathToFileURL(path.resolve(process.argv[1])).href===import.meta.url)main().catch(fatal);
