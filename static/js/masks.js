
function maskCNPJ(v){v=v.replace(/\D/g,'').slice(0,14);if(v.length<=12)return v.replace(/(\d{2})(\d{3})(\d{3})(\d{0,4})/,'$1.$2.$3/$4');return v.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{0,2})/,'$1.$2.$3/$4-$5');}
function maskCPF(v){v=v.replace(/\D/g,'').slice(0,11);return v.replace(/(\d{3})(\d{3})(\d{3})(\d{0,2})/,'$1.$2.$3-$4');}
function maskPhone(v){v=v.replace(/\D/g,'').slice(0,11);if(v.length>10)return v.replace(/(\d{2})(\d{1})(\d{4})(\d{0,4})/,'($1) $2$3-$4');return v.replace(/(\d{2})(\d{4})(\d{0,4})/,'($1) $2-$3');}
function maskMoney(v){v=(v||'').toString().replace(/\D/g,'');if(!v)return'';const num=parseInt(v,10);return (num/100).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});}
function applyMask(el){const type=el.getAttribute('data-mask');const h=(e)=>{let v=e.target.value||'';if(type==='cnpj')e.target.value=maskCNPJ(v);else if(type==='cpf')e.target.value=maskCPF(v);else if(type==='phone')e.target.value=maskPhone(v);else if(type==='money')e.target.value=maskMoney(v);};['input','blur','change'].forEach(evt=>el.addEventListener(evt,h));h({target:el});}
document.addEventListener('DOMContentLoaded',()=>{document.querySelectorAll('[data-mask]').forEach(applyMask);});
