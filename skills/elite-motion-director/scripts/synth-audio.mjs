import fs from 'node:fs/promises';
import path from 'node:path';
import { fatal } from './lib.mjs';
const TAU=Math.PI*2, clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
function rng(seed){let a=seed>>>0;return()=>{a+=0x6D2B79F5;let t=a;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return((t^t>>>14)>>>0)/4294967296;};}
function osc(kind,phase,f,sr){
  if(kind==='triangle')return 2/Math.PI*Math.asin(Math.sin(phase));
  if(kind==='saw'||kind==='square'){
    let s=0;const n=Math.min(24,Math.floor(sr/(2*f)));
    for(let k=1;k<=n;k++){if(kind==='square'&&k%2===0)continue;s+=Math.sin(phase*k)/k;}
    return s*(kind==='square'?4/Math.PI:2/Math.PI);
  }
  return Math.sin(phase);
}
async function main(){
  const [input,output]=process.argv.slice(2);if(!input||!output)throw new Error('用法：node synth-audio.mjs score.json mix.wav');
  const s=JSON.parse(await fs.readFile(input,'utf8')),sr=s.sampleRate||48000;
  if(!Number.isFinite(s.duration)||s.duration<=0||s.duration>600)throw new Error('duration须在0—600秒之间');
  if(![44100,48000].includes(sr))throw new Error('sampleRate支持44100或48000');
  const n=Math.round(s.duration*sr),L=new Float32Array(n),R=new Float32Array(n);
  const events=[...(s.notes||[]),...(s.sfx||[])];
  if(!events.length)throw new Error('没有声音事件；静音影片应跳过合成步骤');
  let index=0;
  for(const e of events){
    const t=Number(e.t),dur=Number(e.duration),amp=Number(e.amp??0.15),kind=e.kind||'sine';
    if(!Number.isFinite(t)||t<0||!Number.isFinite(dur)||dur<=0||!Number.isFinite(amp)||amp<0)throw new Error('无效音频事件时间/时长/幅度');
    if(!['sine','triangle','saw','square','fm','pluck','noise','whoosh','kick'].includes(kind))throw new Error(`不支持音色 ${kind}`);
    const f=Number(e.freq??440*Math.pow(2,((e.midi??60)-69)/12));
    if(!Number.isFinite(f)||f<=0||f>sr/4)throw new Error('音高无效或过高');
    const rand=rng((s.seed??1)+index++*7919),pan=clamp(Number(e.pan??0),-1,1),gl=Math.cos((pan+1)*Math.PI/4),gr=Math.sin((pan+1)*Math.PI/4);
    const start=Math.round(t*sr),length=Math.round(dur*sr),attack=Math.min(dur/4,e.attack??0.008),release=Math.min(dur/2,e.release??0.12);
    let low=0;
    for(let j=0;j<length&&start+j<n;j++){
      const u=j/sr,env=Math.min(1,u/Math.max(1/sr,attack))*Math.min(1,(dur-u)/Math.max(1/sr,release));
      let v;
      if(kind==='noise')v=rand()*2-1;
      else if(kind==='whoosh'){const noise=rand()*2-1;low+=0.08*(noise-low);v=(noise-low)*Math.sin(Math.PI*u/dur)**2;}
      else if(kind==='kick'){const phase=TAU*(f*u+f*3*(1-Math.exp(-25*u))/25);v=Math.sin(phase)*Math.exp(-u*18);}
      else if(kind==='fm'){v=Math.sin(TAU*f*u+(e.modIndex??1.8)*Math.exp(-u*2/dur)*Math.sin(TAU*f*(e.ratio??2)*u));}
      else if(kind==='pluck'){v=(Math.sin(TAU*f*u)+0.3*Math.sin(TAU*2*f*u)+0.12*Math.sin(TAU*3*f*u))*Math.exp(-u*5/dur)/1.42;}
      else v=osc(kind,TAU*f*u,f,sr);
      const x=v*env*amp;L[start+j]+=x*gl;R[start+j]+=x*gr;
    }
  }
  let peak=0,sum=0;
  for(let i=0;i<n;i++){
    const time=i/sr;let gain=Math.min(1,time/0.015,(s.duration-time)/0.035);
    for(const g of s.sectionGain||[]){if(time>=g.start&&time<=g.end){const fade=Math.min(0.05,(g.end-g.start)/2);const blend=Math.min(1,(time-g.start)/fade,(g.end-time)/fade);gain*=1+(g.gain-1)*Math.max(0,blend);}}
    L[i]*=gain;R[i]*=gain;peak=Math.max(peak,Math.abs(L[i]),Math.abs(R[i]));sum+=L[i]**2+R[i]**2;
  }
  if(!Number.isFinite(peak)||peak===0)throw new Error('生成轨道无有效信号');
  const target=clamp(s.peak??0.85,0.05,0.98),gain=Math.min(1,target/peak),bytes=Buffer.alloc(44+n*4);
  bytes.write('RIFF',0);bytes.writeUInt32LE(36+n*4,4);bytes.write('WAVEfmt ',8);bytes.writeUInt32LE(16,16);bytes.writeUInt16LE(1,20);bytes.writeUInt16LE(2,22);bytes.writeUInt32LE(sr,24);bytes.writeUInt32LE(sr*4,28);bytes.writeUInt16LE(4,32);bytes.writeUInt16LE(16,34);bytes.write('data',36);bytes.writeUInt32LE(n*4,40);
  for(let i=0;i<n;i++){bytes.writeInt16LE(Math.round(clamp(L[i]*gain,-1,1)*32767),44+i*4);bytes.writeInt16LE(Math.round(clamp(R[i]*gain,-1,1)*32767),46+i*4);}
  await fs.mkdir(path.dirname(path.resolve(output)),{recursive:true});await fs.writeFile(output,bytes);
  console.log(JSON.stringify({path:path.resolve(output),seconds:n/sr,sampleRate:sr,channels:2,events:events.length,peak:peak*gain,rms:Math.sqrt(sum/(2*n))*gain}));
}
main().catch(fatal);
