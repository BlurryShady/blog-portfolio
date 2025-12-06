// ---------------- Avatar preview ----------------
(() => {
  const input = document.getElementById("id_avatar");
  const preview = document.getElementById("avatarPreview");
  if (!input || !preview) return;

  input.addEventListener("change", () => {
    const [file] = input.files || [];
    if (!file) return;
    if (!/^image\/(png|jpeg|webp)$/.test(file.type)) return;
    preview.src = URL.createObjectURL(file);
  });
})();

// ---------------- Delete modal ----------------
(() => {
  let deleteFormTarget = null;
  const modal = document.getElementById("deleteModal");
  const confirmBtn = document.getElementById("confirmDelete");
  const cancelBtn  = document.getElementById("cancelDelete");

  document.addEventListener("click", (e) => {
    const form = e.target.closest("form[data-comment-delete]");
    if (!form) return;
    e.preventDefault();
    deleteFormTarget = form;
    modal?.classList.remove("hidden");
  });

  confirmBtn?.addEventListener("click", () => {
    if (deleteFormTarget) deleteFormTarget.submit();
    modal?.classList.add("hidden");
    deleteFormTarget = null;
  });

  cancelBtn?.addEventListener("click", () => {
    deleteFormTarget = null;
    modal?.classList.add("hidden");
  });
})();

// ---------------- Starfield + eclipse (unchanged) ----------------
(() => {
  const cnv = document.getElementById("bg-stars");
  if (!cnv) return;
  const ctx = cnv.getContext("2d", { alpha: true });
  const DPR = Math.max(1, Math.min(2, window.devicePixelRatio || 1));
  let W = 0, H = 0;

  const STAR_COUNT = 160, SPARKLE_COUNT = 22, SHOOTING_PROB = 0.003;
  const stars = [];
  const sparkles = Array.from({ length: SPARKLE_COUNT }, () => ({ x:0, y:0, life:0, max:0 }));
  let shooting = null;

  const rnd = (a,b)=> a + Math.random()*(b-a);

  function resize() {
    W = cnv.width  = Math.floor(innerWidth  * DPR);
    H = cnv.height = Math.floor(innerHeight * DPR);
    cnv.style.width = innerWidth + "px";
    cnv.style.height = innerHeight + "px";
  }
  function makeStar(){ return { x:Math.random()*W, y:Math.random()*H, r:rnd(0.6,1.9)*DPR, base:rnd(0.2,0.65), phase:Math.random()*Math.PI*2, speed:rnd(0.002,0.012) }; }

  function init(){ resize(); stars.length=0; for(let i=0;i<STAR_COUNT;i++) stars.push(makeStar()); }
  function triggerSparkle(){ const s = sparkles.find(s=>s.life<=0); if(!s) return; s.x=Math.random()*W; s.y=Math.random()*H*0.7; s.max=rnd(18,36); s.life=s.max; }
  function maybeShoot(){ if (shooting || Math.random()>SHOOTING_PROB) return; shooting={ x:rnd(W*.2,W*.8), y:rnd(H*.1,H*.4), vx:rnd(-4,-2)*DPR, vy:rnd(1.2,2.2)*DPR, life:rnd(30,55) }; }

  function drawConstellations(){
    ctx.save();
    ctx.globalAlpha = 0.08;
    ctx.strokeStyle = "#7fd2ff";
    ctx.lineWidth = Math.max(0.6*DPR,0.6);
    for (let i=0;i<stars.length;i+=7){
      const a=stars[i], b=stars[(i+13)%stars.length];
      const d = Math.hypot(a.x-b.x, a.y-b.y);
      if (d < 120*DPR && a.y < H*.65 && b.y < H*.65){
        ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke();
      }
    }
    ctx.restore();
  }

  function frame(){
    ctx.clearRect(0,0,W,H);
    for (const s of stars){
      s.phase += s.speed;
      const a = s.base + (Math.sin(s.phase)*0.25 + 0.25);
      ctx.globalAlpha = a; ctx.fillStyle="#cfe7ff"; ctx.beginPath(); ctx.arc(s.x,s.y,s.r,0,Math.PI*2); ctx.fill();
      ctx.globalAlpha = a*0.35; ctx.fillStyle="#90caff"; ctx.beginPath(); ctx.arc(s.x,s.y,s.r*2.2,0,Math.PI*2); ctx.fill();
    }
    if (Math.random()<0.04) triggerSparkle();
    for (const sp of sparkles){
      if (sp.life>0){
        const t=1-Math.abs((sp.life/sp.max)*2-1);
        ctx.globalAlpha=0.35+t*0.45; ctx.fillStyle="#e6f4ff";
        const r=(1+t*2.5)*DPR; ctx.beginPath(); ctx.arc(sp.x,sp.y,r,0,Math.PI*2); ctx.fill(); sp.life--;
      }
    }
    maybeShoot();
    if (shooting){
      ctx.globalAlpha = 0.9; ctx.strokeStyle="#e8f6ff"; ctx.lineWidth=Math.max(1.2*DPR,1);
      ctx.beginPath(); ctx.moveTo(shooting.x,shooting.y); ctx.lineTo(shooting.x - shooting.vx*6, shooting.y - shooting.vy*6); ctx.stroke();
      shooting.x += shooting.vx; shooting.y += shooting.vy; if(--shooting.life<=0) shooting=null;
    }
    drawConstellations();
    requestAnimationFrame(frame);
  }

  window.addEventListener("resize", init, { passive:true });
  init(); frame();
})();

// ---------------- Theme toggle (button in nav) ----------------
(() => {
  const THEMES = ["cyan","crimson"];       // names used in CSS: body[data-theme="..."]
  const root = document.body;

  const saved = localStorage.getItem("bs-theme");
  if (saved && THEMES.includes(saved)) root.setAttribute("data-theme", saved);
  else root.setAttribute("data-theme", "cyan");

  const btn = document.querySelector("[data-theme-toggle]") || document.getElementById("themeBtn");
  function cycle(){
    const cur = root.getAttribute("data-theme") || "cyan";
    const next = cur === "crimson" ? "cyan" : "crimson";
    root.setAttribute("data-theme", next);
    localStorage.setItem("bs-theme", next);
  }
  btn?.addEventListener("click", (e)=>{ e.preventDefault(); cycle(); });
})();
