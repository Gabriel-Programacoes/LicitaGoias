const output = document.getElementById('message');
const token = new URLSearchParams(location.search).get('token') || '';
fetch('/v1/email/unsubscribe', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({token}),
}).then(() => {
  output.textContent = 'Solicitação processada. Se o link era válido, suas notificações foram desativadas.';
}).catch(() => {
  output.textContent = 'Não foi possível concluir agora. Tente novamente mais tarde.';
});
