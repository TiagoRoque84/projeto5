
document.addEventListener('DOMContentLoaded',()=>{
  document.querySelectorAll('input[data-cnpj="1"]').forEach(inp=>{
    const fetchCNPJ = async ()=>{
      const cnpj=(inp.value||'').replace(/\D/g,''); if(cnpj.length!==14) return;
      try{
        const r = await fetch(`https://brasilapi.com.br/api/cnpj/v1/${cnpj}`);
        const data = await r.json();
        if(data && !data.error){
          const form = inp.closest('form'); if(!form) return;
          const set=(n,v)=>{const el=form.querySelector(`[name="${n}"]`); if(el && (!el.value || el.value.trim()==='')) el.value=v||''; };
          set('razao_social', data.razao_social || data.nome || '');
          set('nome_fantasia', data.nome_fantasia || '');
          set('cep', (data.cep||'').replace(/\D/g,''));
          set('logradouro', data.logradouro||''); set('numero', data.numero||''); set('complemento', data.complemento||'');
          set('bairro', data.bairro||''); set('cidade', data.municipio||''); set('uf', data.uf||'');
        }
      }catch(e){ console.warn('CNPJ lookup', e); }
    };
    ['blur','change'].forEach(evt=> inp.addEventListener(evt, fetchCNPJ));
  });
});
