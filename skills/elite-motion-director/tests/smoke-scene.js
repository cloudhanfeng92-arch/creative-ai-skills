/* Integration-only scene. Never reuse its visual design as a user film. */
window.createScene=(stage,c)=>{
 const canvas=document.createElement('canvas');canvas.width=c.width;canvas.height=c.height;stage.appendChild(canvas);const x=canvas.getContext('2d');
 function render(t){
  const w=c.width,h=c.height;x.fillStyle='#edf0ee';x.fillRect(0,0,w,h);
  const u=Math.max(0,Math.min(1,t/c.duration)),e=u*u*(3-2*u);
  x.strokeStyle='#293833';x.lineWidth=2;x.beginPath();x.moveTo(w*.16,h*.7);x.lineTo(w*.84,h*.7);x.stroke();
  x.fillStyle='#1c4034';x.beginPath();x.arc(w*(.22+.54*e),h*.58,h*.12,0,Math.PI*2);x.fill();
  x.fillStyle='#293833';x.font=`700 ${Math.round(h*.085)}px sans-serif`;x.textAlign='left';x.fillText('相遇的轨迹',w*.12,h*.23);
 }
 return {ready:Promise.resolve(),render,cover:()=>render(c.duration*.5)};
};
