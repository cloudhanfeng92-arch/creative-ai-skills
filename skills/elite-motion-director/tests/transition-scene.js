/* Integration fixture, NOT a user film, composition template or default style.
 * The harness bundles engine/motion.mjs into window.MotionKit before this file.
 */
window.createScene=(stage,c)=>{
 const canvas=document.createElement('canvas');canvas.width=c.width;canvas.height=c.height;
 stage.appendChild(canvas);const ctx=canvas.getContext('2d'),M=window.MotionKit;
 if(!M)throw new Error('Test harness must provide MotionKit');
 function render(t){
  const w=c.width,h=c.height,b=M.bridgeState(t,c.duration*.3,c.duration*.42);
  const point=M.handoff2D(t,{start:0,duration:c.duration,from:{x:w*.22,y:h*.57},to:{x:w*.76,y:h*.4}});
  // The outgoing scene remains present until the incoming mask fully covers it.
  ctx.fillStyle='#122139';ctx.fillRect(0,0,w,h);
  ctx.strokeStyle='#4b7290';ctx.lineWidth=1;
  ctx.beginPath();ctx.moveTo(w*.12,h*.72);ctx.lineTo(w*.9,h*.72);ctx.stroke();
  ctx.font=`600 ${Math.round(h*.10)}px sans-serif`;ctx.textAlign='left';ctx.fillStyle='#edf5f4';
  ctx.fillText('相遇的轨迹',w*.12,h*.24);
  if(b.incomingVisible){
   ctx.save();ctx.beginPath();ctx.arc(point.x,point.y,M.coveringCircleRadius(w,h,point.x,point.y)*b.eased,0,Math.PI*2);ctx.clip();
   ctx.fillStyle='#dde8e2';ctx.fillRect(0,0,w,h);ctx.fillStyle='#193f43';
   ctx.font=`600 ${Math.round(h*.10)}px sans-serif`;ctx.fillText('轨迹，继续延伸',w*.12,h*.80);
   ctx.strokeStyle='#567773';ctx.beginPath();ctx.moveTo(w*.1,h*.4);ctx.lineTo(w*.89,h*.4);ctx.stroke();ctx.restore();
  }
  // Shared object is drawn once, above both scenes, from the same absolute t.
  ctx.fillStyle='#d17c42';ctx.beginPath();ctx.arc(point.x,point.y,h*.065,0,Math.PI*2);ctx.fill();
 }
 return {ready:Promise.resolve(),render,cover:()=>render(c.duration*.9)};
};
