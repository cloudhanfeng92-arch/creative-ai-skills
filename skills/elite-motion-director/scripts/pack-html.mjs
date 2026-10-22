import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { config,sha,writeJSON,fatal } from './lib.mjs';
import { claimArtifacts } from './artifacts.mjs';
const here=path.dirname(fileURLToPath(import.meta.url));
const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const script=s=>s.replace(/<\/script/gi,'<\\/script');
const mime={'.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp','.svg':'image/svg+xml','.gif':'image/gif','.m4a':'audio/mp4','.aac':'audio/aac','.mp3':'audio/mpeg','.wav':'audio/wav','.ogg':'audio/ogg','.glb':'model/gltf-binary','.bin':'application/octet-stream','.json':'application/json'};
async function dataURL(file){
  const ext=path.extname(file).toLowerCase();
  if(/\.(woff2?|ttf|otf|ttc|eot)$/i.test(file))throw new Error('不分发字体文件；请用系统字体或本片实际文字的矢量路径');
  if(!(ext in mime))throw new Error(`未声明可内联的素材类型：${ext}`);
  const bytes=await fs.readFile(file);return `data:${mime[ext]};base64,${bytes.toString('base64')}`;
}
async function main(){
  const c=await config(process.argv[2]);
  const visual=await fs.readFile(c.entry,'utf8');
  if(/^\s*(import\s+(?!\()|export\s)/m.test(visual))throw new Error('先把visual.js打包成不含外部模块的IIFE/经典脚本');
  const css=c.css?await fs.readFile(path.resolve(c.root,c.css),'utf8'):'';
  if(/@font-face|data:font\/|url\([^)]*\.(?:woff2?|ttf|otf)/i.test(css+visual))throw new Error('交付内容不得内嵌或分发字体文件');
  const assets={};for(const [k,v] of Object.entries(c.assets||{}))assets[k]=await dataURL(path.resolve(c.root,v));
  const audio=c.audio?await dataURL(c.audio):null;
  const player=await fs.readFile(path.join(here,'../engine/player.js'),'utf8');
  const publicConfig={title:c.title,width:c.width,height:c.height,fps:c.fps,duration:c.duration,seed:c.seed??1,coverTime:c.coverTime,...(c.scene?{scene:c.scene}:{})};
  const title=escape(c.title), bg=escape(c.stageBackground||'#000000');
  const html=`<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${title}</title><style>
*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#080808}body{display:flex;flex-direction:column;align-items:center;justify-content:center}
#viewport{position:relative;flex:none;overflow:hidden}#stage{position:absolute;left:0;top:0;width:${c.width}px;height:${c.height}px;transform-origin:top left;overflow:hidden;background:${bg}}
#controls{height:44px;flex:none;width:min(94vw,900px);display:flex;gap:12px;align-items:center;color:#ddd;font:12px system-ui,sans-serif}#controls button{border:0;background:transparent;color:inherit;padding:8px;cursor:pointer}#scrub{flex:1;min-width:30px}#stamp{min-width:88px;text-align:right}#mix{display:none}
html[data-export="1"] body{display:block}html[data-export="1"] #controls{display:none}html[data-export="1"] #stage{transform:none!important}
${css.replace(/<\/style/gi,'<\\/style')}
</style></head><body><div id="viewport"><div id="stage" aria-label="${title}"></div></div>
<div id="controls"><button id="play" aria-label="播放或暂停">▶</button><button id="restart" aria-label="重新播放">↺</button><input id="scrub" type="range" min="0" value="0" aria-label="进度"><span id="stamp"></span></div>
${audio?`<audio id="mix" preload="auto" src="${audio}"></audio>`:''}
<script>window.MOTION_CONFIG=${script(JSON.stringify(publicConfig))};window.MOTION_ASSETS=${script(JSON.stringify(assets))};</script>
<script>${script(visual)}</script><script>${script(player)}</script></body></html>`;
  await claimArtifacts(c);await fs.writeFile(c.files.html,html);
  await writeJSON(path.join(c.out,'bundle-manifest.json'),{title:c.title,files:c.names,configSHA256:c.configSHA256,width:c.width,height:c.height,fps:c.fps,duration:c.duration,frames:c.frames,htmlSHA256:sha(html),entrySHA256:sha(visual),audioSHA256:c.audio?sha(await fs.readFile(c.audio)):null,assetCount:Object.keys(assets).length,bytes:Buffer.byteLength(html)});
  console.log(c.files.html);
}
main().catch(fatal);
