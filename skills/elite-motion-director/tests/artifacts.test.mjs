import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {safeTitle,artifactNames,outputPaths,claimArtifacts} from '../scripts/artifacts.mjs';
import {config,assertBundle} from '../scripts/lib.mjs';

test('video HTML cover and source use exactly the same Chinese title',()=>{
 const n=artifactNames('光的旅程');
 assert.equal(n.video,'光的旅程.mp4');assert.equal(n.html,'光的旅程.html');
 assert.equal(n.cover,'光的旅程_封面.png');assert.equal(n.source,'光的旅程_源码.zip');assert.equal(n.sourceRoot,'光的旅程_源码');
});
test('unsafe punctuation is normalized without translating a Chinese title',()=>{
 assert.equal(safeTitle('光/影: 为什么?'),'光／影： 为什么？');
 assert.equal(safeTitle('../旧\\新\n片*'),'_..／旧＼新 片＊');
});
test('cross-platform names handle reserved names, Unicode and path limits',()=>{
 assert.equal(safeTitle('CON'),'_CON');assert.equal(safeTitle('e\u0301'),'é');
 assert.equal(safeTitle('《星际之旅》'),'《星际之旅》');
 assert.ok(Buffer.byteLength(safeTitle('光'.repeat(200)))<=180);
 assert.throws(()=>safeTitle('....'));assert.throws(()=>safeTitle('【名称】'));assert.throws(()=>safeTitle(''));
});
test('version suffix applies to the entire deliverable set, not just MP4',()=>{
 const n=artifactNames('光的旅程','v2');assert.equal(n.html,'光的旅程_v2.html');assert.equal(n.source,'光的旅程_v2_源码.zip');
});
test('sourceRoot is a single safe segment and paths stay within output',()=>{
 const names=artifactNames('../../escape');const paths=outputPaths('/tmp/output',names);
 for(const v of Object.values(paths))assert.equal(path.dirname(v),'/tmp/output');
 assert.ok(!names.sourceRoot.includes('/'));
});
test('config resolves output paths from its title with no final fallback',async()=>{
 const root=await fs.mkdtemp(path.join(os.tmpdir(),'motion-name-'));
 try{const f=path.join(root,'motion.project.json');await fs.writeFile(f,JSON.stringify({title:'相遇的轨迹',width:640,height:360,fps:30,duration:1}));
 const c=await config(f);assert.equal(c.names.video,'相遇的轨迹.mp4');assert.equal(c.names.html,'相遇的轨迹.html');
 assert.throws(()=>assertBundle(c,{title:'旧名称'}));
 }finally{await fs.rm(root,{recursive:true,force:true});}
});
test('owned updates work; unowned same-name files are preserved',async()=>{
 const root=await fs.mkdtemp(path.join(os.tmpdir(),'motion-own-'));
 try{const names=artifactNames('同名视频');const c={out:root,names,files:outputPaths(root,names),title:'同名视频',configPath:path.join(root,'one.json')};
 await fs.writeFile(c.files.video,'existing');await assert.rejects(()=>claimArtifacts(c));
 assert.equal(await fs.readFile(c.files.video,'utf8'),'existing');
 await fs.rm(c.files.video);await claimArtifacts(c);await fs.writeFile(c.files.video,'ours');await claimArtifacts(c);
 await assert.rejects(()=>claimArtifacts({...c,configPath:path.join(root,'other.json')}));
 }finally{await fs.rm(root,{recursive:true,force:true});}
});
