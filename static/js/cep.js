
document.addEventListener('DOMContentLoaded',()=>{
  const fillFromCEP = async (inp)=>{
    const cep=(inp.value||'').replace(/\D/g,'');
    if(cep.length!==8) return;
    try{
      const res = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
      const data = await res.json();
      if(data && !data.erro){
        const form = inp.closest('form'); if(!form) return;
        const set=(n,v)=>{const el=form.querySelector(`[name=${n}]`); if(el && !el.value) el.value=v||'';};
        set('logradouro', data.logradouro); set('bairro', data.bairro); set('cidade', data.localidade); set('uf', data.uf);
      }
    }catch(e){ console.warn('CEP lookup falhou', e); }
  };
  document.querySelectorAll('input[data-cep="1"]').forEach(inp=>{
    ['blur','change','keyup'].forEach(evt=> inp.addEventListener(evt, ()=>{
      const d=(inp.value||'').replace(/\D/g,''); if(d.length===8) fillFromCEP(inp);
    }));
  });
});
