document.addEventListener("DOMContentLoaded", function () {
    const messagesContainer = document.querySelector('#messages_container');
    const messages = document.querySelectorAll('.message');

    // Função para esconder as mensagens após 7 segundos
    function hideMessage(message) {
        setTimeout(function () {
            message.style.display = 'none';

            // Verifica se o container não tem filhos e o esconde
            if (messagesContainer && messagesContainer.children.length === 0) {
                messagesContainer.style.display = 'none'; // Esconde o container se não houver mais mensagens
            }
        }, 7000);
    }

    // Esconde as mensagens existentes
    messages.forEach(function (message) {
        hideMessage(message);
    });

    // Usando MutationObserver para observar novas mensagens sendo adicionadas
    const observer = new MutationObserver(function (mutationsList) {
        for (let mutation of mutationsList) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function (node) {
                    if (node.classList && node.classList.contains('message')) {
                        hideMessage(node); // Esconde a nova mensagem após 5 segundos
                    }
                });
            }
        }
    });

    // Configura o MutationObserver para observar a adição de novos filhos
    observer.observe(messagesContainer, { childList: true });
});
