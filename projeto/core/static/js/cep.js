// Arquivo: static/js/cep.js

function buscaCep() {
    let cep = document.getElementById('id_cep').value;
    if (cep !== "") {
        let url = "https://brasilapi.com.br/api/cep/v1/" + cep;

        let req = new XMLHttpRequest();
        req.open("GET", url);
        req.send();

        // Tratar a resposta
        req.onload = function() {
            if (req.status === 200) {
                let endereco = JSON.parse(req.responseText);
                document.getElementById('id_rua').value = endereco.street;
                document.getElementById('id_bairro').value = endereco.neighborhood;
                document.getElementById('id_cidade').value = endereco.city;
                document.getElementById('id_estado').value = endereco.state;
                document.getElementById('id_numero').focus();
            } else if (req.status === 404) {
                alert("CEP não encontrado");
            } else {
                alert("Erro ao fazer a requisição");
            }
        };

        req.onerror = function() {
            alert("Erro ao fazer a requisição");
        };
    }
}

window.onload = function() {
    let btnBuscarCep = document.getElementsByClassName('btn_buscar_cep');
    for (let i = 0; i < btnBuscarCep.length; i++) {
        btnBuscarCep[i].addEventListener('click', buscaCep);
    }
};
