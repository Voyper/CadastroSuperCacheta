// Máscara para CPF
document.querySelector('.field-cpf').addEventListener('input', function () {
  let v = this.value.replace(/\D/g, '');
  v = v.slice(0, 11);
  v = v.replace(/(\d{3})(\d)/, '$1.$2');
  v = v.replace(/(\d{3})(\d)/, '$1.$2');
  v = v.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
  this.value = v;
});

// Máscara para telefone
document.querySelector('.field-contact').addEventListener('input', function () {
  let v = this.value.replace(/\D/g, '');
  v = v.slice(0, 11);
  v = v.replace(/^(\d{2})(\d)/g, '($1) $2');
  v = v.replace(/(\d{5})(\d)/, '$1-$2');
  v = v.slice(0, 15);
  this.value = v;
});


// Etapa 1: Envio do formulário de cadastro
document.getElementById('cadastroForm').addEventListener('submit', function (e) {
  //e.preventDefault()

  const senha = document.querySelector('.field-password').value;
  const confirmarSenha = document.querySelector('.field-confirm').value;

  if (senha.length < 6 || senha.length > 12) {
    alert('A senha deve ter entre 6 e 12 caracteres.');
    return;
  }

  if (!/\d/.test(senha)) {
    alert('A senha deve conter pelo menos um número.');
    return;
  }

  if (senha !== confirmarSenha) {
    alert('As senhas não coincidem.');
    return;
  }


  // Oculta formulário, mostra verificação (etapa 2)
  //document.getElementById('cadastroForm').style.display = 'none';
  //document.getElementById('verificacaoContainer').style.display = 'block';
});

// Etapa 2: Escolha do método de envio do código
//document.getElementById('btnEnviarCodigo').addEventListener('click', function () {
  //const metodo = document.querySelector('input[name="metodo_envio"]:checked').value;

 // alert("Código será enviado via: " + metodo);

  // Oculta tela de escolha, mostra código (etapa 3)
  //document.getElementById('verificacaoContainer').style.display = 'none';
  //document.getElementById('codigoContainer').style.display = 'block';
});


// Auto-tab nos campos de código de verificação
const codigoInputs = document.querySelectorAll('.code-digit');

codigoInputs.forEach((input, index) => {
  input.addEventListener('input', () => {
    // Apenas números
    input.value = input.value.replace(/\D/g, '');

    if (input.value && index < codigoInputs.length - 1) {
      codigoInputs[index + 1].focus();
    }
  });

  // Permitir backspace para o campo anterior
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Backspace' && !input.value && index > 0) {
      codigoInputs[index - 1].focus();
    }
  });
});
