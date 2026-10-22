/* Single time authority. Visuals live in window.createScene, not this player. */
(() => {
  const c=window.MOTION_CONFIG, stage=document.getElementById('stage');
  const outer=document.getElementById('viewport'), controls=document.getElementById('controls');
  const play=document.getElementById('play'), restart=document.getElementById('restart');
  const scrub=document.getElementById('scrub'), stamp=document.getElementById('stamp');
  const audio=document.getElementById('mix');
  let scene=null, playing=false,t=0,anchor=0,anchorTime=0,raf=0;
  const clamp=x=>Math.max(0,Math.min(c.duration,Number(x)||0));
  function fit(){
    const exporting=document.documentElement.dataset.export==='1';
    const aw=exporting?c.width:window.innerWidth, ah=exporting?c.height:Math.max(1,window.innerHeight-controls.offsetHeight);
    const s=Math.min(aw/c.width,ah/c.height);
    outer.style.width=`${c.width*s}px`;outer.style.height=`${c.height*s}px`;
    stage.style.transform=`scale(${s})`;
  }
  function display(){scrub.value=t;stamp.textContent=`${t.toFixed(1)} / ${c.duration.toFixed(1)}`;play.textContent=playing?'❚❚':'▶';}
  async function draw(time){t=clamp(time); await scene.render(t);display();}
  function pause(){playing=false;audio?.pause();cancelAnimationFrame(raf);display();}
  async function tick(now){
    if(!playing)return;
    const current=audio?audio.currentTime:anchorTime+(now-anchor)/1000;
    await draw(current);
    if(t>=c.duration-0.0001 || audio?.ended){pause();return;}
    if(playing)raf=requestAnimationFrame(tick);
  }
  async function start(){
    await api.ready;
    if(t>=c.duration-0.02)await seek(0);
    if(audio){audio.currentTime=t;await audio.play();}
    anchor=performance.now();anchorTime=t;playing=true;display();raf=requestAnimationFrame(tick);
  }
  async function seek(time){
    const resume=playing;pause();t=clamp(time);if(audio)audio.currentTime=t;
    await draw(t);if(resume)await start();
  }
  const api=window.__motion={
    ready:null,
    duration:c.duration,width:c.width,height:c.height,fps:c.fps,
    render:async time=>{await api.ready;await draw(time);},
    cover:async()=>{await api.ready;if(scene.cover)await scene.cover();else await draw(c.coverTime);},
    pause,play:start,seek,
    exportMode:()=>{pause();document.documentElement.dataset.export='1';fit();},
    state:()=>({time:t,playing,audioTime:audio?.currentTime??null})
  };
  window.seek=api.render;
  api.ready=(async()=>{
    if(typeof window.createScene!=='function')throw new Error('缺少createScene：画面代码未实现或打包失败');
    scene=await window.createScene(stage,c,window.MOTION_ASSETS||{});
    if(typeof scene?.render!=='function')throw new Error('createScene必须返回render(t)');
    await scene.ready;await document.fonts?.ready;
    for(const image of stage.querySelectorAll('img')){if(!image.complete)await image.decode();if(!image.naturalWidth)throw new Error('图片资源加载失败');}
    await scene.render(0);display();fit();
  })();
  scrub.max=c.duration; scrub.step=1/c.fps;
  play.addEventListener('click',()=>{if(playing)pause();else start().catch(console.error);});
  restart.addEventListener('click',async()=>{pause();await seek(0);await start();});
  scrub.addEventListener('input',()=>seek(scrub.value).catch(console.error));
  audio?.addEventListener('ended',()=>{pause();draw(c.duration).catch(console.error);});
  window.addEventListener('resize',fit);
  document.addEventListener('keydown',e=>{if(e.code==='Space'&&!['INPUT','BUTTON'].includes(document.activeElement.tagName)){e.preventDefault();play.click();}});
})();
