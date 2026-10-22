import fs from 'node:fs/promises';
import path from 'node:path';
import {deflateRawSync} from 'node:zlib';
import {config,exists,fatal} from './lib.mjs';
import {claimArtifacts} from './artifacts.mjs';
const table=Array.from({length:256},(_,n)=>{let c=n;for(let k=0;k<8;k++)c=c&1?0xedb88320^(c>>>1):c>>>1;return c>>>0;});
function crc(b){let c=0xffffffff;for(const v of b)c=table[(c^v)&255]^(c>>>8);return(c^0xffffffff)>>>0;}
const blockedDirs=new Set(['node_modules','.git','.motion-cache','.cache','__pycache__']);
const blockedFile=p=>/(^|\/)(\.env(?:\..*)?|auth\.json|credentials(?:\..*)?|secrets?(?:\..*)?)$/i.test(p)||/\.(woff2?|otf|ttf|ttc|eot|pem|key|p12|pfx|zip)$/i.test(p);
async function main(){
 const c=await config(process.argv[2]),files=new Map();
 const inside=p=>{const rel=path.relative(c.root,p);return rel&&!rel.startsWith('..'+path.sep)&&rel!=='..'&&!path.isAbsolute(rel);};
 async function collect(abs){
  abs=path.resolve(abs);if(!inside(abs))throw new Error(`源码引用位于项目外，请先有选择地复制到项目：${abs}`);
  if(abs===c.out||abs.startsWith(c.out+path.sep))return;
  const rel=path.relative(c.root,abs).split(path.sep).join('/');
  if(blockedFile(rel)||rel.split('/').some(x=>blockedDirs.has(x)))return;
  const st=await fs.lstat(abs);if(st.isSymbolicLink())return;
  if(st.isDirectory()){for(const name of await fs.readdir(abs))await collect(path.join(abs,name));}
  else if(st.isFile()){if(st.size>1024*1024*512)throw new Error('单文件超过512MB，需明确制定源素材交付方式');files.set(rel,await fs.readFile(abs));}
 }
 const paths=new Set([c.configPath,c.entry,...(c.css?[path.resolve(c.root,c.css)]:[]),...(c.audio?[c.audio]:[]),...Object.values(c.assets||{}).map(p=>path.resolve(c.root,p)),...(c.sourcePaths||[]).map(p=>path.resolve(c.root,p))]);
 for(const name of ['README.md','direction.md','source-notes.md','package.json','package-lock.json','pnpm-lock.yaml','yarn.lock','score.json','src','scripts','engine'])if(await exists(path.join(c.root,name)))paths.add(path.join(c.root,name));
 for(const p of paths)await collect(p);
 const bodies=[],central=[];let offset=0;
 for(const [name,data] of [...files].sort((a,b)=>a[0].localeCompare(b[0]))){
  const filename=Buffer.from(`${c.names.sourceRoot}/${name}`),packed=deflateRawSync(data,{level:6}),checksum=crc(data);
  const h=Buffer.alloc(30);h.writeUInt32LE(0x04034b50,0);h.writeUInt16LE(20,4);h.writeUInt16LE(0x800,6);h.writeUInt16LE(8,8);h.writeUInt16LE(33,12);h.writeUInt32LE(checksum,14);h.writeUInt32LE(packed.length,18);h.writeUInt32LE(data.length,22);h.writeUInt16LE(filename.length,26);
  const z=Buffer.alloc(46);z.writeUInt32LE(0x02014b50,0);z.writeUInt16LE(20,4);z.writeUInt16LE(20,6);z.writeUInt16LE(0x800,8);z.writeUInt16LE(8,10);z.writeUInt16LE(33,14);z.writeUInt32LE(checksum,16);z.writeUInt32LE(packed.length,20);z.writeUInt32LE(data.length,24);z.writeUInt16LE(filename.length,28);z.writeUInt32LE(offset,42);
  bodies.push(h,filename,packed);central.push(z,filename);offset+=h.length+filename.length+packed.length;
 }
 if(files.size>65535||offset>0xffffffff)throw new Error('超过基础ZIP格式限制，请使用项目可用的ZIP64工具');
 const cd=Buffer.concat(central),end=Buffer.alloc(22);end.writeUInt32LE(0x06054b50,0);end.writeUInt16LE(files.size,8);end.writeUInt16LE(files.size,10);end.writeUInt32LE(cd.length,12);end.writeUInt32LE(offset,16);
 await claimArtifacts(c);const file=c.files.source;await fs.writeFile(file,Buffer.concat([...bodies,cd,end]));console.log(`${file} (${files.size} files)`);
}
main().catch(fatal);
