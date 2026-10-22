import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {verify} from '../scripts/verify.mjs';
import {preserveReview,reviewStatus} from '../scripts/visual-review.mjs';
import {config,sha} from '../scripts/lib.mjs';

const basis={videoSHA256:'a'.repeat(64),coverSHA256:'b'.repeat(64)};
const observed=()=>({...preserveReview(null,basis),status:'reviewed',coverage:[{start:0,end:2,kind:'continuous',playbackRate:1}],cover:{status:'reviewed',notes:'标题与主体清楚'},constraints:'仅记录实际观察；不推断未看内容'});
const issue={id:'subtitle-1',area:'video',start:0.8,end:1.2,description:'一处字幕遮挡',status:'open'};

test('technical completion never creates visual coverage; only genuine full-speed records derive reviewed',()=>{
 const blank=preserveReview(null,basis);assert.equal(blank.status,'not-checked');
 const review=observed();assert.equal(preserveReview(review,basis,2).status,'reviewed');
 review.constraints=[];assert.equal(reviewStatus(review,2),'partial');review.constraints='约束已检查';
 review.coverage=[{start:0,end:2,kind:'keyframe',playbackRate:1}];assert.equal(preserveReview(review,basis,2).status,'partial');
 review.coverage=[{start:0,end:2,kind:'continuous',playbackRate:2}];assert.equal(reviewStatus(review,2),'partial');
 review.coverage=[{start:0,end:0.9,kind:'continuous',playbackRate:1},{start:1.1,end:2,kind:'continuous',playbackRate:1}];assert.equal(reviewStatus(review,2),'partial');
 review.coverage=[{start:0,end:1,kind:'continuous',playbackRate:1},{start:1,end:2,kind:'continuous',playbackRate:1}];assert.equal(reviewStatus(review,2),'reviewed');
 review.issues=[issue];assert.equal(preserveReview(review,basis,2).status,'issues-open');
 review.issues=[{...issue,status:'fixed-pending-review'}];assert.equal(reviewStatus(review,2),'issues-open');
 review.issues=[{...issue,status:'resolved',needsRecheck:true}];assert.equal(reviewStatus(review,2),'issues-open');
});

test('changed video or cover clears current coverage and retains one old snapshot plus issue tracking',()=>{
 for(const key of ['videoSHA256','coverSHA256']){
  const old=observed();old.issues=[{...issue,status:'resolved'}];
  const changed={...basis,[key]:'c'.repeat(64)};
  const next=preserveReview(old,changed,2);
  assert.equal(next.status,'needs-review');assert.deepEqual(next.coverage,[]);assert.equal(next.cover.status,'not-checked');
  assert.equal(next.issues[0].needsRecheck,true);assert.equal(next.history.length,1);assert.deepEqual(next.history[0].coverage,old.coverage);
  assert.equal(old.issues[0].needsRecheck,undefined);
  const again=preserveReview(next,{...changed,[key]:'d'.repeat(64)},2);assert.equal(again.history.length,1);assert.equal(again.history[0].history,undefined);assert.deepEqual(again.history[0].coverage,old.coverage);
 }
 const fresh=preserveReview(observed(),{...basis,videoSHA256:'c'.repeat(64)},2);
 assert.equal(preserveReview(fresh,fresh.basis,2).status,'needs-review');
 const shorter=preserveReview({...observed(),issues:[issue]},{...basis,videoSHA256:'d'.repeat(64)},0.5);
 assert.equal(preserveReview(shorter,shorter.basis,0.5).status,'issues-open');
 assert.equal(shorter.issues[0].start,0.8);
});

test('unknown hashes never approve old observations and restored identical files recover them',()=>{
 const old=observed(),unknown={videoSHA256:null,coverSHA256:null};
 let next=preserveReview(old,unknown);
 for(let i=0;i<3;i++)next=preserveReview(next,unknown);
 assert.equal(next.status,'needs-review');assert.equal(next.history.length,1);
 const recovered=preserveReview(next,basis,2);assert.equal(recovered.status,'reviewed');assert.deepEqual(recovered.coverage,old.coverage);
});

test('invalid observation fields are rejected, constraints may be text or text array',()=>{
 const value=observed();value.constraints=['只看到已记录的片段'];assert.equal(reviewStatus(value,2),'reviewed');
 value.coverage[0].end=3;assert.throws(()=>reviewStatus(value,2),/coverage/);
 value.coverage[0].end=2;value.issues=[issue,issue];assert.throws(()=>reviewStatus(value,2),/唯一/);
});

async function fixture(){
 const root=await fs.mkdtemp(path.join(os.tmpdir(),'motion-verify-'));
 const project=path.join(root,'motion.project.json');
 await fs.writeFile(project,JSON.stringify({title:'观察测试',width:320,height:180,fps:30,duration:2,output:'deliverables'}));
 const c=await config(project);await fs.mkdir(c.out);
 const html='<!doctype html><title>观察测试</title>';
 const cover=Buffer.alloc(24);cover.write('PNG',1);cover.writeUInt32BE(320,16);cover.writeUInt32BE(180,20);
 await fs.writeFile(c.files.video,'fake-video-fixture');await fs.writeFile(c.files.cover,cover);await fs.writeFile(c.files.html,html);
 await fs.writeFile(path.join(c.out,'bundle-manifest.json'),JSON.stringify({title:c.title,files:c.names,configSHA256:c.configSHA256,htmlSHA256:sha(html)}));
 await fs.writeFile(path.join(c.out,'render-log.json'),JSON.stringify({status:'complete',bundleSHA256:sha(html)}));
 const calls=[];
 const runner=async(name,args)=>{calls.push({name,args});return name==='ffprobe'?{stdout:JSON.stringify({streams:[{codec_type:'video',width:320,height:180,avg_frame_rate:'30/1',duration:'2',codec_name:'h264'}],format:{duration:'2'}})}:{stdout:''};};
 return {root,project,c,runner,calls,reportFile:path.join(c.out,'verification.json')};
}

test('one decode per verification; unchanged observations survive and final content changes invalidate them',async()=>{
 const f=await fixture();
 try{
  const first=await verify(f.project,{runner:f.runner});assert.equal(first.technical.status,'passed');assert.equal(first.visualReview.status,'not-checked');
  assert.equal(f.calls.filter(x=>x.name==='ffmpeg').length,1);
  first.visualReview={...observed(),basis:first.artifacts,issues:[{...issue,status:'resolved'}]};
  await fs.writeFile(f.reportFile,JSON.stringify(first));
  const same=await verify(f.project,{runner:f.runner});assert.equal(same.visualReview.status,'reviewed');assert.deepEqual(same.visualReview.coverage,first.visualReview.coverage);
  await fs.appendFile(f.c.files.video,'changed');
  const changed=await verify(f.project,{runner:f.runner});assert.equal(changed.visualReview.status,'needs-review');assert.equal(changed.visualReview.issues[0].needsRecheck,true);assert.equal(changed.visualReview.history.length,1);
 }finally{await fs.rm(f.root,{recursive:true,force:true});}
});

test('probe/decode/bundle/config failures replace old passing reports and expose running state before tools',async()=>{
 for(const failure of ['probe','decode','bundle','config']){
  const f=await fixture();
  try{
   const old=await verify(f.project,{runner:f.runner});old.visualReview={...observed(),basis:old.artifacts};await fs.writeFile(f.reportFile,JSON.stringify(old));
   if(failure==='bundle')await fs.appendFile(f.c.files.html,'changed');
   if(failure==='config'){const raw=JSON.parse(await fs.readFile(f.project,'utf8'));raw.width=0;await fs.writeFile(f.project,JSON.stringify(raw));}
   const runner=async(name,args)=>{
    const inProgress=JSON.parse(await fs.readFile(f.reportFile,'utf8'));assert.equal(inProgress.technical.status,'running');
    if((failure==='probe'&&name==='ffprobe')||(failure==='decode'&&name==='ffmpeg'))throw new Error(`test ${failure} failure`);
    return f.runner(name,args);
   };
   await assert.rejects(()=>verify(f.project,{runner}));
   const failed=JSON.parse(await fs.readFile(f.reportFile,'utf8'));assert.equal(failed.technical.status,'failed');assert.ok(failed.technical.error);assert.notEqual(failed.offline.status,'passed');
   if(failure!=='config')assert.equal(failed.visualReview.status,'reviewed');
  }finally{await fs.rm(f.root,{recursive:true,force:true});}
 }
});
